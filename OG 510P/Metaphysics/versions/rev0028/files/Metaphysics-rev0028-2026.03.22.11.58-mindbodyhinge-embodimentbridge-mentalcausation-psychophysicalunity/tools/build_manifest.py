#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from archive_meta import ROOT, archive_note_paths, current_revision

TOP_LEVEL = [
    "README.md",
    "CHANGELOG.md",
    "INDEX.md",
    "THREADS.md",
    "THREAD_SUMMARY.json",
    "SOURCES.md",
    "SOURCES.json",
    "ARCHIVE_INDEX.json",
    "CONTROL_SURFACES.json",
    "RELEASES.json",
    "VERSION",
    "Makefile",
]


def entry(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }

manifest = {
    "revision": current_revision(),
    "top_level_files": [entry(ROOT / name) for name in TOP_LEVEL],
    "archive_notes": [entry(p) for p in archive_note_paths()],
    "tool_scripts": [entry(p) for p in sorted((ROOT / "tools").glob("*.py"))],
    "tool_data": [entry(p) for p in sorted((ROOT / "tools").glob("*.json"))],
}
(ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
