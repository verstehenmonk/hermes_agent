# Hermes Business OS — Program Overview

A single AI-run operating layer for a solo-founder B2B SaaS, built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent). Eight department
"heads" + a Chief of Staff, deterministic SOPs, scheduled cadences,
event-driven webhooks, and a knowledge base — all delivered as data + config
that sits next to Hermes core, never inside it.

---

## 1. Program Overview

### What it is

A self-contained bundle under `business/` that turns one founder's Hermes
install into a whole company. Each department is a **personality overlay**
on top of Hermes (Chief of Staff, Head of Engineering, Head of Product, Head
of Marketing, Head of Sales, Head of Ops, CFO, Head of Customer Success).
Each personality has:

- A scope statement and a set of owned KPIs
- A scoped toolset (the CFO can't push code; the Head of Engineering can't
  email customers)
- A Slack channel it posts to
- A library of SOPs (markdown playbooks) it follows
- A set of cron-scheduled cadences and webhook-triggered reactions

### What problem it solves

A solo founder cannot operate seven departments. The default failure mode
is: engineering eats everything; sales, marketing, finance, ops, CS get
sporadic attention; the founder context-switches all day. This bundle gives
each department a competent default behaviour — autonomous on the safe
stuff, draft-only on anything customer-facing — so the founder's attention
goes to decisions, not coordination.

### Design split: deterministic vs. agentic

| Deterministic | Agentic |
|---|---|
| SOPs as markdown the agent reads at runtime | Webhook handlers reacting to real-world events |
| Cron jobs at fixed cadences (daily/weekly/monthly) | Chief-of-Staff interactive sessions in Slack |
| Approval gates baked into every customer-facing prompt | LLM-reasoned routing and synthesis |
| Per-job model + toolset pinning for cost containment | Cross-departmental reasoning during weekly review |

### Why Hermes specifically

Hermes already ships every primitive the bundle needs:
cron scheduler (`cron/jobs.py`), webhook subscriptions
(`gateway/platforms/webhook.py`), skills system (`skills/`), multi-channel
gateway (Slack/Telegram/Discord/etc.), personality overlays in
`cli-config.yaml`, MCP client support, subagent delegation, persistent
memory + Honcho user modeling, and `[SILENT]` notification suppression. The
bundle adds zero new infrastructure — only data, prompts, and a thin
bootstrap.

---

## 2. Success Criteria

The bundle is "working" when **all** of the following hold for two
consecutive weeks:

### Operational

- [ ] All Phase-1 crons fire on schedule with zero manual intervention
- [ ] PR review webhook posts a verdict to `#eng` within 5 minutes of PR
      open, for every PR
- [ ] No customer-facing email/post/Stripe action is sent without an
      explicit `:approve:` reaction in Slack
- [ ] `hermes cron usage` shows < $X/month aggregate spend at the
      founder's chosen cap

### Founder experience

- [ ] Founder reads `#cos` weekly briefing in < 5 minutes and walks away
      with a clear top-3 decisions list
- [ ] Founder spends < 30 sec per drafted customer reply (approve/edit/
      discard)
- [ ] Founder receives zero unexpected alerts during deep-work blocks
      (`#alerts` is silent unless red, calendar prep DMs only fire when
      meetings exist)

### Quality

- [ ] PR review verdicts surface at least one real correctness/security
      concern per non-trivial PR (measured against founder's own review
      ground truth)
- [ ] Support reply DRAFTS are sent without edits ≥ 60% of the time
- [ ] Monthly close numbers match the founder's manual reconciliation to
      within 1% on revenue and within 5% on spend categories

### Guardrails

- [ ] Zero secrets committed to the repo (smoke test green every commit)
- [ ] No webhook handler runs past `max_turns: 15` more than once a week
- [ ] No cron job uses Opus when Sonnet would have sufficed (monthly cost
      audit)

---

## 3. Use Cases

Concrete moments where the bundle earns its keep.

### Engineering

- **PR opened** → `head-of-engineering` posts a review comment within
  minutes citing correctness, tests, security, and blast radius; cross-posts
  one-line verdict to `#eng`. CI red ⇒ verdict is `[BLOCKED]`, not a
  review.
- **Merge to main** → `pr-merged-deploy-watch` tails Vercel + Fly for 10
  minutes, posts "deploy green" or proposes rollback per
  `sops/engineering/deploy-rollback.md` (founder runs the rollback
  command).
