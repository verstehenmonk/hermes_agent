---
name: business-os-engineering
description: "Solo-founder engineering: sprint planning, code review, deploys, on-call triage, technical debt tracking. Agent-assisted, founder-approved."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: [GITHUB_TOKEN, LINEAR_API_KEY]
  commands: [git, gh, curl]
metadata:
  hermes:
    tags: [Engineering, DevOps, Code Review, Sprint Planning, On-Call, SaaS]
---

# Engineering — Solo Founder Playbook

You are the entire engineering org. The agent is your second pair of eyes, your first-pass reviewer, your on-call buddy, and your tireless backlog groomer. Use it liberally for the mechanical work. Reserve your attention for architecture, customer-impacting bugs, and "is this the right thing to build" calls.

## Cadences

| Cadence  | Activity                              | Tier   |
|----------|---------------------------------------|--------|
| Hourly   | CI status watch; alert on red main    | AUTO   |
| Daily    | PR review queue summary               | AUTO   |
| Daily    | Error tracker (Sentry/etc) triage     | DRAFT  |
| Weekly   | Sprint plan from prioritized backlog  | DRAFT  |
| Weekly   | Tech debt audit (TODO/FIXME/perf)     | AUTO   |
| Monthly  | Architecture review (drift + ADRs)    | DRAFT  |

## Sprint Planning (weekly, Mon)

1. Read `state/kpis.yaml` → find any engineering KPI off-track (uptime, p95 latency, error rate, time-to-fix).
2. Pull Linear issues:
   - `state:triage` count → if >10, propose a triage session before planning.
   - Top 20 in backlog ordered by priority + age.
3. Cross-reference with `~/.hermes/business-os/feedback/` to surface customer-asked items.
4. Generate a draft sprint:
   - **Bucket 1 (must)**: customer-impact bugs, security, SLA-critical.
   - **Bucket 2 (should)**: roadmap commitments due this sprint.
   - **Bucket 3 (could)**: tech debt, infra, paydown.
   - Capacity assumption: solo founder ships ~3 medium issues/week. Cap the plan accordingly.
5. Deliver as a markdown checklist. DRAFT — founder approves before issues move to "Up Next".

## Code Review

Every PR goes through the agent before the founder. The agent acts as a strict reviewer using the `code-review` skill conventions: reuse, quality, correctness, security.

**PR review prompt template:**

> Review PR #<N> against the engineering bar in CHARTER.md and the codebase conventions in AGENTS.md / CONTRIBUTING.md. Identify: (1) bugs, (2) security issues, (3) test gaps, (4) any reuse violations. Do NOT comment on style; the linter handles that. Output a checklist; mark each item BLOCKING or NIT.

**Auto-merge rules**: never. Even tiny PRs get a human eyeball — this is the last quality gate.

## Deploys

Two paths.

### Hot path (production)

1. Founder types `/deploy <env> <ref>`.
2. Agent runs deploy checklist (deterministic): tests green? migrations dry-run clean? feature flags set? rollback ready?
3. If any check fails → STOP, surface to founder.
4. If all checks pass → execute deploy, watch error rate for 10 minutes, post status.

### Cold path (preview / staging)

Auto-deploy on push to non-main branches. Agent posts the preview URL.

**Trust tier**: deploys are DRAFT — the agent runs the checklist but the founder presses the button. Promote to AUTO only for staging.

## On-Call Triage

Page sources: Sentry, BetterUptime, Stripe webhooks failing, customer Slack/Intercom escalations.

When a page lands (webhook → this skill):

1. Classify severity:
   - **SEV1**: customer-visible outage, payment failure, data loss risk. Page founder immediately.
   - **SEV2**: degraded perf, partial feature down, single-customer impact. DRAFT a triage note; ping if no founder action in 15 min.
   - **SEV3**: noise, known issue, transient. AUTO close with a tag.

2. For SEV1/SEV2: open a Linear issue with template `templates/post-mortem.md` pre-filled with the incident signal, related deploys, error traces, and the customer(s) affected.

3. Post a status thread the founder can drop into.

## Tech Debt

Run weekly: grep the repo for `TODO(`, `FIXME`, `XXX`, deprecated API usage, and packages >2 major versions behind. Compare to last week's count. If it grew >10%, surface a list with proposed cleanup PRs.

## Error Budget

Track in `state/kpis.yaml`:
- p95 API latency target: 800ms
- Error rate target: <0.5% of requests
- Uptime target: 99.5% monthly (≈3.6h of downtime/month is acceptable)

If error budget is >50% consumed by mid-month, the agent freezes feature work in the next sprint plan and surfaces "STABILIZE" as the must-bucket.

## Useful Commands

```bash
# Open PRs needing my review
gh pr list --search "is:open review-requested:@me"

# Linear issues in triage
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ issues(filter:{state:{type:{eq:\"triage\"}}}){ nodes{ identifier title } } }"}'

# Current week's commits
git log --since='1 week ago' --pretty=format:'%h %ad %s' --date=short
```

## Spawned Subagents

For multi-file changes, the engineering skill spawns a coding subagent with full repo context, then the founder reviews the resulting PR. Subagent prompt template:

> Implement: `<one-line description>`. Repo conventions in AGENTS.md. Tests required for new logic. Open a draft PR with a 3-section description: (1) what changed, (2) why, (3) test plan. Do NOT edit anything outside the listed files without explicitly justifying why.

## Anti-patterns

- Letting the agent merge its own PRs.
- Generating "cleanup" PRs that touch >20 files for non-cleanup work.
- Skipping the post-deploy 10-minute watch.
- Treating SEV3 as SEV2; the founder learns to ignore the channel and misses real fires.
