# SOP: NPS Follow-up

Triggered when an NPS survey response arrives (webhook from your NPS tool,
or manual paste into `#cs`).

## Classify

- Promoter (9-10): ask for a referral or testimonial
- Passive (7-8): probe for one thing they'd improve
- Detractor (0-6): empathy first, root-cause probe, escalate

## Drafts

### Promoter
```
Subject: thanks — quick ask?

Hi <name>,

Thanks for the 9/10. Two quick asks:

1. Would you write a one-paragraph testimonial we can put on our site?
   I'll draft one for you to edit if that's easier.
2. Anyone in your network who'd benefit from <product>? I'd love an
   intro — happy to draft the intro note for you.

Either is great, both is amazing. No pressure.

— founder
```

### Passive
```
Subject: what's the one thing?

Hi <name>,

Thanks for the 7. If we fixed one thing for you, what would it be?

I read every reply.

— founder
```

### Detractor
```
Subject: I'd like to make this right

Hi <name>,

Thanks for the honest feedback. A 4 means we're not delivering. Can I grab
15 minutes to understand what's not working? I'll bring fixes, not excuses.

Here are three slots: <calendar slots>

— founder
```

## Log

For every detractor, file a Linear issue tagged `nps-detractor` with the
verbatim comment, and route to Head of Product for root cause review.
