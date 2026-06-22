from fastapi import APIRouter
from backend.services import db_service

router = APIRouter(prefix="/api/call-logs", tags=["call-logs"])


@router.get("/{lead_id}")
async def get_call_logs(lead_id: str):
    """Return all call logs for a specific lead."""
    logs = await db_service.get_call_logs_by_lead(lead_id)
    return {"call_logs": logs}
