#!/usr/bin/env python3
"""
Categorize the last N hours of Gmail into buckets the agent can act on.

Writes ~/.hermes/business/inbox/latest.json with shape:
  {
    "generated_at": "...",
    "window_hours": 12,
    "buckets": {
      "urgent": [...],
      "customer": [...],
      "sales": [...],
      "vendor": [...],
      "noise": [...]
    },
    "counts": {...}
  }

This is deterministic categorization based on senders/subjects/labels.
The agent reads the JSON, picks what needs founder attention, and drafts
replies for the rest.

Auth: uses the Gmail API with a service account or OAuth refresh token via
GMAIL_OAUTH_REFRESH_TOKEN + GMAIL_CLIENT_ID + GMAIL_CLIENT_SECRET. If those
aren't set, the script writes a "not_connected" sentinel.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
OUT_PATH = HERMES_HOME / "business" / "inbox" / "latest.json"
TIMEOUT = 15

CUSTOMER_DOMAINS = set(filter(None, os.environ.get("CUSTOMER_DOMAINS", "").split(",")))
VENDOR_DOMAINS = {
    "stripe.com", "mercury.com", "vercel.com", "github.com", "linear.app",
    "sentry.io", "posthog.com", "notion.so", "resend.com", "loops.so",
    "cal.com", "attio.com", "plain.com", "vanta.com", "iubenda.com",
}
NOISE_PATTERNS = re.compile(
    r"(newsletter|unsubscribe|digest|weekly recap|sale ends|promo|webinar)",
    re.I,
)
URGENT_PATTERNS = re.compile(
    r"(urgent|asap|down|outage|broke[nl]?|can't (login|access|pay)|refund|cancel|chargeback|legal|subpoena)",
    re.I,
)
SALES_PATTERNS = re.compile(
    r"(demo|pricing|trial|interested in|quote|how much|enterprise|team plan)",
    re.I,
)


def get_access_token() -> str | None:
    rt = os.environ.get("GMAIL_OAUTH_REFRESH_TOKEN")
    cid = os.environ.get("GMAIL_CLIENT_ID")
    cs = os.environ.get("GMAIL_CLIENT_SECRET")
    if not (rt and cid and cs):
        return None
    body = urllib.parse.urlencode({
        "client_id": cid,
        "client_secret": cs,
        "refresh_token": rt,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data.get("access_token")


def gmail_get(path: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        f"https://gmail.googleapis.com/gmail/v1/users/me/{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def extract_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def categorize(sender: str, subject: str, snippet: str, labels: list[str]) -> str:
    sender_domain = sender.split("@")[-1].strip(">").lower() if "@" in sender else ""
    text = f"{subject} {snippet}"

    if URGENT_PATTERNS.search(text):
        return "urgent"
    if "CATEGORY_PROMOTIONS" in labels or NOISE_PATTERNS.search(text):
        return "noise"
    if sender_domain in CUSTOMER_DOMAINS:
        return "customer"
    if SALES_PATTERNS.search(text):
        return "sales"
    if sender_domain in VENDOR_DOMAINS:
        return "vendor"
    if "INBOX" in labels and "CATEGORY_PERSONAL" in labels:
        return "customer"
    return "noise"


def main() -> int:
    window_hours = int(os.environ.get("INBOX_WINDOW_HOURS", "12"))

    token = get_access_token()
    if not token:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "not_connected",
            "missing": ["GMAIL_OAUTH_REFRESH_TOKEN", "GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET"],
        }, indent=2))
        print("gmail not connected; wrote sentinel", file=sys.stderr)
        return 0

    query = f"newer_than:{window_hours}h in:inbox"
    listing = gmail_get(f"messages?q={urllib.parse.quote(query)}&maxResults=100", token)
    msg_ids = [m["id"] for m in listing.get("messages", [])]

    buckets: dict[str, list[dict]] = {
        "urgent": [], "customer": [], "sales": [], "vendor": [], "noise": [],
    }

    for mid in msg_ids:
        msg = gmail_get(f"messages/{mid}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date", token)
        headers = msg.get("payload", {}).get("headers", [])
        sender = extract_header(headers, "From")
        subject = extract_header(headers, "Subject")
        snippet = msg.get("snippet", "")
        labels = msg.get("labelIds", [])
        bucket = categorize(sender, subject, snippet, labels)
        buckets[bucket].append({
            "id": mid,
            "from": sender,
            "subject": subject,
            "snippet": snippet[:200],
            "thread_id": msg.get("threadId"),
        })

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": window_hours,
        "buckets": buckets,
        "counts": {k: len(v) for k, v in buckets.items()},
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(
        f"inbox: {out['counts']} → {OUT_PATH}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
