# Approval Gate Protocol

Every customer-facing output (email replies, social posts, blog publishes,
billing actions, prospect outreach) is a DRAFT until the founder approves it
in Slack.

## How to emit a draft

End every customer-facing message with the canonical footer:

```
[DRAFT — react :approve: in #<channel> to send, :discard: to cancel]
```

Include the channel name explicitly. Do NOT send the artifact via the
underlying tool (gmail, social API, etc.) yourself.

## What counts as customer-facing

- Outbound email to a customer or prospect
- Reply to a support ticket
- Tweet / LinkedIn post / blog publish
- Stripe action (refund, subscription change, plan switch)
- Calendar invite to a non-founder external party
- Linear comment that will be visible to a customer

## What does NOT need approval

- Internal Slack updates and standups
- Linear issue creation / internal comments
- Notion edits to internal docs
- Reading anything (always allowed)
- Drafting and posting the DRAFT itself to Slack

## Approval flow

1. Agent produces artifact, posts to the relevant Slack channel with the
   `[DRAFT ...]` footer.
2. Founder reads the draft.
3. If good: react `:approve:` — the bot picks up the reaction and executes
   the underlying send.
4. If not: react `:discard:` or reply with edits — the agent revises and
   reposts a new DRAFT.

## Edge cases

- **High-stakes** (billing > $500 MRR, churn risk, legal): require
  `:approve:` from the founder in person, not just any user.
- **Time-sensitive** (incident response, security): the Head of Engineering
  may post to internal channels without approval. External comms still
  require approval.
- **Bulk** (a marketing send to > 100 recipients): post the full recipient
  list + sample to `#marketing`, require explicit `:approve-bulk:` reaction.
