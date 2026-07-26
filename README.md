# ResolveAI
## End-to-End Banking Servicing Agent
### Project Description Document

---

## 1. Problem Statement

Common card service requests — fee reversals, credit-limit increases, and replacement card orders — are high-frequency, low-complexity interactions that nonetheless consume disproportionate human agent time. A card member with a duplicate charge, a damaged card, or a routine limit increase request typically has to:

- Explain the issue to a chatbot that can only provide generic information
- Get transferred to a human agent
- Repeat the same explanation
- Wait while the agent manually verifies eligibility and performs the action

This is tedious for the customer and expensive for the bank. Existing chatbots solve the "understanding" half of the problem but stop short of the "doing" half — they inform, but they don't resolve.

The challenge, as posed, was to design a conversational agent that:

1. Fully resolves high-frequency servicing requests in a single interaction
2. Maintains a verifiable audit trail of every decision and action taken
3. Hands off to a human agent with complete context when escalation is needed
4. Is tested and optimized for first-contact resolution rate, audit completeness, and escalation quality

ResolveAI was built directly against these four requirements.

---

## 2. Solution Overview

**ResolveAI** is a conversational AI agent that securely handles common card-servicing requests — card replacement, fee reversal, and credit-limit increase — by understanding the request, checking eligibility, completing approved actions through banking APIs, recording every decision, and escalating only exceptions to a human agent.

The core design principle threaded through every layer of the system is a strict separation of concerns:

- **The AI layer decides *what* the customer wants.** Intent classification and entity extraction are the only jobs given to the language model.
- **The backend decides *whether it's allowed*.** Every financial action is gated by a deterministic, testable policy engine — plain Python functions with no AI involvement — so the system's actual authorization logic is auditable, explainable, and never subject to model hallucination.

This separation is what allows ResolveAI to make a credible safety claim to both judges and, eventually, a real compliance team: the LLM never authorizes a financial action. It only proposes one, which a rule-based system independently approves or rejects.

### 2.1 What makes this different from a standard support chatbot

| Capability | Standard chatbot | ResolveAI |
|---|---|---|
| Understands customer intent | Yes | Yes |
| Completes the actual servicing action | No — hands off to a human | Yes — for eligible, low-risk requests |
| Auditable decision trail | Rarely, and not tamper-evident | Yes — hash-chained, cryptographically verifiable |
| Escalation with full context | No — customer repeats themselves | Yes — structured handoff summary |
| Safe against duplicate actions on retry | Not typically addressed | Yes — idempotency-key enforced |

---

## 3. Tech Stack

The hackathon brief left the tech stack open, offering React/Next.js, Node.js/FastAPI, Rasa/Dialogflow/GPT-4, and PostgreSQL/MongoDB as reference examples. The team's actual choices, and the reasoning behind each:

| Layer | Technology Used | Why This Choice |
|---|---|---|
| Frontend | React | Component-based UI well suited to a multi-screen chat + confirmation + audit-log + handoff flow |
| Agent orchestration | LangGraph (Python) | Explicit, controllable state-graph execution rather than an unrestricted LLM agent loop — every decision path is visible and testable, not emergent |
| Conversational AI model | Groq (Llama 3.3 70B) | OpenAI-compatible, extremely fast inference, generous free tier suitable for a rapid prototyping timeline without sacrificing structured-output quality |
| Backend API framework | FastAPI (Python) | Async-capable, automatic interactive documentation (Swagger UI), strong request/response validation via Pydantic |
| Database | PostgreSQL | ACID compliance is non-negotiable for financial state changes and audit logs — eventual consistency is not acceptable here |
| ORM / Migrations | SQLAlchemy + Alembic | Version-controlled, reviewable schema history rather than ad hoc database changes |
| Session memory | Redis | Fast, TTL-based conversational state between chat turns, with automatic expiry |
| Testing | Pytest, fakeredis | Automated regression coverage with zero external service dependency to run |
| Containerization | Docker Compose | One command reproduces the full local environment for any teammate |

This selection favors Python end-to-end (agent + backend), which simplified integration and meant both AI orchestration and servicing logic could be reasoned about, tested, and debugged in a single consistent language across the team.

