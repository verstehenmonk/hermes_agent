#!/usr/bin/env python3
"""
Pipeline health pre-processor.

Used by the sales skill's weekly review. Pulls the full open pipeline from
HubSpot, classifies stalls, computes stage-by-stage conversion against
state/sales_stages.yaml targets, and emits a structured JSON blob.

Stdout is the agent's input. Stderr is for the operator.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def http_get(url: str, headers: dict[str, str]) -> dict:
    req = Request(url, headers=headers)
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_stages() -> dict:
    """Parse sales_stages.yaml without requiring PyYAML — only the bits we need."""
    p = Path(__file__).resolve().parent.parent / "state" / "sales_stages.yaml"
    if not p.exists():
        return {}
    out: dict[str, dict] = {}
    current: dict | None = None
    for line in p.read_text().splitlines():
        s = line.rstrip()
        if s.startswith("  - id:"):
            if current is not None and "name" in current:
                out[current["name"]] = current
            current = {"id": s.split(":", 1)[1].strip()}
        elif current is not None and ":" in s:
            stripped = s.strip()
            k, _, v = stripped.partition(":")
            current[k.strip()] = v.strip().strip('"')
    if current is not None and "name" in current:
        out[current["name"]] = current
    return out


def fetch_deals() -> list[dict]:
    key = os.environ.get("HUBSPOT_API_KEY")
    if not key:
        raise SystemExit("HUBSPOT_API_KEY not set")
    url = (
        "https://api.hubapi.com/crm/v3/objects/deals?limit=100"
        "&properties=amount,dealstage,dealname,hs_lastmodifieddate,closedate,createdate,hubspot_owner_id"
    )
    deals: list[dict] = []
    next_url: str | None = url
    while next_url:
        data = http_get(next_url, headers={"Authorization": f"Bearer {key}"})
        deals.extend(data.get("results", []))
        paging = data.get("paging", {}).get("next", {})
        next_url = paging.get("link")
    return deals


def main() -> int:
    stages = load_stages()
    try:
        deals = fetch_deals()
    except (SystemExit, OSError) as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 1

    now = datetime.now(timezone.utc)

    by_stage: dict[str, dict] = {}
    stalled: list[dict] = []
    closing_soon: list[dict] = []

    for d in deals:
        props = d.get("properties", {})
        stage = props.get("dealstage", "unknown")
        try:
            amt = float(props.get("amount") or 0)
        except (TypeError, ValueError):
            amt = 0.0

        if stage in {"closedwon", "closedlost"}:
            continue

        by_stage.setdefault(stage, {"count": 0, "value": 0.0})
        by_stage[stage]["count"] += 1
        by_stage[stage]["value"] += amt

        last_mod = props.get("hs_lastmodifieddate")
        if last_mod:
            last_mod_dt = datetime.fromisoformat(last_mod.replace("Z", "+00:00"))
            age_days = (now - last_mod_dt).days
            if age_days > 14:
                stalled.append({
                    "id": d["id"],
                    "name": props.get("dealname"),
                    "stage": stage,
                    "value": amt,
                    "days_stalled": age_days,
                })

        closedate = props.get("closedate")
        if closedate:
            cd = datetime.fromisoformat(closedate.replace("Z", "+00:00"))
            days_to_close = (cd - now).days
            if 0 <= days_to_close <= 14:
                closing_soon.append({
                    "id": d["id"],
                    "name": props.get("dealname"),
                    "stage": stage,
                    "value": amt,
                    "days_to_close": days_to_close,
                })

    out = {
        "generated_at": now.isoformat(),
        "by_stage": {k: {"count": v["count"], "value": round(v["value"], 2)} for k, v in by_stage.items()},
        "total_open_value": round(sum(v["value"] for v in by_stage.values()), 2),
        "total_open_count": sum(v["count"] for v in by_stage.values()),
        "stalled_14d": sorted(stalled, key=lambda x: -x["value"])[:10],
        "closing_within_14d": sorted(closing_soon, key=lambda x: x["days_to_close"]),
        "stage_targets": {k: {"target_conversion_to_next": v.get("target_conversion_to_next")} for k, v in stages.items()},
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
