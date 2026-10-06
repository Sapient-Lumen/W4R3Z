#!/usr/bin/env python3
"""Ensure meta-engineering docs remain discoverable from primary entry points.

Why:
  - The docs >=397 are the "design law / archive wiring" surfaces.
  - If they are not linked from discovery surfaces, humans/LLMs drift.

Rule:
  - Every numbered doc under docs/ with id >= 397 must be referenced (repo-relative path)
    in either:
      - docs/00-index.md, or
      - docs/110-juicy-os-lessons.md

This is intentionally conservative and fast: it only checks for the presence of the
repo-relative path string in either discovery file.

Usage:
  python3 tools/check_meta_doc_discoverability.py

Exit codes:
  0: ok
  1: missing wiring
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
INDEX = DOCS_DIR / "00-index.md"
JUICY = DOCS_DIR / "110-juicy-os-lessons.md"

DOC_NUM_RE = re.compile(r"^(?P<num>\d+)-.+\.md$")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _meta_docs() -> list[str]:
    out: list[str] = []
    for p in sorted(DOCS_DIR.glob("*.md")):
        m = DOC_NUM_RE.match(p.name)
        if not m:
            continue
        n = int(m.group("num"))
        if n < 397:
            continue
        # Generated docs are still part of the discovery surface; include them.
        out.append(f"docs/{p.name}")
    return out


def main() -> int:
    errors: list[str] = []

    if not INDEX.exists():
        print("Missing docs/00-index.md")
        return 1
    if not JUICY.exists():
        print("Missing docs/110-juicy-os-lessons.md")
        return 1

    index_txt = _read(INDEX)
    juicy_txt = _read(JUICY)

    for rel in _meta_docs():
        if rel not in index_txt and rel not in juicy_txt:
            errors.append(rel)

    if errors:
        print("Meta doc discoverability check FAILED. Link these from docs/00-index.md or docs/110-juicy-os-lessons.md:\n")
        for p in errors:
            print(f"- {p}")
        return 1

    print("Meta doc discoverability check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
