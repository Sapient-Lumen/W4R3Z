#!/usr/bin/env python3
"""Remove local transient files that can poison archive lint/package reuse."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True

TRANSIENT_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}
TRANSIENT_FILE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".tmp", ".swp", ".zip"}
TRANSIENT_FILE_NAMES = {".DS_Store"}


def is_transient(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in TRANSIENT_DIR_NAMES for part in rel.parts):
        return True
    if path.name in TRANSIENT_FILE_NAMES:
        return True
    if path.suffix in TRANSIENT_FILE_SUFFIXES:
        return True
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    removed_dirs = 0
    removed_files = 0
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path == root or not is_transient(path, root):
            continue
        if path.is_dir():
            shutil.rmtree(path)
            removed_dirs += 1
        elif path.is_file():
            path.unlink()
            removed_files += 1
    print(f"CLEAN TRANSIENTS OK removed_dirs={removed_dirs} removed_files={removed_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
