---
name: business-os-customer-service
description: "Solo-founder customer service: ticket triage, response drafting, churn-signal detection, NPS analysis, onboarding."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [INTERCOM_TOKEN, RESEND_API_KEY]
  commands: [curl]
metadata:
  hermes:
    tags: [Customer Service, Support, Churn, NPS, Onboarding, Retention, SaaS]
---

# Customer Service — Solo Founder Playbook

Best support team in B2B SaaS is the founder. Worst is "no one available". The agent's job is to keep response times under 1 hour during business hours and 12 hours always — without you being chained to the inbox.

## Cadences

| Cadence  | Activity                                  | Tier   |
|----------|-------------------------------------------|--------|
| Every 15min | New ticket triage                      | AUTO   |
| Per ticket | Response draft                          | DRAFT  |
| Daily    | Onboarding nudges (trial users)            | AUTO   |
| Daily    | Health-score recompute                     | AUTO   |
| Weekly   | At-risk customer review                    | DRAFT  |
| Monthly  | NPS survey send + analyze                  | DRAFT  |
| Per close | Win-back / churn-save playbook            | DRAFT  |

## Triage (AUTO)

When a ticket arrives (Intercom webhook):

1. **Classify** with one of: `bug`, `feature-request`, `confusion`, `billing`, `integration`, `outage`, `feedback`, `spam`.
2. **Severity**: `P0` (customer blocked), `P1` (customer impaired), `P2` (annoyance), `P3` (question).
3. **Customer context**: pull plan, MRR, signup date, health score from CRM.
4. **Route**:
   - `outage` + `P0` → engineering skill IMMEDIATELY + page founder.
   - `bug` → file Linear issue, draft acknowledgement to customer.
   - `feature-request` → log to feedback file (product skill picks up), draft acknowledgement.
   - `confusion` → DRAFT answer using docs + past tickets, founder reviews.
   - `billing` → draft answer, founder reviews (always — billing is high-stakes).
   - `feedback` → log to feedback file, draft thank-you.
   - `spam` → AUTO close with tag.

5. **Response SLA**:
   - P0: 15 minutes (page founder).
   - P1: 1 hour (DRAFT ready in 5 min, founder reviews).
   - P2/P3: 12 hours.

## Response Drafting (DRAFT)

Every customer-facing response is DRAFT. Even for "common" questions, founder eyeballs before send. The agent:

1. Reads the ticket + customer history + relevant docs.
2. Drafts a response that:
   - Acknowledges the specific issue (not "thanks for reaching out").
   - Answers in the first sentence if possible.
   - Includes a code snippet, screenshot, or doc link if relevant.
   - Asks at most one follow-up question.
   - Closes with a specific next step ("I'll update you by EOD" not "let me know").
3. Founder approves; agent sends via Intercom.

Founder can configure auto-send for specific tags (e.g., "password reset") once trust is built.

## Onboarding Nudges (AUTO)

Trial users get a touch schedule:

| Day | Trigger condition                                              | Action                                          |
|-----|----------------------------------------------------------------|-------------------------------------------------|
| 0   | Signup                                                          | Welcome email + setup checklist                 |
| 1   | No event ingested yet                                           | "Stuck? Here's the integration in 3 steps"      |
| 3   | <100 events ingested                                            | Founder personal note: "saw your signup, here to help"|
| 5   | First NL query run                                              | "Here's one more cool query to try"             |
| 7   | <500 events OR no query in 24h                                  | "Want a 15-min call?" → demo booking link        |
| 10  | Has 1000+ events AND queries → product-qualified                | DRAFT upgrade-to-paid email for founder review  |
| 14  | Trial ending: paid or not                                       | Conversion or "exit interview" path             |

Agent watches these conditions hourly. Founder sees daily summary of who hit which milestone.

## Health Score (AUTO, daily recompute)

Per paid customer, score 0–100:
- **Usage** (40 pts): weekly active users, queries run, dashboards viewed.
- **Engagement** (20 pts): newsletter opens, in-app NPS answers, support tickets.
- **Sentiment** (20 pts): NPS score, support ticket sentiment.
- **Growth** (20 pts): event volume growth, seat growth, query volume growth.

Color bands:
- Green: 70+, healthy, expansion candidate.
- Yellow: 40–69, watch list.
- Red: <40, churn risk, intervention needed.

State stored in `~/.hermes/business-os/health/`. Trends matter more than absolute score; agent flags any account dropping >10 points in 7 days.

## At-Risk Review (DRAFT, weekly Fri 14:00)

For every red or rapidly-dropping account:
1. Summarize signals (drop in usage, recent tickets, missed renewal, exec departure visible on LinkedIn).
2. Identify last positive interaction.
3. Propose intervention:
   - Founder phone call (best, expensive).
   - Personal email from founder (good, fast).
   - Free month or service credit (last resort).
4. If intervention >$1k value → HUMAN tier, founder decides.

## NPS (monthly)

Send to one cohort per month so customers don't get bombarded. Cohort = customers in the same signup month, 90+ days in.

After collection (agent waits 7 days):
- Score breakdown.
- Top 3 verbatim themes from detractors.
- Top 3 verbatim themes from promoters.
- Follow-up: 1:1 emails to every detractor (DRAFT for founder).

## Churn Save

Triggered when a customer requests cancellation:

1. AUTO pause the cancellation (Stripe API — pause-collection-at-period-end, NOT immediate cancel).
2. DRAFT a save play:
   - "We saw your cancel — what could we have done better?"
   - Offer: 30-day extension OR pause-and-keep-data OR free strategy call.
3. If customer responds: founder takes over.
4. If no response after 5 days: process cancellation, send exit survey, AUTO log churn reason.

## Onboarding Templates

`templates/customer-onboarding.md` holds the canonical sequence. New customer = pull the template, customize (company name, integration type, named champion), schedule.

## Anti-patterns

- Templated empathy ("I totally understand how frustrating this is"). Customers see through it.
- Auto-sending answers to billing questions. One bad auto-send = one churned customer.
- Letting health scores go stale. Stale data → wrong interventions.
- Treating NPS as a vanity metric. The verbatims are the data; the score is just a sorting key.
