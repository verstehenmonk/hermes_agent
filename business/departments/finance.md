# Finance Department Brief

## Scope

Keep the books accurate. Keep cash flowing. Tell the founder, weekly, how long
the runway is and what's pulling on it. Solo means we automate the boring 90%
and reserve human time for tax decisions and pricing changes.

## What "good" looks like

- Books reconcile within 3 business days of month-end.
- Cash position known to the dollar at any moment.
- MRR walk reconciles to Stripe (new + expansion − contraction − churn = net).
- Tax obligations are visible 60 days before they're due.
- Every recurring vendor charge is traceable to a business reason.

## Tools we use

- **Stripe** (`STRIPE_API_KEY`) — revenue, subscriptions, refunds, disputes.
- **Mercury** (`MERCURY_API_KEY`) — banking, ACH, cards, balances.
- **Beancount** (text-based double-entry) OR **QuickBooks Online** — the ledger.
- **A 1Password vault for tax/EIN/banking docs** (manual).

## Daily check (deterministic via `scripts/metrics_snapshot.py`)

```
{
  "cash_on_hand": <Mercury all accounts sum>,
  "mrr": <Stripe MRR>,
  "mrr_delta_24h": <change from yesterday>,
  "failed_payments_24h": <count + total $>,
  "active_subscriptions": <count>,
  "trial_to_paid_24h": <count>,
  "refunds_issued_24h": <count + total $>
}
```

If `mrr_delta_24h < 0` or `failed_payments_24h > 0`, the finance skill investigates
before the morning brief lands.

## Monthly close playbook

1. Pull Stripe invoices for the month → match to ledger.
2. Pull Mercury transactions → categorize (revenue, infra, payroll, software, taxes, founder draw).
3. Compute: MRR walk, gross margin, burn (3-mo trailing), runway.
4. Reconcile differences. Flag anything categorized as "uncategorized" > $100.
5. Draft a one-page monthly statement: where we are, where we were, what changed.
6. File the statement to `~/.hermes/business/journal/finance/YYYY-MM.md`.

## Standing rules

- **Refunds under $X (see CHARTER spending authority) get issued immediately.** Log reason in Stripe metadata.
- **No vendor charge exceeds $200/mo without a Notion entry** explaining its business purpose. Audit monthly.
- **Reserve 30% of every payment for taxes** in a separate Mercury vault. Never touch.
- **Quarterly estimated taxes are calendar events**, set 21 days ahead with the amount pre-calculated.
- **Never auto-pay invoices over $500.** Drafts go to founder.

## Pricing rules

- Pricing on the public site is the source of truth.
- Any deal at a discount > 20% requires a memo: who, why, what they get, what's the renewal price.
- All annual deals: charge upfront, recognize monthly. Cash and revenue are different things — the agent should never conflate them.

## Weekly questions the agent answers

1. Cash, burn, runway. (One sentence each.)
2. MRR walk this week. Where did the movement come from?
3. Are any customers at risk of involuntary churn (failed payments, expiring cards)?
4. Did any unexpected charges hit the bank account?
5. What tax/legal obligation is coming up in the next 60 days?

## Inputs to the daily brief

- MRR + Δ since yesterday.
- Failed payments overnight (count + customers to follow up).
- Cash balance.
- Any single transaction > $1,000 overnight.