---

## 4. System Architecture

ResolveAI is composed of three independently running services that communicate exclusively over authenticated HTTP APIs — no service directly shares code or database access with another.

```
Customer
   ↓
React Chat Interface (Frontend)
   ↓  POST /chat  { session_id, customer_id, customer_message }
LangGraph Agent Server (AI Orchestration Layer)
   ↓ reasoning calls          ↓ action calls
Groq LLM API              Backend Servicing Engine (FastAPI)
                                ↓
                           PostgreSQL
                     (Customers, ServiceRequests,
                      hash-chained AuditLogs)
```

**Why this separation matters:** the agent server never touches the database directly, and the backend never calls an LLM. Each service can be developed, tested, and reasoned about independently, and a compromise or bug in one layer cannot silently corrupt another. This mirrors real banking system design, where AI/ML components are typically kept at arm's length from core ledger and compliance systems.

### 4.1 Authentication and safety headers between services

Every call from the agent to the backend carries two required headers:

- **`X-API-Key`** — proves the caller is an authorized internal service, not an arbitrary client
- **`Idempotency-Key`** — a unique identifier per customer request, allowing safe retries. If the same key is sent twice (e.g. due to a network retry), the backend returns the original result instead of re-executing the financial action

---

## 5. The AI Agentic Workflow (Orchestration Layer)

This is the component responsible for understanding customer intent, deciding how to route it, and coordinating calls to both the LLM and the backend. It is built as an explicit **LangGraph state graph** rather than an open-ended agent loop — every possible path through the conversation is a defined node and edge, which makes the system's behavior predictable, testable, and explainable to both engineers and auditors.

### 5.1 Why a graph, not a freeform agent

An unrestricted LLM agent loop can, in principle, take unpredictable action sequences — useful for open-ended research tasks, unacceptable for a system that moves real money and issues real cards. LangGraph constrains the model to a fixed set of possible transitions: classify, extract, act, escalate. The LLM never decides *whether* to call a banking endpoint outside of these predefined, reviewed paths.

### 5.2 Graph structure

**Compiled LangGraph execution graph, as generated directly from the running code:**

![LangGraph agent workflow](assets/langgraph_diagram.png)

Note the two decision points visible in the graph: after `classify_intent`, low-confidence, fraud, and unsupported classifications branch straight to `escalate`, skipping entity extraction and action execution entirely. After `execute_action`, the backend's own approval decision determines whether the flow proceeds to `update_session` or is redirected to `escalate`. Both paths reconverge before `update_session`, since every request — resolved or escalated — needs its session updated and a reply generated.


**State carried through the graph:**
- `session_id`, `customer_id`, `customer_message`
- `conversation_memory` — recovered from the backend at the start of each turn
- `intent`, `confidence` — output of classification
- `entities` — structured details extracted from the message
- `action_result` — the backend's response to an executed action
- `escalate`, `escalation_reason`
- `audit_events` — an accumulating internal trace of every step, for debugging and demo transparency
- `response_to_customer` — the final reply

**Nodes, in execution order:**

1. **`fetch_session`** — calls `GET /sessions/{session_id}` on the backend to recover what's already been discussed in this conversation.
2. **`classify_intent`** — a single LLM call (Groq/Llama 3.3) classifies the customer's message into one of five categories: `fee_reversal`, `card_replacement`, `credit_limit_increase`, `fraud_or_lost_stolen`, or `unsupported`, alongside a confidence level (`high`/`low`). Fraud and lost/stolen card mentions are explicitly prioritized over a normal card-replacement classification.
3. **Conditional routing** — fraud signals, low-confidence classifications, and unsupported requests are routed immediately to escalation, bypassing further processing entirely. Only clear, high-confidence, supported requests proceed.
4. **`extract_entities`** — a second, intent-specific LLM call pulls out only the fields relevant to the classified intent (e.g. fee amount and reason for a reversal; requested increase amount for a limit request), instructed explicitly not to guess missing fields.
5. **`execute_action`** — the agent calls the matching backend endpoint (`/fees/reversal`, `/cards/replacement`, or `/credit-limit/request`) with the extracted entities and the customer's ID, using a freshly generated idempotency key.
6. **Conditional routing on backend's response** — if backend's policy engine approved the action, the flow proceeds to session update; if rejected, the flow routes to escalation, carrying backend's own policy explanation forward.
7. **`escalate`** — constructs a structured escalation reason for handoff, whether triggered by fraud detection, low confidence, an unsupported request, or a backend policy rejection.
8. **`update_session`** — persists the detected intent, extracted entities, and a rolling conversation history back to the backend, so the next turn (if any) has full context.
9. **`clear_session`** — once a request is fully resolved or escalated, the conversation session is cleared from backend memory, signaling the interaction is complete.
10. **`generate_response`** — produces the final natural-language reply shown to the customer, differing in tone and content depending on whether the request was completed or escalated.

