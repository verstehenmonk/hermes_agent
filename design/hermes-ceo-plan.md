# Hermes: Solo-Founder AI Business Operating System

> Design doc for a **new repo** that uses the `hermes_agent` framework as a reference (not a dependency). Captured here so the plan lives next to its main inspiration.

## Context

You're a solo founder building an **AI analytics SaaS**. You want every department (engineering, product, marketing, sales, ops, finance, customer service) to be run by AI agents under your direction, with both deterministic systems (for high-stakes, repeatable work) and agentic workflows (for research, drafting, triage). This will live in a **new repo** — separate from the existing `hermes_agent` framework, which we'll treat as a reference, not a dependency.

**Hermes** is your chief of staff: orchestrator + messenger + conversational front-end (you said "get max value, use it all"). You talk to Hermes in Slack/Telegram; Hermes decomposes requests, dispatches to department agents, tracks progress, and reports back. Stack is **Python + Postgres + Next.js**. Default policy: **auto-act on low-risk, ask on high-risk**. v1 integrations are the **core ops bundle**: Email, Calendar, Slack/Telegram, GitHub.

The outcome we're after: a system that lets you spend your time on the highest-leverage decisions while the agents handle everything that can be drafted, triaged, scheduled, monitored, or reported — without surprises, with a clean audit trail, and with the ability to learn from your corrections.

---

## System overview

```
┌────────────────────────────────────────────────────────────────┐
│  You ──► Slack / Telegram ──► Hermes (orchestrator + chat)     │
│                                    │                            │
│                                    ▼                            │
│                            Planner & Risk classifier            │
│                                    │                            │
│        ┌───────────────┬───────────┼────────────┬──────────┐    │
│        ▼               ▼           ▼            ▼          ▼    │
│   Engineering      Product     Marketing      Sales     Finance │
│       │               │           │            │          │    │
│       └─── shared skills (email, calendar, github, docs) ──────┘
│                                    │                            │
│                                    ▼                            │
│             Approval layer (auto / notify / approve)            │
│                                    │                            │
│        ┌─────────────┬─────────────┼─────────────┐              │
│        ▼             ▼             ▼             ▼              │
│   Postgres      pgvector       Audit log     Cron/queues        │
│   (state)       (memory)       (every act)   (workflows)        │
│                                    │                            │
│                                    ▼                            │
│                       Next.js dashboard (review, approvals)     │
└────────────────────────────────────────────────────────────────┘
```

---

## Repo layout (new repo, recommended name `hermes-ceo`)

```
/apps
  hermes-api/         # FastAPI: chat ingress, agent runtime, REST for dashboard
  hermes-web/         # Next.js: dashboard, approvals queue, audit, configs
  hermes-worker/      # Background: cron, async agent jobs, long workflows

/packages
  agents/             # Hermes + department agents (one module each)
  skills/             # Reusable capabilities (send_email, schedule_meeting, open_pr, …)
  workflows/          # Deterministic workflow definitions (Python + YAML)
  core/               # LLM clients, prompt registry, tracing, memory, eval
  integrations/       # Provider adapters: Gmail, GCal, Slack, TG, GitHub
  db/                 # SQLAlchemy models, Alembic migrations
  policies/           # Risk classifier, approval rules, kill switch

/infra
  docker-compose.yml  # local dev: postgres + redis + api + worker + web
  fly.toml or terraform/  # deploy target

/evals
  goldens/            # frozen task → expected behavior per agent
  runners/            # eval harness, regression checks
```

---

## Hermes agent (the centerpiece)

A single agent that plays three roles:

1. **Conversational front-end** — Slack/Telegram bot. Handles natural-language requests, threads context, and answers in your tone.
2. **Planner & dispatcher** — Decomposes a request into tasks, picks one or more department agents, sends structured task envelopes via the internal bus (Postgres LISTEN/NOTIFY for v1, Redis Streams when scale demands).
3. **Reporter** — Collects results, summarizes, surfaces anything in the approval queue, and writes a daily digest.

**Memory it owns:**
- Per-thread episodic history (Postgres).
- Semantic memory across all of your business knowledge — emails, docs, decisions, customer notes — in pgvector.
- A small KV "identity" store: who you are, brand voice, no-go zones, current priorities. Editable from the web dashboard.

**Tooling it can call directly** (not via department agents): `ask_user`, `delegate(department, task)`, `search_memory`, `schedule_followup`, `read_audit_log`.

---

## Department agents (v1 set)

Each agent is a Python module under `/packages/agents/<name>/` with: system prompt, allowed skills, risk profile, and golden evals. Same shape for all; only the prompt and skill set differ.

