#!/usr/bin/env python3
"""
Morning brief pre-processor.

Runs BEFORE the agent's turn (Hermes cron `--script` flag). Pulls overnight
data from external systems and emits a structured JSON blob to stdout. The
agent reads this JSON, combines it with state/kpis.yaml + CHARTER.md, and
produces the brief.

Modes:
  morning  — overnight deltas, decisions queue (default)
  eod      — end-of-day digest
  weekly   — Mon morning longer review

Every API call is wrapped: on failure the script logs the error to
~/.hermes/business-os/logs/morning_brief.log and continues with partial data.
The agent is told which sources failed so the brief can still go out.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
LOG_DIR = HERMES_HOME / "business-os" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "morning_brief.log"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    with LOG_FILE.open("a") as f:
        f.write(f"{ts} {msg}\n")


def http_get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 10) -> Any:
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post_json(url: str, body: dict, headers: dict[str, str] | None = None, timeout: int = 10) -> Any:
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers={**(headers or {}), "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def safe(name: str, fn):
    """Run fn(); on exception, log + return {error: ...}."""
    try:
        return fn()
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError, KeyError) as e:
        log(f"[{name}] {type(e).__name__}: {e}")
        return {"error": f"{type(e).__name__}: {e}"}


def fetch_stripe_revenue_delta() -> dict:
    """Yesterday's new + churned MRR via Stripe."""
    key = os.environ.get("STRIPE_API_KEY")
    if not key:
        return {"error": "STRIPE_API_KEY not set"}

    yesterday_ts = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())
    auth = {"Authorization": f"Bearer {key}"}

    # New subscriptions created since yesterday.
    new = http_get_json(
        f"https://api.stripe.com/v1/subscriptions?status=active&created[gte]={yesterday_ts}&limit=100",
        headers=auth,
    )
    new_mrr = sum(
        (item["plan"]["amount"] / 100.0) if item.get("plan", {}).get("interval") == "month"
        else (item["plan"]["amount"] / 100.0 / 12.0)
        for item in new.get("data", [])
        if item.get("plan")
    )

    # Canceled subscriptions since yesterday.
    canceled = http_get_json(
        f"https://api.stripe.com/v1/subscriptions?status=canceled&canceled_at[gte]={yesterday_ts}&limit=100",
        headers=auth,
    )
    churn_mrr = sum(
        (item["plan"]["amount"] / 100.0) if item.get("plan", {}).get("interval") == "month"
        else (item["plan"]["amount"] / 100.0 / 12.0)
        for item in canceled.get("data", [])
        if item.get("plan")
    )

    # Failed payments in last 24h.
    failed = http_get_json(
        f"https://api.stripe.com/v1/charges?created[gte]={yesterday_ts}&limit=100",
        headers=auth,
    )
    failed_count = sum(1 for c in failed.get("data", []) if c.get("status") == "failed")

    return {
        "new_mrr_yesterday": round(new_mrr, 2),
        "churn_mrr_yesterday": round(churn_mrr, 2),
        "failed_payments_24h": failed_count,
        "new_subs_yesterday": len(new.get("data", [])),
    }


def fetch_linear_summary() -> dict:
    """Issues created / completed in last 24h + PRs awaiting review."""
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        return {"error": "LINEAR_API_KEY not set"}

    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    query = {
        "query": (
            "query($since: DateTime!) {"
            "  created: issues(filter: { createdAt: { gte: $since } }, first: 100) {"
            "    nodes { identifier title priority state { type } }"
            "  }"
            "  completed: issues(filter: { completedAt: { gte: $since } }, first: 100) {"
            "    nodes { identifier title }"
            "  }"
            "  triage: issues(filter: { state: { type: { eq: \"triage\" } } }, first: 50) {"
            "    nodes { identifier title priority }"
            "  }"
            "}"
        ),
        "variables": {"since": since},
    }
    data = http_post_json("https://api.linear.app/graphql", query, headers={"Authorization": key})
    d = data.get("data", {})
    return {
        "created_24h": len(d.get("created", {}).get("nodes", [])),
        "completed_24h": len(d.get("completed", {}).get("nodes", [])),
        "triage_count": len(d.get("triage", {}).get("nodes", [])),
        "triage_top": [
            f"{n['identifier']}: {n['title']}"
            for n in d.get("triage", {}).get("nodes", [])[:3]
        ],
    }


