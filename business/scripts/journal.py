#!/usr/bin/env python3
"""
Journal utility — append entries to the decisions / incidents / standup logs.

Used by skills via `journal.py <kind> [--review-in DAYS] -` where stdin is the
entry body. Keeps writes consistent and atomic.

Kinds:
  decision    - append to journal/decisions.md
  incident    - append to journal/incidents/<date>-<slug>.md
  standup     - write journal/<date>-standup.md
  weekly      - write journal/<YYYY-Www>-weekly.md
  monthly     - write journal/finance/<YYYY-MM>.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
JOURNAL = HERMES_HOME / "business" / "journal"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "untitled"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["decision", "incident", "standup", "weekly", "monthly"])
    p.add_argument("--title", default="")
    p.add_argument("--review-in", type=int, default=None,
                   help="For decisions: schedule a review in N days")
    p.add_argument("body", nargs="?", default="-",
                   help="Body text. Use '-' (default) to read stdin.")
    args = p.parse_args()

    body = sys.stdin.read() if args.body == "-" else args.body
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    JOURNAL.mkdir(parents=True, exist_ok=True)

    if args.kind == "decision":
        path = JOURNAL / "decisions.md"
        review_line = ""
        if args.review_in:
            review_date = (now + timedelta(days=args.review_in)).strftime("%Y-%m-%d")
            review_line = f"\n_review by {review_date}_"
        entry = f"\n## {today} — {args.title or 'decision'}\n\n{body.strip()}\n{review_line}\n"
        with path.open("a") as f:
            f.write(entry)
        print(str(path))
        return 0

    if args.kind == "incident":
        (JOURNAL / "incidents").mkdir(parents=True, exist_ok=True)
        path = JOURNAL / "incidents" / f"{today}-{slugify(args.title)}.md"
        path.write_text(f"# Incident: {args.title}\n\n_Started {now.isoformat()}_\n\n{body.strip()}\n")
        print(str(path))
        return 0

    if args.kind == "standup":
        path = JOURNAL / f"{today}-standup.md"
        path.write_text(body)
        print(str(path))
        return 0

    if args.kind == "weekly":
        iso_year, iso_week, _ = now.isocalendar()
        path = JOURNAL / f"{iso_year}-W{iso_week:02d}-weekly.md"
        path.write_text(body)
        print(str(path))
        return 0

    if args.kind == "monthly":
        (JOURNAL / "finance").mkdir(parents=True, exist_ok=True)
        path = JOURNAL / "finance" / f"{now.strftime('%Y-%m')}.md"
        path.write_text(body)
        print(str(path))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
