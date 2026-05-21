# Product Department Brief

## Scope

Decide what to build and what not to build. Translate customer pain into specs.
Measure whether what we shipped actually moved the metric we built it for.

## What "good" looks like

- The roadmap is three columns: Now (1 thing), Next (3 things), Later (everything else).
- Every "Now" item has a clear user pain, a hypothesis, and a measurable success criterion *before* engineering starts.
- 60%+ of shipped features have measurable adoption within 30 days. Below 40%, we're guessing.
- Top 10 customer requests are visible at a glance and updated weekly.

## Tools we use

- **PostHog** (`POSTHOG_API_KEY`) — events, funnels, retention cohorts, session replay.
- **Linear** (`LINEAR_API_KEY`) — specs live as Linear issues with the `spec` label.
- **Notion** (`NOTION_API_KEY`) — long-form PRDs and research notes.
- **Plain** (`PLAIN_API_KEY`) — customer requests, tagged with `feature-request`.

## Weekly questions the agent answers

1. What got shipped? What's the early signal — adoption, complaints, silence?
2. What's the top 5 unsolicited request from customers this week?
3. Which feature shipped in the last 90 days has the lowest adoption? Why?
4. Where is the funnel leaking? (signup → activation → first-value → paid)
5. Which experiments are running? Which should be ended?

## Spec template (the agent uses this when drafting specs)

```
## Problem
One paragraph. Who hurts, why, when, and how often.

## Evidence
Links to: customer quotes, PostHog funnel, support tickets, sales-lost reasons.
Anything but our internal hunches.

## Hypothesis
We believe that [change] will cause [outcome] because [reason].
We'll know we're right when [metric] moves to [number] within [time].

## Sketch
A drawing, a screenshot, or pseudocode. Not a Figma file unless the design is the point.

## Out of scope
The five adjacent things we considered and explicitly cut.

## Risks
What could break, what could surprise us, what we're not sure about.
```

## Standing rules

- **No spec without a metric.** If we can't measure success, we don't ship it.
- **Kill, don't iterate.** If a feature is under 20% adoption after 90 days, sunset it. Carrying dead weight slows everything down.
- **Customer quotes beat internal opinions** in any priority dispute. Bring receipts.
- **Roadmap is public to customers** (subset of it). Vote count visible. Honesty earns trust.

## Inputs to the daily brief

- Net new signups (24h).
- Signups → activated within 1 hour rate (today's cohort).
- Top new feature requests from support overnight.
- Any PostHog cohort that crossed a target.
