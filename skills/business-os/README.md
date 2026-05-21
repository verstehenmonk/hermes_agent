# Solo Founder Business OS

A complete operating system for a solo founder running an **AI Analytics B2B SaaS**, built on top of [Hermes Agent](../../README.md). One human, many agents, every function covered.

## Philosophy

The job of a solo founder is to **decide what matters and let agents handle the rest**. This OS splits work into two complementary layers:

- **Deterministic systems** — anything that should run the same way every time: cron schedules, state files (KPIs, ICP, pricing), templates (PRD, runbook, post-mortem), pre-processor scripts that fetch and aggregate data. These are code.
- **Agentic workflows** — anything that needs judgment: triage decisions, content drafting, customer email tone, incident analysis, roadmap synthesis. These are LLM calls, packaged as Hermes skills.

The orchestrator skill picks which workflow to run; each domain skill knows the playbook for its function.

## Layout

```
business-os/
├── CHARTER.md              Business definition: what we sell, to whom, how we win.
├── orchestrator/SKILL.md   Morning brief, daily kickoff, weekly review, routing.
├── engineering/SKILL.md    Sprint planning, code review, deploys, on-call, tech debt.
├── product/SKILL.md        PRDs, feedback synthesis, roadmap, A/B test reads.
├── marketing/SKILL.md      Content calendar, SEO, social, newsletter, attribution.
├── sales/SKILL.md          Lead enrichment, outbound, demos, proposals, CRM hygiene.
├── customer-service/SKILL.md  Ticket triage, response drafting, churn signals, NPS.
├── operations/SKILL.md     Vendor mgmt, runbooks, incident response, compliance.
├── finance/SKILL.md        MRR/ARR, burn, runway, AR/AP, investor updates.
├── scripts/                Python pre-processors run BEFORE the agent (deterministic).
├── templates/              Fill-in templates the agent uses to produce artifacts.
├── state/                  YAML state — KPIs, ICP, pricing, customers list.
└── install-cron.sh         One-shot installer for all recurring schedules.
```

## How a Day Runs

```
07:00  cron → orchestrator → "Morning brief"
       Pre-processor pulls overnight metrics (Stripe, GA, support inbox, error tracker).
       Agent reads CHARTER.md + state/kpis.yaml, drafts a 5-line brief to Telegram.
       SILENT pattern: only pings if something needs your attention.

08:00  You read the brief on phone, reply with one of: "ship X", "ignore Y", "dig into Z".
       Replies route to the relevant domain skill.

Throughout the day:
       - Webhooks (GitHub PR, Stripe event, support ticket, Linear issue) trigger skills.
       - You issue natural-language commands; orchestrator routes to the right skill.
       - Long-running work (write a blog post, draft an outbound sequence) runs in a
         subagent so it doesn't block your main conversation.

18:00  cron → orchestrator → "End-of-day digest"
       What got done, what's stuck, what needs you tomorrow.

Weekly (Mon 07:30): "Weekly review" — KPI deltas, pipeline health, content pipeline,
       customer health scores, finance pulse, decisions queue.

Monthly (1st 08:00): "Investor / self update" — even if you have no investors, you
       write this for yourself. The discipline matters.
```

## Trust Levels

Every action falls into one of three trust tiers. Skill docs label every step.

| Tier      | Meaning                                                   | Examples                                    |
|-----------|-----------------------------------------------------------|---------------------------------------------|
| **AUTO**  | Agent acts, no review.                                    | Tag a ticket, post a metric, archive spam.  |
| **DRAFT** | Agent prepares; you approve before send/merge/publish.    | Customer email, blog post, code PR, invoice.|
| **HUMAN** | You decide; agent gathers context and presents options.   | Pricing, hiring, major architecture, layoffs.|

When in doubt, the agent defaults to DRAFT. Promote actions to AUTO only after they've been DRAFT-correct ≥10 times in a row.

## Setup

```bash
# 1. Customize the charter — what you sell, who buys, how you win.
$EDITOR skills/business-os/CHARTER.md

# 2. Fill in the state files.
$EDITOR skills/business-os/state/kpis.yaml      # current MRR, customers, NPS, etc.
$EDITOR skills/business-os/state/icp.yaml       # ideal customer profile
$EDITOR skills/business-os/state/pricing.yaml   # plans and offers

# 3. Set provider env vars (use the ones you actually have).
#    STRIPE_API_KEY, LINEAR_API_KEY, NOTION_API_KEY, RESEND_API_KEY,
#    POSTHOG_API_KEY, INTERCOM_TOKEN, GITHUB_TOKEN, etc.

# 4. Install all recurring jobs.
bash skills/business-os/install-cron.sh

# 5. Start the gateway so morning briefs land on Telegram.
hermes gateway start
```

## Customizing for Your Business

This bundle ships configured for an **AI Analytics B2B SaaS** — a tool that helps B2B SaaS data/product teams understand their product usage and customer behavior via LLM-powered queries. The CHARTER and state files capture concrete assumptions (ICP = 50–500 person B2B SaaS, ACV = $12k–$60k, GTM = PLG + outbound for >$24k deals).

To repurpose this for a different product, edit `CHARTER.md` and `state/*.yaml`. The skill files reference the charter rather than hard-coding business assumptions.

## Why Hermes

The OS leans on five Hermes primitives that already exist:
- **Cron** for schedules (`hermes cron create`).
- **Webhooks** for event triggers (`hermes webhook subscribe`).
- **Skills** for packaged playbooks (this bundle).
- **Pre-processor scripts** to do deterministic work before the LLM turn.
- **Multi-platform delivery** so briefs land where you live (Telegram, Slack, email).

The OS doesn't reinvent any of those — it composes them.
