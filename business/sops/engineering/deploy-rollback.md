# SOP: Deploy Rollback

Triggered by an incident where the suspected cause is a recent deploy.
Run as `head-of-engineering`. **Always escalate the actual rollback to the
founder — never auto-rollback.**

## Step 1 — Identify the target

- Vercel: `vercel-deploys list --project <name>` — find the last known-good
  deploy ID.
- Fly.io: `flyio-status releases --app <name>` — find the last known-good
  release number.

## Step 2 — Compute the diff

- `gh compare <good-sha>..<current-sha>` — list every PR included.
- Identify the single PR most likely to have introduced the regression
  (correlation with timing, files touched, dependency bumps).

## Step 3 — Draft the rollback

Post to `#eng`:

```
[ROLLBACK PROPOSAL]
Bad deploy:  <current-sha> deployed at <timestamp>
Good deploy: <good-sha>    deployed at <timestamp>
Likely cause: PR #<n> "<title>" by <author>
PRs that ship-rollback:
  - #a "<title>"
  - #b "<title>"
Command to run (founder approval required):
  vercel rollback <good-deploy-id> --project <name>
  # or
  fly releases rollback <good-release-num> --app <name>
```

## Step 4 — Post-rollback

Once the founder confirms the rollback ran:
- Verify health endpoint returns 200.
- Open a Linear issue tagged `regression` linked to the suspect PR.
- Comment on the PR with the rollback context.
