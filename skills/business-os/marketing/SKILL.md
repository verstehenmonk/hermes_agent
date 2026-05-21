---
name: business-os-marketing
description: "Solo-founder marketing: content calendar, blog drafts, SEO, social, newsletter, attribution. AI-native top-of-funnel."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [GHOST_API_KEY, RESEND_API_KEY, POSTHOG_API_KEY]
  commands: [curl]
metadata:
  hermes:
    tags: [Marketing, Content, SEO, Newsletter, Social, Attribution, SaaS]
---

# Marketing — Solo Founder Playbook

The job is top-of-funnel — bringing the ICP to the product. As a solo founder, you compete on **founder voice + speed of publishing**, not budget. The agent drafts, you publish.

## Cadences

| Cadence       | Activity                                  | Tier   |
|---------------|-------------------------------------------|--------|
| Daily         | Topic mining (social, HN, X, customer)    | AUTO   |
| 2×/week       | Blog post draft (Tue + Thu)               | DRAFT  |
| Daily         | One social post (LinkedIn + X)            | DRAFT  |
| Weekly (Fri)  | Newsletter to subscribers                 | DRAFT  |
| Weekly (Mon)  | SEO rank check + content pipeline review  | AUTO   |
| Monthly       | Attribution report                        | AUTO   |

## Content Strategy (set once, revisit quarterly)

Founder-led, opinionated, technical. Three pillars:

1. **Teardown content**: take a real B2B SaaS funnel/dashboard, analyze it publicly. High virality, demonstrates the product implicitly.
2. **AI analytics how-to**: practical posts about using LLMs for product analytics. Ranks for long-tail SEO, attracts ICP buyers.
3. **Founder-build-in-public**: weekly thread/post about the company's metrics, lessons, mistakes. Builds inbound trust.

Ratios per month: 4 teardowns, 4 how-tos, 4 build-in-public. The agent rotates topics so the calendar never goes dry.

## Topic Mining (daily, AUTO)

Pre-processor `scripts/content_radar.py` runs daily. Sources:
- Top 100 HackerNews stories (filter for analytics/AI/SaaS).
- Search r/SaaS, r/ProductManagement, r/analytics for "anyone using X?" / "how do you Y?" posts.
- Last 7 days of support tickets tagged `confusion` or `feature-request` — every confusion is a blog post.
- Newsletters in `state/competitors.yaml` (their content gaps = your opportunities).
- X/Twitter list of B2B SaaS operators (defined in `state/x_lists.yaml`).

Output: `~/.hermes/business-os/content-ideas/YYYY-MM-DD.md` with 10 candidate angles, ranked by ICP-relevance.

## Blog Drafting (Tue + Thu, DRAFT)

Trigger: founder picks an angle from the day's content-ideas file. Agent drafts using `templates/blog-brief.md`.

**Draft requirements** (agent self-checks):
- Working title is a specific claim, not a category ("Why product-led companies miss churn signals" not "About churn").
- First sentence makes a strong claim. No "in this post we will explore".
- Has one concrete example from a real customer or a public company.
- Includes a chart or table (the product exports these — link the export).
- Ends with one specific CTA: "free trial", "book a demo", or "subscribe to newsletter" — never more than one.
- ≤1200 words for teardowns and how-tos; ≤600 words for build-in-public.

Founder approves → agent publishes via Ghost API → schedules the social cross-post.

## Social Posts (daily, DRAFT)

One post per platform per day. Format-fit:

**LinkedIn**: 1300-character story. Hook (first line) → tension → resolution → soft CTA. The agent generates 3 variants; founder picks one.

**X**: thread (≤8 tweets) OR single punchy claim. The agent generates one of each; founder picks form.

**Reuse**: every Tue/Thu blog post seeds 3 short-form posts spread across the next 2 weeks. The agent maintains this schedule automatically.

## SEO

Track:
- Top 30 keywords (defined in `state/seo_keywords.yaml`).
- Search Console position weekly.
- Backlink count via Ahrefs / public tools.

Weekly rank check (Mon AUTO): flag any keyword that dropped >3 positions. Surface the URL and propose a refresh.

**Pillar pages**: maintain 5 pillar pages on core topics ("product analytics for B2B SaaS", "AI dashboards", etc.). Refresh quarterly with new data + customer examples.

## Newsletter (Fri, DRAFT)

Cadence: weekly, sent Fri 09:00. Format:
- **One big idea** (5–7 sentences) — usually riffs on this week's blog post.
- **Three sharp links** — best things you read this week, 1-sentence comment each.
- **One thing we shipped** — single product update, with screenshot or link.
- **One ask** — recruit a customer call, ask for feedback, plug a job (or "tell a friend").

The agent drafts using context from the week's blog + product changelog + Linear closed issues. Founder edits + sends via Resend.

## Attribution

Solo founder doesn't run paid ads (charter says so). Attribution focus is: **of new trials this month, where did they come from?**

Pre-processor pulls trial signups + UTM tags + referrer. Agent produces a monthly report:
- Top sources: organic search, social (which post), referral (which customer), direct.
- Per-source: trial→paid conversion.
- Recommendation: double down on which channel.

## Launch Plays

When product ships a major feature (`product` skill flags it):
1. Schedule a launch day (usually 7 days out).
2. Draft: blog post (long-form), email to all customers, LinkedIn + X posts, Product Hunt listing, optional HN Show post.
3. Day-of: agent posts at the scheduled times; tracks engagement; reports back to founder.
4. Day+7: retro: signups attributed, demos booked, customer reactions. Logged to `~/.hermes/business-os/launches/<feature>.md`.

## Anti-patterns

- Posting more than once a day on a single channel (algorithm punishment).
- Generic AI-flavored content. Voice is founder-first, opinionated, specific.
- CTA stacking ("trial OR demo OR newsletter") — pick one per post.
- Treating LinkedIn and X identically (different audiences, different formats).
- Letting the agent publish unedited. Customer-facing prose is always founder-reviewed.
