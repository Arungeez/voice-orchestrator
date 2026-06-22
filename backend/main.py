"""
Multi-Tenant Agentic Voice Orchestrator -- FastAPI Backend
"""

import sys
import os

# Fix Windows console encoding for emoji characters in print() statements
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from backend.services.db_service import connect_db, close_db
from backend.routers import companies, leads, campaigns, webhooks, call_logs, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — connect/disconnect MongoDB."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Voice Orchestrator API",
    description="Multi-Tenant Agentic Voice AI SaaS — Lead Qualification Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API Routers ───────────────────────────────────────────────────
app.include_router(companies.router)
app.include_router(leads.router)
app.include_router(campaigns.router)
app.include_router(webhooks.router)
app.include_router(call_logs.router)
app.include_router(ws.router)


# ─── Health Check ──────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok", "service": "voice-orchestrator"}


# ─── Serve React Frontend (Production) ─────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react(full_path: str):
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)
