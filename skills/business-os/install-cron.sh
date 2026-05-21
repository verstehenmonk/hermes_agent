#!/usr/bin/env bash
#
# Install all Business OS cron jobs into Hermes.
#
# Idempotent: each job has a stable --name; rerunning updates the existing entry.
# Run after `hermes setup` and after editing CHARTER.md + state/*.yaml.
#
# Most schedules use the [SILENT] pattern so they only ping you when there's
# something to surface. You can change delivery targets per-line (default: telegram).
#
# Usage:
#   bash skills/business-os/install-cron.sh
#   bash skills/business-os/install-cron.sh --delivery slack
#   bash skills/business-os/install-cron.sh --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DELIVERY="${DELIVERY:-telegram}"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --delivery) DELIVERY="$2"; shift 2 ;;
        --dry-run)  DRY_RUN=1; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

create() {
    local schedule="$1"
    local name="$2"
    local prompt="$3"
    local skills="$4"
    local script="${5:-}"

    local cmd=(
        hermes cron create
        "$schedule"
        "$prompt"
        --name "$name"
        --skills "$skills"
        --deliver "$DELIVERY"
    )
    if [[ -n "$script" ]]; then
        cmd+=(--script "$script")
    fi

    echo ""
    echo "→ $name"
    echo "  schedule: $schedule"
    echo "  skills:   $skills"
    [[ -n "$script" ]] && echo "  script:   $script"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        printf "  (dry-run) "; printf "%q " "${cmd[@]}"; echo
    else
        "${cmd[@]}"
    fi
}

echo "Installing Business OS cron jobs (delivery: $DELIVERY)"
echo "Script root: $SCRIPT_DIR"

# 1. Orchestrator — morning brief (daily 07:00 local).
create \
    "0 7 * * *" \
    "Business OS — Morning brief" \
    "Read the JSON above + skills/business-os/CHARTER.md + skills/business-os/state/kpis.yaml. Produce the exact format defined in skills/business-os/orchestrator/SKILL.md > 'Morning brief'. If nothing in OVERNIGHT or DECISIONS QUEUED, reply [SILENT]." \
    "business-os-orchestrator" \
    "$SCRIPT_DIR/scripts/morning_brief.py"

# 2. Orchestrator — end-of-day digest (daily 18:00 local).
create \
    "0 18 * * *" \
    "Business OS — End-of-day digest" \
    "Read the JSON above. Produce the 5-line digest defined in orchestrator/SKILL.md > 'End-of-day digest'. If nothing happened today, [SILENT]." \
    "business-os-orchestrator" \
    "$SCRIPT_DIR/scripts/morning_brief.py --mode eod"

# 3. Orchestrator — weekly review (Mon 07:30).
create \
    "30 7 * * 1" \
    "Business OS — Weekly review" \
    "Produce the full weekly review per orchestrator/SKILL.md > 'Weekly review'. Save the longer version to ~/.hermes/business-os/reviews/YYYY-MM-DD.md and deliver a 12-line summary." \
    "business-os-orchestrator" \
    "$SCRIPT_DIR/scripts/morning_brief.py --mode weekly"

# 4. Engineering — PR review queue (every 4h during work hours).
create \
    "0 9-18/4 * * 1-5" \
    "Engineering — PR queue check" \
    "List GitHub PRs awaiting my review. Score each: BLOCKING / HIGH-VALUE / NIT. Suggest the top 1 to review now. If queue is empty, [SILENT]." \
    "business-os-engineering"

# 5. Engineering — hourly CI watch (always).
create \
    "0 * * * *" \
    "Engineering — CI status" \
    "Check GitHub Actions main branch status. If red, summarize failure + suggest first diagnostic step. If green, [SILENT]." \
    "business-os-engineering"

# 6. Product — weekly feedback synthesis (Mon 09:00).
create \
    "0 9 * * 1" \
    "Product — Feedback synthesis" \
    "Read last 7 days of feedback in ~/.hermes/business-os/feedback/. Produce top 5 themes weighted by customer revenue, one verbatim per theme, and SHIP/STUDY/HOLD/KILL proposal per theme. Per product/SKILL.md." \
    "business-os-product"

# 7. Marketing — daily content radar (07:30).
create \
    "30 7 * * *" \
    "Marketing — Content radar" \
    "Read the radar output above. Pick the top 3 angles by ICP relevance. For each, suggest pillar (teardown/how-to/build-in-public) and target keyword. If no signals, [SILENT]." \
    "business-os-marketing" \
    "$SCRIPT_DIR/scripts/content_radar.py"

# 8. Marketing — Tue + Thu blog draft kickoff.
create \
    "0 8 * * 2,4" \
    "Marketing — Blog draft prompt" \
    "Read latest ~/.hermes/business-os/content-ideas/. Surface the top 3 picks; ask which to draft. If founder approves, draft using templates/blog-brief.md as a subagent." \
    "business-os-marketing"