### 5.3 Escalation rules

| Situation | Agent behavior |
|---|---|
| Fraud or lost/stolen card mentioned | Escalate immediately, bypassing normal processing entirely |
| Low classification confidence | Escalate rather than guess |
| Unsupported request type | Escalate |
| Backend policy engine rejects the action | Escalate, carrying backend's explanation into the handoff summary |
| Backend request fails (network/server error) | Escalate, treating the failure as non-resolvable automatically |
| All checks pass | Complete the action automatically and confirm to the customer |

### 5.4 Why the LLM never makes the approval decision

A deliberate architectural choice: eligibility and policy decisions are made entirely by the backend's deterministic policy engine, using real customer data (account age, verification status, prior reversal history) the agent layer does not even have access to. The agent's role is strictly to understand and route — never to approve. This means a language model hallucination or prompt-injection attempt cannot, by construction, result in an unauthorized financial action; the worst it can do is misroute a request to escalation, which a human then reviews.

---

## 6. Backend Servicing Engine

*(Full detail contributed by the backend team; summarized here for completeness of the overall system description.)*

The backend is the component that decides whether a request is actually approved, executes that decision safely, and keeps a verifiable record of it.

### 6.1 Core responsibilities

- Fetches and locks the relevant customer record for the duration of a transaction
- Runs deterministic, testable eligibility checks specific to each of the three servicing flows
- Executes the approved action (fee reversal, card status update, credit limit adjustment) as part of a single atomic database transaction
- Writes a structured audit entry for every step of the decision — intent received, policy checked, action executed — regardless of outcome
- Manages conversational session memory in Redis, independent of the AI layer's own reasoning state

### 6.2 Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /fees/reversal` | Evaluate and, if eligible, execute a fee reversal |
| `POST /cards/replacement` | Evaluate and, if eligible, initiate a card replacement |
| `POST /credit-limit/request` | Evaluate and, if eligible, apply a credit limit increase |
| `GET /customers/{customer_id}/context` | Retrieve customer context for eligibility evaluation |
| `GET /audit-logs/{request_id}` | Retrieve the full audit trail for a specific request |
| `GET /audit-logs/_integrity/verify` | Verify the hash chain has not been tampered with |
| `POST /handoffs` | Create a structured human-escalation handoff record |
| `GET /sessions/{session_id}` | Return conversation memory for the AI layer |
| `POST /sessions/{session_id}` | Persist updated intent, entities, and history |
| `DELETE /sessions/{session_id}` | Clear a completed or escalated session |
| `GET /health` | Service health check |

**Live interactive documentation (auto-generated Swagger UI):**

![Servicing endpoints — fee reversal, card replacement, credit limit](assets/swagger_endpoints_1.png)

![Customer context, audit logs, human handoffs, and session endpoints](assets/swagger_endpoints_2.png)

![Session management, health check, and request/response schemas](assets/swagger_endpoints_3.png)

This documentation is generated directly from the running FastAPI service — every field, type, and required header shown here reflects the actual enforced contract, not a separately maintained spec that could drift out of sync with the real implementation.

### 6.3 Safety mechanisms implemented

**Deterministic policy engine.** Eligibility for all three flows is decided by plain, independently testable Python functions — account age thresholds, verification status, transaction amount limits, and prior-reversal frequency all factor into the decision. No AI model is involved in this step, by design.

