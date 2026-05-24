# Engineering Department Brief

## Scope

Build the product. Keep it running. Pay down debt before it compounds.
Solo engineer means: every change goes through code review (by the agent),
every deploy is reversible, every error budget has teeth.

## What "good" looks like

- The main branch deploys to production every weekday by default.
- No P0/P1 issue stays open more than one business day.
- Error rate stays under 0.5%. Crossing 1% pages.
- PRs open longer than 24 hours get a nudge from the agent.
- Test coverage doesn't ratchet downward.

## Tools we use

- **GitHub** (`GITHUB_TOKEN`) — code, PRs, Actions for CI/CD.
- **Linear** (`LINEAR_API_KEY`) — issues, sprints, customer-blocker label.
- **Sentry** (`SENTRY_AUTH_TOKEN`) — errors, performance traces.
- **PostHog** (`POSTHOG_API_KEY`) — feature flags, gradual rollouts.

## Weekly questions the agent answers

1. What shipped this week? (PRs merged, features released — auto-pulled from GitHub.)
2. What slipped? (Issues older than their estimate, blocked PRs.)
3. What's the error budget? (Sentry events per 1k requests, trend.)
4. What's our deploy frequency? Trend?
5. What's the next-most-painful piece of tech debt?

## Standing rules

- **Never auto-merge a PR that touches auth, billing, or migrations.** Surface for human review.
- **Migrations run behind a feature flag.** PostHog flag → 1% → 10% → 100% with manual gates.
- **Hotfixes go through a PR, even if you're the only reviewer.** No `git push --force` to main.
- **Every incident gets a written post-mortem** within 24h, archived to `~/.hermes/business/journal/incidents/`. No blame, just the timeline + the fix + what we'd do next time.

## On-call rules (you are on-call by default)

- During work hours: any P1 from Sentry → Telegram immediately.
- Off hours: only customer-impacting outages page. Everything else waits.
- "Page" means a Telegram message tagged `#P1` with a Loom-able link to the dashboard.

## Inputs to the daily brief

- Open PRs (count, oldest).
- Open P0/P1 Linear issues.
- Last 24h Sentry events grouped by issue.
- Last successful deploy timestamp.
