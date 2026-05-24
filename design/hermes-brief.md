# Hermes — Solo-Founder AI Business Operating System

> One-page program brief for the new `hermes-ceo` repo. Covers what it is, what "done" looks like, the day-one use cases, the tech stack, and the implementation outline.

---

## 1. Program Overview

**What it is.** A chief-of-staff system for a solo founder running an AI analytics SaaS. The founder talks to **Hermes** in Slack/Telegram; Hermes plans the work, dispatches it to seven specialized department agents (Engineering, Product, Marketing, Sales, Customer Service, Finance, Operations), gates risky actions behind an approval layer, and reports back with a clean audit trail.

**Why it exists.** A solo founder's bottleneck is attention. Hermes shifts the founder from *doing* every department's work to *directing* AI agents that handle drafts, triage, research, monitoring, scheduling, and reporting — without surprises and without losing institutional memory.

**Core idea.** Mix **deterministic systems** (cron, workflows-as-code, state machines) for anything that touches money, customers, or production, with **agentic workflows** for everything that is judgment, drafting, or exploration.

**Operating principle.** Auto-act on low-risk work, notify on customer-visible work with a cancel window, block on irreversible work until the founder approves. Every action — auto or not — is logged.

**Architecture at a glance.**

```
You ──► Slack/Telegram ──► Hermes (orchestrator + chat + reporter)
                                │
                                ▼
                       Planner + Risk classifier
                                │
   ┌──────────┬──────────┬──────┴──────┬─────────┬──────────┐
   ▼          ▼          ▼             ▼         ▼          ▼
Engineering Product  Marketing       Sales   Finance   Customer Svc / Ops
   └──── shared skills: email, calendar, github, docs ─────┘
                                │
                                ▼
           Approval layer (auto / notify / approve)
                                │
   ┌────────────┬───────────────┼──────────────┐
   ▼            ▼               ▼              ▼
Postgres   pgvector         Audit log    Cron / queues
 (state)   (memory)        (every act)   (workflows)
                                │
                                ▼
              Next.js dashboard (review, approvals, configs)
```

---

## 2. Success Criteria

The system is "working" when **all seven** of these are demonstrably true:

| # | Criterion | Concrete test |
|---|---|---|
| 1 | **End-to-end orchestration** | DM Hermes "review my latest PR and draft a reply to the top customer email." Both happen; you get a single summary; both actions appear in the audit log. |
| 2 | **Approval flow** | A `notify` action queues with a cancel window; an `approve` action blocks until you ✅ in Slack or the dashboard. |
| 3 | **Risk gating** | Ask the Marketing agent to call a Stripe skill. Policy layer denies it, denial is logged, you get an alert. |
| 4 | **Cross-thread memory** | Tell Hermes a preference in thread A ("I sign off as 'best, andt'"); open thread B and ask it to draft an email — the signature appears unprompted. |
| 5 | **Scheduled work** | The weekly review cron runs Monday 8am; a single Slack thread lands with synthesized status from every department. |
| 6 | **Eval guardrails** | Change an agent's prompt in a way that breaks a golden eval; CI fails the PR. |
| 7 | **Kill switch** | One click in the dashboard pauses every in-flight run and every queued action; nothing outbound goes until you re-enable. |

**Quantitative targets for the first 90 days:**

- ≥ **70%** of customer-service ticket replies sent are agent drafts you accepted with ≤1 edit.
- ≤ **5 min** median time-to-first-response on inbound customer emails (agent-drafted, you-approved).
- **0** unapproved actions in the `approve` tier reach external systems.
- ≥ **80%** of Monday weekly reviews land before 9am without manual intervention.
- LLM spend / agent run trends **down month-over-month** at constant throughput (prompt-cache hit rate ≥ 60%).

---

## 3. Use Cases (day-one workflows)

### A. Engineering
- **PR review pass.** "Hermes, review PR #42." → Engineering agent runs lint/tests, reads diff, posts a structured review (correctness, security, style); Hermes summarizes in DM. Auto.
- **CI babysitting.** PR you opened starts failing → Engineering agent re-diagnoses, fixes flake if obvious, asks you if not. Auto for re-runs, ask for code changes.
- **Issue → branch → PR.** "Convert issue #88 into a PR." → branch created, plan written, code drafted, PR opened **as draft**, you approve to mark ready.

### B. Customer Service
- **Inbound ticket triage.** New email → classifier tags it (bug / billing / sales / how-to / churn risk) → CS agent drafts reply against KB → `notify` queue → countdown send. Auto-send for trivial categories you've pre-approved.
- **Escalation.** Sentiment/keyword triggers ("refund", "lawyer", "cancel") → blocks send, pings you, drafts three response options.

### C. Sales
- **Lead enrichment + first touch.** New trial signup → enrich (company, role, ICP fit score) → CS-style welcome + a sales follow-up scheduled 24h later if ICP ≥ threshold.
- **Demo scheduling.** Inbound "can we chat?" → Sales agent proposes 3 slots from your calendar → confirms → adds context doc to invite.

