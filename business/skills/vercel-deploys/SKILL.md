---
name: vercel-deploys
description: "Vercel: query deploy status, logs, environments, and rollback proposals via the Vercel CLI."
version: 1.0.0
author: Hermes Business OS
license: MIT
prerequisites:
  env_vars: [VERCEL_TOKEN]
  commands: [vercel, jq]
metadata:
  hermes:
    tags: [Vercel, Deploys, DevOps]
---

# Vercel Deploys

Thin wrapper around the Vercel CLI. Read-only by default — rollbacks require
founder approval per `sops/engineering/deploy-rollback.md`.

## Setup

1. Install the Vercel CLI: `npm i -g vercel`
2. Get a token: Vercel Dashboard → Account → Tokens
3. Set `VERCEL_TOKEN` in `~/.hermes/secrets/vercel.env`
4. Test: `vercel ls --token "$VERCEL_TOKEN"`

## Common queries

### List recent deployments
```bash
vercel ls <project-name> --token "$VERCEL_TOKEN" | head -20
```

### Get the status of the latest production deploy
```bash
vercel ls <project-name> --prod --token "$VERCEL_TOKEN" | head -5
```

### Inspect a specific deploy
```bash
vercel inspect <deployment-url> --token "$VERCEL_TOKEN"
```

### Fetch logs for a failed deploy
```bash
vercel logs <deployment-url> --token "$VERCEL_TOKEN" | tail -200
```

### Get the commit sha for the latest production deploy
```bash
vercel ls <project-name> --prod --json --token "$VERCEL_TOKEN" \
  | jq -r '.[0].meta.githubCommitSha'
```

## Rollback (draft only — DO NOT execute)

Generate the rollback command, post it to `#eng`, and wait for founder
approval:

```bash
# DRAFT — founder runs this manually:
# vercel rollback <previous-deployment-url> --token "$VERCEL_TOKEN"
```

Identify the previous good deploy:
```bash
vercel ls <project-name> --prod --json --token "$VERCEL_TOKEN" \
  | jq '.[] | select(.state == "READY") | {url, created, sha: .meta.githubCommitSha}' \
  | head -5
```
