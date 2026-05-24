# SOP: Inbound Lead

When a new lead appears in Gmail (label: `inbound-sales`) or a Notion
"Pipeline" entry is created with stage = `lead`.

## Step 1 — Enrich

- Domain: pull from the email
- Company: company name from signature or domain WHOIS
- Role: pulled from signature or LinkedIn (if URL in signature)
- Source: cold inbound | referral | content | event (mark "unknown" if not
  obvious — don't guess)

## Step 2 — Score against ICP

Read `business/knowledge-base/company.md` ICP section. Score 0-5:
- 0: clearly not ICP, polite decline
- 1-2: edge case, route to founder
- 3-4: ICP fit, book a demo
- 5: top-priority ICP, founder personal reply

## Step 3 — Draft reply

Patterns:

- **Score 0**: "Thanks for reaching out — we focus specifically on
  <ICP>. We're not the right fit for <their case>. Wishing you luck with
  <alternative>."
- **Score 3-4**: "Thanks for reaching out — we'd love to show you what we do.
  Here are three 30-min slots this week: <slots from Calendar>. Or grab one
  directly: <booking link>."
- **Score 5**: route to founder for personal reply, draft optional.

Always post the DRAFT to `#sales` with the score and reasoning.

## Step 4 — Log

Create or update the Notion Pipeline row:
- Stage: `qualified` (score ≥ 3) or `closed-lost` (score 0)
- Score, source, enrichment data captured

## Step 5 — Don't send

You do not send. The founder reacts `:approve:` in `#sales`.
