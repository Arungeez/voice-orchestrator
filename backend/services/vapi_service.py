import os
import httpx
from typing import Optional

VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "")
VAPI_BASE_URL = "https://api.vapi.ai"


async def initiate_outbound_call(
    phone_number: str,
    customer_name: str,
    company_name: str,
    company_prompt: str,
    vapi_assistant_id: str,
) -> Optional[dict]:
    """
    Trigger an outbound AI voice call via Vapi.ai REST API.
    Injects customer and company context dynamically.
    """
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": phone_number,
            "name": customer_name,
        },
        "assistantOverrides": {
            "variableValues": {
                "customer_name": customer_name,
                "company_name": company_name,
                "company_prompt": company_prompt,
            },
            "firstMessage": (
                f"Hi {customer_name}, this is an AI assistant calling on behalf of "
                f"{company_name}. Do you have a moment to chat about your property needs?"
            ),
        },
    }

    # Only include assistantId if it's set
    if vapi_assistant_id:
        payload["assistantId"] = vapi_assistant_id

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        response = await http_client.post(
            f"{VAPI_BASE_URL}/call",
            headers=headers,
            json=payload,
        )

    if response.status_code in (200, 201):
        data = response.json()
        return data
    else:
        print(f"❌ Vapi call failed [{response.status_code}]: {response.text}")
        return None


async def get_call_details(call_id: str) -> Optional[dict]:
    """Fetch call details from Vapi by call_id."""
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    async with httpx.AsyncClient(timeout=15.0) as http_client:
        response = await http_client.get(
            f"{VAPI_BASE_URL}/call/{call_id}",
            headers=headers,
        )
    if response.status_code == 200:
        return response.json()
    return None
