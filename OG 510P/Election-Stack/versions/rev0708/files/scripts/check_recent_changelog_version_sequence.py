#!/usr/bin/env python3
"""Ensure recent CHANGELOG version headings form a contiguous descending sequence.

This is a small release-bookkeeping drift fence. It intentionally checks only the
recent head of the changelog so older historical gaps do not force large cleanup
before a scoped revision can ship.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
HEAD_WINDOW = 24
RE_VERSION = re.compile(r"^##\s+v(\d+)\b")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    if not CHANGELOG.exists():
        fail("missing CHANGELOG.md")

    versions: list[int] = []
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        m = RE_VERSION.match(line.strip())
        if m:
            versions.append(int(m.group(1)))
            if len(versions) >= HEAD_WINDOW:
                break

    if len(versions) < 2:
        fail("CHANGELOG.md must contain at least two recent '## vNNN' headings")

    for cur, nxt in zip(versions, versions[1:]):
        if nxt != cur - 1:
            fail(
                "recent CHANGELOG version sequence is not contiguous: "
                f"v{cur} followed by v{nxt}"
            )

    print(f"PASS: recent changelog version sequence ({len(versions)} headings checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
