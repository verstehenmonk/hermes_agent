#!/usr/bin/env bash
# Hermes Business OS bootstrap.
# Idempotent installer. Reads business/manifest.yaml and installs only the
# phases that are enabled.
#
# Usage:
#   ./business/bootstrap.sh           # install
#   ./business/bootstrap.sh --dry-run # show what would be installed
#   ./business/bootstrap.sh --force   # overwrite existing personalities/crons

set -euo pipefail

DRY_RUN=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --force)   FORCE=1 ;;
        --help|-h)
            sed -n '2,12p' "$0"
            exit 0
            ;;
    esac
done

BIZ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
CONFIG_FILE="${HERMES_CONFIG:-$HERMES_HOME/cli-config.yaml}"
CRON_FILE="$HERMES_HOME/cron/jobs.json"
WEBHOOK_FILE="$HERMES_HOME/webhook_subscriptions.json"
SECRETS_DIR="$HERMES_HOME/secrets"

log() { printf '\033[1;34m[bootstrap]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
err()  { printf '\033[1;31m[err]\033[0m %s\n' "$*" >&2; }

need() {
    command -v "$1" >/dev/null 2>&1 || { err "missing dependency: $1"; exit 1; }
}

need jq
need python3
python3 -c 'import yaml' 2>/dev/null || { err "missing python dependency: pyyaml (pip install pyyaml)"; exit 1; }

# Small wrappers so we don't depend on a particular yq flavor.
yaml_to_json() {
    python3 -c 'import sys, yaml, json; json.dump(yaml.safe_load(sys.stdin), sys.stdout)'
}
yaml_get() {
    # usage: yaml_get <file> '<python expression on d>'
    python3 -c "
import sys, yaml
d = yaml.safe_load(open('$1'))
print($2)
"
}
yaml_set_personality() {
    # usage: yaml_set_personality <config_file> <name> <body>
    python3 - "$1" "$2" "$3" <<'PY'
import sys, yaml
config_file, name, body = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open(config_file) as f:
        cfg = yaml.safe_load(f) or {}
except FileNotFoundError:
    cfg = {}
cfg.setdefault("agent", {}).setdefault("personalities", {})[name] = body
with open(config_file, "w") as f:
    yaml.safe_dump(cfg, f, default_flow_style=False, sort_keys=False)
PY
}

# ----- 1. Sanity checks --------------------------------------------------
log "checking environment"

if [[ ! -f "$BIZ_DIR/manifest.yaml" ]]; then
    err "manifest.yaml not found at $BIZ_DIR/manifest.yaml"
    exit 1
fi

mkdir -p "$HERMES_HOME" "$HERMES_HOME/cron" "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR" 2>/dev/null || true

# ----- 2. Resolve which phases are active --------------------------------
mapfile -t ACTIVE_PHASES < <(
    python3 -c "
import yaml
d = yaml.safe_load(open('$BIZ_DIR/manifest.yaml'))
for k, v in (d.get('phases') or {}).items():
    if v: print(k)
"
)
log "active phases: ${ACTIVE_PHASES[*]:-none}"

phase_active() {
    local p="$1"
    for active in "${ACTIVE_PHASES[@]}"; do
        [[ "$active" == "$p" ]] && return 0
    done
    return 1
}

# ----- 3. Install personalities into cli-config.yaml --------------------
log "installing personalities"

if [[ ! -f "$CONFIG_FILE" ]]; then
    warn "config file $CONFIG_FILE does not exist yet"
    warn "run 'hermes setup' first, then re-run this script"
    if [[ "$DRY_RUN" -eq 0 ]]; then
        exit 1
    fi
fi

for p_file in "$BIZ_DIR"/personalities/*.md; do
    [[ -e "$p_file" ]] || continue
    p_name="$(basename "$p_file" .md)"
    # Strip YAML frontmatter for the system prompt; the body after the
    # second '---' is what becomes the personality overlay.
    p_body="$(awk 'BEGIN{n=0} /^---$/{n++; next} n==2{print}' "$p_file")"

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "  would install personality: $p_name (${#p_body} chars)"
        continue
    fi

    yaml_set_personality "$CONFIG_FILE" "$p_name" "$p_body"
    log "  installed personality: $p_name"
done

# ----- 4. Install cron templates ----------------------------------------
log "installing cron templates"

if [[ -f "$CRON_FILE" ]]; then
    EXISTING_JOBS="$(jq '.jobs // []' "$CRON_FILE")"
else
    EXISTING_JOBS='[]'
fi

NEW_JOBS="$EXISTING_JOBS"

for j_file in "$BIZ_DIR"/cron-templates/*.json; do
    [[ -e "$j_file" ]] || continue
    j_name="$(jq -r '.name' "$j_file")"
    j_phase="$(jq -r '.phase' "$j_file")"

    if ! phase_active "$j_phase"; then
        log "  skip cron $j_name (phase $j_phase inactive)"
        continue
    fi

    # Strip the phase field — Hermes doesn't know about it
    j_clean="$(jq 'del(.phase)' "$j_file")"

    # Replace if name matches, else append. --force replaces unconditionally.
    EXISTS="$(echo "$NEW_JOBS" | jq --arg n "$j_name" '[.[] | select(.name == $n)] | length')"
    if [[ "$EXISTS" -gt 0 && "$FORCE" -eq 0 ]]; then
        log "  cron $j_name already installed (use --force to overwrite)"
        continue
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "  would install cron: $j_name"
        continue
    fi

    NEW_JOBS="$(echo "$NEW_JOBS" | jq --argjson new "$j_clean" --arg n "$j_name" \
        '[.[] | select(.name != $n)] + [$new]')"
    log "  installed cron: $j_name"
done

if [[ "$DRY_RUN" -eq 0 ]]; then
    jq -n --argjson jobs "$NEW_JOBS" '{jobs: $jobs}' > "$CRON_FILE.tmp"
    mv "$CRON_FILE.tmp" "$CRON_FILE"
fi

# ----- 5. Install webhook templates -------------------------------------
log "installing webhook templates"

if [[ -f "$WEBHOOK_FILE" ]]; then
    EXISTING_HOOKS="$(jq '.routes // []' "$WEBHOOK_FILE")"
else
    EXISTING_HOOKS='[]'
fi

NEW_HOOKS="$EXISTING_HOOKS"

for w_file in "$BIZ_DIR"/webhook-templates/*.json; do
    [[ -e "$w_file" ]] || continue
    w_name="$(jq -r '.name' "$w_file")"
    w_phase="$(jq -r '.phase' "$w_file")"

    if ! phase_active "$w_phase"; then
        log "  skip webhook $w_name (phase $w_phase inactive)"
        continue
    fi

    w_clean="$(jq 'del(.phase)' "$w_file")"
    EXISTS="$(echo "$NEW_HOOKS" | jq --arg n "$w_name" '[.[] | select(.name == $n)] | length')"
    if [[ "$EXISTS" -gt 0 && "$FORCE" -eq 0 ]]; then
        log "  webhook $w_name already installed (use --force)"
        continue
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "  would install webhook: $w_name"
        continue
    fi

    NEW_HOOKS="$(echo "$NEW_HOOKS" | jq --argjson new "$w_clean" --arg n "$w_name" \
        '[.[] | select(.name != $n)] + [$new]')"
    log "  installed webhook: $w_name"
done

if [[ "$DRY_RUN" -eq 0 ]]; then
    jq -n --argjson routes "$NEW_HOOKS" '{routes: $routes}' > "$WEBHOOK_FILE.tmp"
    mv "$WEBHOOK_FILE.tmp" "$WEBHOOK_FILE"
fi

# ----- 6. Symlink the knowledge base into AGENTS.md context -------------
log "wiring knowledge base into AGENTS.md context"

KB_MARKER_START="<!-- BEGIN business/knowledge-base auto-include -->"
KB_MARKER_END="<!-- END business/knowledge-base auto-include -->"
AGENTS_FILE="$BIZ_DIR/../AGENTS.md"

if [[ -f "$AGENTS_FILE" && "$DRY_RUN" -eq 0 ]]; then
    if ! grep -qF "$KB_MARKER_START" "$AGENTS_FILE"; then
        {
            echo
            echo "$KB_MARKER_START"
            echo "# Business knowledge base"
            echo
            echo "The following files describe the company. Every agent turn"
            echo "should treat them as ground truth before reasoning."
            echo
            for kb in "$BIZ_DIR"/knowledge-base/*.md "$BIZ_DIR"/knowledge-base/*.yaml; do
                [[ -e "$kb" ]] || continue
                echo "- @business/knowledge-base/$(basename "$kb")"
            done
            echo
            echo "$KB_MARKER_END"
        } >> "$AGENTS_FILE"
        log "  appended KB block to AGENTS.md"
    else
        log "  KB block already present in AGENTS.md"
    fi
fi

# ----- 7. Register custom skills ----------------------------------------
log "registering custom skills"
# Hermes auto-discovers ~/.hermes/skills/* and the repo's skills/ — we symlink
# our custom skills into the user skills dir so they're reachable from any
# repo using this Hermes install.
USER_SKILLS="$HERMES_HOME/skills"
mkdir -p "$USER_SKILLS"

for skill_dir in "$BIZ_DIR"/skills/*/; do
    [[ -e "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    link="$USER_SKILLS/$skill_name"
    if [[ -L "$link" || -e "$link" ]]; then
        log "  skill $skill_name already registered"
    elif [[ "$DRY_RUN" -eq 0 ]]; then
        ln -s "$skill_dir" "$link"
        log "  symlinked skill: $skill_name → $link"
    else
        log "  would symlink skill: $skill_name"
    fi
done

# ----- 8. Done -----------------------------------------------------------
log "done."
if [[ "$DRY_RUN" -eq 1 ]]; then
    log "(dry-run — nothing was written)"
else
    cat <<EOF

Next steps:
  1. Edit business/knowledge-base/company.md — every agent reads it
  2. Run 'hermes gateway setup' to wire Slack
  3. Run 'hermes gateway start' to start receiving
  4. Verify with 'hermes cron list' and 'hermes cron run-now daily-eng-standup'
  5. Smoke-test: ./business/tests/smoke.sh
EOF
fi