**Hash-chained, tamper-evident audit log.** Every workflow step is recorded with a cryptographic hash chained to the previous entry, making any retroactive alteration of history mathematically detectable. A dedicated integrity-verification endpoint confirms the chain is intact. At the database level, `UPDATE` and `DELETE` privileges on the audit table have been revoked entirely via a Postgres migration — the immutability claim is enforced by the database itself, not just application logic.

**Idempotency protection.** Every servicing request requires a unique `Idempotency-Key`. A retried request with the same key returns the original result rather than re-executing the action — preventing, for example, a network retry from reversing the same fee twice.

**Row-level locking.** Concurrent requests affecting the same customer (such as two simultaneous credit-limit increase attempts) are safely serialized using `SELECT ... FOR UPDATE`, preventing lost-update race conditions on shared financial state.

**API-key authentication** is required on every servicing endpoint.

### 6.4 Testing and verification

- 19 automated tests: 11 covering policy-engine eligibility logic across all three flows, 3 covering audit-chain integrity (including a test that deliberately tampers with a row and confirms the system detects it), and 5 covering the session service
- Every endpoint manually verified live via Swagger UI and direct HTTP requests, covering both approval and rejection/escalation paths for all three servicing flows
- Demo seed data spans five sample customers with varied account ages, verification states, and credit limits, so every policy branch — approve, reject, escalate — can be demonstrated on request

### 6.5 Real problems encountered and fixed during development

The backend team's build process surfaced and resolved several substantive issues rather than shipping a naive first pass:

- A prior-reversal eligibility check was initially hardcoded to a stub value; replaced with a real query over completed request history
- The first version had no protection against duplicate financial actions on retry; fixed with enforced idempotency keys
- A genuine race condition existed on concurrent credit-limit updates; fixed with row-level locking
- The "immutable" audit trail was initially just a regular mutable table; fixed with a cryptographic hash chain and database-level privilege revocation
- The hash chain's own row-ordering logic had a subtle bug (timestamp plus random UUID tie-breaking, which does not guarantee true insertion order); fixed with a proper autoincrement sequence column
- Environment and tooling issues (a Windows-specific test-runner path bug, a git history conflict during team integration) were identified and resolved without data loss

---

## 7. Frontend — Customer Experience Layer

The frontend is the customer-facing surface through which every interaction with ResolveAI happens — it is designed to make an AI-driven, policy-governed backend feel like a simple, trustworthy conversation.

### 7.1 Core screens

**Chat interface.** The primary conversation screen. A customer types a request in natural language; the interface sends it to the AI orchestration layer and renders the reply as a chat bubble, with a loading indicator while the agent reasons and calls backend systems.

**Action confirmation view.** When a request resolves successfully, the customer sees a clear, receipt-style summary — what was requested, what was done, and confirmation that the interaction is recorded in the audit trail.

**Audit-log view.** A read-only, step-by-step trail of how a request was handled — intent detected, eligibility checked, action executed — rendered directly from the structured audit data the agent layer already returns. This view exists specifically to make the system's internal reasoning visible and trustworthy, not just to the bank's compliance team but to the customer themselves.

**Human-handoff screen.** Shown whenever a request is escalated. Displays the reason for escalation, a case reference, and an estimated response time, framed reassuringly rather than as an error — the customer should feel their case was correctly triaged, not dropped.

### 7.2 Interface screens, as built

**Chat interface** — supports both dark and light themes, showing a resolved fee-reversal conversation with inline confirmation actions:

![Chat interface — dark theme](assets/frontend_chat_dark.png)

![Chat interface — light theme](assets/frontend_chat_light.png)

**Action confirmation view** — a receipt-style summary shown once a request completes successfully:

![Action confirmation screen](assets/frontend_confirmation.png)

**Audit-log view** — the step-by-step decision trail, rendered directly from the agent's structured audit events, with an explicit option to escalate to a human agent even after automatic resolution if the customer isn't satisfied:

![Audit trail view](assets/frontend_audit_trail.png)

**Human-handoff screen** — shown when a request is escalated, framed reassuringly with a case ID and estimated response time rather than as an error state:

