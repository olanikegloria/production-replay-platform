"""Tests for auth, metering, and commercial stubs."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.accounts import accounts
from app.main import app
from app.store import IncidentStore


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "incidents"))
    monkeypatch.setenv("ACCOUNTS_DIR", str(tmp_path))
    accounts.orgs.clear()
    accounts.users.clear()
    accounts.tokens.clear()
    accounts.load()

    # Fresh incident store bound to temp dir
    import app.store as store_mod
    import app.main as main_mod

    store_mod.store = IncidentStore(tmp_path / "incidents")
    main_mod.store = store_mod.store

    with TestClient(app) as c:
        yield c


def test_landing_and_app_routes(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"ReplaySafe" in r.content or b"redaction" in r.content.lower()

    assert client.get("/app").status_code == 200
    assert client.get("/legal/terms").status_code == 200
    assert client.get("/legal/privacy").status_code == 200


def test_protected_routes_require_auth(client):
    assert client.post("/incidents", json={}).status_code == 401
    assert client.get("/incidents").status_code == 401


def test_demo_token_creates_redacted_incident(client):
    headers = {"Authorization": "Bearer demo"}
    res = client.post(
        "/incidents",
        headers=headers,
        json={
            "method": "POST",
            "path": "/login",
            "headers": {"Authorization": "Bearer tokensecret"},
            "body": {"email": "a@b.co", "password": "pw"},
            "logs": ["Bearer tokensecret for a@b.co"],
        },
    )
    assert res.status_code == 200
    pack = res.json()["incident"]
    blob = str(pack)
    assert "tokensecret" not in blob
    assert "a@b.co" not in blob
    assert pack["headers"]["Authorization"] != "Bearer tokensecret"

    iid = pack["id"]
    assert client.post(f"/incidents/{iid}/brief", headers=headers).status_code == 200
    assert client.post(f"/incidents/{iid}/replay-scaffold", headers=headers).status_code == 200


def test_signup_checkout_and_free_quota(client):
    signup = client.post(
        "/auth/signup",
        json={
            "email": "Buyer@Acme.Dev",
            "password": "secret12",
            "org_name": "Acme Sec",
        },
    )
    assert signup.status_code == 200
    token = signup.json()["token"]
    org_id = signup.json()["org_id"]
    assert signup.json()["plan"] == "free"
    headers = {"Authorization": f"Bearer {token}"}

    login = client.post(
        "/auth/login",
        json={"email": "buyer@acme.dev", "password": "secret12"},
    )
    assert login.status_code == 200

    month = accounts.usage_snapshot(org_id)["month"]
    accounts.orgs[org_id]["usage"] = {month: {"incidents": 25}}
    accounts._persist()

    blocked = client.post(
        "/incidents",
        headers=headers,
        json={"method": "GET", "path": "/x"},
    )
    assert blocked.status_code == 402
    assert blocked.json()["detail"]["error"] == "quota_exceeded"

    checkout = client.post(
        "/billing/checkout-session",
        headers=headers,
        json={"plan": "team"},
    )
    assert checkout.status_code == 200
    payload = checkout.json()
    assert payload["mode"] == "stub"
    assert payload["plan"] == "team"
    assert "upgraded locally" in payload["message"]
    assert accounts.orgs[org_id]["plan"] == "team"