# 9. Marketing — Friday newsletter draft.
create \
    "0 9 * * 5" \
    "Marketing — Friday newsletter draft" \
    "Draft this week's newsletter per marketing/SKILL.md > 'Newsletter'. Pull this week's blog + Linear closed items + product changelog. Deliver as DRAFT for founder review." \
    "business-os-marketing"

# 10. Sales — daily CRM hygiene (08:00).
create \
    "0 8 * * 1-5" \
    "Sales — CRM hygiene" \
    "Run the daily CRM hygiene check from sales/SKILL.md. Auto-fix deterministic issues. Surface stalls + missing fields as a <5min checklist. If clean, [SILENT]." \
    "business-os-sales" \
    "$SCRIPT_DIR/scripts/pipeline_health.py"

# 11. Sales — weekly pipeline review (Mon 08:30).
create \
    "30 8 * * 1" \
    "Sales — Pipeline review" \
    "Produce the weekly pipeline review per sales/SKILL.md. Include stage movement, weighted forecast, top 5 deals, stalls. Format for founder skim in <2 min." \
    "business-os-sales" \
    "$SCRIPT_DIR/scripts/pipeline_health.py"

# 12. Customer service — every 15 min ticket triage.
create \
    "*/15 * * * *" \
    "Customer service — Ticket triage" \
    "Check Intercom for new tickets. For each: classify, severity, customer context, route or DRAFT response. Only ping me on P0/P1 or DRAFTS awaiting review. Otherwise [SILENT]." \
    "business-os-customer-service"

# 13. Customer service — weekly at-risk review (Fri 14:00).
create \
    "0 14 * * 5" \
    "Customer service — At-risk review" \
    "Read churn signal output above. For each red/yellow account, summarize signals + propose intervention. HUMAN tier if intervention >\$1k value." \
    "business-os-customer-service" \
    "$SCRIPT_DIR/scripts/churn_signals.py"

# 14. Operations — hourly vendor status check.
create \
    "0 * * * *" \
    "Operations — Vendor status check" \
    "Check status pages of P0/P1 vendors per state/vendors.yaml. If any reports incident, alert + assess our exposure. Otherwise [SILENT]." \
    "business-os-operations"

# 15. Operations — weekly runbook freshness audit (Sun 21:00).
create \
    "0 21 * * 0" \
    "Operations — Runbook freshness" \
    "Per operations/SKILL.md, audit runbook last-touched + last-executed. List any stale ones with proposed updates. If all fresh, [SILENT]." \
    "business-os-operations"

# 16. Finance — daily revenue pulse (06:00).
create \
    "0 6 * * *" \
    "Finance — Revenue pulse" \
    "Read Stripe data above. Compute yesterday's MRR delta, failed payments, trial conversions. Update state/kpis.yaml deterministically. If significant move (>\$500) or failed payment from >\$1k customer, alert. Otherwise [SILENT]." \
    "business-os-finance" \
    "$SCRIPT_DIR/scripts/morning_brief.py"

# 17. Finance — weekly spend audit (Mon 09:30).
create \
    "30 9 * * 1" \
    "Finance — Spend audit" \
    "Read finance_pulse output above. Surface: top 5 categories, any category up >30% WoW, new vendors, big-charge alerts. Cross-check against state/vendors.yaml." \
    "business-os-finance" \
    "$SCRIPT_DIR/scripts/finance_pulse.py"

# 18. Finance — monthly close (1st of month, 08:00).
create \
    "0 8 1 * *" \
    "Finance — Monthly close" \
    "Run monthly close per finance/SKILL.md. Produce P&L, MRR walk, cohort retention triangle, top wins/losses, runway. Save to ~/.hermes/business-os/finance/close-YYYY-MM.md." \
    "business-os-finance" \
    "$SCRIPT_DIR/scripts/finance_pulse.py --days 30"

# 19. Finance — monthly self/investor update (5th, 09:00).
create \
    "0 9 5 * *" \
    "Finance — Self/investor update draft" \
    "Draft the monthly update using templates/investor-update.md. Pull last month's close. Honest about misses. Deliver as DRAFT for founder review." \
    "business-os-finance"

# 20. Engineering — weekly tech-debt audit (Sun 22:00).
create \
    "0 22 * * 0" \
    "Engineering — Tech debt audit" \
    "Grep repo for TODO/FIXME/XXX + deprecated APIs + outdated packages. Compare to last week. If grew >10%, surface list with cleanup PR proposals." \
    "business-os-engineering"

echo ""
echo "✓ Done. List installed jobs: hermes cron list"
echo "  Edit a job:                 hermes cron edit <id>"
echo "  Disable a job:              hermes cron disable <id>"
