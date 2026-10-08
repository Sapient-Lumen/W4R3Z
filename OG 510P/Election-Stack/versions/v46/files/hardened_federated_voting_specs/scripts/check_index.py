#!/usr/bin/env python3
"""Artifact-index checker (TriKEM-style: no silent incoherence).

Rules:
- Every numbered *canonical* doc under docs/ MUST appear in docs/13-artifact-index.md.
- Tombstone docs are allowed as stable aliases and MAY be omitted from the index.
- Canonical docs are identified as numbered docs that are NOT tombstones.

A doc is treated as a tombstone if its first ~200 chars contain the word 'Tombstone'.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX_PATH = DOCS / "13-artifact-index.md"

def is_numbered_md(p: Path) -> bool:
    return p.suffix == ".md" and re.match(r"^\d{1,3}[-_].*\.md$", p.name) is not None

def is_tombstone(p: Path) -> bool:
    head = p.read_text(encoding="utf-8", errors="ignore")[:200].lower()
    return "tombstone" in head

def main() -> int:
    index = INDEX_PATH.read_text(encoding="utf-8", errors="ignore")

    numbered = sorted([p for p in DOCS.glob("*.md") if is_numbered_md(p)])
    canonical = [p.name for p in numbered if not is_tombstone(p)]

    missing = [name for name in canonical if name not in index]

    if missing:
        print("ERROR: canonical numbered docs missing from docs/13-artifact-index.md:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
