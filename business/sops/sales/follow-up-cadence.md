# SOP: Follow-Up Cadence

Drives the daily 8am `daily-sales-followups` cron. Every follow-up is a
DRAFT to `#sales`.

## Pipeline stages

```
lead → qualified → demo-scheduled → demo-done → proposal → closed-won
                                                          ↘
                                                           closed-lost
```

## Cadence

| Trigger | Day | Action |
|---|---|---|
| qualified, no demo booked | T+2 | DRAFT: "still interested? here are slots" |
| demo-scheduled | T-1 (24h before) | Run `sops/sales/demo-prep.md` |
| demo-done | T+1 | DRAFT: thank-you + recap + next step |
| demo-done | T+3 | DRAFT: "any questions from the demo?" |
| demo-done | T+7 | DRAFT: a relevant resource (case study, blog) |
| demo-done | T+14 | DRAFT: explicit "should we park this or move forward?" |
| proposal sent | T+3 | DRAFT: gentle nudge |
| proposal sent | T+7 | DRAFT: hard nudge with a decision deadline |
| no reply by T+21 from proposal | — | Move to `closed-lost`, DRAFT a "we're here when ready" note |

## Rules

- One DRAFT per prospect per day max — collapse if multiple triggers hit.
- Reference something specific from the demo or prior conversation. No
  generic "just checking in."
- The next-step ask is concrete and time-bound. "Can you reply by Friday
  with a yes/no on a 2-week pilot?"
- After 3 ignored follow-ups, stop and move to `closed-lost`. Don't be the
  person who emails 8 times.

## Output

A single post to `#sales` each morning listing all DRAFTS for the day,
grouped by prospect. Founder reacts `:approve:` per email.