def fetch_github_prs() -> dict:
    """Open PRs in the repo, especially review-requested ones."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("BUSINESS_OS_REPO")  # owner/name
    if not token or not repo:
        return {"error": "GITHUB_TOKEN or BUSINESS_OS_REPO not set"}

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    prs = http_get_json(f"https://api.github.com/repos/{repo}/pulls?state=open", headers=headers)
    open_count = len(prs)
    awaiting_review = sum(1 for p in prs if p.get("requested_reviewers") or p.get("requested_teams"))
    return {
        "open_prs": open_count,
        "awaiting_review": awaiting_review,
        "stalest_pr_days": max(
            (
                (datetime.now(timezone.utc) - datetime.fromisoformat(p["updated_at"].replace("Z", "+00:00"))).days
                for p in prs
            ),
            default=0,
        ),
    }


def fetch_support_summary() -> dict:
    """Open Intercom tickets + first-response SLA breach count."""
    token = os.environ.get("INTERCOM_TOKEN")
    if not token:
        return {"error": "INTERCOM_TOKEN not set"}

    headers = {"Authorization": f"Bearer {token}", "Intercom-Version": "2.11"}
    # Open conversations
    body = {
        "query": {
            "operator": "AND",
            "value": [
                {"field": "open", "operator": "=", "value": True},
            ],
        }
    }
    data = http_post_json("https://api.intercom.io/conversations/search", body, headers=headers)
    convos = data.get("conversations", [])
    open_count = len(convos)
    now = int(time.time())
    breached = sum(
        1 for c in convos
        if c.get("waiting_since") and (now - int(c["waiting_since"])) > 60 * 60
    )
    return {"open_tickets": open_count, "sla_breached_1h": breached}


def fetch_pipeline_summary() -> dict:
    """Pipeline value + stage stalls from HubSpot."""
    key = os.environ.get("HUBSPOT_API_KEY")
    if not key:
        return {"error": "HUBSPOT_API_KEY not set"}

    headers = {"Authorization": f"Bearer {key}"}
    deals = http_get_json(
        "https://api.hubapi.com/crm/v3/objects/deals?limit=100&properties=amount,dealstage,hs_lastmodifieddate",
        headers=headers,
    )
    total = 0.0
    stalled = 0
    now = datetime.now(timezone.utc)
    for d in deals.get("results", []):
        props = d.get("properties", {})
        try:
            amt = float(props.get("amount") or 0)
        except (TypeError, ValueError):
            amt = 0.0
        if props.get("dealstage") not in {"closedwon", "closedlost"}:
            total += amt
            last_mod = props.get("hs_lastmodifieddate")
            if last_mod:
                last_mod_dt = datetime.fromisoformat(last_mod.replace("Z", "+00:00"))
                if (now - last_mod_dt).days > 14:
                    stalled += 1
    return {
        "open_pipeline_total": round(total, 2),
        "stalled_deals_14d": stalled,
    }


def fetch_runway_check() -> dict:
    """Read state/kpis.yaml for cash position. Returns minimal slice."""
    state_path = Path(__file__).resolve().parent.parent / "state" / "kpis.yaml"
    if not state_path.exists():
        return {"error": "state/kpis.yaml missing"}
    text = state_path.read_text()
    # Minimal grep — avoids requiring PyYAML.
    out = {}
    for line in text.splitlines():
        s = line.strip()
        for key in ("bank_balance", "monthly_burn", "runway_months"):
            if s.startswith(f"{key}:"):
                try:
                    out[key] = float(s.split(":", 1)[1].strip())
                except ValueError:
                    pass
    return out


def build(mode: str) -> dict:
    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "sources": {},
    }
    payload["sources"]["stripe"] = safe("stripe", fetch_stripe_revenue_delta)
    payload["sources"]["linear"] = safe("linear", fetch_linear_summary)
    payload["sources"]["github"] = safe("github", fetch_github_prs)
    payload["sources"]["support"] = safe("support", fetch_support_summary)
    payload["sources"]["pipeline"] = safe("pipeline", fetch_pipeline_summary)
    payload["sources"]["finance_local"] = safe("finance_local", fetch_runway_check)
    payload["errors"] = [k for k, v in payload["sources"].items() if isinstance(v, dict) and "error" in v]
    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["morning", "eod", "weekly"], default="morning")
    args = p.parse_args()
    payload = build(args.mode)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
