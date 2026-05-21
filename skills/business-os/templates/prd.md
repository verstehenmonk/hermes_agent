# PRD: <FEATURE NAME>

**Author**: <founder>
**Status**: Draft | In Review | Approved | Building | Shipped | Killed
**Linear**: <link>
**Estimated build time**: <N> days
**Target ship date**: <YYYY-MM-DD>

---

## TL;DR

One paragraph. What is this and why are we building it?

## Problem

The job to be done. Quote a real customer (with name and revenue) describing the pain in their own words. If you can't find a quote, that's signal — go talk to one more customer before writing the PRD.

> "<verbatim quote>" — Customer X ($Y MRR)

## Success metric

A single number that goes up or down because of this work. Must map to an entry in `state/kpis.yaml`.

- Metric: <name from kpis.yaml>
- Baseline: <current value>
- Target: <expected value 30 days post-ship>
- How we'll measure: <SQL query, dashboard, or instrumentation needed>

## What we're shipping

The narrowest thing that solves the problem. Bullet list. Each bullet ≤1 line.

- [ ] <bullet 1>
- [ ] <bullet 2>
- [ ] <bullet 3>

## What we're NOT shipping (and won't until v2)

Non-trivial list. If this section is empty, the scope is too broad.

- <thing 1>
- <thing 2>

## How it works

A walk-through from the customer's perspective. Include screenshots, wireframes, or text mockups. Be concrete.

## Open questions

Anything you don't know yet. Don't pretend they aren't questions.

## Risks

At least one realistic way this could fail.

- <risk 1>
- <risk 2>

## Kill criteria

What would we observe in the first 4 weeks that would tell us to roll this back or stop investing? Examples:
- "Activation rate among users who touch this feature drops below baseline."
- "Inference cost per user with this feature on exceeds $10/mo."
- "No customer mentions it positively within 60 days."

## Release plan

- [ ] Feature flag set up; default off
- [ ] Rolled out to internal account
- [ ] Rolled out to 3 friendly customers
- [ ] Rolled out to 20% of paid base
- [ ] GA + blog post + release notes
- [ ] 30-day check against success metric → SHIP / ITERATE / KILL
