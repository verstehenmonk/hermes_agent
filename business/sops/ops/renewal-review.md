# SOP: Vendor Renewal Review

Runs every Monday 11am via `weekly-vendor-audit` cron.

## Pull from Notion "Vendors" DB

For each vendor:
- Days until renewal
- Trailing 30d cost vs. trailing 30d cost from 3 months ago
- Last-used date (founder marks this manually monthly)

## Flag

Post to `#ops`:

### Renewing in next 30 days
- Vendor, cost, renewal date, days remaining
- Recommendation: renew | renegotiate | cancel

### Cost increase > 10% MoM
- Vendor, prior cost, new cost, % change
- Likely cause (more usage | price hike | both)
- Action: investigate | accept | renegotiate

### Unused > 30 days
- Vendor, cost, last-used date
- Recommendation: cancel | downgrade | keep (with reason)

## Decision

Founder reacts in `#ops`:
- `:renew:` — head-of-ops confirms renewal date in calendar
- `:cancel:` — draft a cancellation email (DRAFT, approval-gated)
- `:downgrade:` — draft the plan-change request

## Quarterly stack review

Every 13 weeks, produce a full stack cost summary: total monthly spend by
category, biggest line items, year-over-year change. Post to `#finance` and
`#ops`.
