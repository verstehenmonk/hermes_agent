# Solo Business Operating System

A management system for a one-person AI SaaS B2B company, built on top of [Hermes Agent](../README.md). It gives you the leverage of an executive team without hiring one: each department is a skill the agent can load on demand, and routine work runs deterministically on a schedule.

You stay in the loop via **Telegram** (interactive + alerts) and **Email** (long-form daily/weekly digests).

## The two layers

**Operating layer** (this directory, `business/`)
Plain markdown + a handful of Python scripts. The CHARTER, department briefs, and rituals are the *constitution* the agent reads. The scripts are deterministic — they pull numbers from Stripe/PostHog/Linear/GitHub and hand the agent a clean snapshot to reason over. `cron.yaml` and `webhooks.yaml` declare what runs when.

**Agent layer** (`../skills/business/`)
One Hermes skill per department (engineering, product, marketing, sales, customer-success, finance, operations, legal) plus a `ceo` skill that orchestrates them. Each skill is a domain expert the agent steps into when you (or a cron job) ask for that department's work.

```
You / cron / webhook
        │
        ▼
   Hermes Agent  ──  loads CHARTER + relevant department brief + skill
        │                          │
        ▼                          ▼
deterministic script         agentic workflow
(numbers, scrapes, diffs)    (reasoning, drafting, deciding)
        │                          │
        └──────────► output ◄──────┘
                       │
                       ▼
              Telegram / Email / Linear / Stripe / ...
```

The deterministic and agentic halves matter. Don't ask the agent to compute MRR — let `scripts/metrics_snapshot.py` do that and feed the agent the number. Don't write a Python script to qualify a sales lead — let the agent read the email and decide.

## The departments

| Skill | Owns | Lives in |
|---|---|---|
| `ceo` | Strategy, weekly review, decisions log, cross-department orchestration | `skills/business/ceo` |
| `engineering` | Code, PRs, on-call, releases, error budget | `skills/business/engineering` |
| `product` | Roadmap, specs, user research, analytics | `skills/business/product` |
| `marketing` | Content, SEO, social, launches, attribution | `skills/business/marketing` |
| `sales` | Pipeline, outbound, demos, contracts | `skills/business/sales` |
| `customer-success` | Onboarding, support, churn signals, expansion | `skills/business/customer-success` |
| `finance` | MRR, burn, runway, invoices, taxes | `skills/business/finance` |
| `operations` | Vendors, secrets, scheduling, internal docs | `skills/business/operations` |
| `legal` | Contracts, ToS, DPAs, compliance | `skills/business/legal` |

Use them directly: `/ceo`, `/engineering`, `/sales`, etc. Or let the cron jobs do it.

## The cadence

| When | What | How |
|---|---|---|
| Every weekday 07:30 | **Daily brief** — yesterday's metrics + today's top 3 + inbox triage | cron → `scripts/metrics_snapshot.py` → `ceo` skill → Telegram |
| Hourly during work hours | **Inbox sweep** — triage Gmail, draft replies, surface escalations | cron → `customer-success` + `sales` skills → Telegram |
| Every Friday 16:00 | **Weekly review** — what shipped, what slipped, decisions, next week's bets | cron → all department skills → Email digest |
| 1st of month 09:00 | **Monthly close** — MRR, churn, burn, cohort retention, narrative | cron → `finance` + `product` skills → Email |
| Quarterly | **OKR review** — score last quarter, set next quarter's three bets | cron → `ceo` skill → Email |
| Real-time | **Alerts** — Stripe failed payment, Sentry error spike, PR blocked > 24h, customer churn signal | webhooks → relevant department skill → Telegram |

All of this is in `cadences.md` and codified in `cron.yaml` + `webhooks.yaml`.

## Recommended stack (picked for an AI SaaS B2B solo founder)

Chosen for: low ops burden, generous solo-tier pricing, good APIs the agent can call directly.

- **Engineering** — GitHub (code) + Linear (issues) + Sentry (errors) + Vercel/Fly (host)
- **Product** — PostHog (analytics + feature flags + session replay, single tool)
- **Marketing** — Astro site + Resend (email) + Plausible *or* PostHog (reuse) + Typefully (social drafting)
- **Sales** — Attio (modern CRM with a real API) + Cal.com (booking) + Apollo (data)
- **Customer success** — Plain (B2B support, API-first) + Loops (lifecycle email)
- **Finance** — Stripe (revenue) + Mercury (banking) + Beancount or QBO (books)
- **Operations** — Notion (SOPs + decisions log) + 1Password (secrets) + Google Workspace
- **Legal / compliance** — Stripe Atlas docs + Vanta (SOC 2) + Iubenda (policies)
- **Comms** — Telegram (you), Slack (customers), Email (long-form)

You don't need all of these on day one. The skills degrade gracefully — if `STRIPE_API_KEY` isn't set, the finance skill says "Stripe not connected" instead of failing.

## Install

```bash
# 1. Fill in the charter — this is the only required step
$EDITOR business/CHARTER.md

# 2. Set API keys for the platforms you actually use
$EDITOR ~/.hermes/.env

# 3. Install cron jobs and webhooks (idempotent)
business/install.sh

# 4. Verify
hermes cron list
hermes webhook list

# 5. Smoke test
hermes -p "/ceo morning brief"
```

## Where to look next

- **`CHARTER.md`** — fill this in. It's the single source of truth on what the business is, who it serves, and what success looks like. Every skill reads it.
- **`north-star.md`** — your metrics. Edit the targets.
- **`cadences.md`** — when each ritual runs.
- **`departments/*.md`** — the brief for each function: scope, KPIs, weekly questions. The agent reads the relevant one when you invoke that skill.
- **`rituals/*.md`** — the playbooks for daily standup, weekly review, monthly close, quarterly OKRs.
- **`scripts/*.py`** — deterministic data-gathering. Run them standalone to debug.

## Design principles

1. **The charter is the constitution.** Every skill reads `CHARTER.md` first. When the business changes, you edit one file.
2. **Deterministic for numbers, agentic for judgment.** Scripts compute. Agent decides.
3. **One department, one skill, one brief.** Each department brief is short and edited by you — not by the agent. The agent's behavior changes when the brief changes.
4. **The CEO skill is the only orchestrator.** Department skills don't call each other. They report up.
5. **Every ritual produces a written artifact.** Daily briefs, weekly reviews, decisions — all archived under `~/.hermes/business/journal/` so next week's agent can read last week's reasoning.
6. **Fail loud, never silently.** If Stripe is down, the finance skill says so in the brief. No quiet retries that mask reality.