| Agent | Owns | Primary skills |
|---|---|---|
| **Engineering** | PR triage, CI babysitting, issue → branch → PR, code review pass, deploy watch | `github.*`, `ci.*`, `code_review`, `run_tests` |
| **Product** | Spec drafts, roadmap upkeep, user-feedback synthesis, A/B-test design | `notion.*` or `docs.*`, `feedback.cluster`, `roadmap.update` |
| **Marketing** | Content drafts, social posts, email campaigns, SEO research, launch checklists | `email.draft`, `social.*` (later), `seo.research`, `content.write` |
| **Sales** | Lead enrichment, outbound drafts, demo scheduling, follow-ups | `email.draft`, `calendar.schedule`, `crm.upsert` (later) |
| **Customer Service** | Ticket triage, KB search, reply drafts, escalation | `email.read`, `email.draft`, `kb.search` |
| **Finance** | Revenue tracking, expense categorization, invoice drafts, burn alerts | `stripe.*` (later), `accounting.*` (later) |
| **Operations** | Calendar, meeting prep, doc filing, vendor renewals, weekly digest | `calendar.*`, `email.*`, `digest.compose` |

For v1 you only need to ship **Engineering + Operations** end-to-end. The others get scaffolding + a stub prompt and graduate as you have time.

---

## Deterministic systems vs agentic workflows

You explicitly asked for both. Rule of thumb:

- **Deterministic** = anything that touches money, customers, or production state. Anything that should happen the same way every time.
- **Agentic** = anything that's a draft, a research task, a triage decision, or an exploration.

**Deterministic systems to build:**
- **Scheduler/cron** (`hermes-worker`): daily digest, weekly review, monthly close, dunning runs, evals.
- **Workflows-as-code** (Python state machines, not LLM-decided):
  - `new_customer_signup` → CRM upsert + welcome email queued + Slack ping + first-touch task created
  - `failed_payment` → retry schedule + customer email + Slack alert
  - `pr_opened_by_me` → Engineering agent reviews → Hermes summarizes in DM
  - `weekly_review` → every agent posts status → Hermes synthesizes a single doc
- **Explicit state machines** for deals, tickets, deploys — with allowed transitions enforced in code.

**Agentic workflows** are everything else, expressed as agent runs.

---

## Risk / approval layer

Every action an agent wants to take is classified before execution:

- `auto` — drafting, internal notes, research, reporting, dashboard updates. Just do it.
- `notify` — anything customer-visible. Goes to a "leaving in N minutes" queue; you can cancel from Slack.
- `approve` — money out, prod deploys, mass emails, account changes, anything irreversible. Blocked until you approve in Slack or the web dashboard.

Classification is hybrid: a deterministic allow/deny list first, then an LLM classifier for the gray zone. Every action — auto or not — lands in `audit_log` with input, output, agent, cost, and trace ID.

A **kill switch** in the dashboard pauses all agents in one click.

---

## Memory model

Four kinds, all backed by Postgres + pgvector:

1. **Episodic** — conversation threads. Used for short-term context.
2. **Semantic** — embedded docs, emails, decisions, customer notes. Used for retrieval.
3. **Procedural** — skills/rules the system learns from your corrections ("when a Stripe dispute lands, always draft a reply within 1 hour"). Stored as structured rules + few-shot examples.
4. **Identity** — you, your business, brand voice, priorities. Small, editable, always in the system prompt.

The `hermes_agent` framework's "closed learning loop" is a good reference for #3 — review `/plugins/memory` and the agent-curated memory patterns.

---

## Integrations (v1 core ops bundle)

Built as **pluggable adapters** behind a common interface (`EmailProvider`, `CalendarProvider`, `ChatProvider`, `CodeHostProvider`) so you can swap Gmail → Outlook, Slack → Discord, later.

- **Email**: Gmail API (read, draft, send-with-approval). OAuth + refresh tokens encrypted at rest.
- **Calendar**: Google Calendar API.
- **Chat/UI**: Slack bot (primary) + Telegram bot (mobile fallback). Both register the same command surface.
- **GitHub**: REST + webhooks for PR/issue events; webhooks → workflow triggers.

Stripe / CRM / analytics show up in Phase 3.

---

## Observability & evals

- **Tracing**: Langfuse (self-hostable, open source) on every LLM call and tool use.
- **Cost tracking** per agent run, exposed in dashboard.
- **Structured logs**: `structlog` → Postgres for short term, S3/object store for long term.
- **Eval harness** in `/evals`: each agent ships with golden tasks (e.g., "triage this PR", "draft reply to this ticket"); a CI job runs them on every change to the agent's prompt or skills.

