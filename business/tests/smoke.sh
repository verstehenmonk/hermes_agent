#!/usr/bin/env bash
# Hermes Business OS smoke test.
# Runs the bundle through validation without touching real APIs or sending
# anything customer-facing.
#
# Usage: ./business/tests/smoke.sh

set -euo pipefail

BIZ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

pass() { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m  ✗\033[0m %s\n' "$*"; FAIL=1; }
log()  { printf '\033[1;34m[smoke]\033[0m %s\n' "$*"; }

# ----- 1. Bootstrap dry-run -------------------------------------------
log "1. bootstrap dry-run"
if "$BIZ_DIR/bootstrap.sh" --dry-run >/dev/null 2>&1; then
    pass "bootstrap --dry-run exits clean"
else
    fail "bootstrap --dry-run failed"
fi

# ----- 2. Every personality has valid frontmatter ----------------------
log "2. personalities"
for p in "$BIZ_DIR"/personalities/*.md; do
    name="$(basename "$p" .md)"
    if head -1 "$p" | grep -qF -- '---'; then
        pass "personality $name has frontmatter"
    else
        fail "personality $name missing frontmatter"
    fi
done

# ----- 3. Every cron template is valid JSON with required fields ------
log "3. cron templates"
for j in "$BIZ_DIR"/cron-templates/*.json; do
    name="$(basename "$j" .json)"
    if ! jq empty "$j" 2>/dev/null; then
        fail "cron $name is not valid JSON"
        continue
    fi
    for field in name schedule personality prompt deliver model phase; do
        if [[ "$(jq -r ".$field // empty" "$j")" == "" ]]; then
            fail "cron $name missing field: $field"
            continue 2
        fi
    done
    pass "cron $name validates"
done

# ----- 4. Every webhook template is valid JSON with required fields ---
log "4. webhook templates"
for w in "$BIZ_DIR"/webhook-templates/*.json; do
    name="$(basename "$w" .json)"
    if ! jq empty "$w" 2>/dev/null; then
        fail "webhook $name is not valid JSON"
        continue
    fi
    for field in name events source personality prompt deliver model phase; do
        if [[ "$(jq -r ".$field // empty" "$w")" == "" ]]; then
            fail "webhook $name missing field: $field"
            continue 2
        fi
    done
    pass "webhook $name validates"
done

# ----- 5. Every cron/webhook references an existing personality -------
log "5. personality references resolve"
mapfile -t PERSONALITIES < <(
    for p in "$BIZ_DIR"/personalities/*.md; do basename "$p" .md; done
)
in_personalities() {
    local target="$1"
    for p in "${PERSONALITIES[@]}"; do [[ "$p" == "$target" ]] && return 0; done
    return 1
}

for j in "$BIZ_DIR"/cron-templates/*.json "$BIZ_DIR"/webhook-templates/*.json; do
    name="$(basename "$j" .json)"
    p="$(jq -r .personality "$j")"
    if in_personalities "$p"; then
        pass "$name → $p"
    else
        fail "$name references unknown personality: $p"
    fi
done

# ----- 6. SOPs referenced from prompts exist --------------------------
log "6. SOP references in prompts"
mapfile -t SOPS < <(
    cd "$BIZ_DIR" && find sops -name '*.md' -type f
)
sop_exists() {
    local target="$1"
    for s in "${SOPS[@]}"; do [[ "$s" == "$target" ]] && return 0; done
    return 1
}

for j in "$BIZ_DIR"/cron-templates/*.json "$BIZ_DIR"/webhook-templates/*.json; do
    name="$(basename "$j" .json)"
    refs="$(grep -oE 'business/sops/[a-zA-Z0-9_/-]+\.md' "$j" 2>/dev/null | sort -u || true)"
    if [[ -z "$refs" ]]; then continue; fi
    while read -r ref; do
        local_path="${ref#business/}"
        if sop_exists "$local_path"; then
            pass "$name → $ref"
        else
            fail "$name references missing SOP: $ref"
        fi
    done <<<"$refs"
done

# ----- 7. Knowledge base files exist ----------------------------------
log "7. knowledge base"
for required in company.md product-spec.md runbook.md kpis.yaml stack.md; do
    if [[ -f "$BIZ_DIR/knowledge-base/$required" ]]; then
        pass "knowledge-base/$required exists"
    else
        fail "knowledge-base/$required missing"
    fi
done

# ----- 8. Custom skill manifests are valid ----------------------------
log "8. custom skills"
for s in "$BIZ_DIR"/skills/*/SKILL.md; do
    name="$(basename "$(dirname "$s")")"
    if head -1 "$s" | grep -qF -- '---'; then
        pass "skill $name has SKILL.md frontmatter"
    else
        fail "skill $name SKILL.md missing frontmatter"
    fi
done

# ----- 9. Fixtures are present and load ------------------------------
log "9. test fixtures"
for f in "$BIZ_DIR"/tests/fixtures/*.json; do
    [[ -e "$f" ]] || { fail "no fixtures present"; break; }
    name="$(basename "$f")"
    if jq empty "$f" 2>/dev/null; then
        pass "fixture $name parses"
    else
        fail "fixture $name is not valid JSON"
    fi
done

# ----- 10. No secrets committed --------------------------------------
# Match real-looking keys (long base64/hex tails), not the placeholder strings
# documented in .env.example or SKILL.md examples.
log "10. secret scan"
SUSPECT="$(grep -rlE '(sk_live_|rk_live_)[A-Za-z0-9]{16,}|xoxb-[0-9]+-[0-9]+-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}' "$BIZ_DIR" \
    --exclude-dir=tests --exclude='.env.example' --exclude='SKILL.md' 2>/dev/null || true)"
if [[ -z "$SUSPECT" ]]; then
    pass "no obvious secrets in business/"
else
    fail "potential secrets found in: $SUSPECT"
fi

# ----- summary --------------------------------------------------------
echo
if [[ "$FAIL" -eq 0 ]]; then
    printf '\033[1;32m✓ all smoke tests passed\033[0m\n'
    exit 0
else
    printf '\033[1;31m✗ smoke tests failed\033[0m\n'
    exit 1
fi
