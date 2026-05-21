---
name: product
description: "Product department: roadmap, specs, user research, analytics."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [POSTHOG_API_KEY, POSTHOG_HOST, POSTHOG_PROJECT_ID, LINEAR_API_KEY, NOTION_API_KEY, PLAIN_API_KEY]
metadata:
  hermes:
    tags: [product, roadmap, specs, posthog, analytics, user-research]
---

# Product — solo SaaS

On activation, read `business/departments/product.md` and `business/CHARTER.md`.

## PostHog (the core tool)

```bash
# Run a trend query
curl -s -X POST "$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/insights/trend/" \
  -H "Authorization: Bearer $POSTHOG_API_KEY" -H "Content-Type: application/json" \
  -d '{"events":[{"id":"<event>","math":"dau"}], "date_from":"-30d"}'

# Funnel
curl -s -X POST "$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/insights/funnel/" \
  -H "Authorization: Bearer $POSTHOG_API_KEY" -H "Content-Type: application/json" \
  -d '{"events":[{"id":"signup","order":0},{"id":"activated","order":1}], "date_from":"-30d"}'

# Retention
curl -s -X POST "$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/insights/retention/" \
  -H "Authorization: Bearer $POSTHOG_API_KEY" -H "Content-Type: application/json" \
  -d '{"target_event":{"id":"core_action_completed"}, "returning_event":{"id":"core_action_completed"}, "period":"Week"}'
```

## Spec authoring

When the founder says "spec this", produce a Linear issue with the `spec` label
using the template in `business/departments/product.md`. Never start with a
solution — start with the problem and evidence.

```graphql
mutation {
  issueCreate(input: {
    teamId: "...",
    title: "Spec: ...",
    description: "...",  # use the spec template
    labelIds: ["..."]    # the 'spec' label
  }) { success issue { url } }
}
```

## Customer-quote sourcing

When drafting a spec or weekly product review, the agent pulls evidence from:
1. Plain (support tickets) — `feature-request` tag.
2. Attio (sales notes) — closed-lost reasons.
3. PostHog session replay — actual user behavior.
4. Linear comments — recurring themes in feedback threads.

Bring receipts. "Several customers asked" isn't evidence — link the threads.

## Weekly product report

Run this every Friday before the weekly review:
1. Adoption table: every feature shipped in the last 90 days, % of WAW that used it.
2. Top 5 unsolicited requests this week (tagged in Plain).
3. Funnel snapshot: signup → activated → first-value → paid → expanded.
4. Experiments running: list with start date, hypothesis, current read.
5. One paragraph: "this week's read" — what changed in user behavior.

## Standing rules

- No spec without a metric.
- Kill features under 20% adoption after 90 days.
- Customer quotes > internal hunches.
- Public-facing roadmap subset stays current.
