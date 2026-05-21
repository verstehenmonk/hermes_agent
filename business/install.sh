#!/usr/bin/env bash
# Install business cron jobs and webhooks via the hermes CLI.
# Idempotent: removes any previously-installed jobs/webhooks with the same name
# before re-creating them.
#
# Usage:
#   business/install.sh              # install cron + webhooks
#   business/install.sh --cron       # cron only
#   business/install.sh --webhooks   # webhooks only
#   business/install.sh --dry-run    # print the hermes commands without running

set -euo pipefail

cd "$(dirname "$0")/.."

WHAT="all"
DRY=0
for arg in "$@"; do
  case "$arg" in
    --cron) WHAT="cron" ;;
    --webhooks) WHAT="webhooks" ;;
    --dry-run) DRY=1 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes CLI not found on PATH. Install: https://hermes-agent.nousresearch.com/docs/" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 required for parsing the yaml manifests." >&2
  exit 1
fi

run() {
  if [[ "$DRY" -eq 1 ]]; then
    printf 'DRY: '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

install_cron() {
  echo "==> Installing cron jobs from business/cron.yaml"
  python3 - <<'PY' | while IFS= read -r cmd; do
import json, sys, shlex
try:
    import yaml  # type: ignore
except ImportError:
    print("# pip install pyyaml (or use the venv where hermes lives)", file=sys.stderr)
    sys.exit(2)
data = yaml.safe_load(open("business/cron.yaml"))
for job in data.get("jobs", []):
    args = ["hermes", "cron", "create", job["schedule"], job["prompt"], "--name", job["name"]]
    if job.get("script"):
        args += ["--script", job["script"]]
    for skill in job.get("skills", []) or []:
        args += ["--skill", skill]
    if job.get("deliver"):
        args += ["--deliver", job["deliver"]]
    for s in job.get("silent_on", []) or []:
        args += ["--silent-on", s]
    print(" ".join(shlex.quote(a) for a in args))
PY
    eval set -- $cmd
    name_idx=$(( $# - 0 ))
    # Best-effort idempotency: try to remove by name first.
    name=""
    args=("$@")
    for ((i=0; i<${#args[@]}; i++)); do
      if [[ "${args[i]}" == "--name" ]]; then name="${args[i+1]}"; break; fi
    done
    if [[ -n "$name" ]]; then
      run hermes cron delete --name "$name" 2>/dev/null || true
    fi
    run "${args[@]}"
  done
}

install_webhooks() {
  echo "==> Installing webhooks from business/webhooks.yaml"
  python3 - <<'PY' | while IFS= read -r cmd; do
import sys, shlex
try:
    import yaml  # type: ignore
except ImportError:
    print("# pip install pyyaml", file=sys.stderr); sys.exit(2)
data = yaml.safe_load(open("business/webhooks.yaml"))
for hook in data.get("webhooks", []):
    args = ["hermes", "webhook", "subscribe", hook["name"],
            "--prompt", hook["prompt"]]
    for ev in hook.get("events", []) or []:
        args += ["--events", ev]
    if hook.get("source"):
        args += ["--source", hook["source"]]
    if hook.get("filter"):
        args += ["--filter", hook["filter"]]
    for skill in hook.get("skills", []) or []:
        args += ["--skill", skill]
    if hook.get("deliver"):
        args += ["--deliver", hook["deliver"]]
    print(" ".join(shlex.quote(a) for a in args))
PY
    eval set -- $cmd
    name="$2"  # webhook subscribe <name>
    run hermes webhook unsubscribe "$name" 2>/dev/null || true
    run "$@"
  done
}

case "$WHAT" in
  all)      install_cron; install_webhooks ;;
  cron)     install_cron ;;
  webhooks) install_webhooks ;;
esac

echo
echo "Done. Verify with:"
echo "  hermes cron list"
echo "  hermes webhook list"
