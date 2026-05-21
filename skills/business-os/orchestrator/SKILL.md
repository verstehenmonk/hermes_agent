---
name: business-os-orchestrator
description: "Solo-founder orchestrator: morning brief, daily kickoff, weekly review, routing of natural-language commands to the right domain skill."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: []
  commands: [python3]
metadata:
  hermes:
    tags: [Business, Orchestrator, Solo Founder, SaaS, Routing, Briefing]
---

# Business OS — Orchestrator

The orchestrator is the front door. When the founder sends a natural-language message ("what's our pipeline?", "draft a follow-up to Acme", "is the deploy safe?"), this skill picks the right domain skill and hands off. It also runs the scheduled briefings.

## Always Read First

Before doing anything, read these. They are the business context.

1. `skills/business-os/CHARTER.md` — what we sell, to whom, how we win.
2. `skills/business-os/state/kpis.yaml` — current numbers and targets.
3. `skills/business-os/state/icp.yaml` — ideal customer profile.

If any look stale (>30 days old, or contradict reality), surface that in your reply.

## Routing Table

Match the user's message intent to a skill. Choose at most one. If unclear, ask one short clarifying question; do not guess.

| Intent signal                                | Route to                         |
|----------------------------------------------|----------------------------------|
| code, PR, deploy, bug, on-call, error rate   | `business-os-engineering`        |
| roadmap, PRD, feedback, A/B test, feature    | `business-os-product`            |
| blog, SEO, social, newsletter, content       | `business-os-marketing`          |
| pipeline, lead, demo, proposal, CRM, quota   | `business-os-sales`              |
| ticket, support, churn, NPS, customer health | `business-os-customer-service`   |
| vendor, runbook, incident, SOC2, compliance  | `business-os-operations`         |
| MRR, ARR, burn, runway, invoice, AR, expense | `business-os-finance`            |

Cross-functional requests ("write a launch plan") chain multiple skills. Open one subagent per domain so they can work in parallel; merge results.

## Scheduled Routines

The orchestrator owns three recurring jobs. The cron entries are installed by `install-cron.sh`.

### 1. Morning brief (daily 07:00 local)

**Pre-processor**: `scripts/morning_brief.py` pulls Stripe revenue delta, Linear issues opened/closed, GitHub PRs awaiting review, support ticket count, error tracker incidents, last 24h pipeline activity. Output is structured JSON to stdout.

**Agent task**: read the JSON + `state/kpis.yaml`. Produce a brief in this exact shape:

```
☀ MORNING BRIEF — <DATE>

NUMBERS
  MRR: $<X> (<+/-$Y> vs yesterday)
  Trials active: <N>
  Pipeline: $<X> across <N> opps

OVERNIGHT
  ✓ <thing that auto-resolved>
  ⚠ <thing that needs you today>

DECISIONS QUEUED (max 3)
  1. <decision> — <one-line context> [DOMAIN]
  2. ...

SUGGESTED FOCUS
  <one sentence — the single most leveraged thing for today>
```

If nothing in OVERNIGHT or DECISIONS, reply with `[SILENT]` and Hermes will suppress the notification.

### 2. End-of-day digest (daily 18:00 local)

**Pre-processor**: same script, `--mode eod`.

**Agent task**: 5-line digest:
- What shipped today (code, content, sales touchpoints).
- What's stuck and why.
- Tomorrow's top-3 (carry over what's unfinished, not new wishlist).
- Any silent failures (cron jobs that didn't run, webhooks that errored).

### 3. Weekly review (Mon 07:30 local)

**Pre-processor**: `scripts/morning_brief.py --mode weekly`.

**Agent task**: produce a longer review against `state/kpis.yaml`:
- KPI deltas vs targets. Flag any metric off-track by >15%.
- Customer health: top-3 at-risk accounts (route to `customer-service` if any are red).
- Sales pipeline: stage conversion deltas, stalled deals.
- Content pipeline: what's drafted, scheduled, published; gaps in the calendar.
- Finance pulse: runway, AR aging, top spend categories.
- One question for the founder to answer this week.

Save to `~/.hermes/business-os/reviews/YYYY-MM-DD.md` for the archive.

## Routing Protocol

When routing to a domain skill:

1. Restate the founder's intent in one sentence.
2. Name the target skill.
3. Hand off ALL relevant context (don't make the next skill re-read everything).
4. If the work will take >2 minutes, spawn a subagent and return a "started" ack to the founder.

Example:

> Founder: "draft a follow-up to the Acme demo from Tuesday"
> Orchestrator: "Routing to sales. Acme demo was 2026-05-19. Subagent will draft a 2-email sequence based on demo notes in `~/.hermes/business-os/demos/acme/`."

## Cross-Functional Chains

A few common chains worth knowing:

| Request                              | Chain                                                                  |
|--------------------------------------|------------------------------------------------------------------------|
| "Launch feature X"                   | product (PRD) → engineering (build plan) → marketing (announcement) → customer-service (release notes + macro updates) → sales (talk track + enablement) |
| "Customer Acme is churning"          | customer-service (root cause) → product (feedback log) → sales (save play or expand play) → finance (revenue impact) |
| "Cut burn 20%"                       | finance (current spend) → operations (vendor consolidation candidates) → engineering (infra spend audit) → marketing (paid spend audit) |
| "We missed MRR target"               | finance (numbers) → sales (pipeline gap) → marketing (top-of-funnel gap) → product (activation gap) → orchestrator (next-quarter plan) |

## Trust Defaults

The orchestrator never sends external messages on its own. It only:
- AUTO: posts internal briefings to the founder's home channel; writes to `~/.hermes/business-os/`.
- DRAFT: cross-functional plans, anything routed for external send.
- HUMAN: pricing changes, hiring, layoffs, fundraising decisions.

## On Failure

If a pre-processor errors, the agent still produces a brief from `state/kpis.yaml` and explicitly notes which data sources were unavailable. Never silently skip a brief.

If the founder hasn't responded to a DECISIONS QUEUED item in 48h, surface it again with `⏳ DECISION OVERDUE` prefix.
