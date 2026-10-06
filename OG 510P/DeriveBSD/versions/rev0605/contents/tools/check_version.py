#!/usr/bin/env python3
"""Ensure version metadata is consistent across key entry points.

Checks:
  - README.md ``Last updated`` tag matches the newest CHANGELOG entry
  - README.md ``Version`` tag matches the newest CHANGELOG entry
  - README.md terminal metadata block is ``Last updated`` then ``Version``
  - docs/110-juicy-os-lessons.md ``Last updated`` tag matches and is terminal
  - docs/00-index.md ``Last updated`` tag matches and is terminal

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
VERSION_RE = re.compile(r"^Version:\s*(\S+)\s*$", re.MULTILINE)
CHANGELOG_TOP_RE = re.compile(r"^##\s+(\S+)\s*$", re.MULTILINE)


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_tag(p: Path, tag_name: str, pattern: re.Pattern[str]) -> str:
    txt = _read(p)
    matches = list(pattern.finditer(txt))
    if not matches:
        raise ValueError(f"missing '{tag_name}:' tag in {p.relative_to(ROOT)}")
    if len(matches) > 1:
        raise ValueError(f"multiple '{tag_name}:' tags in {p.relative_to(ROOT)}")
    return matches[0].group(1)


def _extract_last_updated(p: Path) -> str:
    return _extract_tag(p, "Last updated", LAST_UPDATED_RE)


def _extract_readme_version(p: Path) -> str:
    return _extract_tag(p, "Version", VERSION_RE)


def _extract_changelog_top(p: Path) -> str:
    txt = _read(p)
    # First '## ...' after the top heading.
    m = CHANGELOG_TOP_RE.search(txt)
    if not m:
        raise ValueError(f"missing top '## <version>' entry in {p.relative_to(ROOT)}")
    return m.group(1)


def _nonblank_lines(p: Path) -> list[tuple[int, str]]:
    return [
        (i, ln.strip())
        for i, ln in enumerate(_read(p).splitlines(), 1)
        if ln.strip()
    ]


def _check_terminal_last_updated(path: Path, errors: list[str]) -> None:
    lines = _nonblank_lines(path)
    rel = path.relative_to(ROOT)
    if not lines:
        errors.append(f"{rel}: empty file")
        return
    line_no, line = lines[-1]
    if not line.startswith("Last updated:"):
        errors.append(f"{rel}: final nonblank line should be 'Last updated: <version>' (found line {line_no}: {line!r})")


def _check_readme_terminal_metadata(path: Path, errors: list[str]) -> None:
    lines = _nonblank_lines(path)
    if len(lines) < 2:
        errors.append("README.md: expected terminal 'Last updated:' and 'Version:' metadata block")
        return
    last_no, last = lines[-1]
    prev_no, prev = lines[-2]
    if not prev.startswith("Last updated:") or not last.startswith("Version:"):
        errors.append(
            "README.md: final nonblank lines should be "
            f"'Last updated: <version>' then 'Version: <version>' "
            f"(found line {prev_no}: {prev!r}; line {last_no}: {last!r})"
        )


def _compare(label: str, observed: str | None, expected: str | None, errors: list[str]) -> None:
    if observed and expected and observed != expected:
        errors.append(f"{label} {observed} != CHANGELOG.md top entry {expected}")


def main() -> int:
    errors: list[str] = []
    readme = ROOT / "README.md"

    try:
        readme_last_updated = _extract_last_updated(readme)
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        readme_last_updated = None

    try:
        readme_version = _extract_readme_version(readme)
    except Exception as e:  # noqa: BLE001
        errors.append(str(e))
        readme_version = None

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

    _compare("README.md Last updated", readme_last_updated, changelog_v, errors)
    _compare("README.md Version", readme_version, changelog_v, errors)
    _compare("docs/110-juicy-os-lessons.md version", juicy_v, changelog_v, errors)
    _compare("docs/00-index.md version", index_v, changelog_v, errors)

    _check_readme_terminal_metadata(readme, errors)
    _check_terminal_last_updated(ROOT / "docs" / "110-juicy-os-lessons.md", errors)
    _check_terminal_last_updated(ROOT / "docs" / "00-index.md", errors)

    if errors:
        print("Version check failed:")
        for e in errors:
            print("-", e)
        return 1

    print("Version check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
