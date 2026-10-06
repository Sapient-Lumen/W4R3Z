#!/usr/bin/env python3
"""Prevent citation drift in the juicy lessons index (docs/110).

House rule: when introducing new external work, add it to `docs/32-curated-references.md`.

Why this exists:
  - `docs/110-juicy-os-lessons.md` is a high-churn discovery surface.
  - We want a lightweight guardrail that blocks *new* uncataloged URLs without
    forcing retroactive churn across the whole archive.

Mechanism:
  - Parse URLs in `docs/110-juicy-os-lessons.md`.
  - Allow existing historical gaps via an explicit baseline allowlist.
  - Fail if a URL is neither in curated references nor in the allowlist.

Usage:
  python3 tools/check_juicy_lesson_references.py

Exit codes:
  0: ok
  1: missing curated references
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "docs" / "32-curated-references.md"
JUICY = ROOT / "docs" / "110-juicy-os-lessons.md"
ALLOWLIST = ROOT / "tools" / "baselines" / "juicy_urls_allowlist.txt"

URL_RE = re.compile(r"https?://[^\s\)\]\}>]+")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _normalize(u: str) -> str:
    return u.rstrip(".,;:)]")


def _urls_from(p: Path) -> set[str]:
    return {_normalize(u) for u in URL_RE.findall(_read(p))}


def _allowlist_urls() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    lines = [ln.strip() for ln in _read(ALLOWLIST).splitlines()]
    return {ln for ln in lines if ln and not ln.startswith("#")}


def main() -> int:
    if not CURATED.exists():
        print("Missing docs/32-curated-references.md")
        return 1
    if not JUICY.exists():
        print("Missing docs/110-juicy-os-lessons.md")
        return 1

    curated = _urls_from(CURATED)
    juicy = _urls_from(JUICY)
    allow = _allowlist_urls()

    missing = sorted(u for u in juicy if (u not in curated and u not in allow))

    if missing:
        print("Juicy lesson curated reference check FAILED.")
        print("Add these URLs to docs/32-curated-references.md (preferred),")
        print("or (rarely) extend tools/baselines/juicy_urls_allowlist.txt with a justification.")
        for u in missing:
            print("-", u)
        return 1

    print("Juicy lesson curated reference check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
