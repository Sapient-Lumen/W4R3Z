#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
PROJECT = json.loads((ROOT / "PROJECT.json").read_text(encoding="utf-8"))
REQUIRED_TOP = [
    "README.md",
    "START_HERE.md",
    "CHANGELOG.md",
    "INDEX.md",
    "THREADS.md",
    "SOURCES.md",
    "ARCHIVE_INDEX.json",
    "SOURCES.json",
    "RELEASES.json",
    "MANIFEST.json",
    "PROJECT.json",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    for name in REQUIRED_TOP:
        if not (ROOT / name).exists():
            fail(f"missing required file: {name}")

    notes = sorted(ARCHIVE.glob("[0-9][0-9][0-9]-*.md"))
    if not notes:
        fail("no numbered notes found")

    ids = []
    for path in notes:
        m = re.match(r"^(\d{3})-(.+)\.md$", path.name)
        if not m:
            fail(f"bad note filename: {path.name}")
        ids.append(int(m.group(1)))
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines or not lines[0].startswith(f"# {m.group(1)} — "):
            fail(f"bad H1 for {path.name}")
        for section in ["## One-line thesis", "## Why this matters", "## Pattern pack", "## Evidence anchors"]:
            if section not in text:
                fail(f"missing section {section} in {path.name}")
        if "Tags:" not in text:
            fail(f"missing Tags line in {path.name}")
        if len([line for line in lines if line.lstrip().startswith(">")]) > 8:
            fail(f"too many quoted lines in {path.name}")
        if re.search(r"https?://\S+\.pdf(?:\?\S*)?", text, flags=re.IGNORECASE):
            fail(f"raw PDF link found in {path.name}")

    if ids != sorted(ids) or len(ids) != len(set(ids)):
        fail("numbered note ids are not unique and sorted")

    arch = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    if arch.get("revision") != PROJECT["revision"]:
        fail("ARCHIVE_INDEX.json revision mismatch")
    if [n["file"] for n in arch.get("notes", [])] != [str(p.relative_to(ROOT)) for p in notes]:
        fail("ARCHIVE_INDEX.json note list mismatch")

    sources = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    if sources.get("revision") != PROJECT["revision"]:
        fail("SOURCES.json revision mismatch")
    for note in [str(p.relative_to(ROOT)) for p in notes]:
        if note not in sources.get("notes", {}):
            fail(f"SOURCES.json missing note entry for {note}")

    releases = json.loads((ROOT / "RELEASES.json").read_text(encoding="utf-8"))
    if not releases.get("releases"):
        fail("RELEASES.json missing releases")
    first = releases["releases"][0]
    if first.get("revision") != PROJECT["revision"]:
        fail("RELEASES.json first release is not current revision")
    release_notes = first.get("notes", [])
    if sorted(release_notes) != sorted([str(p.relative_to(ROOT)) for p in notes]):
        fail("RELEASES.json first release note list mismatch")

    sources_md = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    if f"Sources used for {PROJECT['revision']}." not in sources_md:
        fail("SOURCES.md revision string mismatch")

    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("revision") != PROJECT["revision"]:
        fail("MANIFEST.json revision mismatch")

    print(f"OK: lint passed for {len(notes)} notes")


if __name__ == "__main__":
    main()
