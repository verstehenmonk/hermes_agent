# Weekly Review Ritual

Runs Friday 16:00 local. The `ceo` skill orchestrates: it calls each
department skill, collects a one-page section, assembles, sends as email.

## Sequence

1. CEO skill posts to Telegram: "Starting weekly review — this'll take ~5 min."
2. For each department in [engineering, product, marketing, sales, customer-success, finance, operations, legal]:
   - Load that department's brief.
   - Run its "Weekly questions" against fresh data.
   - Produce a section (≤ 300 words).
3. CEO skill writes the synthesis section.
4. Assemble into email, send to founder.
5. Archive to `~/.hermes/business/journal/<YYYY-Www>-weekly.md`.
6. Post Telegram summary: "Weekly review sent. Top: {X}. Bottom: {Y}. Decision needed: {Z}."

## Email structure

```
Subject: Week {ISO week} review — {one-line headline}

THE WEEK IN ONE NUMBER
{the one metric that moved most + its meaning}

WHAT SHIPPED
{1–5 bullets, customer-visible only}

WHAT SLIPPED
{1–5 bullets, with why}

DECISIONS MADE
{pulled from the decisions log this week}

NUMBERS (delta vs last week)
  MRR · WAW · Activation · Churn · Burn · Cash · Errors

—— ENGINEERING ——
{section}

—— PRODUCT ——
{section}

—— MARKETING ——
{section}

—— SALES ——
{section}

—— CUSTOMER SUCCESS ——
{section}

—— FINANCE ——
{section}

—— OPERATIONS ——
{section}

—— LEGAL ——
{section}

OPEN QUESTIONS
{things the agent surfaces for founder thought,
 not decisions to make immediately}

NEXT WEEK
  Bet 1: {pulled from quarter's bets, sliced to this week}
  Bet 2: ...
  Bet 3: ...

CALENDAR PREVIEW
{count of meetings, biggest commitments, focus blocks reserved}
```

## Rules for the CEO skill during weekly review

1. **The headline is your editorial call.** Read all sections, then write the headline. Don't write it first.
2. **"Decisions made" comes from the decisions log**, not from chat history.
3. **"Open questions" should be ≤ 5.** This isn't a brain dump.
4. **Cut sections that have nothing to report.** A blank "marketing" section is fine if no work happened.
5. **Be honest about slips.** A weekly review that hides bad news is worthless next quarter.
