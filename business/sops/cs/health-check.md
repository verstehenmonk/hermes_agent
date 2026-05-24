# SOP: Customer Health Check

Runs Friday afternoons (part of `weekly-review`). Scores every active
customer green / yellow / red.

## Score inputs

For each customer, pull:
- **Usage**: trailing 7-day active days (where defined by feature use)
- **Sentiment**: average sentiment score from CS tickets in last 30 days
- **Billing health**: any failed charges, downgrades, or past-due invoices
- **Engagement**: replies to founder emails, attended QBRs/check-ins

## Score

| Color | Definition |
|---|---|
| Green | Usage ≥ baseline AND sentiment ≥ 0 AND billing OK |
| Yellow | One of: usage dropped 30%+ OR no sentiment data 30+ days OR billing issue resolved |
| Red | Two or more yellow conditions, OR sentiment ≤ -1, OR failed billing unresolved |

## Output

Post to `#cs`:

```
## Customer health — week of <date>

🟢 Green (N): list
🟡 Yellow (N): list with one-line "why"
🔴 Red (N): list with one-line "why" + recommended action
```

For each red: open a Linear issue tagged `churn-risk` and route to Head of
Sales for a save plan per `sops/sales/churn-save.md`.

## Onboarding new signups

For customers ≤ 14 days since signup:
- Did they hit the activation event (defined per product in
  `knowledge-base/product-spec.md`)?
- If not: draft a check-in email DRAFT to `#cs` offering a 15-min
  onboarding call
- If yes: draft a "you're rolling, here's an advanced tip" DRAFT
