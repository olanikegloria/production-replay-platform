# Production Replay Platform

**Status:** Phase 0 — planning only. Do not implement until proposal is accepted.  
**Folder:** `04-production-replay-platform`

---

## Problem

Production breaks with: **“I can’t reproduce it.”** Engineers lack a safe, redacted pack of request context, version, logs, and dependency metadata to recreate conditions locally.

## Target users

Backend/SRE/platform engineers debugging incidents.

## Solution (intent)

Capture selected telemetry on incident → **redact secrets/PII** → store an incident pack → recreate a **safe local replay environment**. AI produces evidence-backed incident briefs. This is not a full production traffic mirror.

## Tech stack (planned)

- Collector SDK (language TBD; start with Node or Python)
- Backend: FastAPI
- Replay engine: Dockerised scaffolds
- Storage: PostgreSQL + object storage
- AI: Ollama for incident narrative over structured evidence

## Docs

- [PROPOSAL.md](./PROPOSAL.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [INTERVIEW.md](./INTERVIEW.md)

## Setup

Not runnable yet. Scaffold only.
