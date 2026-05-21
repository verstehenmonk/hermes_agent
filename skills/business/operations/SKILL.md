---
name: operations
description: "Ops: calendar, vendors, secrets, SOPs, backups."
version: 1.0.0
author: Hermes Agent
license: MIT
prerequisites:
  optional_env_vars: [NOTION_API_KEY, GOOGLE_CALENDAR_CLIENT_ID, GOOGLE_CALENDAR_CLIENT_SECRET, GOOGLE_CALENDAR_REFRESH_TOKEN, MERCURY_API_KEY]
metadata:
  hermes:
    tags: [operations, calendar, vendors, sops, notion, google-calendar]
---

# Operations — solo SaaS

On activation, read `business/departments/operations.md`.

## Calendar (Google Calendar via MCP or API)

```bash
# List today's events (OAuth token already obtained via refresh flow)
ACCESS_TOKEN=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=$GOOGLE_CALENDAR_CLIENT_ID" \
  -d "client_secret=$GOOGLE_CALENDAR_CLIENT_SECRET" \
  -d "refresh_token=$GOOGLE_CALENDAR_REFRESH_TOKEN" \
  -d "grant_type=refresh_token" | jq -r '.access_token')

curl -s "https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=...&timeMax=..." \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Or use the calendar MCP server if installed — much cleaner.

## Calendar defenses (the agent's main job here)

When a meeting request lands:
1. **Check working hours.** Decline anything before 10:00 or outside Mon–Fri 09–18.
2. **Check for agenda.** No agenda in the invite → reply asking for one, don't accept yet.
3. **Check meeting load this week.** If already at the cap (≤ 8h of meetings/week), reschedule or decline.
4. **Cluster, don't scatter.** Suggest Tue/Thu afternoons; protect Mon/Wed/Fri.
5. **Always reply within 4h** — silence is rude.

## Notion (SOPs, vendor registry, decisions log)

```bash
# Query the vendor database
curl -s -X POST "https://api.notion.com/v1/databases/$VENDOR_DB_ID/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" -d '{}'

# Create a new SOP page
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"parent":{"page_id":"$SOP_PAGE_ID"}, "properties":{"title":{"title":[{"text":{"content":"..."}}]}}, "children":[...]}'
```

## SOP detection

Watch the chat history for "I've done this before" moments. After the 3rd repeat,
ask: "Want me to write this up as an SOP?" — if yes, file a Notion page under
SOPs and link it from the relevant department brief in `business/departments/`.

## Vendor audit (monthly, runs from cron)

1. Pull last month's Mercury transactions in the "Software" / "Subscriptions" categories.
2. Cross-reference with the Notion vendor registry (last_used date, owner, purpose, plan).
3. Flag:
   - Charges with no registry entry → "unaccounted, investigate"
   - Entries with `last_used > 60d ago` → "candidate for cancellation"
   - Charges that grew > 25% MoM → "price hike, review"
4. Output a memo with a recommendation per row.

## Secrets hygiene (quarterly)

1. List every `*_API_KEY` / `*_TOKEN` / `*_SECRET` in `~/.hermes/.env` (count and names — never values).
2. Look up each in the 1Password vault: when created, when last rotated, scope.
3. Flag: keys > 1 year old, keys with admin scope, keys for vendors no longer in use.
4. Draft a rotation plan. Founder executes.

## Backups (weekly Sunday 03:00)

- Notion workspace export → Mercury-side cold storage.
- `~/.hermes/business/journal/` → encrypted backup off-machine.
- Database snapshots → S3 with lifecycle policy.
- Quarterly: restore one backup to verify it actually works.

## Standing rules

- Telegram is for alerts. Email is for digests. Never blur the two.
- No saved-in-browser passwords for business accounts.
- The founder reviews every backup restore quarterly.
- New vendor onboarding requires a Notion entry before the first charge.
