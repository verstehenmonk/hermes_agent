# SOP: Demo Prep

Triggered 24h before any Google Calendar event tagged `demo` (the
`calendar-meeting-soon` webhook with a `demo` tag fires this SOP).

## Brief structure

Post to `#sales` 24h ahead:

```
## Demo prep — <prospect company> at <date/time>

### Who
- Name, role, LinkedIn
- Company size, industry, stack (if known)
- Source: how did they find us?

### ICP fit
- Score 0-5 from `sops/sales/inbound-lead.md`
- Match against ICP segment: <segment name>

### Pain hypothesis
- Three things they're likely struggling with based on their context
- Cite signals (job description, recent funding, hiring posts, blog content)

### Demo path
- Three product features to emphasize (NOT every feature)
- One feature to deliberately skip (avoid scope confusion)
- Demo script: 5-min intro, 15-min demo, 10-min Q&A

### Likely objections
- Three objections you expect, with the response

### Next-step ask
- The specific commitment you want at the end of the call
```

## Sources

- Calendar: event attendees + description
- LinkedIn: enrich via the Apollo skill if installed, otherwise leave blank
  rather than fabricate
- Notion Pipeline: any prior interaction history
- Gmail: any prior email threads with this prospect

## Quality bar

If you can't fill in the "Pain hypothesis" section with real signals, say so
explicitly and ask the founder for context before the call.