- **Vercel deploy fails** → `vercel-deploy-fail` webhook identifies the
  PR, posts cause + retry-or-rollback recommendation to `#alerts`.
- **Fly alert fires** → opens a Linear incident, ACKs in `#alerts` in
  under 60 seconds, runs `sops/engineering/incident.md`.
- **Daily 9am** → standup of open PRs, merges, Linear deltas, deploy
  health, under 200 words in `#eng`.
- **Hourly** → silent deploy-health probe (Haiku-class model, only speaks
  when red).

### Product

- **GitHub issue opened** → classified into bug | feature | docs | wontfix
  by `head-of-product`; files Linear or Notion artifact, comments on the
  issue with a verdict.
- **Daily 6am** → KB sync pulls Notion "Company KB" → markdown under
  `knowledge-base/`. Every other agent reads from this mirror, never from
  Notion live.
- **New spec request** → produces a draft spec in Notion using
  `sops/product/spec-template.md`. Marked `in-review` until founder
  approves.
- **Pre-launch** → walks `sops/product/launch-checklist.md` and posts a
  go/no-go to `#cos`.

### Marketing

- **Monday 10am** → weekly content plan: 3 bullets in `#marketing`
  covering publishes-this-week, drafting focus, stuck items.
- **Spec moves to `shipped`** → drafts blog post, X thread, LinkedIn
  post, and customer email per `sops/marketing/launch-announce.md`. All
  four are DRAFTS — founder approves each individually with `:approve:`.
- **Quarterly** → SEO audit (`sops/marketing/seo-audit.md`) surfaces
  quick wins and deep rewrites; quick wins flow straight into the content
  pipeline.

### Sales

- **Inbound lead in Gmail** → enriched, ICP-scored, DRAFT reply per
  `sops/sales/inbound-lead.md` posted to `#sales`.
- **24h before a demo** → `calendar-meeting-soon` triggers a demo-prep
  brief in `#sales` (who, pain hypothesis, demo path, likely objections,
  next-step ask).
- **Demo-done T+1/T+3/T+7/T+14** → cadence-driven DRAFT follow-ups in
  `#sales`, each referencing the actual demo content.
- **Customer flagged churn risk** → `sops/sales/churn-save.md` produces
  root cause hypothesis + three save options + conversation script. Founder
  runs the save call personally.

### Ops

- **Monday 11am** → vendor audit: renewing in 30d, MoM cost spikes,
  unused vendors. Founder reacts `:renew:` / `:cancel:` / `:downgrade:`.
- **Monthly 1st** → security checklist walkthrough; reds become Linear
  issues.
- **New vendor** → `sops/ops/vendor-onboard.md` captures cost, renewal,
  data sensitivity, secret location.
- **Calendar protection** → ops flags meeting-load creep against the
  founder's deep-work blocks.

### Finance (CFO)

- **Daily 7am** → burn snapshot. Silent unless runway dropped, MRR
  declined > 2%, or a single spend item > $1k.
- **Monthly 1st 9am** → full close: MRR walk, ARR, churn, NRR, gross
  margin, runway. Appended to `knowledge-base/finance/close-history.md`.
- **Stripe charge fails** → identifies customer, checks health score,
  proposes silent-retry / dunning / personal outreach. MRR > $500 ⇒
  founder DM + DRAFT email.
- **Weekly Wednesday 10am** → invoice collection sweep with DRAFT
  reminders per past-due invoice.

### Customer Success

- **8:30am daily** → triage all overnight support email. Each ticket
  classified (bug | how-to | billing | feature-request | sentiment),
  sentiment scored, reply DRAFTED. Bugs filed in Linear, feature requests
  in Notion.
- **New paying customer (Stripe webhook)** → welcome DRAFT in `#cs` with
  ICP fit score and recommended onboarding path.
- **Linear bug labeled high-severity** → cross-reference open CS tickets,
  identify affected customers, draft proactive outreach DRAFTS.
- **Friday afternoon** → customer health check; green/yellow/red per
  customer; reds become save-plan tasks for Head of Sales.
- **NPS response arrives** → promoter gets a referral-ask DRAFT;
  detractor gets an empathy + 15-min call DRAFT; passive gets a
  what-would-you-fix DRAFT.

### Chief of Staff

- **Friday 4pm** → weekly review pulls KPI deltas from
  `knowledge-base/kpis.yaml`, scans Linear/GitHub/Notion for slipped
  items, runs the customer health check, posts WINS / BLOCKERS /
  DECISIONS NEEDED to `#cos`. Uses Opus.
