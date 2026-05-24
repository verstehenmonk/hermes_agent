---
name: customer-success
description: "Customer success: support, onboarding, churn signals, expansion."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [PLAIN_API_KEY, LOOPS_API_KEY, POSTHOG_API_KEY, CAL_API_KEY, ATTIO_API_KEY]
metadata:
  hermes:
    tags: [customer-success, support, onboarding, churn, plain, loops]
---

# Customer Success — solo SaaS

On activation, read `business/departments/customer-success.md` and the CHARTER's
"spending authority" section (refund limits).

## Plain (support tool)

```bash
# Create a reply on a thread
curl -s -X POST "https://core-api.uk.plain.com/graphql/v1" \
  -H "Authorization: Bearer $PLAIN_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"mutation { replyToThread(input: {threadId: \"...\", textContent: \"...\"}) { ... } }"}'

# Update thread priority/labels
curl -s -X POST "https://core-api.uk.plain.com/graphql/v1" \
  -H "Authorization: Bearer $PLAIN_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"mutation { updateThread(input: {threadId: \"...\", priority: \"P1\"}) { ... } }"}'
```

If Plain isn't connected, fall back to Gmail (read-only) and surface drafts to
the founder.

## Triage loop

For every incoming message:

1. Read the message + customer history (Attio + Plain + PostHog if connected).
2. Apply the triage rubric in the brief. Tag the thread with the right priority.
3. **Acknowledge fast** — even if the answer is "looking, back in 1h."
4. **Resolve** if you can:
   - How-do-I → answer with doc link.
   - Bug → reproduce, file Linear with steps, link the issue back to customer.
   - Billing → pull Stripe, answer with numbers.
   - Refund < spending authority → issue via Stripe, log the reason.
5. **Escalate** if you can't:
   - Cancellation → founder talks to them. Don't try to save with a discount.
   - Refund ≥ authority → draft, founder approves.
   - Renewal / expansion intent → founder owns the conversation.

## Lifecycle (Loops)

The lifecycle sequences are owned in Loops; the agent triggers them via API.

| Trigger | Sequence | Window |
|---|---|---|
| `signup` | Welcome + onboarding tips | Day 0 |
| `activated` | Success congrats + "what's next" | Day 0 (event-driven) |
| `not_activated_72h` | Gentle nudge with the single fastest path to value | Day 3 |
| `paying_customer_day_7` | "How's it going?" personal-feeling check-in | Day 7 |
| `paying_customer_day_30` | First QBR-lite (just numbers) | Day 30 |
| `dormant_14d` | "Anything we can help with?" | When risk-signal fires |
| `churned` | Exit-interview ask + a refund credit if applicable | After cancellation |

```bash
curl -s -X POST "https://app.loops.so/api/v1/events/send" \
  -H "Authorization: Bearer $LOOPS_API_KEY" -H "Content-Type: application/json" \
  -d '{"email":"...", "eventName":"activated", "eventProperties":{"plan":"team"}}'
```

## Churn-signal monitor (runs daily)

Pull from PostHog + Plain + Stripe. A workspace is at-risk when ANY:
- Active users dropped > 50% over 14 days.
- No `core_action_completed` event in 21 days.
- P1 ticket unresolved > 4h during work hours.
- Failed payment, not recovered within 72h.

Draft a personal-from-founder email for each at-risk workspace. Don't send
without founder approval.

## Onboarding playbook

When a new paid customer signs up:
1. Welcome email (Loops `signup` event).
2. Tag in Attio as customer (not lead).
3. Schedule a 30-day check-in on founder's calendar via Cal.com (optional accept).
4. If they're a Business tier or higher, ping founder to do a personal welcome within 24h.
5. Watch the activation metric: did they hit `first_value` in 24h? In 7d?

## Standing rules

- Acknowledge within 1 business hour.
- Refund < spending authority? Issue it. Log the reason.
- Every cancellation gets a real conversation, not a survey.
- Doc as you answer. Repeat questions → doc PR.
- Stop using "ticket." They're customers.
