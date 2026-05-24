---
name: flyio-status
description: "Fly.io: app status, releases, logs, machine health via the fly CLI. Rollbacks are draft-only."
version: 1.0.0
author: Hermes Business OS
license: MIT
prerequisites:
  env_vars: [FLY_API_TOKEN]
  commands: [fly, jq]
metadata:
  hermes:
    tags: [Fly.io, Deploys, Hosting, DevOps]
---

# Fly.io Status

Thin wrapper around the `fly` CLI. Read-only by default. Rollbacks always
escalate to founder per `sops/engineering/deploy-rollback.md`.

## Setup

1. Install: `curl -L https://fly.io/install.sh | sh`
2. Get a token: `fly tokens create deploy -a <app>` (or use a personal
   access token from the Fly dashboard for full read)
3. Set `FLY_API_TOKEN` in `~/.hermes/secrets/fly.env`
4. Test: `fly apps list`

## Common queries

### App status
```bash
fly status -a <app-name>
```

### Recent releases
```bash
fly releases -a <app-name> | head -10
```

### Tail logs
```bash
fly logs -a <app-name> --no-tail | tail -200
```

### Machine list and health
```bash
fly machines list -a <app-name>
```

### Metrics (CPU, memory, request rate)
```bash
fly metrics -a <app-name> --json | jq '.cpu, .memory, .requests'
```

## Rollback (draft only — DO NOT execute)

Identify the previous known-good release:
```bash
fly releases -a <app-name> --json | jq '.[] | {version, status, created_at, image}' | head -10
```

Draft the rollback command, post to `#eng`, founder runs it:
```bash
# DRAFT — founder runs this manually:
# fly releases rollback <version> -a <app-name>
```

## During an incident

Follow `sops/engineering/incident.md`. Don't restart machines or change
config automatically — propose the action, post to `#alerts`, wait for
approval.
