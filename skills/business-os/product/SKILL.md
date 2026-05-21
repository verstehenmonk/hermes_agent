---
name: business-os-product
description: "Solo-founder product: PRDs, customer-feedback synthesis, roadmap, A/B test reads, feature scoping."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [POSTHOG_API_KEY, NOTION_API_KEY]
  commands: [curl, python3]
metadata:
  hermes:
    tags: [Product, PRD, Roadmap, Customer Feedback, A/B Testing, SaaS]
---

# Product — Solo Founder Playbook

You are the only PM. Your job is to keep the engineering effort pointed at things customers will pay for. The agent does the mechanical heavy lifting: synthesizing feedback, drafting PRDs, reading A/B test results, summarizing competitor moves.

## Cadences

| Cadence  | Activity                                | Tier   |
|----------|-----------------------------------------|--------|
| Daily    | Feedback ingestion from support/sales   | AUTO   |
| Weekly   | Feedback synthesis → themes             | DRAFT  |
| Weekly   | Roadmap update + commitments check      | DRAFT  |
| Per spec | PRD draft for upcoming work             | DRAFT  |
| Per test | A/B test read + decision memo           | DRAFT  |
| Monthly  | Competitor roundup                      | DRAFT  |
| Quarterly| Strategy refresh (with founder)         | HUMAN  |

## Feedback Loop (the most important loop)

Every customer signal lands in `~/.hermes/business-os/feedback/` as a flat file. Sources:
- Support tickets (Intercom/Helpscout webhook).
- Sales call notes (from `business-os-sales`).
- NPS responses.
- Direct founder notes (`/feedback <text>` slash command).
- Churn exit reasons.

**Daily ingestion (AUTO)**: agent normalizes each new signal into a single-line entry with `[date] [source] [customer_id] [verbatim] [tag]`. Tags drawn from a controlled vocabulary in `state/feedback_tags.yaml` (created on first run).

**Weekly synthesis (DRAFT)**: agent reads the last 7 days of entries and produces:
- Top 5 themes by frequency, weighted by revenue (a $36k ACV customer counts more than a free trial).
- One direct verbatim per theme (no paraphrase).
- Proposed next action per theme: SHIP (build it), STUDY (more research), HOLD (acknowledge, not now), KILL (won't do, document why).

Deliver to the founder Mon 09:00. Founder approves; SHIP items become Linear issues with feedback links.

## PRDs

Use `templates/prd.md`. The agent fills in everything; founder reviews and signs off.

**PRD trigger**: any feature estimated at >3 days of build time. Below that, a 1-paragraph issue description is enough.

**Bar for a good PRD** (the agent self-checks against this):
1. Problem statement quotes a real customer (with name + revenue).
2. Success metric is numeric and tied to a KPI in `state/kpis.yaml`.
3. The "what we're NOT doing" section exists and is non-trivial.
4. Risks section lists at least one way this could fail.
5. Has a "kill criteria" — what we'd see in the first 4 weeks that would tell us to roll back.

## Roadmap

Single source of truth: a Notion page (or a markdown file at `~/.hermes/business-os/roadmap.md`). The agent maintains it.

Structure:
- **Now (this sprint)**: ≤3 items.
- **Next (next 1–2 sprints)**: ≤5 items.
- **Later (quarter)**: ≤10 themes (not features).
- **Maybe (parked)**: unbounded, but each has a kill date.

Weekly update: agent checks every "Now" item against actual Linear progress. Anything not moving for 7 days gets flagged with a 1-sentence diagnosis.

## A/B Test Reads

When a test runs (PostHog/GrowthBook), agent fetches results 7 days after launch and produces a decision memo using this structure:

```
TEST: <name>
HYPOTHESIS: <original>
RESULT: variant <X> beat control by <Y>% on <metric>, p=<Z>.
SECONDARY METRICS: <list, flag any regressions>
SAMPLE SIZE: <N>, power achieved?
DECISION: SHIP / KILL / ITERATE / RUN LONGER
REASONING: <2-3 sentences>
LEARNING: <what we now know that we didn't before>
```

Auto-kill any variant with p>0.2 after 14 days unless founder objects.

## Competitor Roundup (monthly)

Pre-processor pulls:
- Competitor changelog pages (defined in `state/competitors.yaml`).
- Their pricing pages (diff against last month).
- New funding announcements (Crunchbase / press releases).
- Their hiring pages (signal of where they're investing).

Agent produces a 1-page roundup with the question "does this change anything we should do?"

## Customer Discovery

Founder runs customer interviews. Agent doesn't replace this. But it CAN:
- Schedule them (calendar tool).
- Pre-research the company (revenue, headcount, tech stack from BuiltWith).
- Draft the interview guide based on `state/icp.yaml` and current open questions.
- After the call (founder uploads recording), transcribe + extract: jobs-to-be-done, current solution, willingness to pay, decision criteria.
- File the synthesis to `~/.hermes/business-os/interviews/<company>-<date>.md`.

Target cadence: **3 customer interviews per week**. If founder slips, the orchestrator's morning brief surfaces it.

## Anti-patterns

- PRDs without a kill criterion. (You'll never stop building.)
- Roadmaps with no "Maybe" → "Later" promotion bar. (Wishlist creep.)
- A/B tests with no pre-registered metric. (You'll p-hack.)
- Treating support tickets as bugs instead of feature signals. (Misses pivots.)
