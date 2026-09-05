# Pricing — Production Replay Platform (ReplaySafe)

**Positioning:** Higher-trust incident debugging — pay for seats and create capacity where redaction is non-negotiable.

---

## Plans at a glance

| | **Free** | **Team** | **Business** |
|---|----------|----------|--------------|
| **Price** | $0 | **$129 / month** | **$349 / month** |
| **Seats** | 1 | Up to 15 | Up to 60 |
| **Incident creates / month** | 25 | 500 | Unlimited\* |
| **Mandatory redaction** | Yes | Yes | Yes |
| **Brief + replay scaffold** | Yes | Yes | Yes |
| **Audit / SSO** | — | Roadmap | Roadmap priority |
| **Support** | Community docs | Email (48h) | Priority |

\*Fair-use rate limits still apply on Business.

---

## Why priced above generic tooling

Security and trust are the product. Buyers are on-call and platform teams who cannot paste production headers into a random SaaS. Team ($129) and Business ($349) reflect that bar — not a race to the cheapest log viewer.

---

## Free / local policy

- Develop and demo with **JSON files + local FastAPI** only  
- **No paid telemetry vendors** required  
- **No OpenAI / paid LLM** required for briefs (deterministic evidence-bound summaries)  
- Checkout stub upgrades plan locally; Stripe optional later  

---

## What we meter today (MVP)

| Meter | Free limit | Notes |
|-------|------------|-------|
| `POST /incidents` (and collector alias) | **25 / calendar month / org** | Enforced; **HTTP 402** when exceeded |
| Seats | Soft limits in docs | Hard enforcement with billing webhooks later |

Auth required for incident APIs. Local demos may use Bearer token `demo`.

---

## Upgrade path

1. Sign up → Free org + API token  
2. Hit quota → `POST /billing/checkout-session`  
3. **Stub mode** (default): upgrades plan locally with no Stripe key  
4. Optional later: set `STRIPE_SECRET_KEY` and wire real Checkout  
