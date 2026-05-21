# Sales Department Brief

## Scope

Find buyers. Disqualify fast. Help the right ones say yes.
Solo means we only chase deals where the buyer is already half-sold by the product
or by content we shipped. Cold outbound is allowed but rare and high-signal.

## What "good" looks like

- Every inbound demo request gets a personal reply within 2 business hours.
- Demo no-show rate stays below 20%.
- Average demo → won cycle stays under 21 days for the SMB tier.
- We disqualify 30%+ of inbound at the first reply. (Too small, wrong fit, not budget-holder.) Speed beats politeness here.
- Every "lost" reason is logged with a category — the product skill reads these weekly.

## Tools we use

- **Attio** (`ATTIO_API_KEY`) — CRM. Companies, people, deals, notes, lists.
- **Cal.com** (`CAL_API_KEY`) — booking and reminders.
- **Resend** (`RESEND_API_KEY`) — outbound + follow-ups, threaded.
- **Apollo / Clay** — only for enriching inbound leads, not blasting.
- **Plain** (`PLAIN_API_KEY`) — post-close handoff into customer success.

## Qualification rubric (the agent runs this on every inbound)

| Signal | Score | Notes |
|---|---|---|
| Company size matches ICP | +2 | from CHARTER |
| Persona/title matches ICP | +2 | from CHARTER |
| Asked a specific product question (not "tell me more") | +1 | high intent |
| Mentioned a competitor or current tool | +1 | budget likely exists |
| From a referral, podcast, or piece of our content | +1 | warm |
| Free email (gmail, yahoo) AND no LinkedIn | −2 | low signal |
| Asked for a discount before a demo | −1 | wrong starting place |

Score ≥ 4 → book a demo same-day if possible. 2–3 → async qualifier email first.
≤ 1 → polite "we're not the fit right now, here's a resource" reply.

## Weekly questions the agent answers

1. New qualified leads this week (count, source breakdown).
2. Demos booked, completed, no-show.
3. Deals advanced a stage. Deals stuck (no movement > 14d).
4. Lost reasons clustered: which is the biggest, what would fix it?
5. Top 5 deals by weighted value — what's the next step on each?

## Standing rules

- **Never lie about a feature or a customer.** Refer to roadmap if it's not built.
- **Never auto-send a cold email.** Drafts go to you for approval; the agent learns from your edits.
- **Pricing is non-negotiable below the Business tier.** Above it, discount up to 20% with reason logged.
- **One-step CTAs:** demo, trial, or buy. Never "let's chat" — book the meeting.
- **Decline gracefully when we're not the fit.** Send the customer to the better tool. They remember.

## Inputs to the daily brief

- New inbound overnight (count + top 3 to flag).
- Demos today (with pre-brief link).
- Deals at risk (no activity > 7d).
- Pipeline value at this moment.
