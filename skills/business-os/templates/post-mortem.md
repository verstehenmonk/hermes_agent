# Post-mortem: <INCIDENT NAME>

**Date**: <YYYY-MM-DD>
**Duration**: <N minutes / hours>
**Severity**: SEV1 | SEV2 | SEV3
**Customer impact**: <count of customers affected, $MRR exposed, % of requests failed>
**Author**: founder
**Status**: Draft | Published | Closed
**Public**: yes | no

---

## TL;DR

One paragraph. What happened, who was affected, what we did, what we learned.

## Timeline

All times in UTC unless noted.

| Time       | Event |
|------------|-------|
| YYYY-MM-DD HH:MM | First signal (Sentry alert / customer ticket / monitoring page) |
| HH:MM | Founder acknowledged |
| HH:MM | Root cause hypothesis |
| HH:MM | Mitigation applied |
| HH:MM | Customer-visible recovery |
| HH:MM | All-clear posted to status page |

## What customers experienced

Be concrete. Which features failed, what they saw.

## Root cause

The actual technical cause. Not "we shipped a bug" — *why* did the bug ship?

## Five whys

1. Why did <symptom> happen? → <answer>
2. Why did <answer 1>? → <answer>
3. Why did <answer 2>? → <answer>
4. Why did <answer 3>? → <answer>
5. Why did <answer 4>? → <root cause>

## What went well

We want a deliberate practice of recognizing the good. Examples: alerting fired correctly, runbook was useful, customer comms were timely.

- <thing 1>
- <thing 2>

## What went poorly

Without blame.

- <thing 1>
- <thing 2>

## Action items

Each item must have:
- A specific change (not "be more careful").
- An owner (founder).
- A due date.
- A Linear issue link.

| Action | Owner | Due | Linear |
|--------|-------|-----|--------|
| <action 1> | founder | <date> | <link> |
| <action 2> | founder | <date> | <link> |

## Lessons (for the agent's memory)

What general principle did we learn that the agent should apply elsewhere?

> <principle, written so future runs of unrelated skills can pattern-match>
