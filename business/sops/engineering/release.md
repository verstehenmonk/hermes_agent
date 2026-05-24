# SOP: Release

Run as `head-of-engineering` when the founder says `/release` or when a PR
labeled `release-candidate` merges to main.

## Pre-flight

- CI is green on `main`
- No open incidents in Linear
- It is NOT Friday after 3pm local time (founder override required)
- Last release was > 2 hours ago

If any pre-flight fails, post the failure to `#eng` and stop.

## Build & deploy

- Vercel: deploys happen automatically on merge to `main`. Wait for the
  preview → production promotion to complete via `vercel-deploys`.
- Fly.io: trigger `fly deploy` only via the founder's approval. Draft the
  exact command in `#eng` with the target app name.

## Verify

- Hit the production health endpoint (curl) and confirm 200.
- Smoke-test the three top user flows (defined in `knowledge-base/runbook.md`).
- Check error rates in Vercel / Fly for the next 15 minutes — alert if
  baseline + 2σ.

## Announce

- Post a release note to `#eng` with: PRs included, deploy URL, smoke-test
  results.
- If user-facing: draft a release note for `#cs` and `#marketing` via the
  Head of Product. DRAFTS, not sends.
