"""Production Replay Platform — FastAPI + HTML UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .redaction import redact_incident
from .replay import build_brief, build_replay_scaffold
from .store import store

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="Production Replay Platform",
    description="Redacted incident packs + safe replay scaffolds",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "incidents": len(store.list())}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(html_path.read_text())


@app.post("/incidents")
def create_incident(payload: dict[str, Any]) -> dict[str, Any]:
    """Accept request metadata/headers/body/logs, redact, store as JSON pack."""
    redacted = redact_incident(payload)
    pack = store.create(redacted)
    return {"ok": True, "incident": pack}


@app.get("/incidents")
def list_incidents() -> dict[str, Any]:
    return {"incidents": store.list()}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return pack


@app.post("/incidents/{incident_id}/replay-scaffold")
def replay_scaffold(incident_id: str) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return build_replay_scaffold(pack)


@app.post("/incidents/{incident_id}/brief")
def incident_brief(incident_id: str) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return build_brief(pack)


# Alias collector-style path
@app.post("/collector/incidents")
def collector_create(payload: dict[str, Any]) -> dict[str, Any]:
    return create_incident(payload)
