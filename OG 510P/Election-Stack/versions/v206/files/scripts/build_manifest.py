#!/usr/bin/env python3
"""Build MANIFEST.sha256 for the archive.

This is a low-tech integrity layer: it helps detect accidental edits, partial zips,
or malicious tampering in redistribution.

By default this script *writes* MANIFEST.sha256.
Use --check to fail if the working tree does not match the existing manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MANIFEST.sha256"

EXCLUDE = {
    "MANIFEST.sha256",
}

# Never ship interpreter/build caches inside the archive.
EXCLUDE_DIR_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

EXCLUDE_FILENAMES = {
    ".DS_Store",
}

# Directories that may contain operator-local state or downloaded third-party bytes.
# These MUST NOT affect the archive manifest.
EXCLUDE_PREFIXES = {
    "evidence/cache/",
    # Local release outputs. Normative bundles are built via scripts/build_release_zip.py
    # and distributed out-of-tree; keep dist/ out of the integrity manifest to prevent
    # size growth from accumulating release artifacts.
    "dist/",
}


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest_text() -> str:
    files: list[str] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()

        # Explicit exclude list and VCS dirs.
        if rel in EXCLUDE or rel.startswith(".git/"):
            continue

        # Prefix excludes.
        if any(rel.startswith(pfx) for pfx in EXCLUDE_PREFIXES):
            continue

        # Exclude cache/build directories anywhere in the tree.
        parts = set(Path(rel).parts)
        if parts.intersection(EXCLUDE_DIR_PARTS):
            continue

        # Exclude unwanted file suffixes / names.
        if p.suffix in EXCLUDE_SUFFIXES or p.name in EXCLUDE_FILENAMES:
            continue

        files.append(rel)

    lines = []
    for rel in sorted(files):
        sha = file_sha256(ROOT / rel)
        lines.append(f"{sha}  {rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build or check MANIFEST.sha256")
    ap.add_argument("--check", action="store_true", help="fail if MANIFEST.sha256 does not match")
    args = ap.parse_args()

    manifest_text = build_manifest_text()

    if args.check:
        if not OUT.exists():
            print("FAIL: MANIFEST.sha256 missing")
            return 2
        current = OUT.read_text(encoding="utf-8")
        if current == manifest_text:
            print("PASS: MANIFEST.sha256 matches")
            return 0
        # Keep output small: emit a short summary.
        want_n = len(manifest_text.splitlines())
        cur_n = len(current.splitlines())
        print("FAIL: MANIFEST.sha256 does not match")
        print(f"  expected_entries: {want_n}")
        print(f"  current_entries:   {cur_n}")
        print("  hint: run scripts/build_manifest.py to regenerate")
        return 2

    OUT.write_text(manifest_text, encoding="utf-8")
    print(f"Wrote {OUT} with {len(manifest_text.splitlines())} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
