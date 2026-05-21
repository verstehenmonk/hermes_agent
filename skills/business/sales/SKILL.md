---
name: sales
description: "Sales department: qualification, pipeline, demos, follow-up."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [ATTIO_API_KEY, CAL_API_KEY, RESEND_API_KEY]
metadata:
  hermes:
    tags: [sales, crm, attio, cal-com, pipeline, qualification]
---

# Sales — solo SaaS

On activation, read `business/departments/sales.md` and `business/CHARTER.md`
(especially the ICP and qualification rubric).

## Attio (CRM)

Modern CRM with a clean REST API. Auth: `Bearer $ATTIO_API_KEY`.

```bash
# Find a person by email
curl -s -X POST "https://api.attio.com/v2/objects/people/records/query" \
  -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
  -d '{"filter":{"email_addresses":{"$eq":"..."}}}'

# Create a person
curl -s -X POST "https://api.attio.com/v2/objects/people/records" \
  -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
  -d '{"data":{"values":{"name":[{"first_name":"...","last_name":"..."}], "email_addresses":["..."]}}}'

# Add note
curl -s -X POST "https://api.attio.com/v2/notes" \
  -H "Authorization: Bearer $ATTIO_API_KEY" -H "Content-Type: application/json" \
  -d '{"data":{"parent_object":"people","parent_record_id":"...","title":"...","content":"..."}}'
```

## Cal.com

```bash
# List bookings
curl -s "https://api.cal.com/v2/bookings" -H "Authorization: Bearer $CAL_API_KEY"
```

## Inbound triage (the agent's main loop)

When a new email/booking/form arrives:

1. **Score it.** Run the qualification rubric in `business/departments/sales.md`.
2. **Score ≥ 4** → Book the demo same-day. Send a confirmation that includes:
   the time, the Cal.com link if they haven't booked yet, 1 line of personalization
   (something from their company you read in the last 24h), and a single specific
   question for them to think about.
3. **Score 2–3** → Async qualifier email. Two questions max. Tie them to the
   highest-uncertainty rubric dimension.
4. **Score ≤ 1** → Polite disqualify. Refer them to the better tool if you know one.
5. **Always log to Attio** with the score and reasoning.

## Demo pre-brief (runs from Cal webhook)

For every booked demo, 30 min before:
1. Pull the attendee's Attio record.
2. Enrich: their company size, recent news, their LinkedIn (manual link surfaced).
3. Pull any prior PostHog activity for their workspace if they have one.
4. Score them again with fresh info.
5. Draft a one-page brief: what to show, what to ask, where they are in the cycle, the one objection to expect.
6. Email the brief to the founder.

## Follow-up cadences

- Demo done → Send thank-you + recap (with action items) within 4h.
- No response in 4d → Bump with a relevant resource (not just "circling back").
- No response in 10d → One last short, specific note.
- No response in 14d → Mark as nurture, log lost reason as "ghost".

## Lost reason taxonomy (use these exact strings — product team reads them)

- `no-budget` — they liked it but couldn't fund it
- `wrong-fit` — we couldn't actually solve their problem
- `chose-competitor` — they bought from X (always log X)
- `chose-build` — they're building it internally
- `chose-status-quo` — they decided to do nothing
- `feature-missing` — specific feature gap (log the feature)
- `ghost` — no response after the cadence finished
- `timing` — real interest but later (set a follow-up date)

## Standing rules

- Never lie about a feature or a customer.
- Never auto-send cold email — drafts to founder.
- Pricing is non-negotiable below the Business tier.
- One-step CTAs (book / try / buy). Never "let's chat".
- Decline gracefully when we're not the fit.
