# SOP: Spec Template

Every net-new feature in Notion uses this structure. Specs that don't follow
it are not "ready for Linear."

## Frontmatter

```
title:        <feature name>
status:       draft | in-review | approved | in-build | shipped
owner:        head-of-product (drafts) → founder (approves)
requested_by: <customer name or "internal">
target_release: <month-year or "TBD">
linear_epic:  <linear epic id if approved>
```

## Sections

### 1. Problem
One paragraph. What user pain are we solving? Cite the customer quote(s) or
data that surfaced it.

### 2. Non-goals
What this spec explicitly does NOT include. Useful for scope-creep
prevention.

### 3. User stories
3-7 stories of the form "As a <persona>, I want <capability>, so that
<outcome>." Persona must match an ICP segment from
`business/knowledge-base/company.md`.

### 4. UX sketch
Wireframe or text description. Doesn't need to be polished — it needs to be
unambiguous about state transitions.

### 5. Data model changes
Tables touched, new columns, migration risk. Reference existing schema.

### 6. Telemetry
What events will we emit to measure adoption? Match the metric to a KPI in
`kpis.yaml`.

### 7. Risks
Three risks max. Each with a mitigation.

### 8. Open questions
Items requiring founder decision before "approved." If empty, the spec is
ready for `/spec approve`.
