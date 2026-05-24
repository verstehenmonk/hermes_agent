---
name: engineering
description: "Engineering department: PRs, deploys, incidents, error budget."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [GITHUB_TOKEN, LINEAR_API_KEY]
  optional_env_vars: [SENTRY_AUTH_TOKEN, SENTRY_ORG, SENTRY_PROJECT, POSTHOG_API_KEY]
metadata:
  hermes:
    tags: [engineering, github, linear, sentry, deploys, code-review]
---

# Engineering — solo SaaS

On activation, read `business/departments/engineering.md` (the brief) and
`business/CHARTER.md`. Then use the tools below.

## GitHub (curl)

Auth header: `Authorization: Bearer $GITHUB_TOKEN`, `Accept: application/vnd.github+json`.

Common operations:
```bash
# List open PRs
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO/pulls?state=open&per_page=100"

# Get a PR diff (text)
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3.diff" \
  "https://api.github.com/repos/$GITHUB_REPO/pulls/$N"

# Post review comment
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_REPO/pulls/$N/reviews" \
  -d '{"event":"COMMENT","body":"..."}'
```

When the gh CLI is available, prefer it — it handles auth and pagination cleanly.

## Linear (GraphQL)

See `skills/productivity/linear/SKILL.md` for the full skill; use it as a reference.

Quick patterns:
```graphql
# Open P0/P1
query { issues(filter: {priority: {lte: 2}, state: {type: {nin: ["completed","canceled"]}}}) { nodes { id identifier title url } } }

# Customer blockers
query { issues(filter: {labels: {name: {eq: "customer-blocker"}}}) { nodes { id identifier title url assignee { name } } } }

# Create issue
mutation { issueCreate(input: {teamId: "...", title: "...", description: "...", labelIds: ["..."], priority: 2}) { success issue { url } } }
```

## Sentry

```bash
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/?statsPeriod=24h&query=is:unresolved&limit=20"
```

## Code-review protocol (when a webhook fires on PR opened)

1. Fetch the diff.
2. Check against engineering brief's tech principles. Pay attention to:
   - Auth, billing, migration code → flag for human review, no auto-merge.
   - Tests reduced or removed → ask why.
   - Hard-coded secrets, API keys, customer data in fixtures → block.
   - New dependencies → flag the addition + ask "why not existing X?"
3. Post one comment with structured feedback: blockers, suggestions, nits.
4. Don't approve. Don't block on style. Don't be pedantic.

## Incident protocol (when Sentry pages or a customer reports an outage)

1. Open an incident file via `business/scripts/journal.py incident --title "..."`.
2. Capture the timeline as you go (you append; the file is human-readable).
3. Triage: severity, who's affected, how many, business impact.
4. Communicate: customer-facing status update if P1.
5. Mitigate, then fix. Mitigation first.
6. Post-mortem within 24h: timeline, root cause, fix, what would've prevented it. No blame.

## Standing prohibitions

- Never push to main directly. Open a PR even when you're the only reviewer.
- Never auto-merge anything touching auth, billing, or migrations.
- Never `git push --force` to a shared branch.
- Never disable CI to ship a hotfix faster — fix CI in the same PR.
