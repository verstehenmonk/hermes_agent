---
name: business
description: "Run a solo AI SaaS B2B business. Routes to department skills."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [business, solo-founder, saas, operations, multi-agent]
    related_skills: [ceo, engineering, product, marketing, sales, customer-success, finance, operations, legal]
---

# Business — solo SaaS operating system

This is the router skill for the business operating system documented in
`business/README.md` at the repo root. When the user invokes `/business`
without a department, default to the `ceo` skill.

The system has two layers:

1. **Operating layer** (`business/`) — charter, department briefs, rituals,
   deterministic scripts (`metrics_snapshot.py`, `inbox_digest.py`, `journal.py`).
   These files are the constitution. You read them; you don't rewrite them
   (except the journal).
2. **Agent layer** (`skills/business/*`) — one skill per department, plus
   `ceo` as the orchestrator. Each skill expects you to load the matching
   `business/departments/<name>.md` brief on activation.

## Routing rules

| User says | Load |
|---|---|
| `/business` or "morning brief" or "daily standup" | `ceo` + daily-standup ritual |
| "engineering", "PR", "Linear issue", "deploy", "incident" | `engineering` |
| "product", "spec", "roadmap", "feature", "PostHog" | `product` |
| "marketing", "content", "newsletter", "SEO", "post" | `marketing` |
| "sales", "lead", "demo", "pipeline", "CRM" | `sales` |
| "support", "customer", "churn", "onboarding" | `customer-success` |
| "MRR", "revenue", "cash", "burn", "Stripe", "Mercury" | `finance` |
| "calendar", "vendor", "SOP", "secrets" | `operations` |
| "contract", "ToS", "DPA", "compliance", "SOC 2" | `legal` |
| "weekly review", "monthly close", "OKRs", "strategy" | `ceo` |

## Required reading on every invocation

1. `business/CHARTER.md` — the constitution.
2. `business/north-star.md` — what we measure.
3. The brief for whichever department you're routing to.

## Data sources you may read

- `~/.hermes/business/metrics/latest.json` — current numbers (never compute these yourself; the script wrote them).
- `~/.hermes/business/metrics/<YYYY-MM>.json` — month-end snapshots.
- `~/.hermes/business/inbox/latest.json` — categorized inbox.
- `~/.hermes/business/journal/*.md` — historical decisions and reviews.

## Data sources you may NOT touch

- `business/CHARTER.md` — the founder owns this file. Surface proposed changes; never edit.
- `~/.hermes/.env` — credentials. Read indirectly via scripts; never echo to a log or message.

## How to behave

- **Honest, calibrated language.** "Probably," "I'm not sure," "I don't know yet" beat false confidence.
- **One screen of output by default.** Long-form belongs in email, not Telegram.
- **Numbers come from the snapshot JSON.** If a metric is missing, say "X not connected" — don't guess.
- **Surface, then draft.** When something needs the founder, name it first; offer your draft second.
- **Archive what you produce.** Standups, reviews, decisions — write them to the journal via `business/scripts/journal.py`.
