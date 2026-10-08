#!/usr/bin/env python3
"""mkrevzip.py

Create a standard-named Micromax release zip from the current working tree.

This exists to make "hand-evolved offline archives" easy and repeatable.
It intentionally does *not* modify the repo (no auto-bump); it just packages.

Usage:
  python tools/mkrevzip.py --tag fsstat-helplink-heading-mkrevzip-skyotter

The resulting filename uses the conventional pattern:
  Micromax-rev####-YYYY.MM.DD.HH.MM-<tag>.zip

Rev is inferred from the first line of TODO.md ("# TODO (revNN)").
Timestamp is created in America/New_York by default.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def infer_rev(root: Path) -> int:
    todo = root / "TODO.md"
    if todo.exists():
        first = todo.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        if first:
            m = re.search(r"rev\s*(\d+)", first[0], flags=re.IGNORECASE)
            if m:
                return int(m.group(1))

    readme = root / "README.md"
    if readme.exists():
        head = readme.read_text(encoding="utf-8", errors="replace").splitlines()[:3]
        for ln in head:
            m = re.search(r"\(v(\d+)\)", ln)
            if m:
                return int(m.group(1))

    raise SystemExit("Could not infer rev from TODO.md or README.md")


def should_skip(rel: Path) -> bool:
    parts = rel.parts
    if not parts:
        return True

    # Skip common caches and VCS metadata.
    if parts[0].startswith("."):
        if parts[0] in {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            return True
    if "__pycache__" in parts:
        return True

    # Skip already-built archives.
    if rel.suffix.lower() == ".zip":
        return True

    # Skip build outputs (best-effort).
    if parts[0] in {"build", "dist"}:
        return True

    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="hyphenated archive tag (include a codename at end)")
    ap.add_argument("--outdir", default=".", help="output directory (default: repo root)")
    ap.add_argument("--tz", default="America/New_York", help="IANA timezone for timestamp")
    ap.add_argument("--rev", type=int, default=None, help="override rev instead of inferring")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = (root / str(args.outdir)).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rev = int(args.rev) if args.rev is not None else infer_rev(root)
    stamp = datetime.now(tz=ZoneInfo(str(args.tz))).strftime("%Y.%m.%d.%H.%M")
    name = f"Micromax-rev{rev:04d}-{stamp}-{str(args.tag)}.zip"
    outpath = outdir / name

    with zipfile.ZipFile(outpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in root.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(root)
            if should_skip(rel):
                continue
            z.write(p, arcname=str(rel))

    print(str(outpath))


if __name__ == "__main__":
    main()
