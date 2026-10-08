#!/usr/bin/env python3
"""Check that every numbered doc declares a Track header.

Rule: Each numbered doc under docs/ MUST include a line like:
**Track:** ...

Allowed track labels are intentionally permissive, but MUST include one of:
- A
- B
- C
- Shared
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

TRACK_RE = re.compile(r"^\*\*Track:\*\*\s*(.+)$", re.IGNORECASE | re.MULTILINE)

def is_numbered_md(name: str) -> bool:
    return re.match(r"^\d{1,3}[-_].*\.md$", name) is not None

def main() -> int:
    bad = []
    for p in sorted(DOCS.glob("*.md")):
        if not is_numbered_md(p.name):
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        m = TRACK_RE.search(txt[:4000])
        if not m:
            bad.append((p.name, "missing **Track:** header"))
            continue
        label = m.group(1).strip()
        if not any(x in label for x in ["A", "B", "C", "Shared"]):
            bad.append((p.name, f"unrecognized track label: {label!r}"))

    if bad:
        print("ERROR: Track header problems:", file=sys.stderr)
        for fn, msg in bad:
            print(f"  - {fn}: {msg}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
