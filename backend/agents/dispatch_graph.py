"""
LangGraph Dispatch Graph
─────────────────────────
Triggered when admin clicks "Launch Campaign".

Flow:
  START
    → fetch_leads_node       (get all PENDING leads for company)
    → build_prompt_node      (load dynamic system_prompt from DB)
    → dispatch_calls_node    (call Vapi for each lead, update DB)
  END

State is passed forward through each node using TypedDict.
"""

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime

from backend.services import db_service, vapi_service
from backend.services.ws_manager import manager
from backend.models.customer import LeadStatus


# ─── State Schema ──────────────────────────────────────────────────

class DispatchState(TypedDict):
    company_id: str
    company_name: str
    company_industry: str
    company_prompt: str
    vapi_assistant_id: str
    leads: List[dict]
    dispatched: List[dict]
    errors: List[str]


# ─── Node 1: Fetch Leads ────────────────────────────────────────────

async def fetch_leads_node(state: DispatchState) -> DispatchState:
    """Fetch all PENDING leads for the given company."""
    leads = await db_service.get_pending_leads(state["company_id"])
    print(f"📋 Dispatch: found {len(leads)} pending leads for company {state['company_id']}")
    return {**state, "leads": leads}


# ─── Node 2: Build Prompt ───────────────────────────────────────────

async def build_prompt_node(state: DispatchState) -> DispatchState:
    """
    Dynamically load the company's system_prompt from the database.
    This ensures each tenant has a personalized AI voice script.
    """
    company = await db_service.get_company_by_id(state["company_id"])
    if not company:
        return {**state, "errors": state["errors"] + ["Company not found"]}

    return {
        **state,
        "company_name": company.get("name", ""),
        "company_industry": company.get("industry", ""),
        "company_prompt": company.get("system_prompt", ""),
        "vapi_assistant_id": company.get("vapi_assistant_id", ""),
    }


# ─── Node 3: Dispatch Calls ─────────────────────────────────────────

async def dispatch_calls_node(state: DispatchState) -> DispatchState:
    """
    For each PENDING lead:
    1. Trigger an outbound Vapi call
    2. Update lead status → CALL_INITIATED in DB
    3. Broadcast real-time update via WebSocket
    """
    dispatched = []
    errors = list(state.get("errors", []))

    for lead in state["leads"]:
        lead_id = lead["_id"]
        try:
            # Trigger Vapi outbound call with dynamic context
            call_result = await vapi_service.initiate_outbound_call(
                phone_number=lead["phone_number"],
                customer_name=lead["name"],
                company_name=state["company_name"],
                company_prompt=state["company_prompt"],
                vapi_assistant_id=state["vapi_assistant_id"],
            )

            if call_result:
                call_id = call_result.get("id", "")

                # Update lead in DB
                await db_service.update_lead_status(
                    lead_id=lead_id,
                    status=LeadStatus.CALL_INITIATED.value,
                    call_id=call_id,
                )

                # Broadcast live update to dashboard
                await manager.broadcast_to_company(
                    company_id=state["company_id"],
                    data={
                        "type": "lead_update",
                        "lead_id": lead_id,
                        "new_status": LeadStatus.CALL_INITIATED.value,
                        "call_id": call_id,
                        "llm_confidence": None,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                dispatched.append({"lead_id": lead_id, "call_id": call_id})
                print(f"📞 Call initiated: lead={lead['name']}, call_id={call_id}")

            else:
                # Vapi call failed — mark lead as FAILED
                await db_service.update_lead_status(
                    lead_id=lead_id,
                    status=LeadStatus.FAILED.value,
                )
                await manager.broadcast_to_company(
                    company_id=state["company_id"],
                    data={
                        "type": "lead_update",
                        "lead_id": lead_id,
                        "new_status": LeadStatus.FAILED.value,
                        "llm_confidence": None,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                errors.append(f"Vapi call failed for lead {lead['name']}")

        except Exception as e:
            errors.append(f"Error dispatching lead {lead_id}: {str(e)}")
            print(f"❌ Dispatch error for lead {lead_id}: {e}")

    return {**state, "dispatched": dispatched, "errors": errors}


# ─── Build the Graph ────────────────────────────────────────────────

def build_dispatch_graph():
    graph = StateGraph(DispatchState)

    graph.add_node("fetch_leads", fetch_leads_node)
    graph.add_node("build_prompt", build_prompt_node)
    graph.add_node("dispatch_calls", dispatch_calls_node)

    graph.set_entry_point("fetch_leads")
    graph.add_edge("fetch_leads", "build_prompt")
    graph.add_edge("build_prompt", "dispatch_calls")
    graph.add_edge("dispatch_calls", END)

    return graph.compile()


dispatch_graph = build_dispatch_graph()


async def run_dispatch(company_id: str) -> dict:
    """Entry point called by the campaign router."""
    initial_state: DispatchState = {
        "company_id": company_id,
        "company_name": "",
        "company_industry": "",
        "company_prompt": "",
        "vapi_assistant_id": "",
        "leads": [],
        "dispatched": [],
        "errors": [],
    }
    result = await dispatch_graph.ainvoke(initial_state)
    return result
