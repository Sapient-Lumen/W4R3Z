#!/usr/bin/env python3
"""Ensure every CHANGELOG release has a human discovery entry in docs/00-index.md.

Why:
  CHANGELOG.md is the detailed release ledger, while docs/00-index.md is the
  human navigation map. If a changelog release is absent from the index, the
  release remains technically recorded but becomes hard to discover by version
  anchor, especially for reviewers using the index as the archive front door.

Rule:
  - Every ``## <version>`` release heading in CHANGELOG.md must have a matching
    ``## New in <version>`` heading in docs/00-index.md.
  - docs/00-index.md may contain older pre-changelog release entries; those are
    not errors.

Usage:
  python3 tools/check_changelog_index_release_coverage.py

Exit codes:
  0: ok
  1: one or more changelog releases are missing from docs/00-index.md
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
INDEX = ROOT / "docs" / "00-index.md"

CHANGELOG_HDR_RE = re.compile(r"^##\s+(?P<ver>\d{4}-\d{2}-\d{2}r\d+)\s*$", re.MULTILINE)
INDEX_HDR_RE = re.compile(r"^##\s+New in\s+(?P<ver>\d{4}-\d{2}-\d{2}r\d+)\s*$", re.MULTILINE)


def _versions(path: Path, pattern: re.Pattern[str]) -> list[str]:
    return [m.group("ver") for m in pattern.finditer(path.read_text(encoding="utf-8", errors="replace"))]


def main() -> int:
    errors: list[str] = []

    if not CHANGELOG.exists():
        errors.append("missing CHANGELOG.md")
    if not INDEX.exists():
        errors.append("missing docs/00-index.md")

    if errors:
        for error in errors:
            print(error)
        return 1

    changelog_versions = _versions(CHANGELOG, CHANGELOG_HDR_RE)
    index_versions = set(_versions(INDEX, INDEX_HDR_RE))
    missing = [ver for ver in changelog_versions if ver not in index_versions]

    if missing:
        print("Changelog/index release coverage check FAILED.")
        print("Every CHANGELOG.md release must have a matching docs/00-index.md 'New in' heading.")
        for ver in missing:
            print(f"- missing docs/00-index.md heading: ## New in {ver}")
        return 1

    print(f"Changelog/index release coverage check OK: {len(changelog_versions)} changelog releases indexed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
