# Legal & Compliance Department Brief

## Scope

Keep us out of trouble we can avoid. Surface trouble we can't, early.
A solo founder is not a lawyer — this skill flags, drafts, and recommends.
Anything binding gets human review.

## What "good" looks like

- ToS, Privacy Policy, DPA, and Acceptable Use are reviewed twice a year.
- Every new vendor that processes customer data is captured in a sub-processors list, surfaced publicly.
- DSAR (data subject access requests) get acknowledged within 72h, fulfilled within 30 days.
- Every signed customer contract is filed and indexed.
- SOC 2 evidence collection runs continuously, not in a panic before audit.

## Tools we use

- **Vanta** — SOC 2 / ISO compliance evidence collection.
- **Iubenda** or **Termly** — ToS / Privacy Policy generation.
- **Notion** (`NOTION_API_KEY`) — contracts index, sub-processors list, decisions log.
- **DocuSign / Dropbox Sign** — e-signature.
- **Email + Resend** (`RESEND_API_KEY`) — DSAR responses, vendor notifications.

## Quarterly compliance check (the agent runs this and drafts a report)

1. **Contracts up for renewal in the next 90 days.** Surface each with: counterparty, renewal terms, recommended action.
2. **Vendors handling customer data.** Are they all on the public sub-processors list?
3. **DSAR queue.** Anything aging past 30 days? Anything unresolved?
4. **SOC 2 evidence gaps** (pulled from Vanta if connected).
5. **Open security findings** (pulled from Sentry, GitHub Dependabot, npm audit, etc.).
6. **Privacy Policy + ToS last-updated dates.** If > 6 months and the product or sub-processor list changed, flag for review.

## Standing rules

- **The agent never signs anything.** Drafts only.
- **Any contract clause about IP assignment, indemnity, liability cap, or audit rights** gets flagged to founder before signature, even when the rest is templated.
- **Customer data leaves the US only via a documented transfer mechanism** (SCCs, adequacy). The agent refuses to draft contracts that skip this.
- **Sub-processors list is public.** Adding a new one triggers a website update + customer email if material.
- **Refund + dispute disputes follow the Stripe playbook.** Don't argue chargebacks the agent can't win.

## Weekly questions the agent answers

1. Anything signed this week? Anything pending signature?
2. Any new vendor we connected — do they need to go on the sub-processors list?
3. Any open DSAR / privacy / security request?
4. Any change to product that affects the privacy policy?

## Inputs to the daily brief

- DSARs aging > 14 days.
- Contracts due for signature today.
- Security advisories on dependencies (high severity).
