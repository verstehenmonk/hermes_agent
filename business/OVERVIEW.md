# Solo Business Operating System — Program Overview

A management system for a one-person AI SaaS B2B company, built on top of
[Hermes Agent](../README.md). It gives a solo founder the leverage of an
executive team — engineering, product, marketing, sales, customer success,
finance, operations, legal — without hiring one. Each department is a Hermes
skill the agent loads on demand. Routine work (daily brief, inbox sweep,
weekly review, monthly close, OKR review, alerts) runs deterministically on
cron and webhooks.

The founder stays in the loop via **Telegram** (interactive + alerts) and
**Email** (long-form digests).

---

## 1. Program overview

### What it is

Two layers, intentionally separated:

| Layer | Path | What it contains | Who edits it |
|---|---|---|---|
| **Operating** | `business/` | Charter, north-star, department briefs, rituals, deterministic Python scripts, cron + webhook config | The founder |
| **Agent** | `skills/business/` | One skill per department (engineering, product, marketing, sales, customer-success, finance, operations, legal) + `ceo` orchestrator | Mostly stable; tuned by the founder |

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

### Core idea: deterministic for numbers, agentic for judgment

- Scripts compute. The agent decides.
- Don't ask the agent to compute MRR — let `metrics_snapshot.py` pull it
  from Stripe and hand the agent a clean JSON to reason over.
- Don't write a regex to qualify a sales lead — let the agent read the email
  and decide.

### The departments

| Skill | Owns | Path |
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

Invoke directly (`/ceo`, `/engineering`, `/sales`, …) or let cron do it.

---

## 2. Success criteria

### What "working" means

The system is succeeding when:

1. **The founder spends ≤ 10 hours/week on company operations** outside
   product work. The agent absorbs the rest.
2. **No surprise has gone more than 24 hours undetected** — failed payments,
   error spikes, churn signals, no-show demos, runway warnings all surface
   in the daily brief or via webhook alert.
3. **Every non-trivial decision is in the journal.** The CEO skill can read
   the last 30 days of decisions before any weekly or monthly review.
4. **Every cadence produces a written artifact** archived under
   `~/.hermes/business/journal/`. Daily standups, weekly reviews, monthly
   closes, quarterly OKRs — all auditable later.
5. **The agent never silently fails.** A missing Stripe key shows up as
   "Stripe not connected" in the daily brief, not as silent zeros.
6. **The charter is current.** When `business/CHARTER.md` changes,
   every skill's behavior changes — because each skill re-reads it on
   every invocation.

### Quantitative targets

These are the numbers the program is built to drive. Defaults live in
`business/north-star.md`; the founder edits the targets.

| Tier | Metric | Cadence |
|---|---|---|
| **Headline** | Weekly Active Workspaces (WAW) | Weekly |
| **Tier 1 (health)** | MRR, net new MRR, logo churn (30d), NRR, activation rate, p95 latency, error rate | Weekly |
| **Tier 2 (pipeline)** | New qualified leads (7d), demos booked, demo→won conv., open opps, avg sales cycle | Weekly |
| **Tier 3 (marketing)** | Unique visitors (7d), top entry pages, trial signups → activated, content shipped, newsletter open rate | Weekly |
| **Tier 4 (engineering)** | PRs merged, mean PR open→merge time, open P0/P1, Sentry events/1k req, deploy frequency, MTTR | Weekly |
| **Tier 5 (finance)** | Cash on hand, burn (3-mo trailing), runway, gross margin, CAC, payback period, LTV/CAC | Monthly |

### Alert thresholds (failure detected automatically)

Encoded in `webhooks.yaml` and `cron.yaml` health-check jobs:

- Burn jumps > 25% MoM → finance skill drafts an investigation
- MRR drops day-over-day → finance skill checks failed payments / churn
- Error rate > 1% for 15 min → engineering skill pages
- No new signups for 48h during work hours → product skill investigates funnel
- Demo no-show rate > 30% in a week → sales skill investigates booking flow
- Cash runway drops below 6 months → CEO skill drafts an action plan
- Any P1 customer issue open > 4h during work hours → CS skill pages

---

## 3. Use cases

### A. Morning brief (every weekday 07:30)

> Cron → `scripts/metrics_snapshot.py` → `ceo` skill → Telegram

The founder wakes up to a one-screen Telegram message:

- Yesterday's headline numbers vs. trend
- The top 3 things to do today (from open issues, calendar, decisions
  pending review)
- Inbox triage summary (counts by category + items the agent thinks need
  the founder personally)
- Anything that crossed an alert threshold

### B. Inbox sweep (hourly during work hours)

> Cron → `scripts/inbox_digest.py` → `customer-success` + `sales` skills → Telegram

- Gmail pulled and categorized (support, sales, vendor, personal, noise)
- CS skill drafts replies to support tickets (founder approves with one tap)
- Sales skill scores inbound leads against the ICP in `CHARTER.md` and
  schedules a demo via Cal.com if qualified
- Anything ambiguous is surfaced, not auto-actioned

### C. Weekly review (Friday 16:00)

