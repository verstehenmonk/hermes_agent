# SOP: Daily Burn Snapshot

Runs at 7am daily via `daily-burn-snapshot` cron. Use the cheapest model
(Haiku / DeepSeek) — this is a monitor, not a reasoning task.

## Pull

- Yesterday's MRR delta from Stripe (new + expansion - contraction - churn)
- Yesterday's spend total from the latest CSV in `knowledge-base/finance/`
- Current cash from `knowledge-base/finance/cash.yaml`
- Trailing-30 burn = sum of last 30 days' spend
- Runway = cash / (trailing-30 / 30)

## Default output (1 line)

```
[BURN] cash $X | MRR Δ $±Y | 30d burn $Z | runway W months
```

## Escalate to full report when

- Runway dropped > 1 month vs. last week
- Net MRR delta < -2% of MRR
- Single spend item > $1000 in 24h (likely vendor double-bill or cloud
  spike)
- Cash < 6 months of trailing burn

Full report goes to `#finance` AND DMs founder, with:
- What triggered the escalation
- The component that drove it
- Recommended action (cut, raise, ignore — pick one)

## Quiet mode

If none of the escalation triggers fire and runway is healthy, emit
`[SILENT]` — Slack delivery suppresses the post entirely. Don't be noisy.
