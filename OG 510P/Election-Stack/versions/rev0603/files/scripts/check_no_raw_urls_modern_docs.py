#!/usr/bin/env python3
"""scripts/check_no_raw_urls_modern_docs.py

Drift firewall: in newer evidence-facing docs (>=170-*.md), external URLs should be cited via
`source: <id>` (or `xref: <id>`) rather than pasted as raw links.

This keeps the archive small, and ensures citations route through
`evidence/lock/external-sources.toml`.

Policy enforced here:
- For docs/NNN-*.md where NNN >= 170:
  - reject any "http://" or "https://" that appears outside fenced code blocks.

Docs may still reference internal relative links freely.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

URL_RE = re.compile(r"https?://")
FENCE_RE = re.compile(r"^```")


def doc_number(p: Path) -> int | None:
    name = p.name
    m = re.match(r"^(\d{1,3})-", name)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def main() -> int:
    if not DOCS.exists():
        return 0

    offenders: list[str] = []

    for p in sorted(DOCS.glob("[0-9]*-*.md")):
        n = doc_number(p)
        if n is None or n < 170:
            continue

        in_code = False
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            offenders.append(f"{p.relative_to(ROOT)}: read failed: {e}")
            continue

        for i, line in enumerate(lines, start=1):
            if FENCE_RE.match(line.strip()):
                in_code = not in_code
                continue
            if in_code:
                continue
            if URL_RE.search(line):
                offenders.append(f"{p.relative_to(ROOT)}:{i}: raw URL not allowed in docs >=170")

    if offenders:
        for o in offenders:
            print("ERROR:", o, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
