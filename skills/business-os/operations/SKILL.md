---
name: business-os-operations
description: "Solo-founder operations: vendor management, runbooks, incident response, SOC2-lite compliance, business continuity."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  env_vars: []
  commands: [curl, python3]
metadata:
  hermes:
    tags: [Operations, Runbooks, Incident Response, Compliance, Vendors, SaaS]
---

# Operations — Solo Founder Playbook

Operations for a solo founder is mostly "don't let the lights go off". The agent's job is to maintain the runbook library, watch vendor health, drive incident response, and keep the compliance posture good enough to close mid-market deals.

## Cadences

| Cadence  | Activity                                  | Tier   |
|----------|-------------------------------------------|--------|
| Daily    | Vendor status page check                  | AUTO   |
| Weekly   | Runbook freshness audit                   | AUTO   |
| Weekly   | Compliance task review                    | DRAFT  |
| Monthly  | Vendor spend audit (with finance)         | DRAFT  |
| Per incident | Incident response + post-mortem       | DRAFT  |
| Quarterly | Business continuity drill                | DRAFT  |
| Annually | SOC2 / ISO27001 readiness gap analysis    | DRAFT  |

## Vendor Inventory

Tracked in `state/vendors.yaml` (the agent maintains it). For each vendor:
- Name, category (infra, payments, support, etc.).
- Monthly cost, contract end date.
- Criticality (P0 = customer-facing outage if down; P3 = nice-to-have).
- Status page URL.
- Account owner (always the founder; for completeness).
- Last login date (helps spot unused tools).

The list is the source of truth for the monthly spend audit.

## Status Page Monitoring (AUTO)

Every hour, pre-processor checks every P0/P1 vendor's status page (Stripe, AWS, Linear, GitHub, Intercom, Resend, OpenRouter, etc.).

If ANY vendor reports incident:
- AUTO log to `~/.hermes/business-os/vendor-incidents/`.
- If P0 vendor: ping founder immediately + check if our service degrades.
- If multi-vendor outage: orchestrator alerts founder ("you might want to post a status update").

## Runbooks

Stored as `~/.hermes/business-os/runbooks/<name>.md`. Use `templates/runbook.md`.

**Required runbooks** (the agent ensures these exist):

| Runbook                                  | Purpose                                            |
|------------------------------------------|----------------------------------------------------|
| `deploy-prod.md`                         | Step-by-step prod deploy + rollback                |
| `restore-from-backup.md`                 | Database restore procedure                         |
| `stripe-payment-stuck.md`                | Diagnose stuck/failed payments                     |
| `customer-data-export.md`                | GDPR export request flow                           |
| `customer-data-delete.md`                | GDPR deletion request flow                         |
| `incident-response.md`                   | First 30 minutes of any sev1                       |
| `onboarding-new-customer.md`             | Manual onboarding for high-touch deals             |
| `domain-key-rotation.md`                 | Rotate signing keys, API tokens                    |
| `secrets-leak.md`                        | What to do if a secret hits a public repo          |
| `founder-unavailable.md`                 | What the agent should do if founder is offline >24h|

**Freshness audit (weekly, AUTO)**: agent checks each runbook's last-touched date and last-successful-execution date. If a runbook hasn't been touched in 6 months AND hasn't been executed in 12, flag for review.

## Incident Response

When `engineering` skill declares SEV1/SEV2, ops takes over the coordination:

1. **T+0**: open incident channel (Slack / Discord), post initial status: what we see, what we don't yet know, ETA for next update.
2. **T+15**: status update to status page (auto-publish via Statuspage/Instatus API).
3. **T+30**: customer comms decision — if user-visible, send proactive email to affected accounts.
4. **Throughout**: timestamped log to `~/.hermes/business-os/incidents/YYYY-MM-DD-<slug>.md`.
5. **Resolution**: status page resolved, all-clear email.
6. **T+24h**: agent drafts post-mortem using `templates/post-mortem.md`. Founder reviews. If customer-visible, publish externally.

**Post-mortem rules**:
- Blameless (no team to blame anyway — it's a solo founder).
- Five whys minimum.
- One concrete preventive action per root cause, with an owner (founder) and due date.
- Posted publicly if customer-visible OR internally if not.

## Compliance (SOC2-Lite)

Mid-market deals will ask for SOC2. You probably don't have it yet. The agent maintains a "SOC2 readiness" checklist in `~/.hermes/business-os/compliance/soc2-readiness.md`.

Tracked items:
- Access control: MFA on all critical systems (verify monthly).
- Vendor due diligence: per `state/vendors.yaml`, do we have a DPA / sub-processor agreement?
- Encryption: at rest + in transit, verified annually.
- Backup + DR: backups tested quarterly.
- Incident response: process documented in runbook (this skill).
- Code review: enforced via GitHub branch protection (verify monthly).
- Vulnerability management: dependabot enabled + alerts triaged within 7 days.
- Customer data isolation: tenancy model documented.

For deals that require SOC2 today, use Vanta/Drata partner. For deals worth >$50k ARR, the agent recommends pulling the trigger on a formal program.

## Vendor Spend Audit (monthly with finance)

Pre-processor pulls last 30 days of card statements. Cross-reference against `state/vendors.yaml`.

Output:
- Top 10 expenses by category.
- Vendors used <5 times this month (cancel candidates).
- Free tier breaches that auto-billed (consolidate or downgrade).
- Annual contracts renewing in next 60 days (negotiate).
- "New mystery charge" alerts.

## Business Continuity

What if the founder goes offline for a week?

- `templates/runbook.md` → `founder-unavailable.md` defines:
  - Auto-replies on email, support, social.
  - Critical alerts that should still page (server down, payment failure spike, security incident).
  - Agent's authority during the period (auto-approve known-good support drafts, file but don't ship code, pause outbound).
  - Customer SLA adjustments and communication.

Drill: quarterly, founder takes a 24h scheduled offline period and the agent's "founder-unavailable" path is tested for real.

## Anti-patterns

- Runbooks that are never executed. They rot. Test annually at minimum.
- Compliance checklists without dates. The agent stamps every item with last-verified date.
- Single-vendor lock-in for P0 services without a documented "what if they're down for 24h" plan.
- Ignoring sub-processor agreements until a customer asks. (Then it's a fire drill.)
