---
name: kpi-rollup
description: "Compose the company-wide KPI snapshot by reading business/knowledge-base/kpis.yaml and querying each source."
version: 1.0.0
author: Hermes Business OS
license: MIT
prerequisites:
  env_vars: []
  commands: [yq, jq]
metadata:
  hermes:
    tags: [KPI, Metrics, Finance, Founder Dashboard]
---

# KPI Rollup

Reads `business/knowledge-base/kpis.yaml`, queries each KPI from its
declared source, and produces a single markdown table comparing current vs.
target. Used by `weekly-review` and `monthly-close`.

## Setup

No additional setup beyond the source skills (stripe-billing, notion, github,
google-workspace). `yq` and `jq` parse YAML/JSON.

## Read the spec

```bash
yq eval . business/knowledge-base/kpis.yaml
```

Each KPI has:
- `name`: machine-readable id
- `target`: numerical target (interpret unit from name)
- `source`: where to fetch the actual value (stripe | github | notion |
  google_calendar | telemetry | cash_yaml | derived | search_console |
  himalaya | survey | ops_checklist | linear | vercel | app)

## Fetch each value

Implement one fetcher per source:

| Source | How |
|---|---|
| `stripe` | Use `stripe-billing` skill — query subscriptions, charges, events |
| `github` | `gh pr list --json` / `gh api repos/<owner>/<repo>/actions/runs` |
| `linear` | GraphQL via `linear` skill — count issues by status/label |
| `vercel` | `vercel-deploys` skill — count deploys this week |
| `notion` | Query the relevant database — Pipeline, Feedback, Customers, Vendors, Content Pipeline |
| `google_calendar` | `google-workspace` skill — count events per week, sum durations |
| `cash_yaml` | Read `business/knowledge-base/finance/cash.yaml` directly |
| `derived` | Compute from other KPIs (e.g. gross_margin from revenue - cost) |
| `search_console` | (Optional — only if you've wired Search Console API) |
| `telemetry` | (Optional — query your product analytics) |
| `survey` | Read `business/knowledge-base/cs/csat.yaml` (founder updates manually) |
| `ops_checklist` | Count green items in last security checklist post |
| `himalaya` | Compute median response time from sent items |
| `app` | Hit your app's `/admin/stats` endpoint or read a snapshot file |

## Output format

```
| KPI | Current | Target | Δ | Status |
|---|---|---|---|---|
| net_new_arr | $4,200 | $5,000 | -$800 | 🟡 |
| pr_cycle_time_hours | 18 | 24 | +6 | 🟢 |
| ...
```

Status emoji:
- 🟢 at or beyond target
- 🟡 within 20% below target
- 🔴 > 20% below target

## Quality bar

- If a source is unreachable, mark the row `?` and continue. Don't fabricate.
- Always note the timestamp the snapshot was taken.
- Cache fetched values to `~/.hermes/kpi-cache/<YYYY-MM-DD>.json` so the
  same day's weekly-review doesn't re-query everything.
