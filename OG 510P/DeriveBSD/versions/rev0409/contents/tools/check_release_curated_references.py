#!/usr/bin/env python3
"""Ensure newest release docs don't introduce uncataloged external URLs.

House rule: when introducing new external work, add it to `docs/32-curated-references.md`.

We already enforce this for meta docs (>=397) via `tools/check_curated_references.py`.
This check extends that discipline to the *newest release surface only*:

- parse the newest `CHANGELOG.md` entry
- collect any numbered docs mentioned there (backticked repo paths)
- fail if any external URL in those docs is missing from `docs/32-curated-references.md`

This prevents “new doc ships with citations in prose but never gets added to the pointer map”,
while avoiding retroactive churn across the full archive.

Usage:
  python3 tools/check_release_curated_references.py

Exit codes:
  0: ok
  1: missing references
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
CURATED = ROOT / "docs" / "32-curated-references.md"

# Backticked repo-relative paths.
PATH_RE = re.compile(r"`((docs|rfcs|adrs|spec|tools)/[^`]+?)`")
CHANGELOG_TOP_RE = re.compile(r"^##\s+(\S+)\s*$", re.MULTILINE)
DOC_PATH_RE = re.compile(r"^docs/(?P<num>\d+)-.+\.md$")

# Discovery surfaces are already pointer maps; do not require full URL duplication there.
SKIP_DOCS = {
    "docs/00-index.md",
    "docs/110-juicy-os-lessons.md",
    "docs/32-curated-references.md",
}

URL_RE = re.compile(r"https?://[^\s\)\]\}>]+")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _normalize(u: str) -> str:
    return u.rstrip(".,;:)]")


def _curated_urls() -> set[str]:
    if not CURATED.exists():
        raise FileNotFoundError("missing docs/32-curated-references.md")
    return {_normalize(u) for u in URL_RE.findall(_read(CURATED))}


def _extract_changelog_top_block() -> str:
    txt = _read(CHANGELOG)
    m = CHANGELOG_TOP_RE.search(txt)
    if not m:
        raise ValueError("missing top '## <version>' entry in CHANGELOG.md")
    start = m.start()
    m2 = CHANGELOG_TOP_RE.search(txt, m.end())
    return txt[start : (m2.start() if m2 else len(txt))]


def main() -> int:
    curated = _curated_urls()
    block = _extract_changelog_top_block()

    mentioned = [m[0] for m in PATH_RE.findall(block)]
    docs = [ROOT / rel for rel in mentioned if DOC_PATH_RE.match(rel)]

    errors: list[str] = []

    for p in docs:
        rel = str(p.relative_to(ROOT))
        if rel in SKIP_DOCS:
            continue
        if not p.exists():
            # Existence is enforced elsewhere (check_discovery), but keep behavior deterministic.
            continue
        urls = {_normalize(u) for u in URL_RE.findall(_read(p))}
        missing = sorted(u for u in urls if u not in curated)
        for u in missing:
            errors.append(f"{p.relative_to(ROOT)}: missing from curated references: {u}")

    if errors:
        print("Release curated reference check failed.")
        print("Add missing URLs to docs/32-curated-references.md (keep it minimal/high-signal).")
        for e in errors:
            print("-", e)
        return 1

    print("Release curated reference check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