- **Cross-department questions in `#cos`** ("can we afford to hire?",
  "should we ship Feature X this week?") get reasoned synthesis across
  finance, eng, product, sales context.
- **4×/day** → calendar-prep brief DMs the founder before each block of
  external meetings.

---

## 4. Technical Details

### Architecture

```
                            ┌─────────────────────────┐
                            │     Slack workspace      │
                            │  #cos #eng #product …    │
                            └──────────────┬───────────┘
                                           │ messages, reactions
                            ┌──────────────▼───────────┐
                            │   Hermes gateway          │
                            │ (gateway/run.py)          │
                            └──────┬─────────────┬──────┘
                                   │             │
                ┌──────────────────▼──┐  ┌───────▼─────────────┐
                │  cron/scheduler.py  │  │ gateway/platforms/   │
                │   (every 60 sec)    │  │     webhook.py        │
                └─────────┬───────────┘  └──────────┬───────────┘
                          │                          │
                          │ load job + personality   │ load route +
                          │ + skills + toolsets      │ personality
                          ▼                          ▼
                ┌────────────────────────────────────────────────┐
                │             AIAgent (run_agent.py)              │
                │  personality overlay → skills → SOPs → tools    │
                └────┬────────────────────────────────────┬───────┘
                     │ read                               │ act
            ┌────────▼────────┐               ┌──────────▼──────────┐
            │ knowledge-base/ │               │ GitHub / Linear /    │
            │  AGENTS.md      │               │ Notion / Stripe /    │
            │  kpis.yaml etc. │               │ Vercel / Fly / Gmail │
            └─────────────────┘               └──────────────────────┘
```

### Hermes primitives reused (zero modifications)

| Primitive | Where | Role |
|---|---|---|
| Cron scheduler | `cron/scheduler.py`, `cron/jobs.py` | Runs scheduled cadences; per-job `model`, `enabled_toolsets`, `skills`, `deliver` |
| Webhook platform | `gateway/platforms/webhook.py` | Routes external POSTs to agent runs; HMAC-auth; idempotency cache |
| Skills | `skills/<category>/<name>/SKILL.md` | Domain knowledge the agent loads on demand |
| Personalities | `cli.py` → `agent.personalities` map in config | Per-conversation system-prompt overlay (`/personality NAME`) |
| Gateway | `gateway/run.py` | Multi-channel messaging (Slack, Telegram, Discord, Email, …) |
| Context files | `AGENTS.md` workspace context | Always-read company KB |
| Subagents | `agent/subagent.py` | Parallel workstreams within a single task |
| MCP client | `agent/transports/` | Stripe / Vercel / Notion MCP servers if present |
| `[SILENT]` pattern | `gateway/delivery.py` | Suppresses noisy notifications |

### Stock skills wired into departments

| Department | Skills used |
|---|---|
| Engineering | `skills/github/*`, `skills/productivity/linear/` |
| Product | `skills/productivity/notion/`, `linear`, `github` |
| Marketing | `notion`, `skills/social-media/xurl`, `google-workspace` |
| Sales | `skills/productivity/google-workspace/`, `notion`, optional `airtable` |
| Ops | `notion`, `google-workspace` |
| Finance | `business/skills/stripe-billing/` (read-only), `kpi-rollup`, `google-workspace` |
| Customer Success | `skills/email/himalaya`, `notion`, `linear` |

### Custom skills (only what stock Hermes doesn't already cover)

| Skill | File | Purpose |
|---|---|---|
| `stripe-billing` | `business/skills/stripe-billing/SKILL.md` | Read-only Stripe via curl with restricted key (`rk_live_*`) |
| `vercel-deploys` | `business/skills/vercel-deploys/SKILL.md` | Deploy status, logs, rollback drafts (vercel CLI) |
| `flyio-status` | `business/skills/flyio-status/SKILL.md` | App status, releases, logs, rollback drafts (fly CLI) |
| `kpi-rollup` | `business/skills/kpi-rollup/SKILL.md` | Reads `kpis.yaml`, queries each source, produces the weekly KPI table |

### Cost containment

Every cron and webhook template pins `model` explicitly:

| Cadence | Model | Rationale |
|---|---|---|
| Hourly monitors | Haiku 4.5 / DeepSeek | Returns `[SILENT]` 99% of the time |
| Daily triage / standups | Sonnet 4.6 | Right size for routine reasoning |
| Weekly review / incidents | Opus 4.7 | Cross-department reasoning, high stakes |

