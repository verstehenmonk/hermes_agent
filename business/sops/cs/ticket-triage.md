# SOP: Ticket Triage

For every new support email (himalaya skill, label: `support`).

## Classify

- **Type**: bug | how-to | billing | feature-request | sentiment
- **Severity** (for bugs): SEV1-4 per `sops/product/bug-triage.md`
- **Sentiment**: score -2 (churn risk) to +2 (testimonial-worthy)
- **Customer tier**: from Stripe MRR — enterprise (>$1k) | pro | starter | free

## Route by type

### Bug
- File a Linear issue per `sops/product/bug-triage.md`
- Draft customer reply: acknowledge, link the Linear issue, give ETA
  category (today | this week | this sprint | backlog)

### How-to
- Search `knowledge-base/product-spec.md` for the answer
- If found: draft a reply with the answer + link to docs
- If not found: escalate to Head of Product as a docs gap; draft a "let me
  get back to you" reply

### Billing
- Pull customer's Stripe state via `stripe-billing` (read-only)
- For simple questions (when am I billed, what plan am I on): draft an
  answer with the facts
- For changes (refunds, plan switches): escalate to CFO + founder, draft a
  "I'll get a teammate to handle this" reply

### Feature request
- Log in Notion "Feedback" DB with customer name + quote + use case
- Draft a "we hear you, this is captured" reply (don't promise anything)

### Sentiment (low score)
- Always escalate to founder + Head of Sales
- Draft an empathetic reply that acknowledges the issue without committing
  to specifics

## Quality bar

Every DRAFT:
- Greets by first name (extract from signature)
- Addresses the specific issue (no generic templates)
- Has a concrete next step (with timeline)
- Signs off as the founder, not as "support"

## Post

To `#cs`, threaded:
- Original email summary
- Classification
- DRAFT reply
- Linear / Notion artifacts created
- Approval gate footer
