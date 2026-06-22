import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from backend.models.customer import LeadStatus

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/voice_orchestrator")
DB_NAME = "voice_orchestrator"

client: Optional[AsyncIOMotorClient] = None


def get_database():
    return client[DB_NAME]


async def connect_db():
    global client
    client = AsyncIOMotorClient(MONGODB_URI)
    print("✅ Connected to MongoDB")


async def close_db():
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")


def _serialize(doc) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc["_id"] = str(doc["_id"])
    if "company_id" in doc and isinstance(doc["company_id"], ObjectId):
        doc["company_id"] = str(doc["company_id"])
    if "customer_id" in doc and isinstance(doc["customer_id"], ObjectId):
        doc["customer_id"] = str(doc["customer_id"])
    return doc


# ─────────────────────────── COMPANIES ────────────────────────────

async def get_all_companies() -> List[dict]:
    db = get_database()
    cursor = db.companies.find({})
    return [_serialize(doc) async for doc in cursor]


async def get_company_by_id(company_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db.companies.find_one({"_id": ObjectId(company_id)})
    return _serialize(doc) if doc else None


# ─────────────────────────── CUSTOMERS ────────────────────────────

async def get_leads_by_company(company_id: str) -> List[dict]:
    db = get_database()
    cursor = db.customers.find({"company_id": company_id})
    return [_serialize(doc) async for doc in cursor]


async def get_pending_leads(company_id: str) -> List[dict]:
    db = get_database()
    cursor = db.customers.find({
        "company_id": company_id,
        "status": LeadStatus.PENDING.value
    })
    return [_serialize(doc) async for doc in cursor]


async def get_lead_by_id(lead_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db.customers.find_one({"_id": ObjectId(lead_id)})
    return _serialize(doc) if doc else None


async def get_lead_by_call_id(call_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db.customers.find_one({"call_id": call_id})
    return _serialize(doc) if doc else None


async def update_lead_status(
    lead_id: str,
    status: str,
    call_id: Optional[str] = None,
    llm_confidence: Optional[float] = None
) -> bool:
    db = get_database()
    update_fields = {
        "status": status,
        "last_called_at": datetime.utcnow()
    }
    if call_id:
        update_fields["call_id"] = call_id
    if llm_confidence is not None:
        update_fields["llm_confidence"] = llm_confidence

    result = await db.customers.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": update_fields}
    )
    return result.modified_count > 0


async def update_lead_by_id(lead_id: str, data: dict) -> bool:
    db = get_database()
    result = await db.customers.update_one(
        {"_id": ObjectId(lead_id)},
        {"$set": data}
    )
    return result.modified_count > 0


# ─────────────────────────── CALL LOGS ────────────────────────────

async def create_call_log(log_data: dict) -> str:
    db = get_database()
    log_data["created_at"] = datetime.utcnow()
    result = await db.call_logs.insert_one(log_data)
    return str(result.inserted_id)


async def get_call_logs_by_lead(customer_id: str) -> List[dict]:
    db = get_database()
    cursor = db.call_logs.find({"customer_id": customer_id}).sort("created_at", -1)
    return [_serialize(doc) async for doc in cursor]


async def get_call_log_by_call_id(call_id: str) -> Optional[dict]:
    db = get_database()
    doc = await db.call_logs.find_one({"call_id": call_id})
    return _serialize(doc) if doc else None
