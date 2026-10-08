#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
from archive_meta import current_notes_from_index, current_revision

CURRENT_REV = current_revision()
CURRENT_NOTES = current_notes_from_index()

CHANGELOG_RE = re.compile(r"^## (rev\d{4}) — (\d{4}-\d{2}-\d{2}) — ([a-z0-9]+)$")


def release_for_note(note_number: int) -> str | None:
    if note_number < 403:
        return None
    offset = (note_number - 403) // 3
    return f"rev{403 + offset:04d}"


def main() -> None:
    release_meta: dict[str, dict] = {}
    for line in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        m = CHANGELOG_RE.match(line.strip())
        if m:
            release_meta[m.group(1)] = {
                "revision": m.group(1),
                "date": m.group(2),
                "codename": m.group(3),
                "notes": [],
            }

    for path in sorted(ARCHIVE.glob("[0-9][0-9][0-9]-*.md")):
        num = int(path.name.split("-", 1)[0])
        rev = release_for_note(num)
        if rev and rev in release_meta:
            release_meta[rev]["notes"].append(str(path.relative_to(ROOT)))

    # Allow the current continuation snapshot to declare its note set explicitly,
    # even when the historical note-to-revision numbering convention is imperfect.
    for item in release_meta.values():
        item["notes"] = [note for note in item.get("notes", []) if note not in CURRENT_NOTES]
    if CURRENT_REV in release_meta:
        release_meta[CURRENT_REV]["notes"] = sorted(CURRENT_NOTES)

    ordered = sorted(release_meta.values(), key=lambda item: item["revision"], reverse=True)
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "releases": ordered,
    }
    (ROOT / "RELEASES.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote RELEASES.json")


if __name__ == "__main__":
    main()
