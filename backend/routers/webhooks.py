from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.agents.evaluation_graph import run_evaluation

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _parse_transcript_messages(artifact: dict) -> list:
    """Extract structured message list from Vapi artifact."""
    messages = []
    raw = artifact.get("messages", [])
    for msg in raw:
        role = msg.get("role", "")
        content = msg.get("message", msg.get("content", ""))
        if role in ("assistant", "user", "bot") and content:
            messages.append({
                "role": "assistant" if role in ("assistant", "bot") else "user",
                "content": content,
                "time": msg.get("time"),
            })
    return messages


@router.post("/vapi")
async def vapi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives real-time call events from Vapi.ai.
    Processes 'end-of-call-report' events by routing
    the transcript through the LangGraph evaluation workflow.
    
    Returns 200 immediately — processing happens in background.
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    message = payload.get("message", {})
    msg_type = message.get("type", "")

    print(f"📩 Vapi webhook received: type={msg_type}")

    if msg_type == "end-of-call-report":
        call_data = message.get("call", {})
        call_id = call_data.get("id", "")
        transcript = message.get("transcript", "")
        summary = message.get("summary", "")
        artifact = message.get("artifact", {})
        duration = call_data.get("endedAt")  # Will extract seconds below

        # Parse duration
        started_at = call_data.get("startedAt")
        ended_at = call_data.get("endedAt")
        duration_seconds = None
        if started_at and ended_at:
            try:
                from datetime import datetime
                fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
                s = datetime.strptime(started_at[:26] + "Z", fmt) if started_at else None
                e = datetime.strptime(ended_at[:26] + "Z", fmt) if ended_at else None
                if s and e:
                    duration_seconds = int((e - s).total_seconds())
            except Exception:
                pass

        transcript_messages = _parse_transcript_messages(artifact)

        if call_id:
            # Run evaluation in background so Vapi doesn't time out
            background_tasks.add_task(
                run_evaluation,
                call_id=call_id,
                transcript=transcript,
                transcript_messages=transcript_messages,
                summary=summary,
                duration_seconds=duration_seconds,
            )
            print(f"✅ Queued evaluation for call_id={call_id}")
        else:
            print("⚠️ Webhook missing call_id — skipping")

    # Always return 200 to Vapi
    return JSONResponse(status_code=200, content={"status": "received"})
