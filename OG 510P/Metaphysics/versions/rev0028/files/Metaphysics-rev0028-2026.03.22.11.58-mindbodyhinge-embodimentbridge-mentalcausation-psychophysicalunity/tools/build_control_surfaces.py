#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import ROOT, archive_note_paths, current_revision

payload = {
    "revision": current_revision(),
    "authoritative_surfaces": [
        "README.md",
        "CHANGELOG.md",
        "INDEX.md",
        "ARCHIVE_INDEX.json",
        "SOURCES.md",
        "SOURCES.json",
        "THREADS.md",
        "THREAD_SUMMARY.json",
        "MANIFEST.json",
        "RELEASES.json",
    ],
    "current_note_set": [str(path.relative_to(ROOT)) for path in archive_note_paths()],
    "admission_rule": "All archive notes must be numbered markdown files with a one-line thesis, explicit failure modes, and a load-bearing source entry in SOURCES.json.",
    "scope_posture": "non-skeptical, non-reductive, portfolio-based metaphysics archive",
}
(ROOT / "CONTROL_SURFACES.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
