# Solo Business OS — built on Hermes Agent

A single-operator business stack where Hermes Agent is the runtime, deterministic Python/shell scripts are the spine, and LLM-driven skills handle judgment. You own one inbox, one dashboard, one approval queue. The agents own everything else.

---

## 1. Program overview

### Goal
Let one person run a company across **Engineering, Product, Marketing, Sales, Operations, Finance, and Customer Service** without context-switching between ten SaaS apps. Each function is implemented as:

- a **deterministic core** — a Python script or cron job that fetches, validates, computes, and writes — *no LLM involved*; and
- an **agentic shell** — a Hermes skill that reasons over the deterministic output, drafts the human-facing artifact, and queues actions for approval.

This split is the whole design. Determinism handles anything that must be repeatable, auditable, or cheap. Agents handle anything that needs judgment, writing, or cross-domain synthesis.

### Operating model
```
                ┌──────────────────────────────┐
                │   You (solo operator)        │
                │   one inbox · one queue      │
                └────────────┬─────────────────┘
                             │ approves / redirects
                             ▼
        ┌──────────────────────────────────────────────┐
        │   Hermes Agent  (TUI · Telegram · Slack)     │
        │   skills · cron · webhooks · MCP · memory    │
        └─────┬──────────┬──────────┬──────────┬───────┘
              │          │          │          │
       ┌──────▼─┐   ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
       │ Eng    │   │Growth  │  │Revenue │  │ Ops    │
       │Skills  │   │Skills  │  │Skills  │  │Skills  │
       └──────┬─┘   └────┬───┘  └───┬────┘  └──┬─────┘
              ▼          ▼          ▼          ▼
       ┌──────────────────────────────────────────────┐
       │ Deterministic core: scripts, SQL, GraphQL,   │
       │ Stripe API, GitHub API, Linear, mailers…     │
       └──────────────────────────────────────────────┘
```

### Layers
| Layer | Lives in | Touched by |
|---|---|---|
| **L0 — Source of truth** | Stripe, GitHub, Linear, Notion, Postgres, S3 | Anyone (read-only by default) |
| **L1 — Deterministic core** | `solo_business/scripts/*.py` | Cron + agents |
| **L2 — Agentic skills** | `skills/business/*` | Hermes during conversations + cron |
| **L3 — Schedulers & triggers** | Hermes cron, webhook subscriptions | Hermes |
| **L4 — Surface** | Telegram / Slack / TUI + a single Markdown daily brief | You |

---

## 2. Success criteria

These are the things the system has to be true for, not "nice to haves." Each one is measurable.

| # | Criterion | Measurement | Target |
|---|---|---|---|
| SC-1 | **One operator, full function coverage** | All 7 functions (Eng, Product, Marketing, Sales, Ops, Finance, CS) have at least one cron job *and* one skill defined. | 7/7 |
| SC-2 | **Inbox-zero by 9am local** | Daily brief generated and delivered before 09:00, summarizing overnight events from all functions. | ≥6 of last 7 days |
| SC-3 | **No silent failures** | Every cron job writes a structured run log; failures surface to Telegram within 5 minutes. | 100% of failed runs alert |
| SC-4 | **Reversible by default** | Destructive actions (send, charge, deploy, delete) require explicit approval unless allow-listed for the function. | 0 un-approved destructive actions / month |
| SC-5 | **Audit trail** | Every agent action writes to `~/.hermes/business/audit.jsonl` with timestamp, skill, inputs, outputs, approval state. | Reconstructable for any past 90 days |
| SC-6 | **Cost ceiling** | Daily LLM spend < $X (configurable; default $5/day). Daily ops cost (LLM + infra) visible on brief. | ≤ ceiling on ≥27 days/month |
| SC-7 | **Hermes-native** | No new agent framework, no new scheduler. Everything is implemented as Hermes skills, cron jobs, webhooks, and scripts. | 0 ad-hoc daemons |
| SC-8 | **Bus-factor 1 is OK** | Onboarding doc + restore script can rebuild the OS on a fresh `$5 VPS` in ≤30 minutes. | Tested quarterly |

