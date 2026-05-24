# Stack

> The canonical inventory of tools, where they're hosted, and what depends
> on them.

## Code & build

- **Editor**: VS Code, Claude Code, Codex
- **VCS / hosting**: GitHub (Pro+ plan), private repo
- **CI/CD**: GitHub Actions
- **Code review**: GitHub PRs + the `pr-review` Hermes webhook

## Production

- **Frontend hosting**: Vercel
- **Backend hosting**: Fly.io
- **Database**: (Postgres / other — fill in)
- **Background jobs**: (queue tech — fill in)
- **Storage / CDN**: (R2, S3, Vercel Blob — fill in)
- **DNS**: (registrar)

## Business systems

- **Project management**: Linear
- **Knowledge base**: Notion (DBs: Company KB, Pipeline, Customers, Vendors, Feedback, Content Pipeline)
- **Productivity**: Google Workspace (Gmail, Calendar, Drive, Docs, Sheets)
- **Comms**: Slack (primary channel for Hermes Business OS)
- **Email**: Gmail via `himalaya` skill

## Money

- **Billing**: Stripe (use restricted keys; read-only for the CFO agent)
- **Banking / cards**: (Brex / Mercury — fill in)

## Observability

- **Frontend monitoring**: Vercel Analytics
- **Backend monitoring**: Fly metrics + (Grafana / Sentry — fill in)
- **Status page**: (statuspage.io / instatus — fill in)

## AI infra

- **Agent**: Hermes Agent (this repo)
- **LLM providers**: (Anthropic, OpenAI, OpenRouter — fill in which you use)
- **Embeddings**: (if any)
- **Vector store**: (if any)

## Secrets

All secrets live in `~/.hermes/secrets/` with 0600 permissions. Each file is
named after the integration (e.g. `stripe.env`, `linear.env`). Never check
secrets into this repo.
