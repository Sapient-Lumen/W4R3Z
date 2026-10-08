#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from archive_meta import GENERATED, current_notes_from_index, current_revision, generated_at_utc

CURRENT_REV = current_revision()

TOP_THREAD_LIMIT = 80
PER_THREAD_EXAMPLE_LIMIT = 8

INTRO = """# Threads

This generated crosswalk is a compact reader route for archive threads. It does not republish every tag-to-note edge. Use `generated/THREAD_SUMMARY.json` for complete tag rollups and `generated/ARCHIVE_INDEX.json` for note-level theses, tags, and metadata.
"""


def note_number(note: dict) -> int:
    return int(Path(note["file"]).name.split("-", 1)[0])


def note_label(note: dict) -> str:
    return f"{note_number(note)} — `{Path(note['file']).name}`"


def thread_row(tag: str, notes: list[dict]) -> dict:
    ordered = sorted(notes, key=note_number)
    latest = ordered[-1]
    return {
        "tag": tag,
        "count": len(ordered),
        "first": ordered[0],
        "latest": latest,
        "examples": ordered[-PER_THREAD_EXAMPLE_LIMIT:],
    }


def main() -> None:
    data = json.loads((GENERATED / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    groups: dict[str, list[dict]] = defaultdict(list)
    for note in data.get("notes", []):
        for tag in note.get("tags", []):
            groups[tag].append(note)

    rows = [thread_row(tag, notes) for tag, notes in groups.items()]
    rows.sort(key=lambda row: (-row["count"], row["tag"]))
    current_notes = set(current_notes_from_index())
    current_tags = sorted(
        tag
        for tag, notes in groups.items()
        if any(note.get("file") in current_notes for note in notes)
    )

    lines = [INTRO.rstrip(), ""]
    lines.extend([
        f"Generated for `{CURRENT_REV}` at `{generated_at_utc()}`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Threads | {len(rows)} |",
        f"| Archive notes | {len(data.get('notes', []))} |",
        f"| Current-revision threads | {len(current_tags)} |",
        f"| Top thread rows rendered | {min(TOP_THREAD_LIMIT, len(rows))} |",
        "",
        "## Current-revision threads",
        "",
    ])
    if current_tags:
        for tag in current_tags:
            latest = max(groups[tag], key=note_number)
            lines.append(f"- `{tag}` — latest {note_label(latest)}")
    else:
        lines.append("- None.")
    lines.extend([
        "",
        "## Largest threads",
        "",
        "Only the largest thread rows are rendered here. The full note membership remains derivable from the machine surfaces named above.",
        "",
        "| Thread | Count | First note | Latest note |",
        "| --- | ---: | --- | --- |",
    ])
    for row in rows[:TOP_THREAD_LIMIT]:
        lines.append(
            f"| `{row['tag']}` | {row['count']} | {note_label(row['first'])} | {note_label(row['latest'])} |"
        )
    lines.extend([
        "",
        "## Recent examples for largest threads",
        "",
    ])
    for row in rows[: min(20, len(rows))]:
        lines.append(f"### {row['tag']}")
        lines.append("")
        for note in row["examples"]:
            lines.append(f"- {note_label(note)}")
        if row["count"] > len(row["examples"]):
            lines.append(f"- … {row['count'] - len(row['examples'])} earlier note(s) omitted from this reader surface")
        lines.append("")
    lines.extend([
        "## Full-detail route",
        "",
        "For complete tag membership, rebuild from `generated/ARCHIVE_INDEX.json` (`notes[].tags`) or read `generated/THREAD_SUMMARY.json` for per-tag counts and latest notes. This file is deliberately capped so thread routing cannot become a megabyte-scale first-reader tax.",
        "",
    ])

    (GENERATED / "THREADS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("OK: wrote generated/THREADS.md")


if __name__ == "__main__":
    main()
