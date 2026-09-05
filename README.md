# Production Replay Platform

**Status:** Runnable MVP scaffold  
**Folder:** `04-production-replay-platform`

Narrow HTTP incident packs with **mandatory redaction**, evidence-bound briefs, and safe replay scaffolds (compose + sanitized fixtures).

---

## What works in this MVP

- `POST /incidents` — accept request metadata, headers, body, logs
- Redaction of Authorization, API keys, passwords, emails, Bearer tokens
- Incident packs stored as JSON under `data/incidents/`
- `POST /incidents/{id}/replay-scaffold` — docker-compose snippet + sanitized fixture
- `POST /incidents/{id}/brief` — evidence-bound deterministic summary
- HTML UI to submit sample incident and view pack/brief
- pytest suite for redaction (must pass)

## Stack

| Layer | Choice |
|-------|--------|
| API + UI | Python FastAPI + static HTML |
| Store | JSON files |
| Tests | pytest |

## Quick start (local)

```bash
cd 04-production-replay-platform
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export PYTHONPATH=backend
export DATA_DIR=$PWD/data/incidents
uvicorn app.main:app --reload --port 8004
```

Open http://localhost:8004/

```bash
curl -X POST http://localhost:8004/incidents \
  -H 'Content-Type: application/json' \
  -d '{
    "method":"POST","path":"/api/checkout","status_code":500,
    "headers":{"Authorization":"Bearer secret-token","X-Api-Key":"sk_live_x"},
    "body":{"email":"a@b.co","password":"pw","cart_id":"1"},
    "logs":["Bearer secret-token for a@b.co"]
  }'

# Replace INC_ID from response
curl -X POST http://localhost:8004/incidents/INC_ID/brief
curl -X POST http://localhost:8004/incidents/INC_ID/replay-scaffold
```

### Tests

```bash
cd 04-production-replay-platform
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend pytest tests/ -q
```

## Docker

```bash
cd 04-production-replay-platform
docker compose up --build
```

UI/API: http://localhost:8004/

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Submit / pack UI |
| POST | `/incidents` | Ingest + redact + store pack |
| GET | `/incidents` | List packs |
| GET | `/incidents/{id}` | Get pack |
| POST | `/incidents/{id}/replay-scaffold` | Compose + fixture |
| POST | `/incidents/{id}/brief` | Evidence-bound summary |
| POST | `/collector/incidents` | Alias for ingest |

## Layout

```text
backend/app/     FastAPI, redaction, store, replay/brief
collector/       Thin collect() helper
frontend/        HTML UI
tests/           Redaction unit tests
data/incidents/  Stored JSON packs
```

## Docs

- [PROPOSAL.md](./PROPOSAL.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [INTERVIEW.md](./INTERVIEW.md)
