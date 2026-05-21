#!/usr/bin/env python3
"""
Deterministic metrics snapshot for the business operating system.

Pulls live numbers from Stripe, Mercury, PostHog, Sentry, Linear, GitHub.
Writes a single JSON blob the agent reads — so the agent never computes numbers.

Usage:
    metrics_snapshot.py            # daily snapshot to latest.json
    metrics_snapshot.py --month-close   # full monthly snapshot to YYYY-MM.json
    metrics_snapshot.py --verify   # print the snapshot to stdout instead of writing

Degrades gracefully: if a tool's API key is missing, that section is marked
"not_connected" and the rest of the snapshot still runs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
OUT_DIR = HERMES_HOME / "business" / "metrics"
TIMEOUT = 15


def _http_json(url: str, headers: dict[str, str], data: bytes | None = None) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=headers, data=data, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get(url: str, *, auth: str | None = None, bearer: str | None = None) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if auth:
        headers["Authorization"] = auth
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    return _http_json(url, headers)


def section_stripe() -> dict[str, Any]:
    key = os.environ.get("STRIPE_API_KEY")
    if not key:
        return {"status": "not_connected"}
    try:
        subs = _get(
            "https://api.stripe.com/v1/subscriptions?status=active&limit=100",
            bearer=key,
        )
        mrr_cents = 0
        active = 0
        for s in subs.get("data", []):
            active += 1
            for item in s.get("items", {}).get("data", []):
                price = item.get("price") or {}
                unit = price.get("unit_amount") or 0
                interval = (price.get("recurring") or {}).get("interval")
                qty = item.get("quantity") or 1
                amount = unit * qty
                if interval == "year":
                    amount = amount / 12
                elif interval == "week":
                    amount = amount * (52 / 12)
                elif interval == "day":
                    amount = amount * (365 / 12)
                mrr_cents += int(amount)

        since = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
        events = _get(
            f"https://api.stripe.com/v1/events?created[gte]={since}&limit=100",
            bearer=key,
        )
        failed = 0
        refunded_cents = 0
        for ev in events.get("data", []):
            t = ev.get("type", "")
            obj = (ev.get("data") or {}).get("object") or {}
            if t == "invoice.payment_failed":
                failed += 1
            elif t == "charge.refunded":
                refunded_cents += obj.get("amount_refunded") or 0

        return {
            "status": "ok",
            "mrr_usd": round(mrr_cents / 100, 2),
            "active_subscriptions": active,
            "failed_payments_24h": failed,
            "refunded_24h_usd": round(refunded_cents / 100, 2),
        }
    except urllib.error.HTTPError as e:
        return {"status": "error", "detail": f"stripe http {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"stripe: {e!r}"}


def section_mercury() -> dict[str, Any]:
    key = os.environ.get("MERCURY_API_KEY")
    if not key:
        return {"status": "not_connected"}
    try:
        accounts = _get("https://api.mercury.com/api/v1/accounts", bearer=key)
        total_cents = 0
        for a in accounts.get("accounts", []):
            total_cents += int(round((a.get("currentBalance") or 0) * 100))
        return {
            "status": "ok",
            "cash_usd": round(total_cents / 100, 2),
            "account_count": len(accounts.get("accounts", [])),
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"mercury: {e!r}"}


def section_posthog() -> dict[str, Any]:
    key = os.environ.get("POSTHOG_API_KEY")
    host = os.environ.get("POSTHOG_HOST", "https://us.posthog.com")
    project = os.environ.get("POSTHOG_PROJECT_ID")
    if not key or not project:
        return {"status": "not_connected"}
    try:
        url = f"{host}/api/projects/{project}/insights/trend"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = json.dumps({
            "events": [{"id": "core_action_completed", "math": "dau"}],
            "date_from": "-7d",
            "interval": "day",
        }).encode()
        data = _http_json(url, headers, payload)
        series = (data.get("result") or [{}])[0].get("data") or []
        return {
            "status": "ok",
            "core_actions_7d": series,
            "core_actions_7d_total": int(sum(series)),
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"posthog: {e!r}"}


def section_sentry() -> dict[str, Any]:
    token = os.environ.get("SENTRY_AUTH_TOKEN")
    org = os.environ.get("SENTRY_ORG")
    project = os.environ.get("SENTRY_PROJECT")
    if not token or not org or not project:
        return {"status": "not_connected"}
    try:
        url = (
            f"https://sentry.io/api/0/projects/{org}/{project}/issues/"
            "?statsPeriod=24h&query=is:unresolved&limit=20"
        )
        data = _http_json(url, {"Authorization": f"Bearer {token}"})
        issues = data if isinstance(data, list) else data.get("data", [])
        return {
            "status": "ok",
            "unresolved_24h": len(issues),
            "top_issues": [
                {"title": i.get("title"), "count": i.get("count"), "id": i.get("id")}
                for i in issues[:5]
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"sentry: {e!r}"}


def section_linear() -> dict[str, Any]:
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        return {"status": "not_connected"}
    try:
        url = "https://api.linear.app/graphql"
        headers = {"Authorization": key, "Content-Type": "application/json"}
        query = """
        query {
          p0: issues(filter: {priority: {eq: 1}, state: {type: {nin: ["completed","canceled"]}}}) { nodes { id } }
          p1: issues(filter: {priority: {eq: 2}, state: {type: {nin: ["completed","canceled"]}}}) { nodes { id } }
          blockers: issues(filter: {labels: {name: {eq: "customer-blocker"}}, state: {type: {nin: ["completed","canceled"]}}}) { nodes { id title url } }
        }
        """
        payload = json.dumps({"query": query}).encode()
        data = _http_json(url, headers, payload).get("data", {})
        return {
            "status": "ok",
            "open_p0": len((data.get("p0") or {}).get("nodes") or []),
            "open_p1": len((data.get("p1") or {}).get("nodes") or []),
            "customer_blockers": [
                {"title": n.get("title"), "url": n.get("url")}
                for n in (data.get("blockers") or {}).get("nodes") or []
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"linear: {e!r}"}


def section_github() -> dict[str, Any]:
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO")  # e.g. "owner/name"
    if not token or not repo:
        return {"status": "not_connected"}
    try:
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100&sort=updated&direction=desc"
        prs = _http_json(url, {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        if not isinstance(prs, list):
            return {"status": "error", "detail": f"github: {prs!r}"}
        merged_7d = sum(
            1 for p in prs
            if p.get("merged_at") and p["merged_at"] >= since
        )
        now = datetime.now(timezone.utc)
        open_prs = [p for p in prs if p.get("state") == "open"]
        oldest_hours = 0
        if open_prs:
            ts = min(
                datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))
                for p in open_prs
            )
            oldest_hours = int((now - ts).total_seconds() / 3600)
        return {
            "status": "ok",
            "open_prs": len(open_prs),
            "merged_7d": merged_7d,
            "oldest_open_pr_hours": oldest_hours,
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "detail": f"github: {e!r}"}


def deltas(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    """Compute deltas vs previous snapshot for headline numbers."""
    out: dict[str, Any] = {}
    cur_stripe = current.get("stripe", {})
    prev_stripe = previous.get("stripe", {})
    if cur_stripe.get("status") == "ok" and prev_stripe.get("status") == "ok":
        out["mrr_delta_usd"] = round(
            (cur_stripe.get("mrr_usd", 0) - prev_stripe.get("mrr_usd", 0)), 2
        )
    cur_cash = current.get("mercury", {}).get("cash_usd")
    prev_cash = previous.get("mercury", {}).get("cash_usd")
    if cur_cash is not None and prev_cash is not None:
        out["cash_delta_usd"] = round(cur_cash - prev_cash, 2)
    return out


def runway_months(snapshot: dict[str, Any]) -> float | None:
    """Naive runway: cash / 3-month rolling burn. Reads previous monthly snapshots."""
    cash = snapshot.get("mercury", {}).get("cash_usd")
    if cash is None:
        return None
    monthly_files = sorted(OUT_DIR.glob("20*-*.json"))[-3:]
    if not monthly_files:
        return None
    burns = []
    for i in range(len(monthly_files) - 1):
        a = json.loads(monthly_files[i].read_text())
        b = json.loads(monthly_files[i + 1].read_text())
        a_cash = a.get("mercury", {}).get("cash_usd")
        b_cash = b.get("mercury", {}).get("cash_usd")
        if a_cash and b_cash and a_cash > b_cash:
            burns.append(a_cash - b_cash)
    if not burns:
        return None
    avg_burn = sum(burns) / len(burns)
    return round(cash / avg_burn, 1) if avg_burn > 0 else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month-close", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    snapshot: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stripe": section_stripe(),
        "mercury": section_mercury(),
        "posthog": section_posthog(),
        "sentry": section_sentry(),
        "linear": section_linear(),
        "github": section_github(),
    }

    prev_path = OUT_DIR / "latest.json"
    if prev_path.exists():
        try:
            previous = json.loads(prev_path.read_text())
            snapshot["deltas"] = deltas(snapshot, previous)
        except Exception:
            pass

    rw = runway_months(snapshot)
    if rw is not None:
        snapshot["runway_months"] = rw

    if args.verify:
        json.dump(snapshot, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prev_path.write_text(json.dumps(snapshot, indent=2, default=str))

    if args.month_close:
        ym = datetime.now(timezone.utc).strftime("%Y-%m")
        (OUT_DIR / f"{ym}.json").write_text(json.dumps(snapshot, indent=2, default=str))

    print(f"wrote {prev_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
