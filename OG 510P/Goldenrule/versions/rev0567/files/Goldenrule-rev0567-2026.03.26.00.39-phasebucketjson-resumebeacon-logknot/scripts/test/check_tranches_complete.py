#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

LINE_RE = re.compile(r"^\s*(\d+)\.\s+\[([ xX])\]\s+(.+)$")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    tranches = (root / "docs" / "TRANCHES.md").read_text(encoding="utf-8").splitlines()

    total = 0
    unchecked = []
    last = 0
    for ln in tranches:
        m = LINE_RE.match(ln)
        if not m:
            continue
        idx = int(m.group(1))
        mark = m.group(2).lower()
        title = m.group(3).strip()
        total += 1
        if idx != last + 1:
            print(f"tranches: non-sequential numbering at {idx} (prev={last})", file=sys.stderr)
            return 1
        last = idx
        if mark != "x":
            unchecked.append((idx, title))

    if total == 0:
        print("tranches: no tranche entries found", file=sys.stderr)
        return 1

    if unchecked:
        for idx, title in unchecked:
            print(f"tranches: unchecked item {idx}: {title}", file=sys.stderr)
        return 1

    print(f"tranches: ok ({total} completed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
