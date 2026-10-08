#!/usr/bin/env python3
"""Build MANIFEST.sha256 for the archive.

This is a low-tech integrity layer: it helps detect accidental edits, partial zips,
or malicious tampering in redistribution.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MANIFEST.sha256"

EXCLUDE = {
    "MANIFEST.sha256",
}

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> None:
    files = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or rel.startswith(".git/"):
            continue
        files.append(rel)

    lines = []
    for rel in sorted(files):
        sha = file_sha256(ROOT / rel)
        lines.append(f"{sha}  {rel}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(lines)} entries.")

if __name__ == "__main__":
    main()
