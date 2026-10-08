#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"
TOOLS = ROOT / "tools"
PROJECT = json.loads((ROOT / "PROJECT.json").read_text(encoding="utf-8"))


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.name


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


def main() -> None:
    manifest = {
        "project": PROJECT["project"],
        "revision": PROJECT["revision"],
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "top_level_files": [
            file_entry(p)
            for p in sorted(ROOT.iterdir())
            if p.is_file() and p.name not in {"MANIFEST.json", "RELEASE-MANIFEST.json"}
        ],
        "archive_notes": [titled_entry(p) for p in sorted(ARCHIVE.glob("[0-9][0-9][0-9]-*.md"))],
        "tool_scripts": [file_entry(p) for p in sorted(TOOLS.glob("*.py"))],
    }
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("OK: wrote MANIFEST.json")


if __name__ == "__main__":
    main()
