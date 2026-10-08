#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
CATALOG = ROOT / "tools" / "note_catalog.json"
SOURCE_DATA = ROOT / "tools" / "source_data.json"
REV_RE = re.compile(r"^# Metaphysics — (rev\d{4})$")
TITLE_RE = re.compile(r"^#\s+(\d{3})\s+—\s+(.+)$")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def current_revision() -> str:
    first = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[0].strip()
    m = REV_RE.match(first)
    if not m:
        raise RuntimeError(f"Could not parse revision from README heading: {first!r}")
    return m.group(1)


def note_catalog() -> dict:
    return read_json(CATALOG)


def source_data() -> dict:
    return read_json(SOURCE_DATA)


def archive_note_paths() -> list[Path]:
    return sorted(ARCHIVE.glob("[0-9][0-9][0-9]-*.md"))


def slug_to_title(path: Path) -> str:
    first = path.read_text(encoding="utf-8").splitlines()[0].strip()
    m = TITLE_RE.match(first)
    if not m:
        raise RuntimeError(f"Bad title line in {path}: {first!r}")
    return m.group(2)


def first_section_text(path: Path, heading: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    target = f"## {heading}"
    capture = False
    out: list[str] = []
    for line in lines:
        if line.strip() == target:
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            out.append(line)
    return "\n".join(out).strip()


def thesis_for(path: Path) -> str:
    thesis = first_section_text(path, "One-line thesis")
    if not thesis:
        raise RuntimeError(f"Missing thesis in {path}")
    return thesis.splitlines()[0].strip()


def summary_for(path: Path) -> str:
    text = first_section_text(path, "Why this matters")
    if not text:
        raise RuntimeError(f"Missing summary section in {path}")
    paragraphs = [p.strip().replace("\n", " ") for p in text.split("\n\n") if p.strip()]
    return paragraphs[0]
