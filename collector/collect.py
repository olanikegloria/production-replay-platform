"""Thin collector facade — posts to the same redaction pipeline."""

from app.redaction import redact_incident
from app.store import store


def collect(payload: dict) -> dict:
    return store.create(redact_incident(payload))
