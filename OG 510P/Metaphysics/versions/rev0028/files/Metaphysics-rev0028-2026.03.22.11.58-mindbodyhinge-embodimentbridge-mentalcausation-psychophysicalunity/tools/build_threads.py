#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict

from archive_meta import ROOT, archive_note_paths, current_revision, note_catalog, thesis_for

catalog = note_catalog()
thread_to_notes: dict[str, list[dict]] = defaultdict(list)
tag_counter: Counter[str] = Counter()
for path in archive_note_paths():
    rel = str(path.relative_to(ROOT))
    cfg = catalog[rel]
    thread_to_notes[cfg["thread"]].append({"file": rel, "thesis": thesis_for(path), "tags": cfg["tags"]})
    tag_counter.update(cfg["tags"])

thread_summary = {
    "revision": current_revision(),
    "threads": [
        {
            "thread": thread,
            "count": len(items),
            "files": [item["file"] for item in items],
            "tags": sorted({tag for item in items for tag in item["tags"]}),
        }
        for thread, items in sorted(thread_to_notes.items())
    ],
    "tag_frequency": dict(sorted(tag_counter.items())),
}
(ROOT / "THREAD_SUMMARY.json").write_text(json.dumps(thread_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

lines = ["# Threads", "", f"Threaded view for {current_revision()}.", ""]
for thread, items in sorted(thread_to_notes.items()):
    lines.append(f"## {thread}")
    lines.append("")
    for item in items:
        file_name = Path(item["file"]).name
        lines.append(f"- `{file_name}` — {item['thesis']}")
    lines.append("")
(ROOT / "THREADS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
