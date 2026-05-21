#!/usr/bin/env python3
"""
Content radar — daily topic mining.

Mines content ideas from:
  - HackerNews top stories (filter for analytics/SaaS/AI)
  - r/SaaS new posts asking "anyone using" / "how do you" / "what's the best"
  - Last 24h support tickets tagged 'confusion' (each confusion = a blog post)

Emits a markdown file with 10 ranked angles. Saved both to stdout (so the
agent sees it) and to ~/.hermes/business-os/content-ideas/YYYY-MM-DD.md.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
OUT_DIR = HERMES_HOME / "business-os" / "content-ideas"
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = [
    "analytics", "product analytics", "saas", "b2b", "metrics", "mrr",
    "churn", "retention", "cohort", "amplitude", "mixpanel", "posthog",
    "llm", "ai", "agent", "dashboard", "north star",
]


def http_get_json(url: str, headers: dict | None = None) -> any:
    req = Request(url, headers=headers or {"User-Agent": "business-os-radar"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def hn_top() -> list[dict]:
    """Top 50 HN stories; filter by keyword match."""
    try:
        ids = http_get_json("https://hacker-news.firebaseio.com/v0/topstories.json")[:50]
    except OSError:
        return []
    results = []
    for sid in ids:
        try:
            item = http_get_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        except OSError:
            continue
        title = (item.get("title") or "").lower()
        if any(k in title for k in KEYWORDS):
            results.append({
                "source": "HackerNews",
                "title": item.get("title"),
                "url": item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                "score": item.get("score"),
            })
    return results


def reddit_questions(subreddit: str) -> list[dict]:
    """Recent posts in a subreddit asking 'anyone using' / 'how do you'."""
    try:
        data = http_get_json(
            f"https://www.reddit.com/r/{subreddit}/new.json?limit=50",
            headers={"User-Agent": "business-os-radar/1.0"},
        )
    except OSError:
        return []
    out = []
    patterns = [r"anyone using", r"how do you", r"what(?:'s|s| is) the best", r"recommendations? for"]
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        title = (post.get("title") or "").lower()
        if any(re.search(p, title) for p in patterns):
            out.append({
                "source": f"r/{subreddit}",
                "title": post.get("title"),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "score": post.get("score"),
            })
    return out


def confusion_signals() -> list[dict]:
    """Pull last 24h support tickets tagged 'confusion' from local feedback log."""
    p = HERMES_HOME / "business-os" / "feedback"
    if not p.exists():
        return []
    cutoff = datetime.now(timezone.utc).date().isoformat()
    out = []
    for f in sorted(p.glob("*.md"))[-7:]:
        text = f.read_text(errors="ignore")
        for line in text.splitlines():
            if "confusion" in line.lower() and cutoff[:7] in line:
                out.append({"source": "support", "title": line.strip(), "url": str(f)})
    return out[:20]


def rank(items: list[dict]) -> list[dict]:
    """Score: confusion signals > reddit > HN, and prefer recent."""
    src_weight = {"support": 3, "r/SaaS": 2, "r/ProductManagement": 2, "r/analytics": 2, "HackerNews": 1}
    return sorted(items, key=lambda x: -src_weight.get(x.get("source", ""), 0))[:15]


def to_markdown(items: list[dict]) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    lines = [f"# Content radar — {today}", ""]
    lines.append("Top angles to consider for the next 2–4 blog posts. Pick one and the agent will draft.")
    lines.append("")
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. **{item.get('title')}** _{item.get('source')}_  ")
        lines.append(f"   → {item.get('url')}")
        lines.append("")
    if not items:
        lines.append("(no signals today — check API keys or widen sources)")
    return "\n".join(lines)


def main() -> int:
    items: list[dict] = []
    items += hn_top()
    items += reddit_questions("SaaS")
    items += reddit_questions("ProductManagement")
    items += reddit_questions("analytics")
    items += confusion_signals()
    ranked = rank(items)
    md = to_markdown(ranked)

    today = datetime.now(timezone.utc).date().isoformat()
    out_path = OUT_DIR / f"{today}.md"
    out_path.write_text(md)

    print(md)
    print(f"\nSaved to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