### Anti-goals
- Not a CRM, ERP, or data warehouse — it integrates with whatever you already use.
- Not a multi-tenant system — single operator, single Hermes home directory.
- No new UI to maintain — the surface is messaging + a daily Markdown file.

---

## 3. Use cases

Grouped by function. Each line is a real recurring job — not a hypothetical. Each row maps to a **cron job** (deterministic trigger + script + skill) or a **webhook subscription** (event-driven).

### 3.1 Engineering
| Trigger | What runs | Output |
|---|---|---|
| `0 2 * * *` (nightly) | Pull top P1/P2 issue from Linear, attempt fix via subagent, open draft PR | PR link in morning brief |
| GitHub `pull_request.opened` | Code-review skill leaves inline comments, requests changes, or approves | PR review |
| GitHub `workflow_run.completed` (failure) | Diagnose CI failure, propose fix, push if confidence > threshold | Telegram alert + fix PR |
| `every 15m` | Health-check production endpoints; if down, page operator | Telegram with last-known-good vs current |
| Weekly Mon 08:00 | Dependency audit (CVE scan + outdated deps) | Notion page + Linear issues for criticals |

### 3.2 Product
| Trigger | What runs | Output |
|---|---|---|
| Daily 07:00 | Aggregate user feedback (Intercom, GitHub issues, Discord) → cluster → rank | Top-5 themes in brief |
| Webhook `feature_flag.toggled` | Snapshot active flags + write changelog entry | Notion + Slack |
| Weekly Fri 16:00 | Generate experiment readout from analytics warehouse | Stat-sig table + recommendation |
| On-demand `/spec <idea>` | Skill writes one-page PRD from a sentence-long input, attaches user-evidence | Draft PRD in Notion |

### 3.3 Marketing
| Trigger | What runs | Output |
|---|---|---|
| Weekly Mon 09:00 | Plan content calendar from backlog + trending topics | Schedule in Notion |
| Daily 16:00 | Draft tomorrow's social posts (LI/X), queue for approval | Draft thread + approve/edit buttons |
| Monthly 1st | SEO crawl + content-drift report | Top 20 pages with action items |
| On `signup.completed` | Add to drip; personalize first email with profile lookup | Sent email + audit row |

### 3.4 Sales
| Trigger | What runs | Output |
|---|---|---|
| New inbound (form / webhook) | Enrich (Clearbit-equiv), score, draft reply within 5 min | Draft reply + lead row |
| Daily 08:00 | Pipeline standup: deltas since yesterday, stalled deals, next actions | Brief section |
| `every 2h` business hours | Watch shared inbox for buying signals (keywords + sentiment) | Telegram nudge |
| Weekly Fri 17:00 | Forecast next-month bookings from current pipeline + close rates | Spreadsheet update |

### 3.5 Operations
| Trigger | What runs | Output |
|---|---|---|
| Daily 23:00 | Backup Postgres, encrypt, ship to S3; verify restore on sample | Status line in brief |
| `every 5m` | Tail error logs; group by fingerprint; open Linear issue if novel × frequency > N | Linear issue |
| Weekly Sun 22:00 | Rotate secrets nearing expiry; open Linear issue 14 days before | Issue + Telegram |
| Monthly 1st | Vendor review: usage vs spend per SaaS, flag candidates to cut | Brief section |

### 3.6 Finance
| Trigger | What runs | Output |
|---|---|---|
| Daily 06:00 | Stripe MRR/ARR snapshot, refunds, failed payments, dunning queue | Brief section |
| `invoice.payment_failed` webhook | Trigger dunning ladder; pause service if 3rd attempt fails | Audit row + customer email |
| Monthly 28th | Close-the-month: reconcile Stripe ↔ bank ↔ accounting; flag drift | PDF report |
| Quarterly | Runway model under 3 scenarios from current burn + pipeline | Notion doc |

