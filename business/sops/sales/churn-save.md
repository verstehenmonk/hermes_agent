# SOP: Churn Save

Triggered when CFO flags a downgrade or cancellation request, or CS scores a
customer's sentiment ≤ -1 with billing health degrading.

## Step 1 — Hypothesize root cause

Read in this order:
- Last 5 support tickets from this customer
- Usage telemetry: was core feature usage flat / declining for the last 30
  days?
- Plan history: did they recently downgrade? When?
- Industry: did something change in their market that reduces our value
  prop?

Pick the single most likely cause. Label confidence: high | medium | low.

## Step 2 — Save plan options

Produce three options ranked by cost:
1. **Education** — schedule a 30-min call, walk through the feature they're
   not using
2. **Discount / extend** — propose specific terms (e.g. "20% off for 3
   months while we ship X")
3. **Pause** — let them pause for 60 days with data preserved

Each option lists: cost to us, likelihood of save (low/med/high), what we
commit to deliver.

## Step 3 — Conversation script

Draft a script for the save call, with:
- Open: empathy + specific reference to their situation
- Probe: 3 questions to confirm or deny the root cause hypothesis
- Pivot: based on confirmed cause, which option to lead with
- Close: explicit next step + commitment

## Step 4 — Escalate

Post all of the above to `#sales` and DM the founder. The founder runs the
save call personally. Never auto-email a save offer.
