"""Replay scaffold + evidence-bound brief generation."""

from __future__ import annotations

import json
from typing import Any


def build_replay_scaffold(pack: dict[str, Any]) -> dict[str, Any]:
    method = (pack.get("method") or "POST").upper()
    path = pack.get("path") or pack.get("url") or "/unknown"
    status = pack.get("status_code") or pack.get("status") or 500
    service = (pack.get("metadata") or {}).get("service") or "app"

    fixture = {
        "request": {
            "method": method,
            "path": path,
            "headers": pack.get("headers") or pack.get("request_headers") or {},
            "body": pack.get("body"),
        },
        "expected_status": status,
        "logs": pack.get("logs") or [],
        "notes": "Sanitized fixture — secrets already redacted at ingest.",
    }

    compose = f"""# Replay scaffold for incident {pack.get('id')}
# Safe local scaffolding only — no live production traffic.
services:
  {service}:
    image: {service}:local
    environment:
      REPLAY_MODE: "1"
      INCIDENT_ID: "{pack.get('id')}"
    ports:
      - "8080:8080"
    volumes:
      - ./fixtures/{pack.get('id')}.json:/fixtures/incident.json:ro
"""

    return {
        "incident_id": pack.get("id"),
        "docker_compose": compose,
        "fixture": fixture,
        "fixture_filename": f"fixtures/{pack.get('id')}.json",
    }


def build_brief(pack: dict[str, Any]) -> dict[str, Any]:
    method = pack.get("method") or "?"
    path = pack.get("path") or pack.get("url") or "?"
    status = pack.get("status_code") or pack.get("status") or "?"
    logs = pack.get("logs") or []
    log_lines = logs if isinstance(logs, list) else [str(logs)]
    evidence = [
        f"HTTP {method} {path} → {status}",
        f"headers_keys={sorted((pack.get('headers') or pack.get('request_headers') or {}).keys())}",
        f"body_present={pack.get('body') is not None}",
        f"log_count={len(log_lines)}",
    ]
    for line in log_lines[:5]:
        evidence.append(f"log: {line}")

    summary = (
        f"Incident {pack.get('id')}: {method} {path} returned {status}. "
        f"Evidence from redacted pack only ({len(evidence)} facts). "
        "No secrets included."
    )

    return {
        "incident_id": pack.get("id"),
        "summary": summary,
        "evidence": evidence,
        "pack_excerpt": {
            "method": method,
            "path": path,
            "status": status,
            "stored_at": pack.get("stored_at"),
            "body": pack.get("body"),
            "logs": log_lines[:10],
        },
        "raw_json_preview": json.dumps(
            {"id": pack.get("id"), "method": method, "path": path, "status": status},
            indent=2,
        ),
    }
