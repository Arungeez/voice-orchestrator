"""
Database Seeder
---------------
Run this script once to populate MongoDB with:
  - 2 companies (Apex Realty, UrbanNest Rentals)
  - 5 leads total (3 for Apex, 2 for UrbanNest)

Usage:
  python -m backend.seed
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/voice_orchestrator")
DB_NAME = "voice_orchestrator"


COMPANIES = [
    {
        "name": "Apex Realty",
        "industry": "Real Estate - Property Sales",
        "vapi_assistant_id": "",
        "system_prompt": (
            "You are a friendly AI assistant calling on behalf of Apex Realty, a premium real estate agency. "
            "Your goal is to qualify leads who are interested in buying or selling a property. "
            "Ask the customer: 1) Are they looking to buy or sell? 2) What type of property? "
            "3) What is their timeline? 4) What is their budget range? "
            "Be warm, professional, and concise. Do not pressure the customer."
        ),
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "UrbanNest Rentals",
        "industry": "Real Estate - Property Rentals",
        "vapi_assistant_id": "",
        "system_prompt": (
            "You are a helpful AI assistant calling on behalf of UrbanNest Rentals, a rental property agency. "
            "Your goal is to qualify leads who are looking to rent an apartment or house. "
            "Ask the customer: 1) Are they looking to rent? 2) How many bedrooms? "
            "3) Which neighborhoods interest them? 4) When do they need to move in? "
            "Keep the conversation friendly and under 3 minutes."
        ),
        "created_at": datetime.now(timezone.utc),
    },
]

CUSTOMERS_TEMPLATE = [
    # Apex Realty leads
    {"company_key": "Apex Realty",      "name": "James Carter", "phone_number": "+10000000001"},
    {"company_key": "Apex Realty",      "name": "Priya Sharma", "phone_number": "+10000000002"},
    {"company_key": "Apex Realty",      "name": "Marcus Webb",  "phone_number": "+10000000003"},
    # UrbanNest Rentals leads
    {"company_key": "UrbanNest Rentals","name": "Elena Russo",  "phone_number": "+10000000004"},
    {"company_key": "UrbanNest Rentals","name": "David Kim",    "phone_number": "+10000000005"},
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]

    print("Starting database seed...")

    # Clear existing data
    await db.companies.delete_many({})
    await db.customers.delete_many({})
    await db.call_logs.delete_many({})
    print("Cleared existing collections")

    # Insert companies
    await db.companies.insert_many(COMPANIES)
    print("Inserted 2 companies")

    # Build lookup: company name -> ObjectId string
    company_map = {}
    async for company in db.companies.find({}):
        company_map[company["name"]] = str(company["_id"])

    # Insert customers
    customers = []
    for tmpl in CUSTOMERS_TEMPLATE:
        company_id = company_map.get(tmpl["company_key"])
        if not company_id:
            print(f"  WARNING: Company '{tmpl['company_key']}' not found, skipping {tmpl['name']}")
            continue
        customers.append({
            "company_id": company_id,
            "name": tmpl["name"],
            "phone_number": tmpl["phone_number"],
            "status": "PENDING",
            "call_id": None,
            "llm_confidence": None,
            "last_called_at": None,
            "created_at": datetime.now(timezone.utc),
        })

    await db.customers.insert_many(customers)
    print(f"Inserted {len(customers)} customers")

    print("\nSummary:")
    for name, cid in company_map.items():
        count = await db.customers.count_documents({"company_id": cid})
        print(f"  {name}: {count} leads  (id={cid})")

    print("\nDatabase seeded successfully!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
