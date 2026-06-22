from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.services.ws_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket, company_id: str = Query(...)):
    """
    WebSocket endpoint for real-time lead status updates.
    Clients connect with ?company_id=X and receive push notifications
    when any lead's status changes for that company.
    """
    await manager.connect(websocket, company_id)
    try:
        while True:
            # Keep connection alive — wait for client pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, company_id)
