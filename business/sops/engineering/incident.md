# SOP: Incident Response

Triggered by Vercel/Fly alert webhook or manual `/incident <description>` in
`#alerts`. Run as `head-of-engineering` with `max_turns: 25`.

## Step 1 — Acknowledge in 60 seconds

- Post to `#alerts`: "Incident ACK <timestamp>. Investigating."
- Open a Linear issue: title `[INC] <one-line summary>`, severity
  derived from alert (SEV1 = customer-facing down, SEV2 = degraded, SEV3 =
  internal-only, SEV4 = noise).
- Create a timeline entry in the Linear issue description with the alert
  payload pasted verbatim.

## Step 2 — Triage

- `vercel-deploys`: check last 5 deploys for the affected project — when did
  it start, what shipped just before?
- `flyio-status`: check Fly app status, last restart, resource metrics.
- Read recent logs (Vercel or Fly) for error patterns.
- Cross-check: did a dependency outage happen? (Quick Twitter/X search via
  xurl for "Vercel status" / "Fly status" / Stripe / Anthropic / etc.)

## Step 3 — Communicate

If SEV1 or SEV2:
- Post status update to `#alerts` every 15 minutes — even if it's "still
  investigating, no new info."
- Draft a customer-facing status page update (if you have one) — emit as
  DRAFT per `sops/_shared/approval-gate.md`.

## Step 4 — Resolve

- If the cause is a recent deploy: propose a rollback via `vercel-deploys`.
  Do NOT execute the rollback — escalate to founder with the exact command.
- If the cause is a dep outage: post the upstream's status link and ETA.
- If the cause is unknown after 30 minutes: escalate to founder by DM. State
  what you tried, what failed, what you'd try next.

## Step 5 — Postmortem

After resolution, append to the Linear issue:
- Timeline of events with timestamps
- Root cause
- Detection gap (how long from impact to alert?)
- Action items: file each as a separate Linear issue, link in postmortem.

Never close an incident issue until the postmortem is filled.