### D. Marketing
- **Content drafts.** Weekly: "draft a launch note for [feature]" → Marketing agent produces blog + tweet thread + LinkedIn post + email; all `notify` queued for your edit.
- **SEO research.** Topic in, brief out (keyword cluster, competitor angles, suggested outline).

### E. Product
- **Feedback synthesis.** Every Friday, all customer messages + Slack threads tagged "feedback" → Product agent clusters themes, surfaces top 5 with quotes and counts.
- **Spec drafting.** "Spec the new dashboard widget" → draft RFC in Notion/docs, sized by Engineering agent.

### F. Finance
- **Revenue snapshot.** Daily Stripe pull (Phase 3) → cards: MRR, new, expansion, churn, failed payments.
- **Failed payment workflow.** Deterministic: retry schedule + customer email (notify) + Slack alert. No LLM in the money path.

### G. Operations (and Hermes itself)
- **Weekly review.** Monday 8am: every agent posts status; Hermes synthesizes one doc — wins, blockers, decisions needed, week plan.
- **Daily digest.** 8pm: what happened today across all departments, with links into the dashboard.
- **Meeting prep.** 30 min before each meeting: brief with attendee context, last touch, agenda draft, open threads.
- **"Catch me up."** Anytime: Hermes scans the last N hours of activity, gives you the 90-second version.

---

## 4. Technical Details

### 4.1 Stack

| Layer | Choice | Why |
|---|---|---|
| API | **FastAPI** (Python 3.12) | Async, mature, plays well with LLM SDKs |
| Agent runtime | **Anthropic SDK (primary)** + OpenAI SDK (fallback) | Prompt caching on by default; multi-provider via a thin abstraction |
| DB | **Postgres 16** + **pgvector** | Single store for relational + embeddings |
| Queue / bus | Postgres **LISTEN/NOTIFY** (v1) → **Redis Streams** (when scale demands) | Start simple; upgrade later |
| Worker | Python (`arq` or `dramatiq`) | Cron + async jobs |
| Web | **Next.js 14** (App Router) + TypeScript | Dashboard, approvals UI, audit log |
| Auth | **Clerk** or **Auth.js** | One user (you), but extensible |
| Tracing | **Langfuse** (self-host) | Per-run cost, latency, token use |
| Logging | **structlog** → Postgres → S3 | Cheap short-term, archival long-term |
| Secrets | **Doppler** / Infisical | OAuth tokens KMS-encrypted at rest |
| Deploy | **Fly.io** (api, worker, web) + managed Postgres | Solo-founder friendly |
| Local dev | **Docker Compose** | `docker compose up` brings the whole stack |

### 4.2 Data model (load-bearing tables)

- `users` — you (and future teammates).
- `threads` — one per Slack/Telegram thread; holds episodic history.
- `messages` — append-only chat log.
- `agent_runs` — every invocation: agent, prompt version, inputs, outputs, tokens, cost, latency, trace ID.
- `actions` — every external side-effect: tier (`auto`/`notify`/`approve`), status, payload, result, agent_run_id.
- `approval_requests` — pending `approve`-tier actions, with countdown and resolver.
- `audit_log` — append-only mirror of every action, immutable.
- `memories` — `{kind: episodic|semantic|procedural|identity, content, embedding, source, weight}`.
- `workflows` — registered deterministic flows; `workflow_runs` — instances + state.
- `policies` — risk rules (allow/deny/classifier hints) editable from the dashboard.

### 4.3 Risk / approval layer

1. **Deterministic prefilter** — hard allow/deny list per agent × skill.
2. **LLM classifier** — only for the gray zone; outputs tier + reason.
3. **Approval surfaces** — Slack Block Kit buttons + dashboard cards. Same action ID across surfaces.
4. **Audit hook** — every classification + every execution writes to `audit_log` *before* the side effect runs.
5. **Kill switch** — sets a global flag the runtime checks before every external call; in-flight runs cancel cooperatively at the next checkpoint.

### 4.4 Memory layer

- **Episodic**: thread history, summarized when it exceeds N tokens (trajectory-compression pattern).
- **Semantic**: pgvector index over docs, emails, decisions, customer notes; hybrid BM25 + vector retrieval.
- **Procedural**: structured rules + few-shot examples learned from your corrections; reviewed weekly in the dashboard.
- **Identity**: small editable KV always injected into every agent's system prompt.

### 4.5 Integrations (v1 core ops bundle)

Common interfaces (`EmailProvider`, `CalendarProvider`, `ChatProvider`, `CodeHostProvider`) so providers are swappable.

- **Gmail API** — read, draft, send-with-approval; OAuth refresh tokens encrypted.
- **Google Calendar API** — read, propose, create.
- **Slack** — Bolt SDK; bot user, slash commands, Block Kit modals/approvals, events API.
- **Telegram** — `python-telegram-bot`; mirror command surface as Slack.
- **GitHub** — REST + webhooks; PR/issue events trigger workflows; CI status polled.

