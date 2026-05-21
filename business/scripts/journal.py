#!/usr/bin/env python3
"""
Journal utility — append entries to the decisions / incidents / standup logs.

Used by skills via `journal.py <kind> [--review-in DAYS] -` where stdin is the
entry body. Writes are atomic (write-temp + os.replace) for one-shot files and
fcntl-locked for append-only logs.

Kinds:
  decision    - append to journal/decisions.md (fcntl-locked append)
  incident    - write journal/incidents/<date>-<slug>.md (atomic)
  standup     - write journal/<date>-standup.md (atomic)
  weekly      - write journal/<YYYY-Www>-weekly.md (atomic)
  monthly     - write journal/finance/<YYYY-MM>.md (atomic)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.platform != "win32":
    import fcntl
else:
    fcntl = None  # type: ignore[assignment]

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
JOURNAL = HERMES_HOME / "business" / "journal"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "untitled"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)


def locked_append(path: Path, content: str) -> None:
    """Append with an exclusive fcntl lock so concurrent skills don't interleave."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        if fcntl is not None:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(content)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        else:
            # Windows fallback — best-effort, no locking.
            f.write(content)


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
            # Machine-readable; rituals grep for ^review_by:.
            review_line = f"\nreview_by: {review_date}\n"
        entry = f"\n## {today} — {args.title or 'decision'}\n\n{body.strip()}\n{review_line}"
        locked_append(path, entry)
        print(str(path))
        return 0

    if args.kind == "incident":
        path = JOURNAL / "incidents" / f"{today}-{slugify(args.title)}.md"
        atomic_write(path, f"# Incident: {args.title}\n\n_Started {now.isoformat()}_\n\n{body.strip()}\n")
        print(str(path))
        return 0

    if args.kind == "standup":
        path = JOURNAL / f"{today}-standup.md"
        atomic_write(path, body)
        print(str(path))
        return 0

    if args.kind == "weekly":
        iso_year, iso_week, _ = now.isocalendar()
        path = JOURNAL / f"{iso_year}-W{iso_week:02d}-weekly.md"
        atomic_write(path, body)
        print(str(path))
        return 0

    if args.kind == "monthly":
        path = JOURNAL / "finance" / f"{now.strftime('%Y-%m')}.md"
        atomic_write(path, body)
        print(str(path))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
