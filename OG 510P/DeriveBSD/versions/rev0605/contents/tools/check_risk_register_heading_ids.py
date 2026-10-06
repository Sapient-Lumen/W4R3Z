#!/usr/bin/env python3
"""Ensure risk-register item identifiers are unique.

Why:
  The long-form risk register uses heading ids (``## 63) ...``) as stable
  references in generated context packs and review summaries. If an id is
  reused, generated indexes can silently fork one item identity into two topics
  and downstream references become ambiguous.

Rule:
  - Scan ``docs/266-open-questions-and-risk-register.md`` for item headings of
    the form ``## <number>[suffix]) ...``.
  - Reject duplicate ids across both open and ``[DECIDED]`` sections.
  - Accept suffixed insertions such as ``22a`` or ``62a``; those are explicit
    stable ids, not duplicates of the base numeric item.

Usage:
  python3 tools/check_risk_register_heading_ids.py

Exit codes:
  0: ok
  1: duplicate item id found
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "266-open-questions-and-risk-register.md"
ITEM_HEAD_RE = re.compile(r"^##\s+(?P<id>\d+[a-z]?)\)\s+(?P<title>.+?)\s*$")


def main() -> int:
    text = SRC.read_text(encoding="utf-8", errors="replace")
    seen: dict[str, tuple[int, str]] = {}
    duplicates: dict[str, list[tuple[int, str]]] = defaultdict(list)

    for line_no, line in enumerate(text.splitlines(), 1):
        m = ITEM_HEAD_RE.match(line)
        if not m:
            continue
        item_id = m.group("id")
        title = m.group("title")
        if item_id in seen:
            duplicates[item_id].append(seen[item_id])
            duplicates[item_id].append((line_no, title))
        else:
            seen[item_id] = (line_no, title)

    if duplicates:
        print("Risk-register heading id check FAILED.")
        print("docs/266-open-questions-and-risk-register.md reuses stable item ids:")
        for item_id, entries in sorted(duplicates.items(), key=lambda kv: (int(re.match(r"\d+", kv[0]).group(0)), kv[0])):
            print(f"- {item_id}:")
            # Preserve order while removing accidental duplicate reports for ids
            # with more than two repeated headings.
            emitted: set[tuple[int, str]] = set()
            for line_no, title in entries:
                if (line_no, title) in emitted:
                    continue
                emitted.add((line_no, title))
                print(f"  - line {line_no}: {title}")
        return 1

    print(f"Risk-register heading id check OK ({len(seen)} unique item ids)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
