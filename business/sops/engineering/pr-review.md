# SOP: Pull Request Review

Triggered by GitHub `pull_request.opened` webhook. Run as `head-of-engineering`.

## Step 1 — Read the PR

- Use `gh pr view <number> --json title,body,files,additions,deletions,baseRefName`
- Fetch the diff: `gh pr diff <number>`
- Identify: title, author, target branch, files touched, total LOC delta.

## Step 2 — Pre-flight checks

Abort with `[BLOCKED]` if any of:

- Target branch is `main` AND the PR has no description
- Diff > 1000 lines AND the PR is not tagged `large-ok`
- Touches `business/secrets/`, `.env*`, or anything under
  `~/.hermes/secrets/`
- CI status is not green or pending

If blocked, post the reason to `#eng` and stop. Do not produce a review.

## Step 3 — Review dimensions

For each changed file, evaluate:

1. **Correctness** — does the code do what the description says?
2. **Tests** — is there coverage proportional to the risk? Point at missing
   cases by name.
3. **Security** — input validation, authn/authz boundaries, secrets, dep
   updates. Reference OWASP top-10 categories where relevant.
4. **Blast radius** — if this ships broken, what breaks? Cite the failure
   mode (5xx, data loss, billing, UX regression).
5. **Style** — only call out style issues that an existing linter would
   catch (and didn't), or that hurt readability for a future reader.

## Step 4 — Output

Post the review as a GitHub comment via `gh pr review <number> --comment -F -`.
Format:

```
## Review by Head of Engineering

**Verdict:** APPROVE | REQUEST_CHANGES | COMMENT_ONLY

### Correctness
- ...

### Tests
- ...

### Security
- ...

### Blast radius
- ...

### Nits (optional)
- ...
```

Cross-post a one-line summary to `#eng` Slack with a link to the PR.

## Step 5 — Stop conditions

- Never auto-merge.
- Never approve a PR you can't fully understand. Say so: "This touches X
  which I don't have enough context on. Founder review required."
