# Sales playbook — Production Replay Platform (ReplaySafe)

---

## ICP

| Dimension | Fit |
|-----------|-----|
| **Company** | 30–500 engineers; HTTP microservices; real incident load |
| **Buyer** | Platform / SRE lead, Security-adjacent Eng Manager |
| **Champion** | On-call engineer who redacts screenshots by hand today |
| **Trigger** | Post-mortem where a token leaked into Slack / a ticket |
| **Anti-ICP** | Teams happy dumping raw HAR files into shared drives |

**One sentence:** Teams that need to reproduce production failures without replaying secrets.

---

## Pain

1. **Secret sprawl** — Authorization headers and emails land in tickets, Slack, and HAR dumps.  
2. **Replay fear** — Nobody wants to re-run production payloads locally without a redaction guarantee.  
3. **Brief theater** — Generic LLM summaries invent causes; buyers need evidence-bound text.

Wedge: **redaction non-negotiable**, then brief + safe scaffold. Free/local — no paid telemetry vendors required.

---

## Demo script (12–15 minutes)

### 0. Setup

- Open `/` → security messaging → **Open app** → `/app`  
- Bearer `demo`

### 1. Frame

> “We store incident packs only after redaction. Briefs cite evidence. Scaffolds ship sanitized fixtures — not live secrets.”

Show Free / Team ($129) / Business ($349).

### 2. Capture + redact

```bash
export TOKEN=demo
curl -X POST http://localhost:8004/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method":"POST","path":"/api/checkout","headers":{"Authorization":"Bearer secret"},"body":{"email":"a@b.co","password":"pw"},"logs":["Bearer secret for a@b.co"]}'
```

Show pack has `[REDACTED]`. Then brief + replay-scaffold.

### 3. Commercial motion

```bash
curl -X POST http://localhost:8004/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@acme.dev","password":"demo-pass","org_name":"Acme Sec"}'

curl -X POST http://localhost:8004/billing/checkout-session \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"plan":"team"}'
# → stub upgrades plan locally
```

Optionally burn Free quota (25 creates) until **402**.

### 4. Close

> “Team at $129/mo is the buying unit for a squad that owns incident hygiene. Runs free locally — no paid APIs.”

---

## Objections

| Objection | Response |
|-----------|----------|
| “We already have Datadog / Sentry.” | Complementary: we optimize for **redacted packs + safe local replay**, not full APM. |
| “Will you send data to OpenAI?” | No. Briefs are deterministic and evidence-bound. Free stack. |
| “$129 seems high.” | You’re buying trust under incident pressure. One prevented secret leak pays for years of Team. |
| “Self-host?” | JSON/SQLite-friendly MVP; Docker Compose today. |

---

## Qualification

1. Where do raw Authorization headers end up today?  
2. Who owns post-incident reproduction?  
3. Seat count for the on-call rotation that would create packs weekly?
