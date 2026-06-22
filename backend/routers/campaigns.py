from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

from backend.agents.dispatch_graph import run_dispatch

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


class CampaignTriggerRequest(BaseModel):
    company_id: str


@router.post("/trigger")
async def trigger_campaign(request: CampaignTriggerRequest):
    """
    Start an outbound voice campaign for a company.
    Runs the LangGraph dispatch graph which:
    1. Fetches all PENDING leads
    2. Dynamically loads company's AI prompt
    3. Triggers Vapi calls for each lead
    4. Updates statuses and broadcasts WebSocket events
    """
    if not request.company_id:
        raise HTTPException(status_code=400, detail="company_id is required")

    try:
        result = await run_dispatch(company_id=request.company_id)

        dispatched_count = len(result.get("dispatched", []))
        errors = result.get("errors", [])

        return {
            "message": f"Campaign dispatched — {dispatched_count} calls initiated",
            "dispatched_count": dispatched_count,
            "dispatched": result.get("dispatched", []),
            "errors": errors,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign failed: {str(e)}")