> Cron → all department skills → Email digest

Each department posts:

- What shipped this week
- What slipped and why
- Numbers vs. last week
- The one thing they recommend for next week

The CEO skill stitches the eight inputs into a single 1–2 page email
with the founder's three bets for the following week.

### D. Monthly close (1st of month 09:00)

> Cron → `finance` + `product` skills → Email

Finance reconciles Stripe + Mercury, computes MRR, churn, burn, runway,
NRR. Product computes cohort retention and the activation funnel. The
agent writes the narrative ("MRR grew 14% MoM but new logo growth slowed;
the dip in week 2 was a payment processor outage, not real churn") and
emails it.

### E. Real-time alerts (webhooks)

> Stripe / Sentry / Linear / GitHub → relevant department skill → Telegram

- Stripe failed payment → finance skill drafts a dunning email
- Sentry error spike → engineering skill opens a Linear issue and posts a
  triage summary
- PR blocked > 24h → engineering skill nudges or escalates
- Customer downgrade event → CS skill drafts a save call invite

### F. Ad-hoc invocations (any time)

The founder types:

- `/sales review the pipeline and tell me who I should personally call`
- `/finance what would happen to runway if I hired one engineer at $180k?`
- `/legal draft a DPA we can send to the Acme procurement team`
- `/ceo I'm thinking of pivoting to vertical X — argue both sides`

The agent loads the charter, the relevant brief, and the skill, and
answers.

### G. Quarterly OKR review

> Cron → `ceo` skill → Email

Scores the last quarter's three bets (from `CHARTER.md` → "three bets
this quarter"), proposes the next quarter's three, surfaces the
trade-offs explicitly. The founder edits and commits.

---

## 4. Technical & implementation details

### 4.1 Repository layout

```
business/
├── CHARTER.md              # The constitution. Every skill reads this first.
├── north-star.md           # Metrics & alert thresholds.
├── cadences.md             # When each ritual runs and why.
├── README.md               # User-facing intro.
├── OVERVIEW.md             # This file.
├── install.sh              # Idempotent installer (cron + webhooks).
├── cron.yaml               # Scheduled jobs declaration.
├── webhooks.yaml           # Event-triggered jobs declaration.
├── departments/            # One brief per department (scope, KPIs, weekly questions).
│   ├── ceo.md
│   ├── engineering.md
│   ├── product.md
│   ├── marketing.md
│   ├── sales.md
│   ├── customer-success.md
│   ├── finance.md
│   ├── operations.md
│   └── legal.md
├── rituals/                # Playbooks for each cadence.
│   ├── daily-standup.md
│   ├── weekly-review.md
│   ├── monthly-close.md
│   └── quarterly-okrs.md
└── scripts/                # Deterministic data-gathering. Python 3.11+.
    ├── metrics_snapshot.py # Pulls numbers from Stripe/PostHog/Linear/GitHub.
    ├── inbox_digest.py     # Pulls + categorizes Gmail.
    └── journal.py          # Appends decisions/reviews to the journal.

skills/business/
├── SKILL.md                # Router skill.
├── ceo/SKILL.md            # Orchestrator.
├── engineering/SKILL.md
├── product/SKILL.md
├── marketing/SKILL.md
├── sales/SKILL.md
├── customer-success/SKILL.md
├── finance/SKILL.md
├── operations/SKILL.md
└── legal/SKILL.md
```

### 4.2 Runtime state

Lives under `$HERMES_HOME` (default `~/.hermes/business/`):

```
~/.hermes/business/
├── metrics/
│   ├── latest.json         # Most recent snapshot (read by every skill).
│   └── 2026-05.json        # Month-end archive for finance.
├── inbox/
│   └── latest.json         # Categorized Gmail snapshot.
└── journal/
    ├── decisions.md        # Appended by `journal.py decision`.
    ├── standups/2026-05-24.md
    ├── reviews/2026-W21.md
    └── closes/2026-04.md
```

### 4.3 Determinism boundary

| Domain | Tool | Why deterministic |
|---|---|---|
| Numbers (MRR, WAW, churn, latency, error rate) | `metrics_snapshot.py` | Same input → same output; auditable; cheap to run hourly |
| Email categorization counts | `inbox_digest.py` | Counts and categories are deterministic; the *replies* are agentic |
| Journal append | `journal.py` | File I/O with `fcntl` locking; no ambiguity |

| Domain | Tool | Why agentic |
|---|---|---|
| Drafting replies, dunning, save emails | Department skills | Tone, context, judgement |
| Qualifying leads, prioritizing issues | Department skills | Pattern recognition over fuzzy data |
| Weekly narrative, monthly story | `ceo` skill | Synthesis across departments |

### 4.4 The scripts

#### `scripts/metrics_snapshot.py`
- Pulls Stripe (MRR, churn, NRR), PostHog (WAW, activation, latency),
  Sentry (errors), GitHub (PRs, deploys), Linear (open issues), Mercury
  (cash, burn).
- Writes a single JSON to `~/.hermes/business/metrics/latest.json`.
- On the 1st of the month, also writes `~/.hermes/business/metrics/<YYYY-MM>.json`.
- Each integration is independent: if `STRIPE_API_KEY` is unset, the
  Stripe block is `{ "connected": false }` rather than failing the run.
- `--verify` flag does a dry-run that checks credentials and shape.

#### `scripts/inbox_digest.py`
- OAuth Gmail pull (newest N unread).
- Heuristic categorization: support / sales / vendor / personal / noise.
- Writes `~/.hermes/business/inbox/latest.json` with subject, from, snippet,
  and category for each item — never the full body in the snapshot.
- Body is fetched lazily by the agent when it needs to draft a reply.

#### `scripts/journal.py`
- `journal decision --title "..." --review-in 7` opens an editor, captures
  what was decided, what was decided against, expected outcome, and review
  date; appends to `decisions.md`.
- `journal standup` / `journal review` / `journal close` write the matching
  ritual artifact.
- Uses `fcntl.flock` so concurrent cron and human edits never corrupt the file.
- Explicit UTF-8 encoding (`Path.open(..., encoding="utf-8")`).

### 4.5 How a skill behaves

Every business skill follows the same shape:

1. **Read** `business/CHARTER.md` (identity, ICP, principles, constraints, stack).
2. **Read** `business/north-star.md` (what we measure).
3. **Read** the matching brief in `business/departments/<name>.md`.
4. **Read** `~/.hermes/business/metrics/latest.json` for numbers — never recompute.
5. **Do the work** for the cadence or query.
6. **Write** the artifact to `~/.hermes/business/journal/...` via `journal.py`.
7. **Reply** to the founder (Telegram = one screen; Email = long form).

Skills degrade gracefully: a missing key in `~/.hermes/.env` makes the
relevant metric show "not connected" rather than crashing the run.

### 4.6 Cron and webhook configuration

`business/cron.yaml` and `business/webhooks.yaml` declare jobs in a format
the Hermes cron + webhook subsystems consume. `install.sh` is idempotent:
running it again reconciles the registered jobs with the YAML and prints
a diff.

Schedule from `cadences.md`:

| When | What | Trigger |
|---|---|---|
| Mon–Fri 07:30 | Daily brief | cron |
| Hourly during work hours | Inbox sweep | cron |
| Fri 16:00 | Weekly review | cron |
| 1st of month 09:00 | Monthly close | cron |
| Quarterly | OKR review | cron |
| Real-time | Stripe / Sentry / Linear / GitHub / Plain alerts | webhook |

### 4.7 Recommended stack (picked for solo AI-SaaS B2B)

Chosen for: low ops burden, generous solo-tier pricing, agent-accessible APIs.

- **Engineering** — GitHub + Linear + Sentry + Vercel/Fly
- **Product** — PostHog (analytics + flags + replays, one tool)
- **Marketing** — Astro site + Resend + Plausible/PostHog + Typefully
- **Sales** — Attio + Cal.com + Apollo
- **Customer success** — Plain + Loops
- **Finance** — Stripe + Mercury + Beancount or QBO
- **Operations** — Notion + 1Password + Google Workspace
- **Legal** — Stripe Atlas docs + Vanta + Iubenda
- **Comms** — Telegram (founder) + Slack (customers) + Email (long form)

None of these are required on day one. Skills check `~/.hermes/.env` for
the matching key and degrade gracefully when one is missing.

### 4.8 Install

```bash
# 1. Edit the constitution.
$EDITOR business/CHARTER.md

# 2. Add API keys for the platforms actually in use.
$EDITOR ~/.hermes/.env

# 3. Install cron + webhooks (idempotent).
business/install.sh

# 4. Verify.
hermes cron list
hermes webhook list

# 5. Smoke test.
hermes -p "/ceo morning brief"
```

### 4.9 Design principles (the agent's defaults)

1. **The charter is the constitution.** Every skill reads `CHARTER.md` first.
   Change the business → edit one file.
2. **Deterministic for numbers, agentic for judgment.**
3. **One department, one skill, one brief.** Briefs are short and human-edited.
4. **The CEO skill is the only orchestrator.** Departments report up, never
   call each other directly.
5. **Every ritual produces a written artifact.** All journaled.
6. **Fail loud, never silently.** Missing integrations are visible in the brief.

### 4.10 Threat model & safety

- `~/.hermes/.env` holds all third-party credentials. Skills read it only
  through the scripts; the agent never echoes it to chat, email, or the
  journal. The router skill explicitly lists it as "may not touch."
- Spending authority is bounded in `CHARTER.md` ("issue refunds up to $X
  without asking"). Anything over the threshold is drafted and surfaced —
  never auto-executed.
- The agent cannot edit `CHARTER.md`. It can propose a diff; the founder
  applies it.
- Decisions are append-only in `decisions.md`. The agent never rewrites
  history.

### 4.11 Compatibility

- Python ≥ 3.11.
- POSIX file locking (`fcntl`) — Linux + macOS. Windows users run scripts
  inside WSL.
- Depends on Hermes Agent's existing `skills/`, `cron`, and `webhook`
  subsystems; no new infrastructure is introduced.
