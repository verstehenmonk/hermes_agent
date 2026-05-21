---
name: marketing
description: "Marketing department: content, SEO, newsletter, launches."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [RESEND_API_KEY, LOOPS_API_KEY, POSTHOG_API_KEY, NOTION_API_KEY]
metadata:
  hermes:
    tags: [marketing, content, seo, newsletter, posthog, resend, loops]
---

# Marketing — solo SaaS

On activation, read `business/departments/marketing.md` and `business/CHARTER.md`.

## Voice (non-negotiable)

Plainspoken, technically honest, no superlatives. "Fast" not "blazing-fast."
"Reliable" only if we have an SLA. Show numbers, code, screenshots — never
abstract claims.

When drafting copy, every claim should answer: "what's the proof?" If you can't
point to a feature, benchmark, or quote, cut the claim.

## Content pipeline (Notion DB)

States: Captured → Outlined → Drafted → Scheduled → Shipped.

```bash
# Add to backlog
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"parent":{"database_id":"<CONTENT_DB>"}, "properties":{"Title":{"title":[{"text":{"content":"..."}}]}, "Status":{"status":{"name":"Captured"}}}}'
```

## Drafting protocol

1. Read the customer-pain evidence (Plain tickets, sales calls, support themes).
2. Pick the one thing the reader leaves with — write it as one sentence first.
3. Draft the outline (H1, H2s, one-sentence summary per section).
4. Surface to founder for the "go/no-go" on direction.
5. Only then write the draft.
6. Include: a working code sample OR a screenshot OR a real number.
7. End with a single CTA tied to the post's specific topic (not "sign up").

## Newsletter (Resend / Loops)

Cadence: weekly digest, sent Thursday morning (best for B2B per Loops benchmarks).
Format: one piece of original content, one tool/article we recommend, one
customer story (with permission). Three sections max.

```bash
# Send via Resend
curl -s -X POST "https://api.resend.com/emails" \
  -H "Authorization: Bearer $RESEND_API_KEY" -H "Content-Type: application/json" \
  -d '{"from":"...", "to":["..."], "subject":"...", "html":"..."}'
```

## SEO + attribution

PostHog handles site analytics if connected. Otherwise check the site's
deployed analytics. Track:
- Top entry pages (last 30d).
- Search queries ranking on page 2 — these are the next push.
- Conversion rate by source.

## Standing rules

- No gated content (email-walled).
- No claims you can't back with a feature, benchmark, or customer quote.
- One CTA per piece.
- Sponsorships > paid ads at this stage.
- Founder approves anything that goes out publicly. Agent drafts; founder ships.
