#!/usr/bin/env python3
"""Ensure release/discovery headings do not reuse a release identifier.

Why:
  `docs/00-index.md` is the human discovery map for archive releases. A
  duplicate `## New in <version>` heading silently forks one release id into two
  unrelated bodies, making anchors ambiguous and causing reviewers to miss one
  of the sections. `CHANGELOG.md` has the same stable-identifier role for
  release history.

Rule:
  - `CHANGELOG.md` must not repeat a `## <version>` heading.
  - `docs/00-index.md` must not repeat a `## New in <version>` heading.

Usage:
  python3 tools/check_release_heading_uniqueness.py

Exit codes:
  0: ok
  1: a release identifier is reused in either release surface
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
INDEX = ROOT / "docs" / "00-index.md"

CHANGELOG_HDR_RE = re.compile(r"^##\s+(?P<ver>\d{4}-\d{2}-\d{2}r\d+)\b", re.MULTILINE)
INDEX_HDR_RE = re.compile(r"^##\s+New in\s+(?P<ver>\d{4}-\d{2}-\d{2}r\d+)\b", re.MULTILINE)


def _duplicates(path: Path, pattern: re.Pattern[str]) -> dict[str, list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    counts = Counter(m.group("ver") for m in pattern.finditer(text))
    repeated = {ver for ver, count in counts.items() if count > 1}
    if not repeated:
        return {}

    lines_by_ver: dict[str, list[int]] = defaultdict(list)
    for m in pattern.finditer(text):
        ver = m.group("ver")
        if ver in repeated:
            lines_by_ver[ver].append(text.count("\n", 0, m.start()) + 1)
    return dict(lines_by_ver)


def main() -> int:
    errors: list[str] = []

    for path, pattern, label in [
        (CHANGELOG, CHANGELOG_HDR_RE, "CHANGELOG.md"),
        (INDEX, INDEX_HDR_RE, "docs/00-index.md"),
    ]:
        if not path.exists():
            errors.append(f"missing {label}")
            continue
        dups = _duplicates(path, pattern)
        for ver, lines in sorted(dups.items()):
            line_list = ", ".join(str(n) for n in lines)
            errors.append(f"{label} repeats release heading {ver} on lines {line_list}")

    if errors:
        print("Release heading uniqueness check FAILED.")
        for error in errors:
            print("-", error)
        return 1

    print("Release heading uniqueness check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
