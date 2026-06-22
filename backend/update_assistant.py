import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

async def update():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["voice_orchestrator"]
    result = await db.companies.update_many({}, {"$set": {"vapi_assistant_id": "d7f73b24-6890-4a38-8644-88543eea9891"}})
    print(f"Updated {result.modified_count} companies with assistant ID")
    client.close()

asyncio.run(update())
