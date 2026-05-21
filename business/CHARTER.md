# Business Charter

> This is the constitution. Every department skill reads this file first.
> Edit it carefully — every change here changes how the agent behaves across all departments.

## Identity

- **Company name:** _e.g. Acme AI_
- **Legal entity:** _Delaware C-corp / LLC / sole prop_
- **Founded:** _YYYY-MM_
- **Founder & sole operator:** _your name, andtut123@gmail.com_
- **One-sentence pitch:** _<verb> for <who> so they can <outcome>._
- **Stage:** _idea / pre-launch / paid beta / public launch / scaling_

## Who we serve

- **Primary ICP (ideal customer profile):**
  - Company size: _e.g. 50–500 engineers_
  - Industry: _e.g. fintech, devtools, e-commerce_
  - Title/persona we sell to: _e.g. VP Engineering, Head of Data_
  - Title/persona we serve: _e.g. backend engineers_
- **The pain we remove:** _what they currently do that's painful or expensive_
- **What they hire us to do (JTBD):** _the job they pay us to finish_
- **Who we explicitly do NOT serve:** _so the agent disqualifies fast in sales_

## What we sell

- **Product(s):** _list_
- **Pricing model:** _seat-based / usage / hybrid / flat_
- **Plans:** _e.g. Free / Team $X / Business $Y / Enterprise (custom)_
- **Contract length:** _monthly / annual / both_
- **Free trial:** _14 days / none / self-serve_

## The three bets this quarter

> Only three. If everything is a priority, nothing is.

1. _e.g. Get to $20k MRR_
2. _e.g. Ship the Slack integration_
3. _e.g. Publish 8 long-form pieces and hit 5,000 organic uniques/mo_

## North-star metric

- **Headline number:** _e.g. weekly active workspaces_
- **Why this and not revenue:** _e.g. predicts conversion 30 days out_
- **Current value:** _filled by `scripts/metrics_snapshot.py`_
- **Target by end of quarter:** _your number_

Sub-metrics in `north-star.md`.

## Principles (how decisions get made when I'm not around)

> These are the agent's defaults when it has to act without you.

1. **Ship narrow, ship now.** When in doubt, smaller scope.
2. **Customer pain > internal preference.** Reorder the roadmap when a paying customer asks for the same thing twice.
3. **Refund first, debate later.** For requests under $X, issue the refund and log the reason.
4. **Reply within one business day, even if the answer is "I don't know yet."**
5. **No silent failures.** Every script that fails surfaces the error in the daily brief.
6. **Default to written.** Anything important goes in the decisions log.
7. **One person, finite hours.** Saying no is a feature.

## Constraints

- **Working hours:** _e.g. Mon–Fri 09:00–18:00 America/New_York. Outside these, only P1 alerts page._
- **Spending authority delegated to the agent:**
  - Issue refunds up to $_____ without asking
  - Approve marketing spend up to $_____ /mo without asking
  - Anything above: draft and surface for approval
- **Tone:** _e.g. plainspoken, technical-honest, no marketing fluff_
- **Public voice:** _the brand voice the marketing skill should use_

## The stack (what's actually connected)

> Update this when you add or remove a tool. Skills check `~/.hermes/.env` for keys
> matching these and degrade gracefully if a key is missing.

| Function | Tool | Env var | Connected? |
|---|---|---|---|
| Code & PRs | GitHub | `GITHUB_TOKEN` | _yes/no_ |
| Issues | Linear | `LINEAR_API_KEY` | _yes/no_ |
| Errors | Sentry | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG` | _yes/no_ |
| Product analytics | PostHog | `POSTHOG_API_KEY`, `POSTHOG_HOST` | _yes/no_ |
| Payments | Stripe | `STRIPE_API_KEY` | _yes/no_ |
| Banking | Mercury | `MERCURY_API_KEY` | _yes/no_ |
| CRM | Attio | `ATTIO_API_KEY` | _yes/no_ |
| Booking | Cal.com | `CAL_API_KEY` | _yes/no_ |
| Support | Plain | `PLAIN_API_KEY` | _yes/no_ |
| Lifecycle email | Loops | `LOOPS_API_KEY` | _yes/no_ |
| Transactional email | Resend | `RESEND_API_KEY` | _yes/no_ |
| Knowledge base | Notion | `NOTION_API_KEY` | _yes/no_ |
| Calendar | Google Calendar | `GOOGLE_CALENDAR_*` | _yes/no_ |
| Inbox | Gmail | `GMAIL_*` | _yes/no_ |
| Delivery (chat) | Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | _yes/no_ |

## Decisions log

Append to `~/.hermes/business/journal/decisions.md` whenever you make a non-trivial
call. Format: date, the decision, what you decided against, expected outcome,
review date. The CEO skill reads the last 30 days of decisions before any weekly
or monthly review.
