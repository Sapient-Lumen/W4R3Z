#!/usr/bin/env python3
from __future__ import annotations

import json
import re

from archive_meta import GENERATED, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
CHANGELOG_RE = re.compile(r"^## (rev\d{4}) — (\d{4}-\d{2}-\d{2}) — ([a-z0-9-]+)$")
SECTION_RE = re.compile(r"^### (rev\d{4}) additions$")
NOTE_RE = re.compile(r"^- `([0-9]{3,}-[^`]+\.md)`")


def release_notes_from_index() -> dict[str, list[str]]:
    releases: dict[str, list[str]] = {}
    current: str | None = None
    for line in (ROOT / "INDEX.md").read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(line.strip())
        if m:
            current = m.group(1)
            releases.setdefault(current, [])
            continue
        if current:
            n = NOTE_RE.match(line.strip())
            if n:
                releases[current].append(f"archive/{n.group(1)}")
    return releases


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

    indexed_notes = release_notes_from_index()
    for revision, notes in indexed_notes.items():
        if revision in release_meta:
            release_meta[revision]["notes"] = sorted(notes)

    ordered = sorted(release_meta.values(), key=lambda item: item["revision"], reverse=True)
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "source": "INDEX.md",
        "releases": ordered,
    }
    (GENERATED / "RELEASES.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/RELEASES.json from INDEX.md")


if __name__ == "__main__":
    main()
