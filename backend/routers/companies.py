from fastapi import APIRouter
from backend.services import db_service

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("/")
async def list_companies():
    """Return all tenant companies."""
    companies = await db_service.get_all_companies()
    return {"companies": companies}


@router.get("/{company_id}")
async def get_company(company_id: str):
    """Return a single company by ID."""
    company = await db_service.get_company_by_id(company_id)
    if not company:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Company not found")
    return company
