---
name: business-os-finance
description: "Solo-founder finance: MRR/ARR tracking, burn/runway, AR/AP, expense categorization, monthly close, investor / self updates."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [STRIPE_API_KEY, MERCURY_API_TOKEN]
  commands: [curl, python3]
metadata:
  hermes:
    tags: [Finance, MRR, ARR, Burn, Runway, Invoicing, SaaS]
---

# Finance — Solo Founder Playbook

The job is to know the numbers, never run out of cash, and tell the truth to yourself monthly. The agent fetches the data, computes the metrics, and drafts the narratives. You make the calls on pricing, spend, and reserves.

## Cadences

| Cadence  | Activity                                  | Tier   |
|----------|-------------------------------------------|--------|
| Daily    | Revenue pulse (MRR delta, failed payments)| AUTO   |
| Daily    | Cash balance check                        | AUTO   |
| Weekly   | Spend categorization + cost-spike alerts  | AUTO   |
| Weekly   | AR aging (overdue invoices)               | DRAFT  |
| Monthly  | Close: P&L, MRR walk, runway              | DRAFT  |
| Monthly  | Self / investor update                    | DRAFT  |
| Quarterly | Pricing review                           | HUMAN  |
| Annually | Tax prep handoff to accountant            | DRAFT  |

## Core Metrics (recomputed daily)

State stored in `state/kpis.yaml`. Daily pre-processor updates these.

### Revenue

| Metric                 | Source                          | Target / floor       |
|------------------------|---------------------------------|----------------------|
| MRR                    | Stripe subscriptions             | Track + target curve |
| ARR                    | MRR × 12                         | $360k by month 12    |
| New MRR (month)        | Stripe new subs - downgrades     | $5k/mo by Q3         |
| Churn $ (month)        | Cancellations × ACV/12           | <2% of MRR/mo        |
| NRR (rolling 90d)      | (start MRR + expansion - churn) / start MRR | >100% |
| ACV                    | Total ARR / customer count       | $14k+                |
| LTV (90d cohort)       | ACV × 1/monthly churn rate       | >$30k                |
| CAC (last 90d)         | sales+marketing $ / new customers| <$3k                 |
| Payback period         | CAC / monthly margin             | <12 months           |

### Cash

| Metric              | Source                  | Target / floor          |
|---------------------|-------------------------|-------------------------|
| Bank balance        | Mercury / bank API      | Minimum 12 months runway|
| Monthly burn        | Bank outflow - inflow   | <$8k initial            |
| Runway (months)     | Balance / burn          | >12 months always       |
| AR outstanding      | Stripe invoices unpaid  | <$5k / <7d aged         |
| Largest single dep. | Top customer % of MRR   | <20%                    |

If runway drops below 9 months, orchestrator escalates DAILY until founder acts.

## Daily Revenue Pulse (AUTO)

Pre-processor runs at 06:00 local. Reports:
- Yesterday's new MRR.
- Yesterday's churn ($, customers).
- Failed payments in last 24h.
- Trials converting today (Stripe trial_will_end webhooks).

If MRR moved >$500 in either direction → surface in morning brief.
If a failed payment is from a >$1k MRR customer → flag immediately, draft a "your payment failed" email DRAFT.

## Weekly Spend Audit (AUTO)

Categorize last 7 days of expenses (Mercury API or CSV import). Categories from `state/expense_categories.yaml`.

Flag:
- Any category up >30% week-over-week.
- New vendor (first appearance) → cross-check with `state/vendors.yaml`; if missing, prompt founder to add.
- Inference/LLM spend trend — this is the #1 watch metric for an AI Analytics product.
- Card transactions outside business hours from unfamiliar geographies → fraud check.

## AR Aging (weekly, DRAFT)

For annual plan customers paying by invoice:
- Pull unpaid invoices, age each.
- 0–30 days: silent.
- 30–45 days: DRAFT polite reminder.
- 45–60 days: DRAFT firm reminder + pause-on-day-60 warning.
- 60+ days: founder decides — call, pause service, or refer.

## Monthly Close (1st business day)

Pre-processor pulls the previous month's data. Agent produces the close:

1. **P&L summary**: revenue, COGS, opex, EBITDA. Compare to last month + last quarter avg.
2. **MRR walk**:
   - Starting MRR
   - + New MRR
   - + Expansion MRR
   - - Contraction MRR
   - - Churn MRR
   - = Ending MRR
3. **Cohort retention**: by signup month, are dollars retained? (Agent generates a triangle.)
4. **Top wins / top losses**: highest expansion + highest churn customers with one-sentence reasons.
5. **Burn breakdown**: payroll (= $0 solo, just founder draw), infra, AI inference, tools, marketing, legal/accounting.
6. **Runway**: months at current burn; months at flat burn but assuming MRR growth continues.
7. **Asks**: what decisions does the founder need to make this month? (Pricing, vendor cuts, hire timing.)

Save to `~/.hermes/business-os/finance/close-YYYY-MM.md`.

## Self / Investor Update (monthly, DRAFT)

Even without investors, write it. The discipline forces honesty.

Use `templates/investor-update.md`:
- The number that matters: MRR.
- What worked.
- What didn't.
- What I learned.
- What I'm doing next month.
- Asks (intros, advice, hires).

Send to: a small list of advisors, ex-bosses, peer founders. Even if it's three people, the act of writing focuses you.

## Pricing Review (quarterly, HUMAN)

The agent does the analysis; the founder decides.

Agent gathers:
- Discount rate (% of deals closed at list vs. discounted).
- Stuck-at-proposal deals citing price.
- Cohort LTV by acquired-at price.
- Competitor pricing diff (from `state/competitors.yaml`).
- Inference cost per customer per plan (key for an AI product — margin lives here).

Decision is the founder's. Common moves:
- Raise list price by 20% for new customers (existing grandfathered).
- Add usage-based component for inference-heavy customers.
- Introduce annual-only discount tier.
- Drop the lowest tier (it costs more to support than it brings in).

## Tax & Compliance

- Sales tax: track by state via Stripe Tax or Anrok.
- 1099 / W9 collection for contractors (typically vendors selling services).
- Quarterly estimated taxes: agent reminds founder 2 weeks before deadline.
- Year-end: agent compiles books, hands to accountant, founder reviews.

## Cost-Spike Alerts (AUTO)

The #1 thing that kills AI products: runaway inference cost. The agent watches:
- LLM API spend per customer per day.
- Any customer exceeding 10× their plan's query allowance.
- Any single query consuming >$1 in tokens (queries gone wrong).

Triggers immediate alert with the customer ID + query log.

## Anti-patterns

- Looking at MRR weekly but not at burn weekly. (Burn surprises faster than MRR.)
- Letting AR age past 60 days. (Sets a precedent.)
- Cohort-blending metrics. (Always look at cohort tables, not aggregate.)
- "We'll figure out unit economics later." Margins on AI products are won or lost in the first 6 months.
- Discount-creep. Every concession on price compounds.
