---
name: stripe-billing
description: "Stripe: read-only billing queries (customers, subscriptions, MRR, charges, invoices) via curl. Write actions require explicit founder approval."
version: 1.0.0
author: Hermes Business OS
license: MIT
prerequisites:
  env_vars: [STRIPE_API_KEY]
  commands: [curl, jq]
metadata:
  hermes:
    tags: [Stripe, Billing, Finance, API]
---

# Stripe Billing

Read-only access to Stripe. Use a **restricted key** (Stripe Dashboard →
Developers → API keys → "Create restricted key") with these permissions:
- Customers: read
- Subscriptions: read
- Invoices: read
- Charges: read
- Events: read

Everything else: NONE. This skill is intentionally write-disabled.

## Setup

1. Create a restricted key as above
2. Set `STRIPE_API_KEY=rk_live_...` (note `rk_`, not `sk_`)
3. Test: `curl -s https://api.stripe.com/v1/customers -u "$STRIPE_API_KEY:" | jq '.data | length'`

## Common queries

### Current MRR (sum of active recurring subscriptions)
```bash
curl -s "https://api.stripe.com/v1/subscriptions?status=active&limit=100" \
  -u "$STRIPE_API_KEY:" \
  | jq '[.data[] | .items.data[0].plan.amount * .items.data[0].quantity] | add / 100'
```

### MRR delta over a date range
```bash
curl -s "https://api.stripe.com/v1/events?type=customer.subscription.created&created[gte]=$(date -d 'yesterday' +%s)" \
  -u "$STRIPE_API_KEY:" \
  | jq '.data[] | {created, customer: .data.object.customer, amount: .data.object.items.data[0].plan.amount}'
```

### Top customers by MRR
```bash
curl -s "https://api.stripe.com/v1/subscriptions?status=active&limit=100" \
  -u "$STRIPE_API_KEY:" \
  | jq '.data | sort_by(.items.data[0].plan.amount * .items.data[0].quantity) | reverse | .[0:10] | .[] | {customer, mrr: (.items.data[0].plan.amount * .items.data[0].quantity / 100)}'
```

### Recent failed charges
```bash
curl -s "https://api.stripe.com/v1/charges?limit=20" \
  -u "$STRIPE_API_KEY:" \
  | jq '.data[] | select(.status == "failed") | {id, customer, amount, failure_code, failure_message, created}'
```

### Open invoices (collections)
```bash
curl -s "https://api.stripe.com/v1/invoices?status=open&limit=100" \
  -u "$STRIPE_API_KEY:" \
  | jq '.data[] | {id, customer, amount_due, due_date, days_past_due: ((now - .due_date) / 86400 | floor)}'
```

## Forbidden actions

You must NEVER:
- Issue refunds
- Cancel subscriptions
- Update subscription plans
- Create payment methods
- Delete customers

If a query needs one of those, draft the action and escalate to founder via
`sops/_shared/approval-gate.md`. The founder runs the action manually in
the Stripe dashboard or via a separate write-enabled key.
