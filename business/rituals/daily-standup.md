# Daily Standup Ritual

Runs weekdays at 07:30 local. Cron job calls the `ceo` skill with this prompt.

## Inputs

- `~/.hermes/business/metrics/latest.json` (written by `scripts/metrics_snapshot.py` 5 minutes earlier)
- `~/.hermes/business/inbox/latest.json` (written by `scripts/inbox_digest.py` 5 minutes earlier)
- Yesterday's standup at `~/.hermes/business/journal/<yesterday>-standup.md` (if exists)
- The current quarter's three bets from `business/CHARTER.md`

## Output (Telegram message + journal file)

```
☤ Morning brief · {weekday} {date}

NUMBERS
  MRR     $X (Δ +$Y, +Z% / day)
  WAW     N  (Δ +M / week)
  Errors  N events · 0.X% rate
  Cash    $X  ·  Runway: N months

NEEDS YOU
  1. {single sentence on what needs founder judgment, with link}
  2. ...
  3. ...
  (nothing else needs you — N items routed/drafted, see /inbox)

TODAY
  → {priority 1, tied to a quarter bet}
  → {priority 2}
  → {priority 3}

HEADS UP
  {one sentence on something brewing — could be a metric trend,
   a customer at risk, a deadline approaching}
```

If everything's quiet, the message is shorter. Be calibrated, don't pad.

## Rules for the agent

1. **Numbers come from `metrics/latest.json`.** Never compute them yourself.
2. **"Needs you" is the highest-value section.** Anything in here should be a decision only the founder can make. Everything else gets handled or drafted.
3. **"Today" priorities ladder up to the quarter's three bets.** If a priority can't be tied to a bet, ask whether it should be.
4. **"Heads up" is one sentence.** Trend, not noise. Don't list everything.
5. **Archive the brief** to `~/.hermes/business/journal/<date>-standup.md` immediately after sending.
6. **Compare to yesterday's brief.** If yesterday flagged "watch out for X" and X happened, lead with it today.
