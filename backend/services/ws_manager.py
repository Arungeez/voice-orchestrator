from fastapi import WebSocket
from typing import Dict, List
import asyncio
import json


class ConnectionManager:
    """
    Manages WebSocket connections keyed by company_id.
    Allows broadcasting live lead status updates only to
    clients viewing the relevant company dashboard.
    """

    def __init__(self):
        # company_id → list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, company_id: str):
        await websocket.accept()
        if company_id not in self.active_connections:
            self.active_connections[company_id] = []
        self.active_connections[company_id].append(websocket)
        print(f"🔌 WS connected: company={company_id}, total={len(self.active_connections[company_id])}")

    def disconnect(self, websocket: WebSocket, company_id: str):
        if company_id in self.active_connections:
            self.active_connections[company_id] = [
                ws for ws in self.active_connections[company_id] if ws != websocket
            ]
        print(f"🔌 WS disconnected: company={company_id}")

    async def broadcast_to_company(self, company_id: str, data: dict):
        """Push a JSON message to all clients watching this company."""
        connections = self.active_connections.get(company_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        # Clean up dead connections
        for ws in dead:
            self.disconnect(ws, company_id)

    async def broadcast_all(self, data: dict):
        """Push a JSON message to every connected client."""
        for company_id in list(self.active_connections.keys()):
            await self.broadcast_to_company(company_id, data)


# Singleton instance — imported by routers and agents
manager = ConnectionManager()