### 3.7 Customer service
| Trigger | What runs | Output |
|---|---|---|
| New ticket | Classify, attach context (account, last events), draft reply citing docs | Draft in queue |
| `every 30m` | SLA watcher: any ticket > SLA → escalate via Telegram | Alert |
| Weekly Fri 12:00 | CSAT + top issue themes + docs gap list | Brief section + docs PRs |
| On `user.churned` | Exit survey trigger + retention-loss writeup | Notion + brief |

---

## 4. Technical details

### 4.1 Stack
Everything runs inside one Hermes home directory (`~/.hermes/`) plus this repo. No new daemons. No new database.

| Concern | How it works |
|---|---|
| **Runtime** | Hermes Agent (this repo) — TUI + gateway + cron + webhook server |
| **Triggers** | `hermes cron` (cron expressions + `every Xm/h/d`) and `hermes webhook subscribe` (GitHub, Stripe, generic POST + HMAC) |
| **Reasoning** | Skills in `skills/business/*` — each is a single `SKILL.md` (frontmatter + Markdown body) Hermes loads on demand |
| **Determinism** | Plain Python scripts in `solo_business/scripts/` — no LLM, just APIs and SQL. Invoked from cron via `--script` |
| **Memory** | Hermes' built-in memory + a per-function append-only journal in `~/.hermes/business/journals/<function>.jsonl` |
| **Audit** | Hermes' session logs + `~/.hermes/business/audit.jsonl` (every approval-gated action) |
| **Delivery** | `--deliver telegram` / `slack` / `email` / `local` — one command, any platform |
| **Models** | Choose per-job. Default: Sonnet for reasoning, Haiku for classification, DeepSeek/local for high-volume monitors. |
| **Secrets** | `.env` loaded by Hermes; per-function scopes in `~/.hermes/business/keymap.yaml` |
| **Approval** | A single `approval_queue.jsonl` polled by the operator via `/approve` in Telegram |

### 4.2 The deterministic / agentic split (the rule)

> **If the same inputs must always produce the same outputs, it is deterministic code.**
> **If the answer requires reading prose, choosing tone, or weighing tradeoffs, it is a skill.**

Concretely:
- Pulling MRR from Stripe → script.
- Deciding what to *say* about MRR in the brief → skill.
- Computing diff between yesterday's and today's pipeline → script.
- Choosing which 3 deals to flag for personal follow-up → skill.

Most jobs are a script that emits structured Markdown, piped into a skill that turns it into a paragraph or an action.

### 4.3 The daily brief
A single Markdown file written to `~/.hermes/business/briefs/YYYY-MM-DD.md` and delivered to your home channel at 08:30. Sections, in order:

1. **Money** — MRR/ARR delta, failed payments, runway months.
2. **Pipeline** — new leads, stalled, today's next actions.
3. **Product & Engineering** — overnight PRs, prod health, top bug.
4. **Customers** — open tickets, SLA risk, top theme.
5. **Marketing** — yesterday's metrics, today's queued posts.
6. **Ops** — backups, secret rotations, vendor flags.
7. **Approvals waiting** — count + first three in queue.
8. **Cost** — yesterday's LLM + infra spend vs ceiling.

### 4.4 Approval model
Three tiers, configured per skill in its frontmatter:

```yaml
metadata:
  business:
    autonomy: propose | act-reversible | act-destructive
```

- **propose** — agent drafts, queues, never sends. Default for finance, ops, sales-outbound.
- **act-reversible** — agent runs reads, drafts replies, posts internal notes. Default for product, eng-review, marketing-drafts.
- **act-destructive** — agent can send, charge, deploy. Only for explicitly trusted skills (e.g. nightly backup).

Any `act-destructive` action also writes to `audit.jsonl` and pings Telegram so the human sees it within seconds.

