# SOP: Vendor Onboarding

When a new SaaS or vendor is added to the stack.

## Capture in Notion "Vendors" DB

- Name
- Category (analytics | hosting | comms | dev-tools | finance | other)
- Cost: monthly | annual | usage-based; current monthly amount
- Renewal date
- Owner (always founder for a solo company)
- Payment method (Brex card | Mercury ACH | other)
- Data sensitivity: none | PII | customer-data | prod-secrets
- API key location: env var name + `~/.hermes/secrets/<file>` path
- Cancellation friction: easy (self-serve) | medium (email) | hard (call)

## Security checklist

- [ ] API key is scoped to least-privilege (read-only where possible)
- [ ] API key stored in `~/.hermes/secrets/` with 0600 perms
- [ ] API key NOT committed to any repo
- [ ] If they handle customer data: signed DPA on file (link in Notion)
- [ ] SSO enabled if available
- [ ] 2FA enabled on the admin account

## Add to monitoring

If the vendor has a webhook or status page, register it:
- Webhook → add a `webhook-templates/<vendor>.json` route
- Status page → add to `knowledge-base/runbook.md` dependency list

## Output

Post a one-line confirmation to `#ops` with vendor name, cost, renewal date.
