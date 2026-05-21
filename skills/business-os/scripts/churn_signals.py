#!/usr/bin/env python3
"""
Churn signal detection.

Computes per-customer health scores from product usage (PostHog), support
tickets (Intercom), and billing data (Stripe). Outputs sorted list of
at-risk accounts with the signals that caused each ranking.

Used by customer-service skill's weekly at-risk review.
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


def fetch_paid_customers() -> list[dict]:
    """List Stripe active subscriptions with customer metadata."""
    key = os.environ.get("STRIPE_API_KEY")
    if not key:
        raise SystemExit("STRIPE_API_KEY not set")
    headers = {"Authorization": f"Bearer {key}"}
    subs = http_get("https://api.stripe.com/v1/subscriptions?status=active&limit=100&expand[]=data.customer", headers)
    out = []
    for s in subs.get("data", []):
        cust = s.get("customer") or {}
        plan = (s.get("plan") or {})
        if not isinstance(cust, dict):
            continue
        out.append({
            "customer_id": cust.get("id"),
            "email": cust.get("email"),
            "name": cust.get("name") or cust.get("email"),
            "mrr": (plan.get("amount", 0) / 100.0) if plan.get("interval") == "month" else (plan.get("amount", 0) / 100.0 / 12.0),
            "created": s.get("created"),
        })
    return out


def fetch_posthog_active_users(customer_email_domain: str | None) -> int:
    """Best-effort WAU lookup. Returns 0 if unavailable."""
    key = os.environ.get("POSTHOG_API_KEY")
    host = os.environ.get("POSTHOG_HOST", "https://app.posthog.com")
    project = os.environ.get("POSTHOG_PROJECT_ID")
    if not (key and project and customer_email_domain):
        return 0
    # Simplified: count events from this domain in last 7 days. Real impl would
    # use a saved insight; the agent can be told to verify.
    headers = {"Authorization": f"Bearer {key}"}
    try:
        url = f"{host}/api/projects/{project}/events?distinct_id__icontains={customer_email_domain}&limit=1"
        http_get(url, headers)
        return 1  # placeholder presence signal
    except OSError:
        return 0


def fetch_recent_tickets(email: str) -> dict:
    """Count tickets in last 30 days for this customer."""
    token = os.environ.get("INTERCOM_TOKEN")
    if not (token and email):
        return {"count": 0, "negative": 0}
    headers = {"Authorization": f"Bearer {token}", "Intercom-Version": "2.11"}
    body = {
        "query": {
            "operator": "AND",
            "value": [
                {"field": "source.author.email", "operator": "=", "value": email},
                {"field": "created_at", "operator": ">", "value": int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())},
            ],
        }
    }
    try:
        data = json.loads(
            urlopen(
                Request(
                    "https://api.intercom.io/conversations/search",
                    data=json.dumps(body).encode("utf-8"),
                    headers={**headers, "Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=10,
            ).read().decode("utf-8")
        )
        convos = data.get("conversations", [])
        negative = sum(
            1 for c in convos
            if any(t.get("name") in {"churn_signal", "pricing_concern", "bug"}
                   for t in c.get("tags", {}).get("tags", []))
        )
        return {"count": len(convos), "negative": negative}
    except OSError:
        return {"count": 0, "negative": 0}


def score_customer(c: dict) -> dict:
    """Compute a 0-100 health score. Higher = healthier."""
    score = 50
    notes = []

    email = c.get("email") or ""
    domain = email.split("@", 1)[1] if "@" in email else None

    wau = fetch_posthog_active_users(domain)
    if wau == 0:
        score -= 25
        notes.append("no_recent_activity")
    else:
        score += 15

    tickets = fetch_recent_tickets(email)
    if tickets["negative"] > 0:
        score -= 15 * tickets["negative"]
        notes.append(f"negative_tickets_{tickets['negative']}")
    elif tickets["count"] == 0:
        score -= 5  # zero engagement is mild red flag
        notes.append("zero_support_contact")
    else:
        score += 5

    if c.get("mrr", 0) >= 1000:
        score += 5  # bigger accounts get a bit more benefit of the doubt
        notes.append("high_value")

    score = max(0, min(100, score))
    color = "green" if score >= 70 else "yellow" if score >= 40 else "red"
    return {
        "customer_id": c.get("customer_id"),
        "name": c.get("name"),
        "mrr": round(c.get("mrr", 0), 2),
        "score": score,
        "color": color,
        "signals": notes,
    }


def main() -> int:
    try:
        customers = fetch_paid_customers()
    except (SystemExit, OSError) as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 1

    scored = [score_customer(c) for c in customers]
    scored.sort(key=lambda x: x["score"])

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "customers": scored,
        "red_count": sum(1 for s in scored if s["color"] == "red"),
        "yellow_count": sum(1 for s in scored if s["color"] == "yellow"),
        "green_count": sum(1 for s in scored if s["color"] == "green"),
        "at_risk_revenue": round(sum(s["mrr"] for s in scored if s["color"] in {"red", "yellow"}), 2),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