---

## Security

- Secrets in Doppler or Infisical (not in env files past dev).
- OAuth tokens encrypted with a KMS-backed key.
- Per-agent scope allowlists — Marketing can't call Stripe even if it asks nicely.
- Outbound action rate limits + circuit breakers.
- Audit log is append-only.

---

## Phasing (suggested 6-week ramp)

| Phase | Scope | Outcome |
|---|---|---|
| **0 (week 1)** | Repo scaffold, Docker Compose, FastAPI + Next.js + Postgres + Alembic + auth | You can `docker compose up` and see a "hello" dashboard |
| **1 (week 2)** | Hermes core: Slack bot, planner, dispatcher stub, memory, audit log, kill switch | You can DM Hermes and it remembers you across threads |
| **2 (week 3)** | Engineering + Operations agents end-to-end, risk policy, approval queue in Slack + web | You can say "review PR #42" and get an approved-or-rejected outcome |
| **3 (week 4)** | Marketing, Sales, Product, Customer Service, Finance agents (scaffolded; prompts iterated weekly) | All seven departments answer to Hermes |
| **4 (week 5)** | Deterministic workflows, scheduler, weekly-review digest | Mondays open with a synthesized state-of-the-business doc |
| **5 (week 6+)** | Procedural memory (learning loop), eval CI, cost dashboards | The system gets visibly better week over week |

---

## Critical files / modules to design first

When you start building, these are the load-bearing pieces — get them right early:

- `packages/core/agent_runtime.py` — the base agent class: prompt + tools + memory + tracing + risk gating. **Every department agent inherits from this.** Look at `hermes_agent/run_agent.py` and `hermes_agent/agent/` (the 47 provider adapters) as reference for tool-calling loops and multi-provider support.
- `packages/core/llm.py` — model client with provider routing (Anthropic primary, OpenAI fallback), prompt-cache friendly. Turn on prompt caching by default.
- `packages/policies/risk.py` — the classifier + allow/deny lists + audit hook. Touched by every action.
- `packages/agents/hermes/` — system prompt, planner, dispatcher, reporter.
- `packages/db/models.py` — `User`, `Thread`, `Message`, `Action`, `AuditLog`, `ApprovalRequest`, `Memory`, `WorkflowRun`. Get the schema right; everything else is downstream.
- `apps/hermes-api/routes/slack.py` — Slack events, slash commands, Block Kit approvals.
- `packages/workflows/registry.py` — workflow definitions + trigger bindings.
- `infra/docker-compose.yml` — Postgres (with `pgvector`), Redis, api, worker, web.

---

## Patterns to reuse from the existing `hermes_agent` repo

You don't need to depend on it, but borrow these designs:

- **Skill auto-discovery + learning loop** (`/skills/`, `/plugins/memory/`) — model your procedural memory after this.
- **Cron scheduler** (`/cron/jobs.py`, `scheduler.py`) — natural-language scheduled tasks with multi-channel delivery.
- **Multi-provider LLM adapters** (`/agent/`) — useful when you want to A/B Anthropic vs OpenAI per agent.
- **Gateway pattern** (`/gateway/`) — clean separation between transport (Slack/TG/email) and agent logic.
- **Trajectory compression** (`trajectory_compressor.py`) — for long-running agent runs that blow context.

---

## Verification (how you'll know it works)

Once built, the system is healthy if:

1. **End-to-end smoke**: DM Hermes in Slack with "review my latest PR and draft a reply to the top customer email"; both happen, you get a single summary, and both actions appear in the audit log.
2. **Approval flow**: trigger a `notify` action (e.g., outbound email draft) and an `approve` action (e.g., a fake "issue refund $X"); first executes after countdown unless cancelled, second blocks on your approval.
3. **Risk gating**: ask the Marketing agent to call a Stripe skill; the policy layer denies it, denial is logged, you get an alert.
4. **Memory**: tell Hermes a preference in thread A ("I sign off as 'best, andt'"); open thread B and ask it to draft an email — the signature shows up without being asked.
5. **Cron**: weekly review runs Monday 8am; a single Slack thread lands with synthesized status from every agent.
6. **Eval CI**: change an agent prompt that breaks a golden; CI catches it and fails the PR.
7. **Kill switch**: hit it in the dashboard; in-flight agent runs cancel, queued actions pause, no further outbound work happens until you re-enable.

If all seven pass, you have a system that can actually run the business.
