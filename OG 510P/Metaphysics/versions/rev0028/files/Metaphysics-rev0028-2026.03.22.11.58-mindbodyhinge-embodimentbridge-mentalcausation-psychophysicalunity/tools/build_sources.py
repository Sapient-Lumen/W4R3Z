#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from archive_meta import ROOT, archive_note_paths, current_revision, source_data

src = source_data()
payload = {"revision": current_revision(), "notes": src["notes"]}
(ROOT / "SOURCES.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

lines = [f"# Sources used for {current_revision()}", "", "These sources are signal and pressure, not sovereignty. Each note records only the load-bearing external materials used to sharpen the archive.", ""]
for path in archive_note_paths():
    rel = str(path.relative_to(ROOT))
    lines.append(f"## `{path.name}`")
    lines.append("")
    for group in src["notes"][rel]["groups"]:
        lines.append(f"- **{group['title']}** — {group['publisher']}")
        lines.append(f"  - URL: {group['url']}")
        lines.append(f"  - Load-bearing use: {group['load_bearing_use']}")
    lines.append("")

(ROOT / "SOURCES.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
