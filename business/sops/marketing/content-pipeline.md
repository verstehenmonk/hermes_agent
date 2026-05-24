# SOP: Content Pipeline

The Notion database "Content Pipeline" has six stages. Pieces flow
left-to-right; never backwards without a comment explaining why.

## Stages

1. **idea** — title + 1-line hypothesis + target ICP segment
2. **outline** — H2/H3 outline, target word count, primary keyword, internal
   links to product
3. **draft** — full draft, footnoted with sources, fact-check passes done
4. **review** — DRAFT posted to `#marketing` for founder approval (uses
   approval gate)
5. **ready** — approved, scheduled publish date set
6. **published** — live URL + initial distribution post on X/LinkedIn (also
   DRAFTS)

## Rules

- Every piece must map to one of three goals: SEO (organic traffic), thought
  leadership (audience trust), product launch (conversion). Tag accordingly.
- Headlines follow the "specific result + specific audience" pattern.
  ("How <ICP> ships <outcome> in <timeframe>")
- Every piece links to one product feature or pricing page. No vague CTAs.
- No content goes to `ready` without:
  - Founder approval reaction in `#marketing`
  - Featured image (Notion attachment)
  - Meta description ≤ 155 chars

## Weekly cadence (Monday 10am cron)

The Head of Marketing scans the pipeline and posts a 3-bullet plan to
`#marketing`:
- This week's publishes (ready → published)
- This week's drafting focus (draft pieces moving to review)
- Pieces stuck > 7 days (with a proposed unstick)
