# SOP: Bug Triage

When a bug arrives from CS, support email, or a GitHub issue.

## Classify

- **Severity**: SEV1 (data loss / down) | SEV2 (degraded core flow) | SEV3
  (annoying edge case) | SEV4 (cosmetic)
- **Reproducibility**: always | sometimes | once
- **Customer impact**: count affected customers (1, < 5, < 20, broad)

## File

Create a Linear issue:
- Title: `[BUG] <one-line user-visible symptom>`
- Description: customer quote verbatim, steps to reproduce, expected vs
  actual, environment (browser, plan tier, etc.)
- Labels: severity, reproducibility, area (frontend | api | billing | data)
- Link the GitHub issue or support ticket

## Route

- SEV1 → page `#alerts`, escalate to founder, run `sops/engineering/incident.md`
- SEV2 → top of next-day standup
- SEV3 → backlog with target sprint
- SEV4 → backlog, no target

## Close the loop

When the bug ships fixed, draft a customer reply (DRAFT to `#cs`) referencing
the original ticket: "you reported X on <date>, this is fixed in today's
release. Thanks for the catch."
