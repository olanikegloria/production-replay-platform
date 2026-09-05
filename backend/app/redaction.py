"""Redact secrets and PII from incident packs."""

from __future__ import annotations

import copy
import re
from typing import Any

REDACTED = "[REDACTED]"

SENSITIVE_HEADER_KEYS = {
    "authorization",
    "proxy-authorization",
    "x-api-key",
    "api-key",
    "x-auth-token",
    "cookie",
    "set-cookie",
}

SENSITIVE_BODY_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "client_secret",
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)
API_KEY_INLINE_RE = re.compile(
    r"(?i)\b(api[_-]?key|apikey|secret|token)\b\s*[:=]\s*['\"]?([^\s'\",;}]+)"
)
PASSWORD_INLINE_RE = re.compile(
    r"(?i)\b(password|passwd)\b\s*[:=]\s*['\"]?([^\s'\",;}]+)"
)


def redact_string(value: str) -> str:
    out = value
    out = BEARER_RE.sub(f"Bearer {REDACTED}", out)
    out = EMAIL_RE.sub(REDACTED, out)
    out = API_KEY_INLINE_RE.sub(lambda m: f"{m.group(1)}={REDACTED}", out)
    out = PASSWORD_INLINE_RE.sub(lambda m: f"{m.group(1)}={REDACTED}", out)
    return out


def _is_sensitive_key(key: str) -> bool:
    k = key.lower().replace("-", "_")
    if k in SENSITIVE_BODY_KEYS or key.lower() in SENSITIVE_HEADER_KEYS:
        return True
    return any(s in k for s in ("password", "secret", "api_key", "apikey", "token", "authorization"))


def redact_headers(headers: dict[str, Any] | None) -> dict[str, Any]:
    if not headers:
        return {}
    out: dict[str, Any] = {}
    for key, value in headers.items():
        if key.lower() in SENSITIVE_HEADER_KEYS or _is_sensitive_key(key):
            out[key] = REDACTED
        elif isinstance(value, str):
            out[key] = redact_string(value)
        else:
            out[key] = value
    return out


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return redact_obj(value)
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def redact_obj(obj: dict[str, Any] | None) -> dict[str, Any]:
    if not obj:
        return {}
    out: dict[str, Any] = {}
    for key, value in obj.items():
        if _is_sensitive_key(key):
            out[key] = REDACTED
        else:
            out[key] = redact_value(value)
    return out


def redact_incident(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied, redacted incident pack."""
    data = copy.deepcopy(payload)
    if "headers" in data:
        data["headers"] = redact_headers(data.get("headers") or {})
    if "request_headers" in data:
        data["request_headers"] = redact_headers(data.get("request_headers") or {})
    if "body" in data:
        body = data["body"]
        if isinstance(body, dict):
            data["body"] = redact_obj(body)
        elif isinstance(body, str):
            data["body"] = redact_string(body)
        else:
            data["body"] = redact_value(body)
    if "logs" in data:
        logs = data["logs"]
        if isinstance(logs, list):
            data["logs"] = [
                redact_string(x) if isinstance(x, str) else redact_value(x) for x in logs
            ]
        elif isinstance(logs, str):
            data["logs"] = redact_string(logs)
    if "metadata" in data and isinstance(data["metadata"], dict):
        data["metadata"] = redact_obj(data["metadata"])
    # Catch any top-level sensitive keys
    for key in list(data.keys()):
        if key in ("headers", "request_headers", "body", "logs", "metadata"):
            continue
        if _is_sensitive_key(key):
            data[key] = REDACTED
        elif isinstance(data[key], str):
            data[key] = redact_string(data[key])
    return data
