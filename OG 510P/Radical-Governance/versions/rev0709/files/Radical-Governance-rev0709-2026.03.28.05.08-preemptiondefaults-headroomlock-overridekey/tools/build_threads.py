#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTRO = "# Threads\n\nThis generated crosswalk groups archive notes by inferred thematic tags so compact continuation bundles remain mergeable by topic as well as by revision.\n"


def main() -> None:
    data = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    groups: dict[str, list[dict]] = defaultdict(list)
    for note in data.get("notes", []):
        for tag in note.get("tags", []):
            groups[tag].append(note)

    lines = [INTRO, ""]
    for tag in sorted(groups):
        lines.append(f"## {tag}")
        lines.append("")
        for note in groups[tag]:
            lines.append(f"- `{Path(note['file']).name}` — {note['thesis']}")
        lines.append("")

    (ROOT / "THREADS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("OK: wrote THREADS.md")


if __name__ == "__main__":
    main()
