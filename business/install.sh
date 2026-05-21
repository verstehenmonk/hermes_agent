#!/usr/bin/env bash
# Install business cron jobs and webhooks via the hermes CLI.
#
# Idempotent: removes any previously-installed jobs/webhooks with the same
# name before re-creating them, by looking the job_id up via
# `hermes cron list`.
#
# Also installs the deterministic Python scripts into
# ~/.hermes/scripts/business/ — Hermes' cron runner restricts script paths
# to that directory tree.
#
# Usage:
#   business/install.sh              # install scripts + cron + webhooks
#   business/install.sh --scripts    # scripts only
#   business/install.sh --cron       # cron only
#   business/install.sh --webhooks   # webhooks only
#   business/install.sh --dry-run    # print the hermes commands without running

set -euo pipefail

cd "$(dirname "$0")/.."

WHAT="all"
DRY=0
for arg in "$@"; do
  case "$arg" in
    --scripts)  WHAT="scripts" ;;
    --cron)     WHAT="cron" ;;
    --webhooks) WHAT="webhooks" ;;
    --dry-run)  DRY=1 ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
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

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SCRIPTS_DEST="$HERMES_HOME/scripts/business"

install_scripts() {
  echo "==> Installing scripts to $SCRIPTS_DEST"
  if [[ "$DRY" -eq 1 ]]; then
    echo "DRY: mkdir -p $SCRIPTS_DEST"
    echo "DRY: cp business/scripts/*.py $SCRIPTS_DEST/"
  else
    mkdir -p "$SCRIPTS_DEST"
    cp business/scripts/*.py "$SCRIPTS_DEST/"
    chmod +x "$SCRIPTS_DEST"/*.py
  fi
}

# Delegate the heavy lifting to Python — invoking hermes directly via
# subprocess avoids any shell-quoting / newline-splitting hazards from
# multi-line YAML prompt blocks.
install_cron_and_webhooks() {
  DRY="$DRY" WHAT="$WHAT" python3 - <<'PY'
import os
import shlex
import subprocess
import sys

try:
    import yaml  # type: ignore
except ImportError:
    sys.stderr.write("install requires PyYAML — run: pip install pyyaml\n")
    sys.exit(2)

DRY = os.environ.get("DRY") == "1"
WHAT = os.environ.get("WHAT", "all")


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess | None:
    pretty = " ".join(shlex.quote(c) for c in cmd)
    if DRY:
        print(f"DRY: {pretty}")
        return None
    return subprocess.run(cmd, check=False, text=True, capture_output=capture)


def find_cron_job_id(name: str) -> str | None:
    """Best-effort: scan `hermes cron list` for a job matching name."""
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"], check=False, text=True, capture_output=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    job_id: str | None = None
    for line in result.stdout.splitlines():
        # Lines tend to look like "ID: <id>  Name: <name>  Schedule: ..."
        if "ID:" in line:
            parts = line.split()
            for i, tok in enumerate(parts):
                if tok == "ID:" and i + 1 < len(parts):
                    job_id = parts[i + 1].rstrip(",")
        if name and name in line and job_id:
            return job_id
    return None


def install_cron(jobs: list[dict]) -> None:
    print("==> Installing cron jobs from business/cron.yaml")
    for job in jobs:
        name = job["name"]
        existing = find_cron_job_id(name)
        if existing:
            run(["hermes", "cron", "remove", existing])

        cmd = ["hermes", "cron", "create", job["schedule"], job["prompt"], "--name", name]
        if job.get("script"):
            cmd += ["--script", job["script"]]
        for skill in job.get("skills") or []:
            cmd += ["--skill", skill]
        if job.get("deliver"):
            cmd += ["--deliver", job["deliver"]]
        run(cmd)


def install_webhooks(hooks: list[dict]) -> None:
    print("==> Installing webhooks from business/webhooks.yaml")
    for hook in hooks:
        name = hook["name"]
        # Idempotency: remove any existing subscription with this name first.
        run(["hermes", "webhook", "remove", name], capture=True)

        cmd = ["hermes", "webhook", "subscribe", name, "--prompt", hook["prompt"]]
        events = hook.get("events") or []
        if events:
            cmd += ["--events", ",".join(events)]
        skills = hook.get("skills") or []
        if skills:
            cmd += ["--skills", ",".join(skills)]
        if hook.get("deliver"):
            cmd += ["--deliver", hook["deliver"]]
        if hook.get("description"):
            cmd += ["--description", hook["description"]]
        run(cmd)


if WHAT in ("all", "cron"):
    data = yaml.safe_load(open("business/cron.yaml")) or {}
    install_cron(data.get("jobs") or [])

if WHAT in ("all", "webhooks"):
    data = yaml.safe_load(open("business/webhooks.yaml")) or {}
    install_webhooks(data.get("webhooks") or [])
PY
}

case "$WHAT" in
  all)
    install_scripts
    install_cron_and_webhooks
    ;;
  scripts)
    install_scripts
    ;;
  cron|webhooks)
    install_cron_and_webhooks
    ;;
esac

echo
echo "Done. Verify with:"
echo "  hermes cron list"
echo "  hermes webhook list"
