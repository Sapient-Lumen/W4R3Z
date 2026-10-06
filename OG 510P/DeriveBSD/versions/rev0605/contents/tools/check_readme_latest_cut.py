#!/usr/bin/env python3
"""Ensure the README front-door latest-cut line matches the newest release.

The archive is meant to be read from the first screen.  A stale `Latest cut:`
line is especially damaging for humans and LLMs because it points review at the
wrong ADR/doc pair even when the footer version is current.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"

CHANGELOG_TOP_RE = re.compile(r"^##\s+(?P<version>\S+)", re.MULTILINE)
LATEST_RE = re.compile(r"^Latest cut:\s*(?P<body>.+)$", re.MULTILINE)
ADR_RE = re.compile(r"adrs/(ADR-(?P<num>\d{4})-[^`\s]+\.md)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _top_changelog() -> tuple[str, str]:
    txt = _read(CHANGELOG)
    m = CHANGELOG_TOP_RE.search(txt)
    if not m:
        raise ValueError("CHANGELOG.md has no release heading")
    start = m.start()
    nxt = CHANGELOG_TOP_RE.search(txt, m.end())
    return m.group("version"), txt[start : (nxt.start() if nxt else len(txt))]


def main() -> int:
    errors: list[str] = []
    readme = _read(README)
    m = LATEST_RE.search(readme)
    if not m:
        errors.append("README.md is missing a top-level `Latest cut:` line")
        latest = ""
    else:
        latest = m.group("body")

    try:
        version, top = _top_changelog()
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))
        version, top = "", ""

    if version and version not in latest:
        errors.append(f"README.md Latest cut does not mention newest release {version}")

    top_adrs = ADR_RE.findall(top)
    newest_adr = top_adrs[0][1] if top_adrs else ""
    if newest_adr and newest_adr not in latest:
        errors.append(f"README.md Latest cut does not mention newest ADR {newest_adr}")

    if errors:
        print("README latest-cut check failed:")
        for e in errors:
            print("-", e)
        return 1

    print("README latest-cut check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
