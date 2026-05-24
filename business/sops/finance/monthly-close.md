# SOP: Monthly Close

Runs on the 1st of each month at 9am via `monthly-close` cron. Output is a
single post to `#finance`.

## Pull data

- Stripe: previous month's revenue, refunds, net revenue, top 10 customers
  by MRR
- Brex / Mercury: previous month's spend (CSV uploaded by founder to
  `knowledge-base/finance/spend-YYYY-MM.csv`)
- Bank balance: current cash (founder enters this in
  `knowledge-base/finance/cash.yaml`)

## Compute

### MRR walk
```
starting MRR  = <prior month ending MRR>
+ new MRR     = sum of new subscriptions × MRR
+ expansion   = sum of upgrades × MRR delta
- contraction = sum of downgrades × MRR delta
- churn       = sum of cancellations × MRR
= ending MRR
```

### Other metrics
- ARR = ending MRR × 12
- Net new ARR = ending ARR - starting ARR
- Gross margin % = (revenue - cost of revenue) / revenue
  - Cost of revenue = hosting (Vercel + Fly + DB) + AI inference + Stripe
    fees
- Logo churn % = customers churned / customers at month start
- Revenue churn % = MRR churned / starting MRR
- Net revenue retention % = (starting MRR + expansion - contraction -
  churn) / starting MRR
- Runway months = cash / trailing 3-month avg burn

## Report

Post to `#finance`:

```
## Monthly close — <month>

**Cash:** $X (Δ vs. last month: ±$Y)
**MRR:** $X → $Y (±Z%)
**ARR:** $X
**Net new ARR:** $X
**Gross margin:** X%
**Logo churn:** X% | Revenue churn: X% | NRR: X%
**Runway:** X months at trailing 3-mo burn

### MRR walk
<table>

### Top 5 spend categories
<table>

### Watch list
- Customers at churn risk (sentiment ≤ -1 from CS)
- Customers downgrading
- One-line summary of any unusual cost spike
```

## Stash

Append the report to `knowledge-base/finance/close-history.md` so trends are
queryable next month.
