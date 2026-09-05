"""Unit tests for secret/PII redaction."""

from app.redaction import REDACTED, redact_headers, redact_incident, redact_string


def test_redacts_authorization_header():
    headers = redact_headers({"Authorization": "Bearer abc.def.ghi", "X-Request-Id": "1"})
    assert headers["Authorization"] == REDACTED
    assert headers["X-Request-Id"] == "1"


def test_redacts_api_key_header():
    headers = redact_headers({"X-Api-Key": "sk_live_secret", "Accept": "application/json"})
    assert headers["X-Api-Key"] == REDACTED
    assert headers["Accept"] == "application/json"


def test_redacts_password_and_email_in_body():
    pack = redact_incident(
        {
            "body": {"email": "user@example.com", "password": "hunter2", "item": "sku-1"},
        }
    )
    assert pack["body"]["password"] == REDACTED
    assert pack["body"]["email"] == REDACTED
    assert pack["body"]["item"] == "sku-1"


def test_redacts_bearer_token_in_logs():
    text = redact_string("auth Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload")
    assert "eyJhbGciOiJIUzI1NiJ9" not in text
    assert REDACTED in text


def test_redacts_inline_api_key_and_password():
    text = redact_string("api_key=sk_live_abc password=hunter2")
    assert "sk_live_abc" not in text
    assert "hunter2" not in text
    assert text.count(REDACTED) >= 2


def test_full_incident_pack_has_no_secrets():
    raw = {
        "method": "POST",
        "path": "/login",
        "headers": {"Authorization": "Bearer tokensecret"},
        "body": {"email": "a@b.co", "password": "pw", "api_key": "key"},
        "logs": ["Bearer tokensecret for a@b.co"],
    }
    pack = redact_incident(raw)
    blob = str(pack)
    assert "tokensecret" not in blob
    assert "a@b.co" not in blob
    assert "pw" not in blob
    assert pack["headers"]["Authorization"] == REDACTED
    assert pack["body"]["password"] == REDACTED
    assert pack["body"]["api_key"] == REDACTED
