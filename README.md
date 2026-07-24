# ResolveAI — Servicing Backend (Hardened)

Mock backend for **ResolveAI**, an end-to-end banking servicing agent
(AMEX hackathon, theme: *End-to-End Servicing Agent*). Handles **fee
reversal**, **card replacement**, and **credit-limit increase**
end to end, with a deterministic policy engine and a hash-chained,
insert-only audit trail.

## Design principle

> The AI/orchestration layer decides *what* the customer wants.
> This backend decides *whether the bank says yes* — in plain, tested
> Python, with zero dependency on any LLM.

## Day 2 addition: Redis session state

Every servicing request was stateless — no memory of what a customer said
in a previous turn. `app/services/session_service.py` + `/sessions/*`
endpoints now give the AI orchestration layer somewhere to persist, per
conversation: last detected intent, extracted entities, and a rolling
history — with a 30-minute inactivity TTL so abandoned sessions clean
themselves up.

```bash
curl http://localhost:8000/sessions/demo-1 -H "X-API-Key: ..."
curl -X POST http://localhost:8000/sessions/demo-1 -H "X-API-Key: ..." \
  -H "Content-Type: application/json" \
  -d '{"last_intent":"fee_reversal","entities":{"fee_amount":199.0}}'
curl -X DELETE http://localhost:8000/sessions/demo-1 -H "X-API-Key: ..."
```

## What changed in the hardening pass

| Flaw | Fix |
|---|---|
| `prior_reversals_90d` was hardcoded to `0` — a fake stub pretending to be policy logic | `policy_engine.count_recent_fee_reversals()` queries real completed requests in the last 90 days |
| No auth on any endpoint | `X-API-Key` header required on every servicing route (`app/security.py`) |
| Multiple `db.commit()` calls per request — a crash mid-flow left orphaned state | Each request is one atomic transaction: create → lock → check → act → log, single commit, rollback on any exception |
| No idempotency — a network retry could double-reverse a fee or double-increase a limit | `Idempotency-Key` header + unique constraint; a repeated key returns the original result instead of re-running the action |
| Race condition on concurrent writes to the same customer (lost update) | `SELECT ... FOR UPDATE` row-locks the customer row for the transaction's duration |
| "Immutable audit trail" was just a mutable table with a nice name | Hash-chained `audit_logs` (`seq` autoincrement ordering + sha256 chain) verifiable via `GET /audit-logs/_integrity/verify`, plus a Postgres migration that revokes `UPDATE`/`DELETE` on the table |

## Project structure

```
resolveai-backend/
├── app/
│   ├── main.py, config.py, database.py, security.py
│   ├── models/           # customers, service_requests (+idempotency_key),
│   │                      # audit_logs (+seq, prev_hash, record_hash), human_handoffs
│   ├── schemas/           # Pydantic request/response contracts
│   ├── routers/           # fees, cards, credit_limit, customers, audit, handoffs
│   ├── services/
│   │   ├── policy_engine.py    # deterministic eligibility rules + real reversal-history query
│   │   ├── audit_service.py    # hash-chained logging + chain verification
│   │   └── session_service.py  # Day 2: Redis-backed conversation state
│   └── seed/seed_data.py
├── alembic/               # 3 migrations: initial schema, hardening (idempotency+hash chain), Postgres insert-only restriction
├── tests/                 # 19 tests: policy engine, audit chain, session service
├── docker-compose.yml
└── README.md
```

## Setup

```bash
docker-compose up -d
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed.seed_data
uvicorn app.main:app --reload
# http://localhost:8000/docs
```
Falls back to local SQLite automatically if Postgres isn't running yet.

## Running tests
```bash
pytest -v
```
19 tests: 11 for the policy engine, 3 for the audit hash chain (including tamper detection), 5 for the Day 2 session service (using fakeredis, so no real Redis connection is needed to run tests).

## Every request now needs two headers
```bash
curl -X POST http://localhost:8000/fees/reversal \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me-in-production" \
  -H "Idempotency-Key: unique-per-logical-request" \
  -d '{"customer_id":"C1001","fee_id":"FEE-8831","fee_amount":199.00,"days_since_charge":3,"reason":"duplicate charge"}'
```
Replaying the same `Idempotency-Key` returns the original result instead of re-running the action.

## Verifying the audit trail is actually tamper-evident
```bash
curl http://localhost:8000/audit-logs/SR-xxxxxxxx -H "X-API-Key: ..."
curl http://localhost:8000/audit-logs/_integrity/verify -H "X-API-Key: ..."
```
The second call recomputes the sha256 chain across the entire table and reports `{"intact": true/false, "broken_at_audit_id": ...}`.

## Demo customers
| customer_id | verification | account age | card status | credit limit |
|---|---|---|---|---|
| C1001 | verified | 24 months | active | 50,000 |
| C1002 | verified | 3 months | active | 15,000 |
| C1003 | unverified | 18 months | active | 30,000 |
| C1004 | verified | 36 months | damaged | 80,000 |
| C1005 | verified | 8 months | blocked | 20,000 |

## Still explicitly out of scope (Round 1/2)
- Real banking system integration, real customer PII
- The AI/LangGraph orchestration layer (this repo is what it calls into)
- Per-caller API keys / real identity provider (single shared key is the floor, not the ceiling)
- Rate limiting

## Scalability
- FastAPI instances are stateless — scale horizontally
- Postgres: indexes, read replicas, partition `audit_logs` by month
- Row-level locking (`FOR UPDATE`) means correctness holds under concurrency without needing external distributed locks
- New servicing flows = new router + policy-engine function pair; existing flows untouched
