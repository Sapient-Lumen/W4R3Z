#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from archive_meta import current_revision

CURRENT_REV = current_revision()


def main() -> None:
    data = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    summary: dict[str, dict] = {}
    for note in data.get("notes", []):
        for tag in note.get("tags", []):
            slot = summary.setdefault(tag, {"count": 0, "latest_note_number": -1, "latest_file": None, "latest_title": None})
            slot["count"] += 1
            number = int(note.get("number", -1))
            if number > slot["latest_note_number"]:
                slot["latest_note_number"] = number
                slot["latest_file"] = note.get("file")
                slot["latest_title"] = note.get("title")

    payload = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "tags": {tag: summary[tag] for tag in sorted(summary)},
    }
    (ROOT / "THREAD_SUMMARY.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote THREAD_SUMMARY.json")


if __name__ == "__main__":
    main()
