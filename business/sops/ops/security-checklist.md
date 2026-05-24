# SOP: Monthly Security Checklist

Run on the 1st of each month. Post results to `#ops` with green/yellow/red
per item. Reds become Linear issues with severity High.

## Accounts & access

- [ ] All admin accounts have 2FA enabled
- [ ] No shared logins (everything is the founder's account or a service
      account with a documented owner)
- [ ] Recovery codes for primary email backed up offline
- [ ] Password manager has a backup export ≤ 90 days old

## Secrets

- [ ] No secrets in any committed file (run `gitleaks detect` on the
      monorepo)
- [ ] `~/.hermes/secrets/` files are 0600
- [ ] No API keys older than 12 months without rotation
- [ ] Stripe restricted keys used wherever possible (not the live secret
      key)

## Infrastructure

- [ ] Vercel: only the founder has admin
- [ ] Fly.io: only the founder has admin; deploy tokens scoped to CI only
- [ ] DNS: registrar 2FA on, recovery email tested
- [ ] All production services have HTTPS only
- [ ] Database backups completing daily (verify last backup timestamp)
- [ ] Database backup restore tested ≤ 90 days ago

## Customer data

- [ ] Customer data exported encrypted only
- [ ] Deletion requests processed within 30 days (check Notion log)
- [ ] DPAs filed for every vendor handling customer data
- [ ] Privacy policy reviewed ≤ 12 months ago

## Dependencies

- [ ] No high/critical vulnerabilities in production deps (npm audit / pip
      audit)
- [ ] Dependabot or equivalent enabled on the main repo

## Output

A markdown table in `#ops` with all items, status, and notes. File any reds
as Linear issues.
