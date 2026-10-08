#!/usr/bin/env python3
"""mxpack: build a clean zip archive of this repo.

Why this exists:

* The project is meant to be hackable "by hand" offline.
* Future LLMs (and humans) will often receive the project as an archive.
* Transient build caches (pycache, pytest cache, etc.) add noise and churn.

This tool makes it easy to produce a clean, deterministic-ish zip.
"""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


EXCLUDE_DIRS = {
    ".git",
    ".artifacts",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".zip",
}

EXCLUDE_FILES = {
    ".DS_Store",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mxpack", description="Create a clean zip archive of the repo")
    ap.add_argument("out", nargs="?", default="micromax.zip", help="output zip path")
    args = ap.parse_args(argv)

    out = Path(args.out)
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    # If the output zip lives inside the repo, ensure we don't include it.
    # Otherwise we'd try to zip the zip while writing it.
    out_in_repo = False
    try:
        out.relative_to(ROOT)
        out_in_repo = True
    except Exception:
        out_in_repo = False

    # Ensure output directory exists.
    out.parent.mkdir(parents=True, exist_ok=True)

    # Build zip.
    if out.exists():
        out.unlink()

    n = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(ROOT.rglob("*")):
            if p.is_dir():
                continue
            if out_in_repo and p.resolve() == out:
                continue
            rel = p.relative_to(ROOT)
            if should_skip(rel):
                continue
            # Use forward slashes for portability.
            arcname = str(rel).replace(os.sep, "/")
            zf.write(p, arcname=arcname)
            n += 1

    print(f"wrote: {out} ({n} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