Track via `hermes cron usage`. The smoke test refuses commits that
introduce secrets via a regex scan of `business/`.

### Approval gate

Every customer-facing SOP ends prompts with the canonical footer from
`sops/_shared/approval-gate.md`:

```
[DRAFT — react :approve: in #<channel> to send, :discard: to cancel]
```

The Slack bot listens for `:approve:` reactions before executing the
underlying send via the relevant skill (himalaya for email, xurl for X,
etc.). Bulk sends (> 100 recipients) require `:approve-bulk:`.

### Phase gating

`business/manifest.yaml` declares which phases are active. `bootstrap.sh`
reads this and installs only matching crons and webhooks. Toggle a phase
to `true`, re-run bootstrap — done. Phase 1 (engineering +
chief_of_staff) is on by default.

---

## 5. Implementation Details

### Directory layout (73 files, ~3000 lines)

```
business/
├── README.md                            # Founder quickstart
├── manifest.yaml                        # Phase + KPI + model config
├── bootstrap.sh                         # Idempotent installer
├── .env.example                         # Secret template (lives in ~/.hermes/secrets/)
├── .gitignore
├── personalities/                       # 8 department overlays
│   ├── chief-of-staff.md
│   ├── head-of-engineering.md
│   ├── head-of-product.md
│   ├── head-of-marketing.md
│   ├── head-of-sales.md
│   ├── head-of-ops.md
│   ├── cfo.md
│   └── head-of-customer-success.md
├── sops/                                # 19 deterministic playbooks
│   ├── _shared/approval-gate.md
│   ├── engineering/  (pr-review, incident, release, deploy-rollback)
│   ├── product/      (spec-template, launch-checklist, bug-triage)
│   ├── marketing/    (content-pipeline, launch-announce, seo-audit)
│   ├── sales/        (inbound-lead, demo-prep, follow-up-cadence, churn-save)
│   ├── ops/          (vendor-onboard, renewal-review, security-checklist)
│   ├── finance/      (monthly-close, burn-report, invoice-collection)
│   └── cs/           (ticket-triage, health-check, nps-followup)
├── cron-templates/                      # 11 scheduled cadences (JSON)
├── webhook-templates/                   # 11 event-driven handlers (JSON)
├── knowledge-base/                      # Symlinked into AGENTS.md
│   ├── company.md                       # Mission, ICP, positioning, pricing — fill in
│   ├── product-spec.md                  # Auto-synced from Notion daily
│   ├── runbook.md                       # On-call + escalation
│   ├── kpis.yaml                        # North-star + per-dept KPIs
│   └── stack.md                         # Tooling inventory
├── skills/                              # 4 custom skills not in stock Hermes
│   ├── stripe-billing/SKILL.md
│   ├── vercel-deploys/SKILL.md
│   ├── flyio-status/SKILL.md
│   └── kpi-rollup/SKILL.md
├── slack/channels.yaml                  # Channel → personality map
├── dashboards/founder-cockpit/          # ASCII KPI dashboard (plugin-style)
└── tests/
    ├── smoke.sh                         # 50+ validation checks
    └── fixtures/                        # GitHub PR, Stripe charge, support email, Vercel fail
```

### What `bootstrap.sh` does

1. **Reads `manifest.yaml`** to determine active phases.
2. **Installs personalities** into `~/.hermes/cli-config.yaml` under
   `agent.personalities.<name>` — these become switchable with
   `/personality NAME`.
3. **Merges cron templates** into `~/.hermes/cron/jobs.json` (only those
   whose `phase` is active in the manifest). Existing jobs with the same
   `name` are left alone unless `--force`.
4. **Merges webhook templates** into
   `~/.hermes/webhook_subscriptions.json` (the file the webhook platform
   loads from at runtime).
5. **Appends a knowledge-base include block** to the workspace `AGENTS.md`
   so every agent turn reads `business/knowledge-base/*` as ground truth.
6. **Symlinks custom skills** from `business/skills/*` into
   `~/.hermes/skills/*` so they're discoverable from any repo using this
   Hermes install.

The whole thing is **idempotent**: re-running won't duplicate anything.
`--dry-run` shows what would change without writing. `--force` overwrites
existing personality/cron entries (use during iteration).

### Install (start to finish)

