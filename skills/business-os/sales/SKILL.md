---
name: business-os-sales
description: "Solo-founder sales: lead enrichment, outbound sequences, demo prep, proposals, CRM hygiene, win/loss analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [HUBSPOT_API_KEY, APOLLO_API_KEY, RESEND_API_KEY]
  commands: [curl]
metadata:
  hermes:
    tags: [Sales, Outbound, CRM, Pipeline, Demos, Proposals, B2B SaaS]
---

# Sales — Solo Founder Playbook

You are AE, SDR, and SE. The agent handles enrichment, sequence drafts, demo prep, follow-ups, CRM hygiene, and proposal generation. You handle the calls, the negotiation, and the close.

## Cadences

| Cadence  | Activity                                | Tier   |
|----------|-----------------------------------------|--------|
| Daily    | CRM hygiene (stage stalls, missing data)| AUTO   |
| Daily    | Inbound triage + qualification          | DRAFT  |
| Daily    | Outbound: 10 enriched touches           | DRAFT  |
| Per demo | Pre-demo brief + post-demo follow-up    | DRAFT  |
| Weekly   | Pipeline review + forecast              | DRAFT  |
| Monthly  | Win/loss analysis                       | DRAFT  |

## Pipeline Stages

Defined in HubSpot (or Notion CRM). Match `state/sales_stages.yaml`.

| Stage          | Definition                                              | Conversion target |
|----------------|---------------------------------------------------------|-------------------|
| 1. Inbound     | Free trial or contact-form submission                    | 60% → Qualified  |
| 2. Qualified   | Matches ICP, has buying signal                           | 50% → Demo       |
| 3. Demo booked | Call on calendar                                         | 80% → Demo done  |
| 4. Demo done   | Showed product, identified champion                      | 50% → POC        |
| 5. POC         | Customer has connected real data, has eval criteria      | 60% → Proposal   |
| 6. Proposal    | Sent quote, contract, security questionnaire             | 70% → Closed-Won |
| 7. Closed-Won  | Signed, paid                                             | —                |

Anything stuck >14 days at any stage triggers a "stall" alert.

## Daily CRM Hygiene (AUTO)

Pre-processor pulls all open deals. Agent checks:
- Missing required fields (champion name, eval criteria, target close).
- Stage stalls (>14 days no activity).
- Next-step missing or in the past.
- Owner field empty.

Output: a checklist for the founder to fix in <5 minutes, or the agent fixes the deterministic ones (next-step rotation, owner assignment).

## Inbound Triage (DRAFT)

When an inbound lead lands (webhook from website form, trial signup):

1. **Enrich** via Apollo / Clearbit:
   - Company size, revenue, tech stack, recent funding.
   - Lead role + LinkedIn.
2. **Qualify against ICP** (`state/icp.yaml`):
   - Hard match? → route to "Qualified" stage, schedule a demo offer email.
   - Soft match? → nurture: add to drip sequence.
   - No match (too small, wrong industry, consumer)? → polite no, add to "not now" list with a 12-month recheck.
3. **First-touch email** (DRAFT): personalized to their company. Reference one specific thing about them (their pricing page, recent blog post, public hire). Never generic.

## Outbound

10 enriched touches per day. Quality > volume. Solo founder + agent doing outbound at $36k+ ACV.

**Daily build** (DRAFT, takes 30 minutes of founder review):
1. Agent picks 10 accounts from `~/.hermes/business-os/sales/target-accounts.csv` based on:
   - ICP match score.
   - Buying signal (new exec hire, funding, job posting for product analyst, churn spike at their company per public reviews).
2. Agent enriches and finds 2 contacts per account (Champion + Decision-maker).
3. Agent drafts a 4-touch sequence using `templates/outbound-sequence.md`:
   - **Touch 1**: 80-word email referencing a specific signal.
   - **Touch 2** (day +3): 60-word follow-up with a teardown link.
   - **Touch 3** (day +7): LinkedIn connect with note (no pitch).
   - **Touch 4** (day +14): break-up email ("closing the loop").
4. Founder reviews + sends. Agent tracks opens/replies; surfaces hot ones for personal follow-up.

## Demo Prep (DRAFT)

12 hours before each demo:
1. Pre-call brief delivered to founder phone:
   - Company snapshot, role of attendees, recent moves.
   - Why they signed up (trial activity log + form notes).
   - Three questions to ask.
   - Two product paths to demo based on their use case.
   - Red flags (budget unclear, no champion identified, etc.).

## Demo Follow-up (DRAFT)

Within 2 hours of demo end:
1. Founder dumps notes via `/demo-notes <company> <text>`.
2. Agent generates:
   - 1-sentence call summary for CRM.
   - Next-step email (3 paragraphs: thanks, what we covered, proposed next step).
   - Internal note: deal score (1–10), specific concerns, expected next 30 days.
3. Updates pipeline stage, schedules next-step reminder.

## Proposals

Trigger: deal reaches stage 6.

Agent generates from `templates/proposal.md` (you'll create per-deal terms). Includes:
- Customer logo + name.
- Plan recommendation based on usage projections from trial data.
- Pricing (from `state/pricing.yaml`) with annual discount if requested.
- Security blurb (link to SOC2 page or roadmap).
- Implementation timeline.
- Mutual close plan: 6 named milestones from signature to go-live.

## Weekly Pipeline Review

Mon 08:30 (after orchestrator's weekly review):
- Total pipeline $ by stage.
- Movement: stage transitions in the last 7 days.
- Forecast: weighted pipeline × historical conversion = expected close this quarter.
- Top 5 deals: status, next step, what would unblock.
- Stalled deals: who's stuck >14 days, recommended action.

## Win/Loss

Monthly. For each closed-won and closed-lost in the period:
- Read demo notes + CRM activity + final emails.
- Code reason: product fit, price, timing, competition, no champion.
- Look for patterns: are we losing the same way? winning the same way?
- Output: 1-page memo with one action per loss reason.

## Anti-patterns

- Sending agent-written emails without review. (One generic email burns a target account.)
- Outbound to non-ICP because the funnel is empty. (Better to keep the funnel empty than waste an account.)
- "Spray and pray" sequences. (10 personalized > 100 generic.)
- Discounting before the customer asks. (Anchor on annual, not discount.)
- Treating POC as a feature request. (POC is a sales motion, not a roadmap.)