### 4.6 Observability & evals

- Langfuse traces every LLM call and tool use; cost rolled up per agent per day in the dashboard.
- `/evals/goldens/<agent>/*.yaml` — frozen task → expected behavior.
- `/evals/runners/run_all.py` — CI job that runs on any change to an agent's prompt or skill set; a regression fails the PR.

### 4.7 Security

- Tokens encrypted with a KMS-backed key; never logged.
- Per-agent scope allowlists (Marketing cannot reach Stripe even if instructed).
- Outbound rate limits + circuit breakers per integration.
- Append-only `audit_log` with periodic hash-chain checkpoint (cheap tamper-evidence).

---

## 5. Implementation Details

### 5.1 Repo layout

```
/apps
  hermes-api/         FastAPI: chat ingress, agent runtime, REST for dashboard
  hermes-web/         Next.js: dashboard, approvals queue, audit, configs
  hermes-worker/      Background: cron, async agent jobs, long workflows

/packages
  agents/             Hermes + department agents (one module each)
  skills/             Reusable capabilities (send_email, schedule_meeting, open_pr, …)
  workflows/          Deterministic workflow definitions (Python + YAML)
  core/               LLM clients, prompt registry, tracing, memory, eval
  integrations/       Provider adapters: Gmail, GCal, Slack, TG, GitHub
  db/                 SQLAlchemy models, Alembic migrations
  policies/           Risk classifier, allow/deny lists, kill switch

/infra
  docker-compose.yml  Local dev: postgres + redis + api + worker + web
  fly.toml | terraform/

/evals
  goldens/            Frozen task → expected behavior per agent
  runners/            Eval harness, regression checks
```

### 5.2 Critical files (design these first; everything else is downstream)

- `packages/core/agent_runtime.py` — base agent class: prompt + tools + memory + tracing + risk gating. Every department agent inherits.
- `packages/core/llm.py` — provider routing (Anthropic primary, OpenAI fallback), prompt caching on by default.
- `packages/policies/risk.py` — classifier + allow/deny lists + audit hook. Touched by every action.
- `packages/agents/hermes/` — system prompt, planner, dispatcher, reporter.
- `packages/db/models.py` — see §4.2.
- `apps/hermes-api/routes/slack.py` — events, slash commands, Block Kit approvals.
- `packages/workflows/registry.py` — workflow definitions + trigger bindings.
- `infra/docker-compose.yml` — Postgres (with `pgvector`), Redis, api, worker, web.

### 5.3 Phasing (6-week ramp)

| Phase | Week | Scope | Demonstrable outcome |
|---|---|---|---|
| 0 | 1 | Repo scaffold, Docker Compose, FastAPI + Next.js + Postgres + Alembic + auth | `docker compose up` → "hello" dashboard |
| 1 | 2 | Hermes core: Slack bot, planner, dispatcher stub, memory, audit log, kill switch | DM Hermes; it remembers you across threads |
| 2 | 3 | Engineering + Operations agents end-to-end, risk policy, approval queue (Slack + web) | "Review PR #42" → approved/rejected with audit |
| 3 | 4 | Marketing, Sales, Product, CS, Finance agents scaffolded (prompts iterate weekly) | All 7 departments answer to Hermes |
| 4 | 5 | Deterministic workflows, scheduler, weekly-review digest | Mondays open with synthesized status doc |
| 5 | 6+ | Procedural-memory learning loop, eval CI, cost dashboards | System gets visibly better week over week |

### 5.4 Patterns to reuse from the existing `hermes_agent` repo

- **Skill auto-discovery + learning loop** (`/skills/`, `/plugins/memory/`) — model procedural memory on this.
- **Cron scheduler** (`/cron/jobs.py`, `scheduler.py`) — natural-language scheduled tasks with multi-channel delivery.
- **Multi-provider LLM adapters** (`/agent/`) — A/B Anthropic vs OpenAI per agent.
- **Gateway pattern** (`/gateway/`) — clean transport (Slack/TG/email) ↔ agent separation.
- **Trajectory compression** (`trajectory_compressor.py`) — for long agent runs that blow context.

### 5.5 Open decisions to make before Phase 0

1. **Hosting region** (Postgres + Fly app region; matters for Gmail/GCal latency).
2. **Single founder identity** vs early multi-user support (affects auth, RLS in Postgres).
3. **Notification cancel window** default (10 min? 30 min? per category?).
4. **Anthropic-only** for the first month or **dual-provider** from day one (cost vs robustness).
5. **Telegram vs Slack** as the *primary* surface — both, but which gets feature parity first.

These can be answered in a half-hour and locked into `docs/decisions/` as ADRs.

---

## 6. Definition of Done (for the program, not v1)

- All seven success-criteria tests pass on demand.
- 90-day quantitative targets met or trending toward them.
- Founder reports spending the majority of working hours on customer conversations, product direction, or strategic writing — not on the work the agents now do.
