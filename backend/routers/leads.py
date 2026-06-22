from fastapi import APIRouter, HTTPException, Query
from backend.services import db_service
from backend.models.customer import CustomerUpdate

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("/")
async def list_leads(company_id: str = Query(..., description="Company ID to filter leads")):
    """Return all leads for a specific company."""
    leads = await db_service.get_leads_by_company(company_id)
    return {"leads": leads}


@router.get("/{lead_id}")
async def get_lead(lead_id: str):
    """Return a single lead by ID."""
    lead = await db_service.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}")
async def update_lead(lead_id: str, update: CustomerUpdate):
    """Manually update a lead's status (e.g., admin override for NEEDS_REVIEW)."""
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")

    # Serialize enum values
    if "status" in update_data and hasattr(update_data["status"], "value"):
        update_data["status"] = update_data["status"].value

    success = await db_service.update_lead_by_id(lead_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found or not updated")
    return {"message": "Lead updated successfully"}
