#!/usr/bin/env python3
"""Check that the open questions/risk register is mechanically usable.

Rule (simple, but high leverage):
- Every *numeric* section heading in docs/266 must contain a line starting with 'Risk:'
  before the next '## ' heading.

Rationale:
- The risk register is only useful if each item names its failure mode explicitly.
- This keeps the context pack and generated indices from silently degrading.

Usage:
  python3 tools/check_risk_register.py

Exit codes:
  0: OK
  1: At least one numeric section missing a Risk: line
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "266-open-questions-and-risk-register.md"

HEAD_RE = re.compile(r"^##\s+(.+?)\s*$")
NUM_RE = re.compile(r"^(?P<num>\d+)\)\s*(?P<title>.+)$")


def main() -> int:
    txt = SRC.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()

    heads: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        if line.startswith("## "):
            h = line.removeprefix("## ").strip()
            m = NUM_RE.match(h)
            if m:
                heads.append((i, m.group("num"), m.group("title").strip()))

    missing: list[str] = []
    for k, (i, num, title) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        has = False
        for line in lines[i + 1 : j]:
            if line.strip().startswith("Risk:"):
                has = True
                break
        if not has:
            missing.append(f"{num}) {title}")

    if missing:
        print("Risk register check FAILED. Add a 'Risk:' line to each missing item:\n")
        for m in missing:
            print(f"- {m}")
        return 1

    print("Risk register check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
