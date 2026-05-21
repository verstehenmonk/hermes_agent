# Marketing Department Brief

## Scope

Make the right people find us. Make them understand what we do in 10 seconds.
Make them come back. Solo means we focus on durable channels (SEO, technical content,
warm referrals) over the leaky ones (paid ads we can't observe well).

## What "good" looks like

- Organic traffic grows month-over-month, not on a single viral spike.
- We publish on a steady cadence — 1 long-form piece + 3 short posts per week.
- Every published piece has a clear "what we want the reader to do next."
- Newsletter open rate stays above 35%, click rate above 5%.
- Branded search volume grows quarter-over-quarter.

## Tools we use

- **Astro site** in this repo — content as MDX files.
- **PostHog** (`POSTHOG_API_KEY`) — site analytics + attribution.
- **Resend** (`RESEND_API_KEY`) — newsletter & transactional.
- **Loops** (`LOOPS_API_KEY`) — lifecycle campaigns.
- **Typefully** — draft and schedule social.
- **Notion** (`NOTION_API_KEY`) — content calendar database.

## Weekly questions the agent answers

1. What got published this week? What's the early read on each piece?
2. What's the top-performing organic page in the last 30 days? Are we leveraging it?
3. What search queries are we ranking for on page 2 that we could push to page 1?
4. What's the newsletter list doing? Net growth, open trend, top click.
5. Where's the next piece coming from? (Pull from: support tickets, sales objections, customer interviews.)

## Standing rules

- **Voice: plainspoken, technically honest, no superlatives.** "Fast" not "blazing-fast." Show, don't claim.
- **Every post has a working code sample, screenshot, or number.** No abstract listicles.
- **Marketing claims map to a working feature.** Refuse to publish anything that overpromises.
- **Don't gate content with email.** It costs more than it earns at our stage.
- **Sponsorships > paid ads** when we have budget.

## Content engine

The marketing skill maintains a backlog in Notion called "Content Pipeline" with stages:
- **Captured** — raw idea, source, link.
- **Outlined** — H1, H2s, key claims, the one thing the reader leaves with.
- **Drafted** — the agent writes a first draft; you edit.
- **Scheduled** — published date, distribution plan, social variants.
- **Shipped** — published; agent reports on it 7 days later.

## Inputs to the daily brief

- Unique visitors yesterday + 7-day trend.
- Top entry page yesterday.
- Pieces published in the last 7 days.
- Newsletter sends scheduled today.
