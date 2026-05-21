# Operating Cadence

> What runs when, and what each ritual produces. Codified in `cron.yaml`.

## Daily

**07:30 weekdays — Daily brief** (Telegram)
1. `scripts/metrics_snapshot.py` writes `~/.hermes/business/metrics/latest.json`.
2. `scripts/inbox_digest.py` categorizes overnight email into [urgent / customer / sales / vendor / noise].
3. `ceo` skill reads CHARTER + metrics + inbox + yesterday's standup note, drafts:
   - 3 numbers that matter (MRR, WAW, error rate, with deltas)
   - 3 things in the inbox that need *you* (everything else routed/drafted)
   - Top 3 priorities for today, pulled from the active quarter's bets
   - One sentence: "Watch out for ___ today."
4. Posted to Telegram. Archived at `~/.hermes/business/journal/YYYY-MM-DD-standup.md`.

**Every 2h, work hours — Inbox sweep** (Telegram, only if something needs you)
- Customer issues → `customer-success` skill triages and drafts replies.
- Sales inbound → `sales` skill qualifies, drafts a reply, books the demo.
- Vendor/admin → `operations` skill files them.
- Anything else → silent unless it scores P1.

**18:00 weekdays — End-of-day wrap** (Telegram, brief)
- What got shipped today (PRs merged, content published, customers closed).
- What slipped (PRs open > 24h, unresolved P1s).
- Tomorrow's pre-loaded priorities (rolled forward).

## Weekly

**Friday 16:00 — Weekly review** (Email, long-form)
- Each department skill writes a one-page section. The `ceo` skill assembles.
- Sections: Numbers, Wins, Slips, Decisions made, Open questions, Next week's bets.
- Sent to your email. Archived at `~/.hermes/business/journal/YYYY-WW-weekly.md`.

**Monday 09:00 — Week kickoff** (Telegram)
- The three bets for the week, derived from the quarter's three bets.
- Pre-staged calendar review (meetings, focus blocks).

## Monthly

**1st of month 09:00 — Monthly close** (Email)
- `finance` skill: MRR walk, burn, runway, gross margin, CAC payback.
- `product` skill: monthly cohort retention, feature adoption, top requests.
- `engineering` skill: incidents, SLO compliance, tech debt trends.
- `marketing` skill: traffic, conversion funnel, content performance.
- `ceo` skill: monthly narrative, what changed, what to watch.

**1st of month — Vendor + tools audit**
- `operations` skill lists all recurring charges from Mercury.
- Flags anything unused (no API hits in 30d) for cancellation review.

## Quarterly

**First Monday of new quarter — OKR review** (Email)
- Score last quarter's three bets honestly (0–1 per bet).
- Draft next quarter's three bets, pulling from open questions in the weekly journals.
- Update `CHARTER.md` ("Three bets this quarter").

**Quarterly — Compliance + legal check** (Email)
- `legal` skill audits: contracts up for renewal, ToS/PP last reviewed, DPA requests fulfilled, SOC 2 evidence collected.

## Event-driven (webhooks)

| Event | Handler | Action |
|---|---|---|
| Stripe `invoice.payment_failed` | `finance` | Retry once, email customer, alert if > $X |
| Stripe `customer.subscription.deleted` | `customer-success` | Send churn survey, log reason |
| Sentry alert: error rate > 1% | `engineering` | Triage, page if not self-healing in 15min |
| GitHub PR opened | `engineering` | Auto-review against CHARTER's tech principles |
| Linear issue label `customer-blocker` | `customer-success` + `engineering` | Page, prioritize |
| Cal.com booking created | `sales` | Pre-brief: research the prospect, draft demo plan |
| New paid signup (PostHog `subscription_started`) | `customer-success` | Send welcome, schedule onboarding check-in |

## Quiet hours

Outside 09:00–18:00 weekdays America/New_York, only P1 alerts page you on Telegram.
Everything else queues for the morning brief.
