#!/usr/bin/env python3
"""Ensure external references stay centralized (amnesia-resistant citations).

House rule: when introducing new external work, add it to `docs/32-curated-references.md`.

This check is intentionally scoped to the meta-engineering doc range (docs >=397) to avoid
retroactive churn while still preventing new drift in the “design law” surfaces.

Usage:
  python3 tools/check_curated_references.py

Exit codes:
  0: ok
  1: missing references
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "docs" / "32-curated-references.md"
DOCS_DIR = ROOT / "docs"

URL_RE = re.compile(r"https?://[^\s\)\]\}>]+")
DOC_NUM_RE = re.compile(r"^(\d+)-")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _normalize(u: str) -> str:
    # strip common trailing punctuation from markdown prose
    return u.rstrip(".,;:)]")


def _curated_urls() -> set[str]:
    if not CURATED.exists():
        raise FileNotFoundError("missing docs/32-curated-references.md")
    return {_normalize(u) for u in URL_RE.findall(_read(CURATED))}


def _meta_docs() -> list[Path]:
    docs: list[Path] = []
    for p in sorted(DOCS_DIR.glob("*.md")):
        m = DOC_NUM_RE.match(p.name)
        if not m:
            continue
        if int(m.group(1)) < 397:
            continue
        if p.name == CURATED.name:
            continue
        docs.append(p)
    return docs


def main() -> int:
    curated = _curated_urls()
    errors: list[str] = []

    for p in _meta_docs():
        urls = {_normalize(u) for u in URL_RE.findall(_read(p))}
        missing = sorted(u for u in urls if u not in curated)
        for u in missing:
            errors.append(f"{p.relative_to(ROOT)}: missing from curated references: {u}")

    if errors:
        print("Curated reference check failed.")
        print("Add missing URLs to docs/32-curated-references.md (keep it minimal/high-signal).")
        for e in errors:
            print("-", e)
        return 1

    print("Curated reference check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
