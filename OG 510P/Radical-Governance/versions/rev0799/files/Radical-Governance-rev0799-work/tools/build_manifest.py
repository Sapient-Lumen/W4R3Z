#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from archive_meta import GENERATED, METADATA_DIR, ROOT, SCHEMA_DIR, SOURCES_DIR, current_revision, generated_at_utc, numbered_archive_paths

TOOLS = ROOT / "tools"


def first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.name


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_entry(path: Path) -> dict:
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256_hex(path),
    }


def titled_entry(path: Path) -> dict:
    entry = file_entry(path)
    entry["title"] = first_heading(path)
    return entry


def files_under(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [p for p in sorted(directory.rglob("*")) if p.is_file()]


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    revision = current_revision()
    generated_files = [p for p in files_under(GENERATED) if p.name != "MANIFEST.json"]
    manifest = {
        "revision": revision,
        "generated_at_utc": generated_at_utc(),
        "top_level_files": [
            file_entry(p)
            for p in sorted(ROOT.iterdir())
            if p.is_file() and not p.name.startswith("meta-")
        ],
        "source_files": [file_entry(p) for p in files_under(SOURCES_DIR)],
        "metadata_files": [file_entry(p) for p in files_under(METADATA_DIR)],
        "schema_files": [file_entry(p) for p in files_under(SCHEMA_DIR)],
        "generated_files": [file_entry(p) for p in generated_files],
        "archive_notes": [titled_entry(p) for p in numbered_archive_paths()],
        "meta_notes": [titled_entry(p) for p in sorted(ROOT.glob("meta-*.md"))],
        "tool_scripts": [file_entry(p) for p in sorted(TOOLS.glob("*.py"))],
    }

    (GENERATED / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK: wrote generated/MANIFEST.json")


if __name__ == "__main__":
    main()
