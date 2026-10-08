#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from archive_meta import ROOT, archive_note_paths, current_revision, note_catalog, slug_to_title, thesis_for, summary_for

catalog = note_catalog()
notes = []
for path in archive_note_paths():
    rel = str(path.relative_to(ROOT))
    cfg = catalog[rel]
    notes.append(
        {
            "file": rel,
            "title": slug_to_title(path),
            "thesis": thesis_for(path),
            "summary": summary_for(path),
            "tags": cfg["tags"],
            "thread": cfg["thread"],
            "status": cfg["status"],
        }
    )

payload = {"revision": current_revision(), "notes": notes}
(ROOT / "ARCHIVE_INDEX.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
