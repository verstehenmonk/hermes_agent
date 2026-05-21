# Business Charter

> The agent reads this on every orchestrator invocation. Keep it current. Keep it honest.

## Identity

- **Company**: `<YOUR_COMPANY_NAME>` (placeholder — edit before going live)
- **One-line pitch**: AI-native product analytics for B2B SaaS teams. Ask in English, get insights in seconds — no SQL, no data team queue.
- **Founder**: solo operator. No employees. Agents do everything else.
- **Stage**: post-MVP, pre-PMF. Goal for the next 12 months: reach $30k MRR with <$8k/mo burn.

## What We Sell

An AI analytics platform that ingests product events (Segment, Rudderstack, direct SDK) and Stripe billing data, then exposes a natural-language query interface plus auto-generated dashboards. Built for product, growth, and ops teams at B2B SaaS companies who don't have a dedicated data engineer.

**Three core jobs the product does:**
1. Answer ad-hoc product questions in <30s ("which features predict 90-day retention?").
2. Generate weekly executive dashboards with LLM-written narrative ("here's why MRR moved").
3. Trigger alerts when key metrics deviate from forecast.

## Who Buys (ICP)

- B2B SaaS, 50–500 employees, $5M–$50M ARR.
- Industries: dev tools, vertical SaaS, fintech, devops.
- Buyer: Head of Product / Head of Growth / VP Product. Champion: PM or growth analyst.
- Technical fluency: medium — uses Mixpanel/Amplitude today, hates writing SQL.
- Trigger event: new exec hire, missed quarter, churn spike, data-team backlog >2 weeks.

See `state/icp.yaml` for the structured version.

## How We Win

- **Speed to answer**: NL query → answer in <30s, including chart. Competitors require modeling, dashboard config, or analyst time.
- **No data engineer required**: connect Segment + Stripe, get value day 1.
- **Narrative, not just numbers**: every chart ships with an LLM-written "what changed and why".
- **Solo-founder economics**: COGS per customer < $40/mo at $1,000/mo ACV. Inference cost is the variable, and we cache aggressively.

## How We Lose

- **Enterprise procurement**: SOC2, SSO, custom contracts. We don't sell here yet. ICP is mid-market.
- **Generic NL2SQL hype**: customers don't trust raw NL2SQL output. We always pair with deterministic templates + show the SQL we ran.
- **Custom event schemas**: customers want their schema preserved; we auto-infer but expose a mapping layer.

## Pricing

| Plan       | Monthly | Annual | Events/mo | Seats | NL queries/mo |
|------------|---------|--------|-----------|-------|---------------|
| Starter    | $499    | $4,990 | 5M        | 5     | 500           |
| Growth     | $1,499  | $14,990| 25M       | 25    | 2,500         |
| Scale      | $3,999  | $39,990| 100M      | unlimited | 10,000    |
| Enterprise | custom  | custom | custom    | custom | custom        |

See `state/pricing.yaml` for the structured version.

## North-Star Metric

**Weekly Active Insight Recipients (WAIR)**: distinct people across all customers who consumed at least one auto-narrative or NL query result in the last 7 days. Proxy for value delivered, not seats sold.

Secondary metrics: NRR, gross margin, time-to-first-insight (target: <10 min from signup).

See `state/kpis.yaml` for current values and targets.

## Strategic Bets (12-month horizon)

1. **AI-native onboarding**: a 5-min agent-led setup that maps the customer's schema and produces three insights before they exit signup. Belief: cuts time-to-value from days to minutes, halves trial→paid loss.
2. **Insight subscriptions**: customers subscribe to recurring narrative reports delivered to Slack/email. Belief: turns the product from "tool you visit" into "feed you receive" — increases stickiness, reduces churn.
3. **PLG → outbound hybrid**: self-serve up to $24k ACV; founder-led outbound above. Belief: solo-founder GTM can cover both tiers if outbound is heavily agent-supported.

## Anti-Goals (things we will not do this year)

- Build a generic BI tool. We are opinionated, not flexible.
- Sell to companies <20 employees. They churn at 12%/mo and use Mixpanel free.
- Raise venture money. We optimize for solo profitability, not growth at all costs.
- Hire. The bet is that agents replace the first 5 hires for 12 months.

## Operating Principles

1. **Defaults beat configurations.** Every screen ships with sensible defaults; configurability is earned through customer pull.
2. **Speed > polish on internal tools, polish > speed on customer-facing.**
3. **Every external email is reviewed by the founder.** No agent sends unreviewed customer-facing prose.
4. **Code review is non-negotiable.** Even agent-written code goes through review (you, or a second agent).
5. **Cache aggressively, regenerate sparingly.** Inference cost is the variable to control.
6. **When in doubt, write the customer.** Hypotheses are cheap; the truth lives in user interviews.

## When This Charter Changes

Update when any of the following shifts: ICP, pricing, north-star metric, or the strategic bets list. Stamp the change in the orchestrator's daily brief so the agent notices.

- Last updated: `<DATE>`
- Next scheduled review: quarterly
