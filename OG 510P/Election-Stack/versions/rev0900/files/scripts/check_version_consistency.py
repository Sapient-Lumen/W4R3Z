#!/usr/bin/env python3
"""Ensure VERSION, CHANGELOG, START_HERE, README, and ARCHIVE_INDEX agree.

This is a small drift firewall: if maintainers bump VERSION but forget the
entrypoints, readers get confused and reviewers lose confidence.  v874 shipped
with VERSION/CHANGELOG current while README.md and ARCHIVE_INDEX.md still said
v873; this check now catches that root-entrypoint drift directly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RE_CHANGELOG_TOP = re.compile(r"^##\s+(v\d+)\b")
RE_START_HERE_RECENT = re.compile(r"^##\s+Recent additions\s*\(v\d+–(v\d+)\)\s*$")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    vfile = ROOT / "VERSION"
    if not vfile.exists():
        fail("missing VERSION")
    version = vfile.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"v\d+", version):
        fail(f"VERSION must be like vNNN, got {version!r}")

    changelog = ROOT / "CHANGELOG.md"
    if not changelog.exists():
        fail("missing CHANGELOG.md")

    top = None
    for line in changelog.read_text(encoding="utf-8").splitlines():
        m = RE_CHANGELOG_TOP.match(line.strip())
        if m:
            top = m.group(1)
            break
    if not top:
        fail("CHANGELOG.md missing top '## vNNN' entry")
    if top != version:
        fail(f"VERSION ({version}) does not match CHANGELOG top entry ({top})")

    start_here = ROOT / "docs" / "START_HERE.md"
    if not start_here.exists():
        fail("missing docs/START_HERE.md")

    recent = None
    for line in start_here.read_text(encoding="utf-8").splitlines():
        m = RE_START_HERE_RECENT.match(line.strip())
        if m:
            recent = m.group(1)
            break
    if not recent:
        fail("docs/START_HERE.md missing '## Recent additions (vX–vY)' header")

    try:
        v_num = int(version[1:])
        recent_num = int(recent[1:])
    except Exception:
        fail("could not parse version numbers")

    if recent_num < v_num:
        fail(f"docs/START_HERE.md recent additions end ({recent}) is behind VERSION ({version})")

    root_entrypoints = {
        "README.md": ROOT / "README.md",
        "ARCHIVE_INDEX.md": ROOT / "ARCHIVE_INDEX.md",
    }
    for label, path in root_entrypoints.items():
        if not path.exists():
            fail(f"missing {label}")
        text = path.read_text(encoding="utf-8")
        if version not in text[:1200]:
            fail(f"{label} does not mention current VERSION ({version}) near the top")
        stale = re.search(r"v(\d+)", text[:400])
        if stale:
            try:
                if int(stale.group(1)) < v_num:
                    fail(f"{label} starts with stale version v{int(stale.group(1))} while VERSION is {version}")
            except ValueError:
                pass

    print("PASS: version consistency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
