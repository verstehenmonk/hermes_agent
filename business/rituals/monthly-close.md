# Monthly Close Ritual

Runs on the 1st of the month at 09:00 local. Produces the monthly narrative —
the document you'd send to a board if you had one.

## Sequence

1. `scripts/metrics_snapshot.py --month-close` — pulls 30 days of Stripe, Mercury,
   PostHog, Linear, GitHub into `~/.hermes/business/metrics/<YYYY-MM>.json`.
2. `finance` skill drafts the MRR walk + cash + runway section.
3. `product` skill drafts retention cohorts + feature adoption section.
4. `engineering` skill drafts incidents + SLO compliance section.
5. `marketing` skill drafts traffic + funnel section.
6. `ceo` skill assembles + writes the narrative.
7. Email to founder. Archive to `~/.hermes/business/journal/finance/<YYYY-MM>.md`.

## Email structure

```
Subject: {Month YYYY} close — {one-line headline}

THE NARRATIVE (≤ 200 words)
{What changed this month, why, and what it implies for next month.
 Written like you're telling a friend who runs another startup.}

THE NUMBERS

  Revenue
    MRR start          $X
    + new              $X
    + expansion        $X
    − contraction     −$X
    − churn           −$X
    MRR end            $X (Δ ±X%)

    ARR                $X
    NRR (annualized)   X%
    Logo churn         X%

  Cash
    Start              $X
    + revenue          $X
    − costs           −$X
    End                $X
    Burn (3-mo avg)    $X/mo
    Runway             N months

  Customers
    Active             N
    New                +N
    Churned            −N
    Net                ±N

  Product
    WAW end            N (Δ ±N)
    7-day activation   X%
    30-day retention   X%

  Engineering
    Deploys            N
    Incidents          N (severity)
    Error rate avg     X%
    MTTR avg           N min

  Marketing
    Uniques            N
    Signups            N (organic / paid breakdown)
    Newsletter         N (Δ ±N)

TOP MOVES THIS MONTH
{the 3 most important things — wins or losses}

TOP RISKS NEXT MONTH
{the 3 things to watch — calibrated)}

DECISIONS WORTH RE-EXAMINING
{decisions logged > 60d ago that we should review now}
```

## Rules for the agent

1. **All numbers come from `metrics/<YYYY-MM>.json`.** Never invent.
2. **The narrative is the most important part.** Numbers are easy; explaining them well is hard. Write it last, when you've read everything.
3. **No corporate-speak.** Plain English, calibrated language, real numbers.
4. **If a number is missing because a tool isn't connected**, say so. Don't paper over.
5. **Decisions to re-examine**: pull from `~/.hermes/business/journal/decisions.md`, filter to entries with a `review_date` ≤ today.
