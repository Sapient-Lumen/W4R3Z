#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from build_utils import generated_at_utc as _environment_generated_at_utc

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
GENERATED = ROOT / "generated"
SOURCES_DIR = ROOT / "sources"
METADATA_DIR = ROOT / "metadata"
SCHEMA_DIR = ROOT / "schema"
README = ROOT / "README.md"
INDEX = ROOT / "INDEX.md"

REV_RE = re.compile(r"^# .+ — (rev\d{4})$")
SECTION_RE = re.compile(r"^### (rev\d{4}) additions$")
NOTE_RE = re.compile(r"^- `([0-9]{3,}-[^`]+\.md)`")
NUMBERED_NOTE_FILENAME_RE = re.compile(r"^(\d{3,})-(.+)\.md$")
RELEASE_UTC_RE = re.compile(
    r"^Timestamp: `[^`]+` / `(\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)`\s*$"
)


def current_revision_timestamp_utc() -> str:
    """Return the immutable UTC timestamp declared by the current release."""
    for line in README.read_text(encoding="utf-8").splitlines()[:20]:
        match = RELEASE_UTC_RE.match(line.strip())
        if match:
            parsed = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M UTC")
            return parsed.replace(tzinfo=timezone.utc).isoformat()
    raise RuntimeError("could not parse release UTC timestamp from README")


def generated_at_utc() -> str:
    """Return a stable release timestamp unless the caller explicitly overrides it.

    ``RG_GENERATED_AT_UTC``, ``RG_GENERATED_AT``, and ``SOURCE_DATE_EPOCH``
    retain the precedence implemented in :mod:`build_utils`. Without an
    override, generation time is the current revision's declared release time,
    so identical source produces byte-identical generated output.
    """
    if any(
        os.environ.get(name, "").strip()
        for name in ("RG_GENERATED_AT_UTC", "RG_GENERATED_AT", "SOURCE_DATE_EPOCH")
    ):
        return _environment_generated_at_utc()
    return current_revision_timestamp_utc()


def numbered_archive_paths() -> list[Path]:
    """Return archive notes whose filenames use the canonical 3+-digit prefix."""
    return sorted(
        path
        for path in ARCHIVE.glob("*.md")
        if NUMBERED_NOTE_FILENAME_RE.fullmatch(path.name)
    )


def current_revision() -> str:
    first = README.read_text(encoding="utf-8").splitlines()[0].strip()
    m = REV_RE.match(first)
    if not m:
        raise RuntimeError(f"could not parse current revision from README heading: {first!r}")
    return m.group(1)


def current_notes_from_index() -> list[str]:
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    current = current_revision()
    in_block = False
    notes: list[str] = []
    for line in lines:
        m = SECTION_RE.match(line.strip())
        if m:
            if in_block:
                break
            in_block = m.group(1) == current
            continue
        if in_block:
            n = NOTE_RE.match(line.strip())
            if n:
                notes.append(f"archive/{n.group(1)}")
    if not notes:
        raise RuntimeError(f"no current revision notes found in INDEX for {current}")
    return notes
