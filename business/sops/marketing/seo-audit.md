# SOP: SEO Audit

Run quarterly (or when organic traffic drops > 20% MoM).

## Crawl

- Run a fresh Lighthouse on the top 10 landing pages
- Check Search Console for the top 50 queries: position, impressions, CTR
- Identify pages where impressions are high and CTR is low (title/meta gap)
- Identify pages where position is 5-15 (one-rewrite-away from page 1)

## Audit

For each problem page:
- Title length, keyword in title, branded suffix
- Meta description present, ≤ 155 chars, includes the primary keyword
- H1 matches title intent
- Word count vs. top-3 SERP competitors
- Internal links pointing in
- Schema markup present (Article / Product / FAQ as appropriate)

## Output

Post to `#marketing`:
- Top 5 quick wins (rewrite title/meta, add internal links)
- Top 3 deep rewrites needed (full content refresh)
- Any technical issues (broken pages, slow LCP, missing alt tags)

Quick wins go straight into the content pipeline as `outline` stage.
