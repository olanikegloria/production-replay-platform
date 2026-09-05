# Production Replay Platform (ReplaySafe)

**Status:** SaaS foundation (auth, metering, commercial docs) on a runnable redaction MVP  
**Folder:** `04-production-replay-platform`

Narrow HTTP incident packs with **mandatory redaction**, evidence-bound briefs, and safe replay scaffolds. Security-first product — Free / Team **$129** / Business **$349**. Free/local stack: **no paid telemetry vendors**, no OpenAI required.

---

## Path to selling

| Stage | What ships here | Next production step |
|-------|-----------------|----------------------|
| **1. Prove value** | Landing `/`, product `/app`, redact + brief + scaffold | Agent collectors in more languages |
| **2. Capture account** | Signup/login → API token; `data/accounts.json` | Managed DB + SSO for Business |
| **3. Meter Free** | 25 incident creates/mo; **HTTP 402** on quota | Soft alerts + upgrade CTA |
| **4. Take payment** | Checkout stub **upgrades plan locally** | Optional `STRIPE_SECRET_KEY` + Checkout |
| **5. Close Team/Business** | $129 / $349 pricing docs | Audit log + DPA path |

Commercial docs:

- [docs/PRICING.md](./docs/PRICING.md) — Free / Team ($129) / Business ($349)
- [docs/SALES.md](./docs/SALES.md) — ICP, demo script, free/local emphasis

Legal stubs: `/legal/terms`, `/legal/privacy`

---

## What works

- Marketing landing at `/` (security-first messaging); product UI at `/app`
- Bearer-protected incident APIs (`demo` token allowed)
- Org signup/login; usage metering; checkout stub
- Redaction of Authorization, API keys, passwords, emails, Bearer tokens
- Incident packs as JSON; brief + replay-scaffold
- pytest suite for redaction (must pass)

## Stack

| Layer | Choice |
|-------|--------|
| API + UI | Python FastAPI + static HTML |
| Store | JSON files |
| Auth | PBKDF2 + opaque API tokens |
| Billing | Stub checkout (local plan upgrade); Stripe optional |
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

# Signup → Free org
curl -X POST http://localhost:8004/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@acme.dev","password":"demo-pass","org_name":"Acme Sec"}'

# Checkout stub upgrades plan locally
curl -X POST http://localhost:8004/billing/checkout-session \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plan":"team"}'
```

Free orgs that exceed **25 incident creates/month** receive **402**.

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
| GET | `/billing/usage` | Bearer | Plan + metre |
| POST | `/billing/checkout-session` | Bearer | Stub upgrade / Stripe-ready |
| POST | `/incidents` | Bearer | Ingest + redact + store (metered) |
| GET | `/incidents` | Bearer | List packs |
| GET | `/incidents/{id}` | Bearer | Get pack |
| POST | `/incidents/{id}/replay-scaffold` | Bearer | Compose + fixture |
| POST | `/incidents/{id}/brief` | Bearer | Evidence-bound summary |
| POST | `/collector/incidents` | Bearer | Alias for ingest (metered) |

## Layout

```text
backend/app/     FastAPI, auth, redaction, store, replay/brief
collector/       Thin collect() helper
frontend/        Landing, app, legal HTML
docs/            PRICING.md, SALES.md
tests/           Redaction + SaaS tests
data/incidents/  Stored JSON packs
```

## Docs

- [PROPOSAL.md](./PROPOSAL.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [INTERVIEW.md](./INTERVIEW.md)
- [docs/PRICING.md](./docs/PRICING.md)
- [docs/SALES.md](./docs/SALES.md)