### 4.5 Observability
- Every cron run: structured log line in `~/.hermes/cron/output/<job_id>/<ts>.md`.
- Failures: tagged `[ALERT]` and forwarded to Telegram automatically.
- Costs: `solo_business/scripts/cost_rollup.py` reads Hermes' usage logs nightly.
- Weekly review: `weekly_review` skill summarizes what ran, what failed, what cost, what to change.

### 4.6 Security posture
- Hermes' built-in command-approval allowlist gates shell access.
- All secrets in env vars or Hermes' secret store — never in skill bodies.
- Webhook endpoints require HMAC signatures.
- The home directory (`~/.hermes/business/`) is `chmod 700`.
- Subagents that touch the internet run in isolated terminals (Docker/Daytona backends).

---

## 5. Implementation details

### 5.1 Repo layout (what gets added)

```
hermes_agent/                          # this repo
├── solo_business/                     # NEW — the business layer
│   ├── README.md                      # how to set up
│   ├── config/
│   │   ├── functions.yaml             # 7 functions × autonomy × delivery
│   │   ├── keymap.yaml                # which secrets each function may read
│   │   └── kpis.yaml                  # targets per function
│   ├── scripts/                       # deterministic core (no LLM)
│   │   ├── _common.py                 # http, retry, audit, env loader
│   │   ├── eng_pr_digest.py
│   │   ├── eng_prod_healthcheck.py
│   │   ├── product_feedback_rollup.py
│   │   ├── marketing_calendar_check.py
│   │   ├── sales_pipeline_diff.py
│   │   ├── ops_backup.py
│   │   ├── finance_mrr_snapshot.py
│   │   ├── cs_sla_watcher.py
│   │   ├── daily_brief_assemble.py    # stitches function sections together
│   │   └── cost_rollup.py
│   ├── cron/
│   │   └── jobs.yaml                  # declarative cron definitions, idempotently applied
│   ├── webhooks/
│   │   └── subscriptions.yaml         # declarative webhook subscriptions
│   └── install.sh                     # one-shot install: writes cron + webhooks
└── skills/business/                   # NEW — agentic skills
    ├── DESCRIPTION.md
    ├── daily-brief/SKILL.md
    ├── pr-reviewer/SKILL.md
    ├── feedback-clusterer/SKILL.md
    ├── content-drafter/SKILL.md
    ├── lead-responder/SKILL.md
    ├── incident-triage/SKILL.md
    ├── dunning-writer/SKILL.md
    ├── ticket-classifier/SKILL.md
    ├── weekly-review/SKILL.md
    └── approval-queue/SKILL.md
```

### 5.2 A cron job, end-to-end

`solo_business/cron/jobs.yaml` (declarative; `install.sh` calls `hermes cron create` for each):

```yaml
- name: finance-mrr-snapshot
  schedule: "0 6 * * *"
  script: solo_business/scripts/finance_mrr_snapshot.py
  skills: [daily-brief]
  prompt: |
    The script output above contains today's Stripe snapshot.
    Write the FINANCE section of the daily brief: 3 short bullets,
    flag anything that crossed a threshold in `config/kpis.yaml`,
    end with "[SILENT]" if nothing material changed.
  deliver: local
  autonomy: act-reversible
```

The script does the work. The skill does the writing. The cron entry is just glue.

### 5.3 A skill (sketch)

`skills/business/daily-brief/SKILL.md`:

```markdown
---
name: daily-brief
description: "Assemble the operator's morning brief from per-function snapshots."
prerequisites:
  files: ["~/.hermes/business/briefs/"]
metadata:
  business:
    autonomy: act-reversible
    function: cross-functional
---

# Daily brief

Inputs: structured Markdown sections produced by each function's script,
already concatenated into stdin under headings `# Money`, `# Pipeline`, ...

Rules:
1. Preserve numbers exactly. Never round or rephrase a metric.
2. Each section ≤ 6 lines. If nothing material happened, write "Quiet."
3. Add an "Approvals waiting" section pulled from approval_queue.jsonl.
4. End with a single "Next action" line — the one thing the operator
   should do first today.
