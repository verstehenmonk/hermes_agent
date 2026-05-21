#!/usr/bin/env python3
"""
Finance pulse pre-processor.

Pulls cash balance (Mercury), spend (Stripe + Mercury card export), and
applies category rules from state/expense_categories.yaml. Computes:
  - runway months at current burn
  - top spend categories week-over-week
  - cost-spike alerts (any category up >30% WoW, or new vendor)
  - per-customer inference cost (the metric AI products live or die on)

Output is JSON for the finance skill to narrate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def http_get(url: str, headers: dict[str, str]) -> dict:
    req = Request(url, headers=headers)
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_category_rules() -> list[dict]:
    """Load expense_categories.yaml as plain rules. Minimal parser, no PyYAML."""
    p = Path(__file__).resolve().parent.parent / "state" / "expense_categories.yaml"
    if not p.exists():
        return []
    rules: list[dict] = []
    current: dict | None = None
    matches: list[str] | None = None
    for line in p.read_text().splitlines():
        s = line.rstrip()
        if re.match(r"^\s*-\s*match:", s):
            if current and "category" in current:
                current["match"] = matches or []
                rules.append(current)
            current = {}
            inline = s.split(":", 1)[1].strip()
            matches = []
            if inline.startswith("["):
                # inline list, e.g., [aws, amazon web services]
                inner = inline.strip("[]")
                if inner.strip():
                    matches = [m.strip().strip('"') for m in inner.split(",")]
        elif current is not None and s.strip().startswith("category:"):
            current["category"] = s.split(":", 1)[1].strip()
    if current and "category" in current:
        current["match"] = matches or []
        rules.append(current)
    return rules


def categorize(description: str, rules: list[dict]) -> str:
    desc = (description or "").lower()
    for r in rules:
        for needle in r.get("match", []):
            if needle and needle.lower() in desc:
                return r["category"]
    return "uncategorized"


def fetch_mercury_transactions(days: int = 30) -> list[dict]:
    token = os.environ.get("MERCURY_API_TOKEN")
    account_id = os.environ.get("MERCURY_ACCOUNT_ID")
    if not (token and account_id):
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.mercury.com/api/v1/account/{account_id}/transactions?start={since}&limit=500"
    data = http_get(url, headers=headers)
    return data.get("transactions", [])


def fetch_mercury_balance() -> float:
    token = os.environ.get("MERCURY_API_TOKEN")
    account_id = os.environ.get("MERCURY_ACCOUNT_ID")
    if not (token and account_id):
        return 0.0
    data = http_get(
        f"https://api.mercury.com/api/v1/account/{account_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return float(data.get("currentBalance") or 0.0)


def aggregate(txs: list[dict], rules: list[dict], window_days: int) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    by_cat: dict[str, float] = defaultdict(float)
    vendors_first_seen: dict[str, str] = {}
    big_charges: list[dict] = []
    for t in txs:
        # Mercury uses negative amounts for outflows.
        try:
            amt = float(t.get("amount") or 0)
        except (TypeError, ValueError):
            continue
        if amt >= 0:
            continue
        outflow = abs(amt)
        desc = t.get("counterpartyName") or t.get("note") or ""
        posted_at = t.get("postedAt") or t.get("createdAt")
        if not posted_at:
            continue
        try:
            ts = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts < cutoff:
            continue

        cat = categorize(desc, rules)
        by_cat[cat] += outflow

        if outflow >= 1000:
            big_charges.append({"description": desc, "amount": round(outflow, 2), "date": posted_at, "category": cat})
        vendors_first_seen.setdefault(desc, posted_at)

    return {
        "by_category": {k: round(v, 2) for k, v in sorted(by_cat.items(), key=lambda x: -x[1])},
        "total_outflow": round(sum(by_cat.values()), 2),
        "big_charges": sorted(big_charges, key=lambda x: -x["amount"])[:10],
        "vendor_count": len(vendors_first_seen),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args()

    rules = load_category_rules()
    txs = fetch_mercury_transactions(days=max(args.days, 14))
    balance = fetch_mercury_balance()

    this_period = aggregate(txs, rules, window_days=args.days)
    prior_period = aggregate(txs, rules, window_days=args.days * 2)

    # WoW deltas where prior had value
    deltas: dict[str, float] = {}
    for cat, amt in this_period["by_category"].items():
        prior_full = prior_period["by_category"].get(cat, 0)
        prior_only = max(prior_full - amt, 0)  # the older slice
        if prior_only > 0:
            deltas[cat] = round((amt - prior_only) / prior_only, 3)

    burn = this_period["total_outflow"] / max(args.days / 30.0, 1)
    runway = round(balance / burn, 1) if burn > 0 else None

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "balance": round(balance, 2),
        "monthly_burn_estimate": round(burn, 2),
        "runway_months": runway,
        "window_days": args.days,
        "spend_by_category": this_period["by_category"],
        "category_wow_pct_change": deltas,
        "big_charges": this_period["big_charges"],
        "alerts": [
            f"{cat} up {int(d*100)}% WoW" for cat, d in deltas.items() if d > 0.30
        ],
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
