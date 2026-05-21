---
name: finance
description: "Finance: MRR, cash, runway, invoices, Stripe + Mercury + ledger."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [STRIPE_API_KEY, MERCURY_API_KEY]
metadata:
  hermes:
    tags: [finance, stripe, mercury, mrr, runway, taxes]
---

# Finance — solo SaaS

On activation, read `business/departments/finance.md` and the CHARTER's spending
authority section.

## Stripe

```bash
# Active subscriptions
curl -s -u "$STRIPE_API_KEY:" \
  "https://api.stripe.com/v1/subscriptions?status=active&limit=100"

# Refund a charge (within authority)
curl -s -X POST -u "$STRIPE_API_KEY:" \
  "https://api.stripe.com/v1/refunds" \
  -d "charge=ch_..." -d "reason=requested_by_customer" \
  -d "metadata[reason_note]=customer asked for X"

# Retry an invoice
curl -s -X POST -u "$STRIPE_API_KEY:" \
  "https://api.stripe.com/v1/invoices/in_.../pay"
```

## Mercury

```bash
# Accounts + balances
curl -s -H "Authorization: Bearer $MERCURY_API_KEY" \
  "https://api.mercury.com/api/v1/accounts"

# Recent transactions
curl -s -H "Authorization: Bearer $MERCURY_API_KEY" \
  "https://api.mercury.com/api/v1/account/$ACCT/transactions?limit=100"
```

## Source-of-truth for numbers

**Do not compute MRR, cash, or runway in this skill.** Those numbers live in
`~/.hermes/business/metrics/latest.json` written by
`business/scripts/metrics_snapshot.py`. If the snapshot is stale (> 6 hours),
run the script first, then read.

You may compute *deltas* (today vs yesterday, this month vs last) by reading
both snapshots.

## Failed-payment playbook (webhook handler)

When `invoice.payment_failed` fires:
1. Look up the customer in Stripe + Attio.
2. Stripe has a built-in dunning retry — let it run once.
3. If still failed after 24h, draft a personal email from founder ("hey, your
   card got rejected, here's how to fix"). Don't sound like a collections agent.
4. If amount > spending-authority threshold, page founder on Telegram immediately.
5. Log to `~/.hermes/business/journal/finance/payment-failures.md`.

## Monthly close (runs from cron)

1. `metrics_snapshot.py --month-close` writes the JSON snapshot.
2. Categorize Mercury transactions for the month:
   - Revenue, infra (Vercel/AWS), software (the vendor list), payroll, founder draw, taxes.
   - Flag uncategorized > $100.
3. Compute the MRR walk (start + new + expansion − contraction − churn = end).
4. Draft the monthly close per `business/rituals/monthly-close.md`.
5. Archive via `business/scripts/journal.py monthly`.

## Tax reserve

For every Stripe payout received, journal a note to set aside ~30% in the
Mercury tax-reserve account. The agent only flags; the founder moves money.

```
Today's payout: $X. Suggested tax reserve: $0.30 * X = $Y. Move via Mercury.
```

## Pricing changes

When asked to change pricing:
1. Confirm with founder (always — even if asked once before).
2. Memo to journal: who, why, what changed, expected impact, review date.
3. Update Stripe Prices (create new, don't edit; grandfather existing).
4. Update Attio "price" field on relevant company records.
5. Update marketing site pricing page (file a PR, don't auto-merge).

## Standing rules

- Refunds < spending authority → issue + log.
- Refunds ≥ authority → draft, escalate.
- Never auto-pay invoices > $500.
- Reserve 30% of every payout for taxes.
- Vendor charges > $200/mo need a Notion entry.
- Quarterly estimated tax dates live on the calendar 21 days early.
