"""
LangGraph Evaluation Graph
───────────────────────────
Triggered when Vapi sends a webhook after a call ends.

Flow:
  START
    → load_call_context_node    (find lead by call_id in DB)
    → evaluate_transcript_node  (send transcript to OpenAI, get structured result)
    → human_loop_check_node     (if confidence < 0.60 → NEEDS_REVIEW)
    → state_update_node         (write final status to DB, save call log, broadcast WS)
  END
"""

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime

from backend.services import db_service
from backend.services.llm_service import evaluate_transcript, CONFIDENCE_THRESHOLD
from backend.services.ws_manager import manager
from backend.models.customer import LeadStatus


# ─── State Schema ──────────────────────────────────────────────────

class EvaluationState(TypedDict):
    call_id: str
    transcript: str
    transcript_messages: List[dict]
    summary: str
    duration_seconds: Optional[int]
    lead: Optional[dict]
    company: Optional[dict]
    llm_outcome: str
    llm_reasoning: str
    llm_confidence: float
    key_signals: List[str]
    final_status: str
    error: Optional[str]


# ─── Node 1: Load Call Context ──────────────────────────────────────

async def load_call_context_node(state: EvaluationState) -> EvaluationState:
    """Find the lead associated with this call_id."""
    lead = await db_service.get_lead_by_call_id(state["call_id"])
    if not lead:
        print(f"⚠️ No lead found for call_id={state['call_id']}")
        return {**state, "error": f"Lead not found for call_id {state['call_id']}"}

    company = await db_service.get_company_by_id(lead["company_id"])
    print(f"🔍 Evaluation context loaded: lead={lead.get('name')}, company={company.get('name') if company else 'unknown'}")
    return {**state, "lead": lead, "company": company}


# ─── Node 2: Evaluate Transcript ────────────────────────────────────

async def evaluate_transcript_node(state: EvaluationState) -> EvaluationState:
    """Send the transcript to OpenAI and get a structured evaluation."""
    if state.get("error"):
        return state  # Skip if context loading failed

    company = state.get("company") or {}
    result = await evaluate_transcript(
        transcript=state.get("transcript", ""),
        summary=state.get("summary", ""),
        company_name=company.get("name", "Unknown Company"),
        company_industry=company.get("industry", "Real Estate"),
    )

    print(f"🤖 LLM result: outcome={result.outcome}, confidence={result.confidence:.2f}")

    return {
        **state,
        "llm_outcome": result.outcome,
        "llm_reasoning": result.reasoning,
        "llm_confidence": result.confidence,
        "key_signals": result.key_signals,
    }


# ─── Node 3: Human-in-Loop Check ────────────────────────────────────

async def human_loop_check_node(state: EvaluationState) -> EvaluationState:
    """
    If the LLM confidence is below the threshold (60%),
    flag the lead for human review instead of auto-classifying.
    """
    if state.get("error"):
        return {**state, "final_status": LeadStatus.FAILED.value}

    confidence = state.get("llm_confidence", 0.0)

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"⚠️ Low confidence ({confidence:.0%}) → NEEDS_REVIEW")
        return {**state, "final_status": LeadStatus.NEEDS_REVIEW.value}
    else:
        final = state.get("llm_outcome", "NOT_INTERESTED")
        status = (
            LeadStatus.QUALIFIED.value
            if final == "QUALIFIED"
            else LeadStatus.NOT_INTERESTED.value
        )
        return {**state, "final_status": status}


# ─── Node 4: State Update ────────────────────────────────────────────

async def state_update_node(state: EvaluationState) -> EvaluationState:
    """
    1. Update lead status in DB
    2. Save full call log document
    3. Broadcast real-time update via WebSocket
    """
    lead = state.get("lead")
    if not lead:
        return state

    lead_id = lead["_id"]
    company_id = lead["company_id"]
    final_status = state.get("final_status", LeadStatus.FAILED.value)
    confidence = state.get("llm_confidence", 0.0)

    # Update customer document
    await db_service.update_lead_status(
        lead_id=lead_id,
        status=final_status,
        llm_confidence=confidence,
    )

    # Save detailed call log
    await db_service.create_call_log({
        "customer_id": lead_id,
        "company_id": company_id,
        "call_id": state["call_id"],
        "transcript": state.get("transcript", ""),
        "transcript_messages": state.get("transcript_messages", []),
        "summary": state.get("summary", ""),
        "llm_reasoning": state.get("llm_reasoning", ""),
        "llm_confidence": confidence,
        "key_signals": state.get("key_signals", []),
        "outcome": final_status,
        "duration_seconds": state.get("duration_seconds"),
    })

    # Broadcast live WebSocket update to dashboard
    await manager.broadcast_to_company(
        company_id=company_id,
        data={
            "type": "lead_update",
            "lead_id": lead_id,
            "new_status": final_status,
            "llm_confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    print(f"✅ Lead {lead.get('name')} updated → {final_status} (confidence: {confidence:.0%})")
    return state


# ─── Build the Graph ────────────────────────────────────────────────

def build_evaluation_graph():
    graph = StateGraph(EvaluationState)

    graph.add_node("load_context", load_call_context_node)
    graph.add_node("evaluate_transcript", evaluate_transcript_node)
    graph.add_node("human_loop_check", human_loop_check_node)
    graph.add_node("state_update", state_update_node)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "evaluate_transcript")
    graph.add_edge("evaluate_transcript", "human_loop_check")
    graph.add_edge("human_loop_check", "state_update")
    graph.add_edge("state_update", END)

    return graph.compile()


evaluation_graph = build_evaluation_graph()


async def run_evaluation(
    call_id: str,
    transcript: str,
    transcript_messages: list,
    summary: str,
    duration_seconds: int = None,
) -> dict:
    """Entry point called by the webhook router."""
    initial_state: EvaluationState = {
        "call_id": call_id,
        "transcript": transcript,
        "transcript_messages": transcript_messages,
        "summary": summary,
        "duration_seconds": duration_seconds,
        "lead": None,
        "company": None,
        "llm_outcome": "",
        "llm_reasoning": "",
        "llm_confidence": 0.0,
        "key_signals": [],
        "final_status": "",
        "error": None,
    }
    result = await evaluation_graph.ainvoke(initial_state)
    return result
