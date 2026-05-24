# Operations Department Brief

## Scope

Keep the lights on. Maintain the systems-of-record and the founder's calendar.
Audit vendors and secrets so we're not leaking money or attack surface.

## What "good" looks like

- The founder's calendar is protected: focus blocks default, meetings batched.
- Every API key in `~/.hermes/.env` is justified, scoped, and rotated annually.
- Every recurring software charge has a Notion entry with a business purpose.
- SOPs (standard operating procedures) for any task done > 3 times exist in Notion.
- Backups (database, secrets vault, Notion export) run weekly and are tested quarterly.

## Tools we use

- **Notion** (`NOTION_API_KEY`) — SOPs, decisions log, vendor registry, internal wiki.
- **Google Calendar** (`GOOGLE_CALENDAR_*`) — scheduling, focus blocks.
- **Gmail** (`GMAIL_*`) — primary inbox.
- **1Password** — secrets vault (humans only; not agent-accessible).
- **Mercury** (`MERCURY_API_KEY`) — vendor charge audit.

## Calendar rules (the agent defends these)

- **Default state of the calendar is focus time**, not "open to meetings."
- **Meetings clustered Tue/Thu afternoons.** Mon/Wed/Fri are makers' days.
- **No meetings before 10:00.** First two hours of the day are deep work.
- **Every internal scheduling request gets booked through Cal.com** — no "what time works for you" emails.
- **Agent declines (politely) any meeting without a clear agenda in the invite.**

## Monthly vendor audit (deterministic)

1. Pull Mercury transactions tagged "Software" or "Subscriptions".
2. Match each to the Notion "Vendor Registry" entry.
3. Flag:
   - Charges with no registry entry (unaccounted).
   - Registry entries with `last_used` > 60d ago (probably cancel).
   - Charges that grew > 25% MoM (price hike).
4. Draft a "Vendors to review" memo with a recommendation per row.

## Secrets hygiene (quarterly)

- List every env var in `~/.hermes/.env`.
- For each: when was it created, last rotated, what scope.
- Anything with `*` or admin scope: justify or downscope.
- Anything > 1 year old: rotate.

## SOP rules

- The agent watches for "I've done this before" moments in the chat history.
- After the 3rd time, it asks: "want me to write this up as an SOP?"
- SOPs live in Notion, linked from the relevant department brief.

## Standing rules

- **The Telegram bot is the only auto-paging channel.** Email is for digests, never for alerts.
- **Backups are tested, not just taken.** Quarterly we restore one and verify.
- **All vendor logins use the 1Password vault.** No saved-in-browser passwords.
- **No work account on the personal phone without 1Password + biometric.**

## Inputs to the daily brief

- Calendar load today (count of meetings + total minutes).
- Meetings without agenda (count — agent declined or pinged for agenda).
- Pending vendor renewals in the next 14d.
