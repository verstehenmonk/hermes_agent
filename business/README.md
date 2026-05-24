# Hermes Business OS

An AI-run business bundle for a solo founder, layered on top of
[Hermes Agent](https://github.com/NousResearch/hermes-agent). Everything in this
directory is **data + config**, never a fork of Hermes core. The bundle gives
you eight department personalities, a Chief-of-Staff orchestrator, deterministic
cron cadences, event-driven webhook handlers, and a knowledge base that every
agent turn reads from.

## What you get

| Layer | Lives in | Purpose |
|---|---|---|
| Personalities | `personalities/` | One overlay per department + Chief of Staff |
| SOPs | `sops/` | Deterministic playbooks the agent loads at runtime |
| Cron jobs | `cron-templates/` | Daily/weekly/monthly cadences with model + toolset pinning |
| Webhook handlers | `webhook-templates/` | Event-driven responses (PRs, support, Stripe, deploys) |
| Knowledge base | `knowledge-base/` | Company, product, KPIs, runbook — symlinked into AGENTS.md |
| Custom skills | `skills/` | Only what stock Hermes skills don't cover (Stripe, Vercel, Fly, KPI rollup) |
| Slack map | `slack/channels.yaml` | Which channel each personality posts to |
| Tests | `tests/smoke.sh` | End-to-end harness with fixtures |

## Install

```bash
cp business/.env.example business/.env       # fill in API keys
./business/bootstrap.sh                       # idempotent installer
hermes gateway setup                          # wire Slack
hermes gateway start                          # start receiving
```

`bootstrap.sh` merges personalities into `~/.hermes/cli-config.yaml`, installs
cron templates into `~/.hermes/cron/jobs.json`, registers webhook routes in
`~/.hermes/webhook_subscriptions.json`, and symlinks `knowledge-base/` into the
workspace `AGENTS.md` so every turn has the company context.

## Use

- `/personality chief-of-staff` in Slack `#cos` — talk to your Chief of Staff
- `/personality head-of-engineering` — review a PR, plan a release
- `hermes cron list` — see every scheduled job and its next run
- `hermes cron run-now <name>` — fire any job manually
- All customer-facing outputs are emitted as **DRAFTS**. React `:approve:` in
  Slack to send.

## Rollout

Don't enable everything at once. Recommended order:

1. **Day 1 (half a day):** Chief-of-Staff + Engineering. Get `pr-review`
   webhook + `daily-eng-standup` cron firing.
2. **Day 2–3:** Customer Success. `support-email-in` + `daily-cs-triage`.
3. **Week 2:** Sales + Marketing (DRAFT-only — no outbound autonomy).
4. **Week 3:** CFO + Stripe webhooks + `monthly-close` + `daily-burn-snapshot`.
5. **Week 4:** Ops, `weekly-review` with full KPI rollup, founder cockpit.

`manifest.yaml` controls which phase is active.

## Cost containment

Every cron and webhook pins `model` explicitly:

| Cadence | Model | Why |
|---|---|---|
| Hourly monitors | Haiku / DeepSeek | Cheap; usually returns `[SILENT]` |
| Daily triage / standups | Sonnet | Right size for routine reasoning |
| Weekly review / incidents | Opus | High-stakes cross-department reasoning |

Track spend with `hermes cron usage`.

## Guardrails

- Every customer-facing SOP includes `sops/_shared/approval-gate.md` — output
  ends with `[DRAFT — react :approve: in #channel to send]`.
- `enabled_toolsets` is scoped per job. The CFO can't push code; the Head of
  Engineering can't email customers.
- Webhook handlers cap at `max_turns: 15`.
- Secrets stay in `~/.hermes/secrets/`, never in this repo.