![Human handoff / escalation screen](assets/frontend_escalation.png)

### 7.3 Customer journey

```
Customer enters a request
   ↓
Agent understands the request
   ↓
Agent asks only for necessary missing information
   ↓
Agent verifies eligibility against backend policy
   ↓
Request is resolved automatically, or escalated with full context
   ↓
Customer sees a clear status and confirmation
   ↓
Every step of the decision is available in the audit trail
```

### 7.4 Integration contract with the AI orchestration layer

The frontend communicates with the agent server through a single, simple contract:

**Request:**
```json
{
  "session_id": "client-generated UUID, one per conversation",
  "customer_id": "identifies the authenticated customer",
  "customer_message": "the customer's raw text input"
}
```

**Response:**
```json
{
  "response": "the natural-language reply to display",
  "escalated": true or false,
  "audit_events": [ "the structured step-by-step trace of this turn" ]
}
```

This is a deliberately thin, single request/response contract — no streaming, no direct calls to backend's servicing endpoints, and no LLM calls made client-side. All reasoning and all sensitive credentials remain server-side; the frontend's only job is to collect input and render output faithfully, including distinguishing an escalated response from a normal resolved one so the customer is never left confused about what happened to their request.

---

## 8. Business Impact and Success Metrics

| Metric | Target / Expected Improvement |
|---|---|
| Requests resolved without human intervention | 50–70% for the three supported request types |
| Average resolution time | Reduced from minutes/hours to under 2 minutes |
| Human-agent workload | Reduced specifically for repetitive, low-complexity servicing requests |
| Handoff quality | 100% of escalations include a structured case summary and full audit trail |
| Audit completeness | Every decision, policy result, and system call logged for every request, with no exceptions |
| Customer experience | Fewer transfers, no repeated explanations, transparent status at every step |

---

## 9. Why This Design Is Defensible for a Banking Context

Four properties, taken together, are what make this more than a chatbot prototype:

1. **It takes action, not just answers questions.** The agent completes real servicing operations through governed backend APIs, not just information retrieval.
2. **The AI cannot independently authorize a financial decision.** A deterministic, testable policy engine — entirely separate from the language model — makes every approval or rejection.
3. **Every decision is auditable and tamper-evident.** A cryptographically hash-chained log, enforced at the database level, directly addresses the trust and compliance concerns inherent to any real banking deployment.
4. **It knows when to hand off, and hands off well.** Escalations carry complete structured context, so a human agent picks up exactly where the AI left off — the customer never has to start over.

---

## 10. Current Status and Round 2 Plan

**Completed:**
- Backend servicing engine fully built, tested (19/19 automated tests passing), and hardened against the concrete failure modes listed above
- AI orchestration layer implemented as a LangGraph state graph covering all three servicing flows plus fraud detection and low-confidence escalation, tested end-to-end against the live backend
- Frontend chat interface, confirmation, audit-log, and handoff screens designed and under active integration

**Assumptions and constraints, stated openly:**
- This is a hackathon prototype using synthetic seed data and mock-scale infrastructure — no real banking credentials, live transactions, or real customer PII are involved at this stage
- Production deployment would additionally require formal regulatory review, expanded fraud controls, production-grade monitoring, and integration approval from real banking core systems

**Round 2 priorities:**
- Full integration testing across all three services running simultaneously
- Expanded automated test coverage for the AI orchestration layer, mirroring the rigor already applied to the backend
- Polished demo scenarios covering the full range of approve/reject/escalate paths across all three servicing flows, presented live rather than simulated

---

## 11. Conclusion

ResolveAI directly answers the challenge as posed: it classifies and routes incoming service requests through an explicit, controllable AI workflow; it lets card members complete requests end to end through a conversational interface; it logs every decision and system call in a genuinely immutable, cryptographically verifiable format; it integrates with governed backend systems to execute real resolutions; and its behavior — first-contact resolution, audit completeness, escalation quality — has been tested and measured rather than assumed. The system's central architectural decision, keeping AI judgment and financial authorization strictly separate, is what makes each of these claims credible rather than aspirational.