5. Write the file to ~/.hermes/business/briefs/{YYYY-MM-DD}.md and print the path.
```

### 5.4 Webhooks

`solo_business/webhooks/subscriptions.yaml`:

```yaml
- name: stripe-payment-failed
  events: [invoice.payment_failed]
  source: stripe
  skills: [dunning-writer]
  prompt: |
    Payment failed for {customer.email}, invoice {invoice.id}, attempt {attempt_count}.
    Draft a dunning email at the configured tone for attempt N, queue it for approval.
  deliver: telegram
  autonomy: propose

- name: github-pr-opened
  events: [pull_request.opened, pull_request.synchronize]
  source: github
  skills: [pr-reviewer]
  prompt: |
    Review PR #{pull_request.number}: {pull_request.title}.
    Check correctness, tests, security, and the project's CONTRIBUTING.md.
    Leave inline comments. Approve only if all checks pass and tests cover the change.
  deliver: github_comment
  autonomy: act-reversible
```

### 5.5 Setup (operator's POV)

```bash
# 0. Hermes itself
./setup-hermes.sh

# 1. Configure providers + secrets once
hermes setup
cp .env.example .env && $EDITOR .env

# 2. Pick KPIs and autonomy levels
$EDITOR solo_business/config/functions.yaml
$EDITOR solo_business/config/kpis.yaml

# 3. Install the business layer (writes cron jobs + webhook subs)
bash solo_business/install.sh

# 4. Start the gateway so Telegram/Slack/email work
hermes gateway start

# 5. Smoke test
hermes cron run finance-mrr-snapshot     # one-shot
hermes cron list                          # confirm all jobs registered
```

### 5.6 Bring-up plan (concrete, phased)

Each phase ends with something useful even if you stop there.

| Phase | Deliverable | Time |
|---|---|---|
| **P0 — Skeleton** | `solo_business/` tree, config files, `_common.py`, `install.sh` idempotent. | 0.5 d |
| **P1 — Money first** | `finance_mrr_snapshot.py` + `daily-brief` skill. Daily brief lands in Telegram. | 1 d |
| **P2 — Eng + Ops** | `eng_pr_digest`, `eng_prod_healthcheck`, `ops_backup`. Reliability scaffolding. | 1 d |
| **P3 — Customers** | `cs_sla_watcher`, `ticket-classifier`, `feedback-clusterer`. | 1 d |
| **P4 — Growth** | `marketing_calendar_check`, `content-drafter`, `lead-responder`. | 1 d |
| **P5 — Review loop** | `weekly-review` skill, `cost_rollup.py`, approval queue UX. | 0.5 d |
| **P6 — Hardening** | Restore script, dry-run mode, integration tests for each script. | 1 d |

Total: ~6 working days for a full end-to-end stand-up.

### 5.7 Failure modes already designed for
- **LLM down / over budget** — scripts still run; brief is delivered with raw Markdown sections, no narration. Function is degraded, not lost.
- **Webhook source flaps** — HMAC + dedupe by event id; replays are idempotent.
- **Script crashes** — cron writes the traceback to the run log and pings Telegram; no silent failure.
- **Wrong agent decision** — `propose` is the default; the audit log lets you reconstruct what was attempted and why.
- **Lost VPS** — `solo_business/install.sh` is idempotent; restoring is `git clone` + `setup-hermes.sh` + `bash solo_business/install.sh` + `.env`.

---

## 6. What this is and isn't

**It is** a thin, opinionated layer on top of Hermes that gives a solo operator one inbox, one queue, and seven well-defined function pipelines — each with a deterministic core and an agentic shell.

**It isn't** a replacement for Hermes, a new framework, or a tool you have to learn. If you can edit YAML and write a Python script that hits an API, you can extend any function.

The whole system is `solo_business/` + `skills/business/`. Everything else is Hermes doing what Hermes already does.
