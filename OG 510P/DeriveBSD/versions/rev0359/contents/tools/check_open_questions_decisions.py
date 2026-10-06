#!/usr/bin/env python3
"""Warn if decided open-question items are missing an ADR link.

We allow docs/266 to carry historical context for decided items, but we want those
items to be pinned to an ADR so the decision doesn't drift back into folklore.

Rule (warning only):
- For each numeric heading tagged with [DECIDED] in docs/266, the section should
  mention an ADR path (e.g., `adrs/ADR-0040-...md`) or an 'ADR-' identifier.

This script intentionally exits 0 even when warnings are emitted.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "266-open-questions-and-risk-register.md"

HEAD_RE = re.compile(r"^##\s+(.+?)\s*$")
NUM_RE = re.compile(r"^(?P<num>\d+)\)\s*(?P<title>.+)$")
DECIDED_TAG_RE = re.compile(r"\[DECIDED\]", re.IGNORECASE)
ADR_REF_RE = re.compile(r"`adrs/ADR-\d{4}[^`]*?\.md`|ADR-\d{4}")


def main() -> int:
    txt = SRC.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()

    heads: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        heading = line.removeprefix("## ").strip()
        if not DECIDED_TAG_RE.search(heading):
            continue
        if not NUM_RE.match(heading):
            continue
        heads.append((i, heading))

    warnings: list[str] = []
    for k, (i, heading) in enumerate(heads):
        # Find next '## ' heading.
        j = len(lines)
        for t in range(i + 1, len(lines)):
            if lines[t].startswith("## "):
                j = t
                break
        body = "\n".join(lines[i + 1 : j])
        if not ADR_REF_RE.search(body):
            warnings.append(heading)

    if warnings:
        print("Open questions decision-link check: WARN\n")
        print("The following [DECIDED] items in docs/266 are missing an ADR reference:")
        for h in warnings:
            print(f"- {h}")
        print("\nAdd an ADR link (preferred: a backticked `adrs/ADR-XXXX-...md` path).")
        return 0

    print("Open questions decision-link check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
