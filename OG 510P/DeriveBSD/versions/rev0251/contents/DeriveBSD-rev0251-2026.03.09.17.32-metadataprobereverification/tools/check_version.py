#!/usr/bin/env python3
"""Ensure version metadata is consistent across key entry points.

Checks:
  - README.md "Last updated" tag matches the newest CHANGELOG entry
  - docs/110-juicy-os-lessons.md "Last updated" tag matches
  - docs/00-index.md "Last updated" tag matches

Usage:
  python3 tools/check_version.py

Exit codes:
  0: ok
  1: mismatch
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAST_UPDATED_RE = re.compile(r"^Last updated:\s*(\S+)\s*$", re.MULTILINE)
CHANGELOG_TOP_RE = re.compile(r"^##\s+(\S+)\s*$", re.MULTILINE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_last_updated(p: Path) -> str:
    m = LAST_UPDATED_RE.search(_read(p))
    if not m:
        raise ValueError(f"missing 'Last updated:' tag in {p.relative_to(ROOT)}")
    return m.group(1)


def _extract_changelog_top(p: Path) -> str:
    txt = _read(p)
    # First '## ...' after the top heading.
    m = CHANGELOG_TOP_RE.search(txt)
    if not m:
        raise ValueError(f"missing top '## <version>' entry in {p.relative_to(ROOT)}")
    return m.group(1)


def main() -> int:
    errors: list[str] = []

    try:
        readme_v = _extract_last_updated(ROOT / "README.md")
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        readme_v = None

    try:
        juicy_v = _extract_last_updated(ROOT / "docs" / "110-juicy-os-lessons.md")
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        juicy_v = None

    try:
        index_v = _extract_last_updated(ROOT / "docs" / "00-index.md")
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        index_v = None

    try:
        changelog_v = _extract_changelog_top(ROOT / "CHANGELOG.md")
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        changelog_v = None

    if readme_v and changelog_v and readme_v != changelog_v:
        errors.append(f"README.md version {readme_v} != CHANGELOG.md top entry {changelog_v}")

    if juicy_v and changelog_v and juicy_v != changelog_v:
        errors.append(f"docs/110-juicy-os-lessons.md version {juicy_v} != CHANGELOG.md top entry {changelog_v}")

    if index_v and changelog_v and index_v != changelog_v:
        errors.append(f"docs/00-index.md version {index_v} != CHANGELOG.md top entry {changelog_v}")

    if errors:
        print("Version check failed:")
        for e in errors:
            print("-", e)
        return 1

    print("Version check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

