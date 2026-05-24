# Customer Success Department Brief

## Scope

Make new customers successful in their first 30 days. Keep existing customers
shipped-on, billed-correctly, and heard. Catch churn signals early enough to do something.

## What "good" looks like

- First reply on any customer issue within one business hour during work hours.
- Onboarding: 80% of new paid signups complete the "first value" event within 7 days.
- Logo churn stays under 2%/month for SMB, under 1%/month for Business+.
- Every churned customer gets an exit interview email; we know the reason.
- Expansion (seats added, plan upgrades) is tracked as a leading indicator, not just a financial one.

## Tools we use

- **Plain** (`PLAIN_API_KEY`) — support inbox, threads, attributes per customer.
- **Loops** (`LOOPS_API_KEY`) — lifecycle email (welcome, day 3, day 7, day 30, dormant).
- **PostHog** (`POSTHOG_API_KEY`) — usage drop detection per workspace.
- **Cal.com** (`CAL_API_KEY`) — onboarding calls.
- **Linear** (`LINEAR_API_KEY`) — when a ticket needs engineering.

## Triage rubric (the agent runs this on every incoming message)

| Type | Severity | Action |
|---|---|---|
| Service down, error, can't pay | P1 | Page founder on Telegram immediately. Draft acknowledgement. Open Linear with `customer-blocker` label. |
| Bug, broken flow, wrong data | P2 | Draft acknowledgement within 1h. Reproduce. File Linear issue with link. |
| How-do-I question | P3 | Draft answer with doc link. If doc doesn't exist, flag for product/marketing. |
| Feature request | P3 | Tag in Plain as `feature-request`, add to product backlog, send thoughtful "noted, here's why we might/might not" reply. |
| Billing question | P2 | Pull Stripe data. Draft a precise answer. Issue refund if < spending authority limit. |
| Renewal / expansion intent | P1 | Surface to founder. Don't auto-reply. |
| Cancellation | P1 | Surface immediately. Don't try to save with a discount before founder reviews. |

## Churn-signal monitor (runs daily)

A workspace is at-risk when ANY of these are true:
- Active users dropped > 50% over 14 days (PostHog).
- No `core_action_completed` event in 21 days.
- Support ticket P1 unresolved > 4h during work hours.
- Failed payment, not recovered within 72h.
- Used a third-party integration that broke (we know via webhook).

When at-risk, the CS skill drafts a personal outreach for you — not a templated NPS survey.

## Weekly questions the agent answers

1. New customers this week — are they activating?
2. Open tickets by severity. Anything escalating?
3. Churned this week — who, why, was it preventable?
4. At-risk accounts — who, the signal, the suggested outreach.
5. Top 5 patterns in support volume — what's the underlying product fix?

## Standing rules

- **Acknowledge fast, answer well.** "I see this, looking now" beats a 6-hour silence.
- **Refund first if < $X (see CHARTER spending authority), debate later.**
- **Every cancellation gets a real conversation, not a survey.** Personal email from you (drafted by agent).
- **Stop using "ticket."** They're customers, not tickets.
- **Doc as you answer.** If you write the same explanation twice, the agent files a doc PR.

## Inputs to the daily brief

- Open P1/P2 tickets.
- New customers in last 24h (and their activation status).
- At-risk accounts (count + top 3).
- Churned accounts in last 24h.
