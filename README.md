# Production Replay Platform (ReplaySafe)

**Status:** Production-ready local product (auth + redaction + brief/scaffold)  
**Folder:** `04-production-replay-platform`

Narrow HTTP incident packs with **mandatory redaction**, evidence-bound briefs, and safe replay scaffolds. Free/local stack: **no paid telemetry vendors**, no OpenAI required.

---

## What works

- Marketing landing at `/` (security-first messaging); product UI at `/app`
- Bearer-protected incident APIs (`demo` token allowed)
- Org signup/login with API tokens
- Redaction of Authorization, API keys, passwords, emails, Bearer tokens
- Incident packs as JSON; brief + replay-scaffold
- pytest suite for redaction (must pass)

Legal stubs: `/legal/terms`, `/legal/privacy`

## Stack

| Layer | Choice |
|-------|--------|
| API + UI | Python FastAPI + static HTML |
| Store | JSON files |
| Auth | PBKDF2 + opaque API tokens |
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

Open http://localhost:8004/ (landing) and http://localhost:8004/app (product).

```bash
export TOKEN=demo

curl -X POST http://localhost:8004/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "method":"POST","path":"/api/checkout","status_code":500,
    "headers":{"Authorization":"Bearer secret-token","X-Api-Key":"sk_live_x"},
    "body":{"email":"a@b.co","password":"pw","cart_id":"1"},
    "logs":["Bearer secret-token for a@b.co"]
  }'

# Replace INC_ID from response
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8004/incidents/INC_ID/brief
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8004/incidents/INC_ID/replay-scaffold

curl -X POST http://localhost:8004/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@acme.dev","password":"demo-pass","org_name":"Acme Sec"}'
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

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Marketing landing |
| GET | `/app` | — | Product UI |
| GET | `/legal/terms`, `/legal/privacy` | — | Legal stubs |
| GET | `/health` | — | Liveness |
| POST | `/auth/signup`, `/auth/login` | — | Account → token |
| GET | `/usage` | Bearer | Incidents created this month |
| POST | `/incidents` | Bearer | Ingest + redact + store |
| GET | `/incidents` | Bearer | List packs |
| GET | `/incidents/{id}` | Bearer | Get pack |
| POST | `/incidents/{id}/replay-scaffold` | Bearer | Compose + fixture |
| POST | `/incidents/{id}/brief` | Bearer | Evidence-bound summary |
| POST | `/collector/incidents` | Bearer | Alias for ingest |

## Layout

```text
backend/app/     FastAPI, auth, redaction, store, replay/brief
collector/       Thin collect() helper
frontend/        Landing, app, legal HTML
tests/           Redaction + auth tests
data/incidents/  Stored JSON packs
```

## Docs

- [PROPOSAL.md](./PROPOSAL.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [INTERVIEW.md](./INTERVIEW.md)
