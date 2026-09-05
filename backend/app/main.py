"""Production Replay Platform — FastAPI + landing + product UI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .accounts import PLAN_PRICES, accounts
from .auth import AuthContext
from .redaction import redact_incident
from .replay import build_brief, build_replay_scaffold
from .store import store

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="Production Replay Platform",
    description="Redacted incident packs + safe replay scaffolds",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    email: str
    password: str
    org_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class CheckoutRequest(BaseModel):
    plan: Literal["team", "business"] = "team"
    success_url: str | None = None
    cancel_url: str | None = None


@app.on_event("startup")
def startup() -> None:
    accounts.load()


def _html(name: str) -> HTMLResponse:
    path = FRONTEND_DIR / name
    return HTMLResponse(path.read_text())


@app.get("/", response_class=HTMLResponse)
def landing() -> HTMLResponse:
    return _html("landing.html")


@app.get("/app", response_class=HTMLResponse)
def product_app() -> HTMLResponse:
    return _html("app.html")


@app.get("/legal/terms", response_class=HTMLResponse)
def legal_terms() -> HTMLResponse:
    return _html("legal-terms.html")


@app.get("/legal/privacy", response_class=HTMLResponse)
def legal_privacy() -> HTMLResponse:
    return _html("legal-privacy.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "incidents": len(store.list())}


@app.post("/auth/signup")
def auth_signup(body: SignupRequest) -> dict[str, Any]:
    try:
        return accounts.signup(body.email, body.password, body.org_name)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/auth/login")
def auth_login(body: LoginRequest) -> dict[str, Any]:
    try:
        return accounts.login(body.email, body.password)
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc


@app.get("/billing/usage")
def billing_usage(auth: AuthContext) -> dict[str, Any]:
    return accounts.usage_snapshot(auth["org_id"])


@app.post("/billing/checkout-session")
def billing_checkout(body: CheckoutRequest, auth: AuthContext) -> dict[str, Any]:
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    plan = body.plan
    if stripe_key:
        return {
            "mode": "stripe_ready",
            "message": "Stripe key detected — wire stripe.checkout.Session.create here.",
            "plan": plan,
            "org_id": auth["org_id"],
            "price_usd": PLAN_PRICES[plan],
            "success_url": body.success_url or "/app?checkout=success",
            "cancel_url": body.cancel_url or "/?checkout=cancel",
        }
    snap = accounts.set_plan(auth["org_id"], plan)
    return {
        "mode": "stub",
        "checkout_url": f"/app?checkout=success&plan={plan}",
        "message": "Stub checkout: plan upgraded locally. Set STRIPE_SECRET_KEY for real charges.",
        "plan": plan,
        "org_id": auth["org_id"],
        "price_usd": PLAN_PRICES[plan],
        "usage": snap,
        "env": {
            "STRIPE_SECRET_KEY": "optional; when set, stub upgrade is skipped for real Checkout wiring",
            "STRIPE_PRICE_TEAM": "optional Price ID for Team ($129/mo)",
            "STRIPE_PRICE_BUSINESS": "optional Price ID for Business ($349/mo)",
        },
    }


def _create_incident(payload: dict[str, Any], auth: dict[str, Any]) -> dict[str, Any]:
    quota = accounts.check_incident_quota(auth["org_id"])
    if not quota["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "message": (
                    f"Free tier limit of {quota['incidents_limit']} incidents/{quota['month']} "
                    "reached. Upgrade via POST /billing/checkout-session."
                ),
                "plan": quota["plan"],
                "incidents_used": quota["incidents_used"],
                "incidents_limit": quota["incidents_limit"],
                "month": quota["month"],
                "upgrade": {"team": "$129/mo", "business": "$349/mo"},
            },
        )
    redacted = redact_incident(payload)
    pack = store.create(redacted)
    accounts.record_incident(auth["org_id"])
    return {"ok": True, "incident": pack}


@app.post("/incidents")
def create_incident(payload: dict[str, Any], auth: AuthContext) -> dict[str, Any]:
    """Accept request metadata/headers/body/logs, redact, store as JSON pack."""
    return _create_incident(payload, auth)


@app.get("/incidents")
def list_incidents(_auth: AuthContext) -> dict[str, Any]:
    return {"incidents": store.list()}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str, _auth: AuthContext) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return pack


@app.post("/incidents/{incident_id}/replay-scaffold")
def replay_scaffold(incident_id: str, _auth: AuthContext) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return build_replay_scaffold(pack)


@app.post("/incidents/{incident_id}/brief")
def incident_brief(incident_id: str, _auth: AuthContext) -> dict[str, Any]:
    pack = store.get(incident_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Incident not found")
    return build_brief(pack)


@app.post("/collector/incidents")
def collector_create(payload: dict[str, Any], auth: AuthContext) -> dict[str, Any]:
    return _create_incident(payload, auth)
