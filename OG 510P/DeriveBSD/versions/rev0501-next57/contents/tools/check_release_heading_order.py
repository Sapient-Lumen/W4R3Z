#!/usr/bin/env python3
"""Ensure release headings stay newest-first in release/discovery surfaces.

Why:
  `CHANGELOG.md` is the detailed ledger and `docs/00-index.md` is the human
  release map. Both are easiest to review when release sections are newest-first.
  A late newer section makes a release technically present but visually buried,
  which is the same class of discovery drift as a missing or duplicated anchor.

Rules:
  - CHANGELOG.md `## YYYY-MM-DDrN` headings must be in non-increasing
    `(date, r-number)` order.
  - docs/00-index.md `## New in YYYY-MM-DD[rN] ...` headings must be in
    non-increasing `(date, r-number)` order; legacy date-only sections sort as
    revision 0 for their date.

Usage:
  python3 tools/check_release_heading_order.py

Exit codes:
  0: ok
  1: a newer release heading appears after an older one
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
INDEX = ROOT / "docs" / "00-index.md"

CHANGELOG_HDR_RE = re.compile(r"^##\s+(?P<date>\d{4}-\d{2}-\d{2})r(?P<rev>\d+)\s*$", re.MULTILINE)
INDEX_HDR_RE = re.compile(r"^##\s+New in\s+(?P<date>\d{4}-\d{2}-\d{2})(?:r(?P<rev>\d+))?\b.*$", re.MULTILINE)


def _headings(path: Path, pattern: re.Pattern[str]) -> list[tuple[tuple[str, int], int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    out: list[tuple[tuple[str, int], int, str]] = []
    for m in pattern.finditer(text):
        key = (m.group("date"), int(m.group("rev") or 0))
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((key, line_no, m.group(0)))
    return out


def _check_order(label: str, path: Path, pattern: re.Pattern[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing {label}")
        return

    headings = _headings(path, pattern)
    for idx, (left, left_line, left_text) in enumerate(headings[:-1]):
        right, right_line, right_text = headings[idx + 1]
        if left < right:
            errors.append(
                f"{label}: newer release heading appears after older heading: "
                f"line {left_line} {left_text!r} before line {right_line} {right_text!r}"
            )


def main() -> int:
    errors: list[str] = []
    _check_order("CHANGELOG.md", CHANGELOG, CHANGELOG_HDR_RE, errors)
    _check_order("docs/00-index.md", INDEX, INDEX_HDR_RE, errors)

    if errors:
        print("Release heading order check FAILED.")
        print("Release sections must stay newest-first so discovery anchors are not buried.")
        for error in errors:
            print("-", error)
        return 1

    print("Release heading order check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
