#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_revision, generated_at_utc

CURRENT_REV = current_revision()


def main() -> None:
    data = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
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
        "generated_at_utc": generated_at_utc(),
        "tags": {tag: summary[tag] for tag in sorted(summary)},
    }
    (GENERATED / "THREAD_SUMMARY.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/THREAD_SUMMARY.json")


if __name__ == "__main__":
    main()
