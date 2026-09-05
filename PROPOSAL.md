# PROJECT PROPOSAL — 04 Production Replay Platform

**Status:** Awaiting review. Do not implement until accepted.  
**Working name:** Production Replay Platform  
**One-liner:** Capture a redacted incident pack so engineers can recreate *safe* local conditions — not a full production mirror.

---

## PROBLEM

Something fails in production. Locally it works. Engineers lack enough structured, redacted context (request shape, version, deps, logs, config non-secrets) to reproduce and debug.

---

## TARGET USER

- Backend engineers
- SREs / platform engineers
- Teams without heavyweight observability suites (learning/demo context)

---

## WHY THEY CARE

Irreproducible bugs are expensive. Full session-replay or enterprise APM may be unavailable or overkill; a focused **incident pack → local replay scaffold** teaches serious systems thinking.

---

## EXISTING ALTERNATIVES

| Alternative | Strength | Gap |
|-------------|----------|-----|
| Sentry / Datadog / full APM | Mature telemetry | Heavy; not “replay pack” pedagogy |
| Browser session replay | Frontend UX | Not backend incident packs |
| Research: traces → regression tests | Emerging | Complex; we stay narrower |
| Manual runbooks | Human | Inconsistent |

---

## OUR DIFFERENTIATOR

1. **Redaction-first** incident packs as the product core.
2. **Safe local replay scaffolds** with explicit fidelity limits.
3. AI briefs that only cite pack evidence.
4. Portfolio honesty: hardest project; narrow HTTP MVP.

---

## MVP

- Collector SDK (pick **one** language: Python or Node)
- On error / manual capture: request metadata, timestamp, app version, selected non-secret config, dependency versions, recent logs
- Redaction pipeline (keys, tokens, password patterns, emails)
- Store incident pack
- “Replay locally” generates a Docker Compose scaffold + sanitized fixture
- AI: likely cause narrative with numbered evidence list

**Non-goals:** Full distributed tracing mesh replay, copying prod DB, storing raw secrets “just for debugging.”

---

## V2

- Broader SDK languages
- Correlation with deploy events
- Richer fidelity (selected spans)
- Team sharing + access control

---

## V3

- Automated regression test generation from packs (careful, optional)
- Org-wide incident similarity search

---

## TECH STACK

| Layer | Choice | Why |
|-------|--------|-----|
| Collector | Python or Node SDK | Match primary apps |
| Backend | FastAPI | Ingest + redaction pipeline |
| Replay | Docker Compose templates | Isolation |
| Storage | Postgres + object storage (local MinIO/S3-compatible free) | Packs |
| Frontend | Next.js | Incident UI |
| AI | Ollama | Evidence-bound briefs |

---

## ARCHITECTURE

See [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## AI COMPONENT

- Summarise packs into likely cause + investigation steps
- Must list evidence fields from the pack
- Refuse overconfident claims when pack is thin

---

## SECURITY

- Non-negotiable redaction before persistence
- Encryption in transit
- Access control on packs
- Retention limits
- Security review checklist in `docs/` before any demo with real data (use synthetic demos by default)

---

## SCALABILITY

| Scale | Plan |
|-------|------|
| 10 | Single backend; local object store |
| 10k | Queue ingest, tiered storage, sampling |
| 1M | Multi-region ingest, strict sampling, separate cold storage — enterprise-shaped |

---

## TESTING

- Redaction unit tests (must-pass suite)
- Ingest integration tests
- Replay scaffold smoke tests
- AI citation eval on synthetic packs

---

## DEPLOYMENT

- Compose for demo
- CI emphasizes redaction tests as gate

---

## ESTIMATED COMPLEXITY

**Highest** of the six. Recommend building **last**, after security design review of this proposal.

---

## RISKS

| Risk | Mitigation |
|------|------------|
| PII/secret leakage | Redaction tests; synthetic demos; legal caution |
| Overclaiming fidelity | Document limits in UI |
| Scope explosion | HTTP metadata MVP only |
| Overlap with commercial APM | Position as focused replay-pack learning system |

---

## ACCEPTANCE

- [ ] MVP fidelity limits accepted
- [ ] SDK language choice accepted
- [ ] Security bar accepted
- [ ] **I accept this** / revise / cut / defer
