#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INDEX = ROOT / "INDEX.md"
REV_RE = re.compile(r"^# .+ — (rev\d{4})$")
SECTION_RE = re.compile(r"^### (rev\d{4}) additions$")
NOTE_RE = re.compile(r"^- `([^`]+\.md)`")


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
