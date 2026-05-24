# SOP: Invoice Collection

For annual / invoice-paying customers (not self-serve Stripe).

## Weekly scan (Wednesday 10am)

Pull Stripe invoices in status `open` or `past_due`.

For each:
- Customer name + contact email
- Amount
- Days past due
- Last reminder sent (from invoice notes)

## Cadence

| Days past due | Action |
|---|---|
| 0-3 | None (give it time) |
| 4-7 | DRAFT polite reminder to `#finance` |
| 8-14 | DRAFT firmer reminder, CC accounts payable contact if known |
| 15-30 | DRAFT escalation to a named person + offer payment plan |
| 30+ | Escalate to founder personally; consider pausing service |

## Output

Single post to `#finance` listing all DRAFTS, grouped by customer, with the
days-past-due and recommended cadence step. Founder approves per invoice.

## Pause-service decision

Never auto-pause. The founder decides. Provide:
- Customer MRR
- Their last login / last activity
- A "if we pause, what breaks for them?" assessment