```bash
# 1. Make sure Hermes itself is installed
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes setup                       # creates ~/.hermes/cli-config.yaml

# 2. Fill in the knowledge base
cp business/.env.example ~/.hermes/secrets/business.env
$EDITOR ~/.hermes/secrets/business.env       # API keys
$EDITOR business/knowledge-base/company.md   # ICP, pricing, positioning
$EDITOR business/knowledge-base/runbook.md   # production URLs, health endpoints

# 3. Install the bundle
./business/bootstrap.sh --dry-run            # preview
./business/bootstrap.sh                      # install Phase 1

# 4. Wire Slack
hermes gateway setup                         # walks through Slack tokens
# Create channels: #cos, #eng, #alerts (at minimum for Phase 1)
hermes gateway start                         # daemonize

# 5. Verify
hermes cron list                             # show installed jobs
hermes cron run-now daily-eng-standup        # manually fire the standup
./business/tests/smoke.sh                    # 50+ green checks
```

### Phased rollout (recommended)

Edit `business/manifest.yaml` to flip phases on, re-run `bootstrap.sh`.

| Phase | When | What turns on |
|---|---|---|
| 1 (default) | Day 1, ½ day setup | Chief of Staff, Head of Engineering — `pr-review` webhook, `daily-eng-standup`, `hourly-deploy-health`, `weekly-review`, `calendar-prep` |
| 2 | Day 2–3 | Customer Success — `support-email-in`, `daily-cs-triage`, `linear-bug-incoming`, `signup-kickoff` |
| 3 | Week 2 | Product + Marketing — `issue-triage`, `daily-kb-sync`, `weekly-content-plan` (drafts only — zero outbound autonomy) |
| 4 | Week 3 | Finance + CFO — Stripe webhooks, `daily-burn-snapshot`, `monthly-close` |
| 5 | Week 4 | Sales + Ops — `daily-sales-followups`, `weekly-vendor-audit`, full KPI rollup in weekly review |

### Verification (smoke test detail)

`./business/tests/smoke.sh` runs 10 sections:

1. Bootstrap dry-run exits clean
2. Every personality has YAML frontmatter
3. Every cron template is valid JSON with required fields
4. Every webhook template is valid JSON with required fields
5. Every cron/webhook references an existing personality
6. Every SOP referenced from a prompt actually exists at the cited path
7. All required knowledge-base files exist
8. Every custom skill has a valid `SKILL.md`
9. Every test fixture parses as JSON
10. No real-looking secrets committed (regex match for `sk_live_*`,
    `rk_live_*`, `xoxb-*`, `ghp_*` with sufficient entropy)

All 50+ checks pass on the current branch.

### Operational footprint

- **Compute**: a $5/mo VPS is enough — Hermes' agent runs are bounded by
  `max_turns` (15 for webhooks, 25 for crons, 40 for the weekly review).
- **LLM spend**: roughly $40–$120/month depending on PR volume and
  support volume, given the model-pinning strategy. Most of that is the
  weekly Opus run (~$2 each) and PR reviews on Sonnet.
- **Storage**: `~/.hermes/cron/output/` accumulates run histories — rotate
  or prune monthly.
- **Secrets**: all live in `~/.hermes/secrets/`, never in this repo. The
  smoke test enforces that.

### Risks & guardrails (recap)

- **Cost runaway** — model pinned per job; `[SILENT]` suppresses empty
  notifications; `hermes cron usage` for spend tracking.
- **Customer-facing misfires** — every customer-facing prompt ends with
  the approval gate; nothing sends without explicit `:approve:`.
- **Notion drift** — `daily-kb-sync` is canonical; AGENTS.md reads the
  synced markdown, never live Notion.
- **Blast radius** — `enabled_toolsets` scoped per job; webhook handlers
  capped at `max_turns: 15`; CFO is read-only on Stripe.
- **Secret leakage** — `business/.gitignore` covers all secret files;
  smoke test rejects committed secrets via regex.

---

## 6. What's next

- Fill in `knowledge-base/company.md` with your actual ICP, pricing, and
  voice. Every agent reads it.
- Set up the Slack channels listed in `slack/channels.yaml`.
- Run `bootstrap.sh` and let Phase 1 fire for a week before flipping
  Phase 2.
- Track the success-criteria checklist above. The bundle is data; the
  contracts are the SOPs and the criteria. Both are editable in this
  repo.

Repo: https://github.com/verstehenmonk/hermes_agent  
PR: https://github.com/verstehenmonk/hermes_agent/pull/4
