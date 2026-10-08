#!/usr/bin/env python3
"""scripts/_shared/md_scan.py

Tiny shared helpers for scanning markdown across the archive.

Rationale:
- multiple drift-firewall scripts need a consistent notion of "repo markdown"
- keep scans size-disciplined by excluding caches/build outputs

This is intentionally stdlib-only.
"""

from __future__ import annotations

from pathlib import Path

# Conservative excludes (match build_release_zip.py intent).
EXCLUDE_PREFIXES = (
    ".git/",
    "dist/",
    "evidence/cache/",
)

EXCLUDE_PARTS = {"__pycache__", ".pytest_cache"}


def iter_markdown_files(root: Path) -> list[Path]:
    """Return markdown files considered part of the archive's docs surfaces.

    Includes: docs/, artifacts/* .md (checklists), playbooks, track-* notes, etc.
    Excludes: cache/build outputs.
    """

    root = root.resolve()
    files: list[Path] = []
    for p in root.rglob("*.md"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root).as_posix()
        except Exception:
            continue
        if any(rel.startswith(pref) for pref in EXCLUDE_PREFIXES):
            continue
        parts = set(rel.split("/"))
        if parts & EXCLUDE_PARTS:
            continue
        files.append(p)
    return sorted(set(files))
