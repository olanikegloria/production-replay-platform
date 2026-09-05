# Architecture — Production Replay Platform

**Status:** Planning. Subject to change after proposal review.

---

## System overview

```text
App under observation
      │ collector SDK (sampled / on-error)
      ▼
Ingest API
      │
      ▼
Redaction pipeline (secrets, tokens, PII patterns)
      │
      ▼
Incident pack store (metadata + artifacts)
      │
      ├── Replay engine (Docker: app version + deps + safe fixtures)
      └── AI incident brief (cites pack fields only)
```

---

## Core components

| Path | Role |
|------|------|
| `collector/` | SDK emitting incident events |
| `backend/` | Ingest, auth, pack APIs |
| `replay-engine/` | Local recreate scripts / Compose |
| `ai/` | Evidence-bound summaries |
| `frontend/` | Incident list, pack viewer, replay trigger |
| `infrastructure/` | Hardening notes, retention |

---

## Non-negotiables

- Never copy production secrets into packs
- Redact passwords, API keys, tokens, personal data
- Replay uses synthetic/safe substitutes
- Explicit fidelity limits documented (what we can/can’t reproduce)

---

## MVP narrowing

Start with **HTTP request/response metadata + selected headers + error + version + dependency versions + recent logs** — not distributed trace replay of entire meshes.

---

## Open questions

1. Which language SDK first?
2. Opt-in capture vs always-on sampling?
3. Legal/compliance framing for demo datasets?
