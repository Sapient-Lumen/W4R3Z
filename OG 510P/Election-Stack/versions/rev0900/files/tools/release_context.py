"""Shared release/version context for deterministic pack builders.

Pack tools used to hard-code the original v862 release-review date.  That made
newer packs carry current VERSION values with an old release date.  Keep this
small helper stdlib-only so no-go/capture packs agree with the archive's top
changelog entry by default, while still allowing tests to override the date.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

_CHANGELOG_HEAD_RE = re.compile(r"^##\s+(v\d+)\s+\((\d{4}-\d{2}-\d{2})\)", re.M)


def archive_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def release_date(root: Path) -> str:
    override = os.environ.get("ELECTION_STACK_RELEASE_DATE", "").strip()
    if override:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", override):
            raise ValueError(f"invalid ELECTION_STACK_RELEASE_DATE={override!r}; expected YYYY-MM-DD")
        return override
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = _CHANGELOG_HEAD_RE.search(text)
    if not m:
        raise ValueError("could not parse top VERSION/date from CHANGELOG.md")
    version, date = m.groups()
    current = archive_version(root)
    if version != current:
        raise ValueError(f"CHANGELOG top version {version} does not match VERSION {current}")
    return date
