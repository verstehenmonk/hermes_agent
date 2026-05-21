# State

YAML files that capture the business' current truth. The agent reads these; you keep them current.

| File                  | Purpose                                                    | Update cadence    |
|-----------------------|------------------------------------------------------------|-------------------|
| `kpis.yaml`           | Current values + targets for every metric that matters     | Daily (auto + manual) |
| `icp.yaml`            | Ideal customer profile — what we sell to                   | Quarterly         |
| `pricing.yaml`        | Plans, ACVs, discount rules                                | When pricing changes |
| `competitors.yaml`    | Competitor list, their URLs, monitoring config             | Monthly           |
| `sales_stages.yaml`   | Pipeline stages + conversion targets                       | When pipeline changes |
| `feedback_tags.yaml`  | Controlled vocab for customer-feedback classification      | Quarterly         |
| `seo_keywords.yaml`   | Tracked SEO keywords                                       | Monthly           |
| `expense_categories.yaml` | Spend categorization rules                             | Quarterly         |
| `x_lists.yaml`        | X/Twitter accounts to mine for content                     | Monthly           |
| `vendors.yaml`        | Vendor inventory with cost + criticality                   | When vendors change |

Some files start empty — they're populated by the agent on first use or by the founder during setup.
