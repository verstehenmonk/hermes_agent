# North Star & Metrics

> Source of truth for what we measure. `scripts/metrics_snapshot.py` pulls live
> numbers and writes them to `~/.hermes/business/metrics/latest.json`. Every
> ritual reads that file rather than asking the agent to compute numbers.

## Headline metric

**Weekly active workspaces (WAW)** — distinct workspaces with ≥1 active user
that performed ≥1 core action in the last 7 days.

- Why this: it leads revenue by ~30 days and is hard to game.
- Source: PostHog event `core_action_completed`, deduped by `workspace_id`.
- Computed by `scripts/metrics_snapshot.py` using a `unique_group` math
  aggregation on the `workspace_id` PostHog group type. Result exposed at
  `posthog.waw` in `~/.hermes/business/metrics/latest.json`.
- Current: _filled by metrics_snapshot.py_
- 90-day target: _your number_

## Tier 1 — health (review weekly)

| Metric | Source | Why |
|---|---|---|
| **MRR** | Stripe | Headline revenue |
| **Net new MRR** | Stripe (new - churn - contractions + expansions) | True growth signal |
| **Logo churn (30d)** | Stripe | Are we leaking? |
| **Net revenue retention (NRR)** | Stripe | Are accounts expanding? |
| **WAW** | PostHog | Engagement |
| **Activated workspaces / new signups (7d)** | PostHog | Onboarding effectiveness |
| **P95 latency (API)** | PostHog or your APM | UX quality |
| **Error rate** | Sentry | Stability |

## Tier 2 — pipeline (review weekly)

| Metric | Source |
|---|---|
| New qualified leads (7d) | Attio |
| Demos booked (7d) | Cal.com |
| Demo → won conversion (rolling 30d) | Attio |
| Open opps + weighted pipeline | Attio |
| Avg sales cycle | Attio |

## Tier 3 — marketing (review weekly)

| Metric | Source |
|---|---|
| Unique visitors (7d) | Plausible / PostHog |
| Top 5 entry pages | Plausible / PostHog |
| Trial signups → activated (7d) | PostHog |
| Content shipped (7d) | Manual / Notion |
| Newsletter list size + open rate | Loops or Resend |

## Tier 4 — engineering (review weekly)

| Metric | Source |
|---|---|
| PRs merged (7d) | GitHub |
| Mean PR open → merge time | GitHub |
| Open P0/P1 issues | Linear |
| Sentry events per 1k requests | Sentry + PostHog |
| Deploy frequency | GitHub Actions |
| Mean time to recovery | Sentry / manual |

## Tier 5 — finance (review monthly)

| Metric | Source |
|---|---|
| Cash on hand | Mercury |
| Burn (3-mo trailing) | Mercury |
| Runway (months) | Mercury |
| Gross margin | Stripe + cost spreadsheet |
| CAC (paid) | Ad spend / new customers |
| Payback period (months) | CAC / ARPU·margin |
| LTV/CAC | (ARPU·margin / churn) / CAC |

## Thresholds that trigger an alert

These become entries in `webhooks.yaml` or `cron.yaml` health-check jobs.

- **Burn jumps > 25% MoM** → finance skill drafts an investigation.
- **MRR drops day-over-day** → finance skill checks for failed payments, churn events.
- **Error rate > 1%** for 15 minutes → engineering skill pages.
- **No new signups for 48h** during work hours → product skill investigates funnel.
- **Demo no-show rate > 30% in a week** → sales skill investigates the booking flow.
- **Cash runway drops below 6 months** → CEO skill drafts an action plan.
- **Any P1 customer issue open > 4h during work hours** → CS skill pages.
