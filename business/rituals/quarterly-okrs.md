# Quarterly OKR Ritual

Runs on the first Monday of a new quarter at 09:00 local.

## Inputs

- Last quarter's CHARTER three bets.
- All 12+ weekly journals from the last quarter.
- The last three monthly closes.
- The decisions log for the quarter.

## Sequence

1. CEO skill reads everything above.
2. Drafts a quarterly review email with two halves:
   - **Score last quarter** — each of the three bets scored 0.0–1.0 with evidence.
   - **Propose next quarter** — three new bets with rationale, the metric each moves, the one risk each carries.
3. Sends to founder. Does NOT auto-update `CHARTER.md`.
4. Posts to Telegram: "Quarterly draft sent. Edit CHARTER.md when you've decided. I'll switch contexts when you push the change."

## Email structure

```
Subject: Q{N} {YYYY} review + Q{N+1} draft

QUARTER REVIEW

Bet 1 — {original bet text}
  Score: 0.X
  Evidence: {2–3 bullet points with data}
  What we'd do differently: {1 sentence}

Bet 2 — ...
Bet 3 — ...

Bets total: X / 3.0
Overall theme: {one-line read on the quarter}

WHAT THE DATA SAYS HAPPENED

  Revenue:    $X → $X     (Δ ±X%, on/off target)
  Customers:  N → N       (Δ ±N)
  WAW:        N → N       (Δ ±N)
  Cash burn:  $X/mo avg
  Runway:     N → N months

LESSONS LOGGED (from the decisions journal)
  - {decision} → {what happened} → {takeaway}
  - ...

PROPOSED NEXT QUARTER

These three bets pull from the open questions across the last 13 weeks
of weekly reviews — see below for traceability.

Bet 1 — {one sentence, with a verb and a number}
  Why: {1–2 sentences}
  Metric: {single metric that proves it}
  Risk: {one sentence}
  Pulled from: {weekly-review references}

Bet 2 — ...
Bet 3 — ...

OPEN QUESTIONS WE DIDN'T PROMOTE TO BETS
{the runners-up, parked for the quarter after next}

CALENDAR SHAPE FOR THE QUARTER
{milestones, conferences, board meetings, holidays, key deadlines}
```

## Rules for the agent

1. **Score honestly.** A 0.6 isn't a failure; a 1.0 every quarter means the bets were too small.
2. **Three bets, never more.** If the agent proposes 4+, force a cut.
3. **Each bet needs a metric.** "Improve onboarding" is not a bet. "Get 7-day activation to 60%" is.
4. **The agent NEVER writes to CHARTER.md.** The founder edits CHARTER.md after deciding. The CEO skill watches for that change and re-orients departments.
