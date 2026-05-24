# Runbook

> Fill this in. The Head of Engineering reads this during incidents and
> deploys. If the answer to a 3am question isn't here, it doesn't exist.

## Production services

| Service | Where it runs | URL | Health endpoint |
|---|---|---|---|
| Web frontend | Vercel | https://... | https://.../health |
| API | Fly.io | https://api.... | https://api..../health |
| Database | (fill in) | — | — |
| Background jobs | (fill in) | — | — |

## Critical dependencies

| Dependency | What breaks if it's down | Status page |
|---|---|---|
| Stripe | new signups, billing | https://status.stripe.com |
| Vercel | website, frontend | https://vercel-status.com |
| Fly.io | API | https://status.flyio.net |
| Anthropic / OpenAI | core product (LLM inference) | (URL) |
| Postgres host | reads + writes | (URL) |

## Top three user flows (smoke-test after every deploy)

1. **Signup → activation event**: <describe>
2. **Core feature usage**: <describe>
3. **Billing / upgrade**: <describe>

For each: the exact curl or playwright steps the Head of Engineering uses to
verify post-deploy.

## On-call

- **Primary**: founder
- **Backup**: none (solo)
- **Pager channel**: Slack `#alerts`
- **Escalation if founder is unreachable**: pause all customer-facing
  features via feature flag, post a status page update

## Common incidents

### "API 5xx spike"
- Check Fly.io status first (status.flyio.net)
- Check our error rate dashboard (URL)
- Most-common cause historically: <fill in once you have history>

### "Frontend white screen"
- Check Vercel status
- Check the latest deploy in vercel-deploys
- Most-common cause historically: <fill in>

### "Billing webhook missing"
- Check Stripe dashboard for delivery status
- Re-deliver via Stripe dashboard if needed

## Useful commands

```bash
fly status -a <app-name>
fly logs -a <app-name>
vercel ls
vercel logs <deployment-url>
gh pr list --state open
```
