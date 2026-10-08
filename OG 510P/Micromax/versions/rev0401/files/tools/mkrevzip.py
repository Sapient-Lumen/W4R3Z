#!/usr/bin/env python3
"""mkrevzip.py

Create a standard-named Micromax release zip from the current working tree.

This exists to make "hand-evolved offline archives" easy and repeatable.
It intentionally does *not* modify the repo (no auto-bump); it just packages.

Usage:
  python tools/mkrevzip.py --tag fsstat-helplink-heading-mkrevzip-skyotter

The resulting filename uses the conventional pattern:
  Micromax-rev####-YYYY.MM.DD.HH.MM-<tag>.zip

Rev is inferred from the current repo context.
Timestamp is created in America/New_York by default.
Each archive also embeds one machine-readable repo-context snapshot so future
humans/LLMs can inspect the packaged revision without reopening half the tree.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from mxcontext import payload as context_payload


def infer_rev(root: Path) -> int:
    """Infer the current revision from the repo's rev breadcrumbs."""
    todo = root / "TODO.md"
    readme = root / "README.md"
    revisions: list[int] = []
    if todo.exists():
        lines = todo.read_text(encoding="utf-8", errors="replace").splitlines()
        if lines:
            m = re.search(r"rev\s*(\d+)", lines[0], flags=re.IGNORECASE)
            if m:
                revisions.append(int(m.group(1)))
        for line in lines:
            if line.strip().startswith("# TODO"):
                m = re.search(r"rev\s*(\d+)", line, flags=re.IGNORECASE)
                if m:
                    revisions.append(int(m.group(1)))
                break
    if readme.exists():
        head = readme.read_text(encoding="utf-8", errors="replace").splitlines()[:8]
        for ln in head:
            m = re.search(r"Rev\s*(\d+)\s+note:", ln, flags=re.IGNORECASE)
            if m:
                revisions.append(int(m.group(1)))
                break
    if revisions:
        return max(revisions)
    raise SystemExit("Could not infer rev from TODO.md or README.md")


def should_skip(rel: Path) -> bool:
    parts = rel.parts
    if not parts:
        return True

    if parts[0].startswith("."):
        if parts[0] in {".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            return True
    if "__pycache__" in parts:
        return True
    if rel.suffix.lower() == ".zip":
        return True
    if parts[0] in {"build", "dist"}:
        return True
    return False


def archive_manifest(*, archive_name: str, tag: str, stamp: str, tz_name: str, manifest_name: str) -> dict[str, object]:
    return {
        "archive": {
            "name": archive_name,
            "tag": tag,
            "timestamp": stamp,
            "timezone": tz_name,
            "context_path": manifest_name,
            "created_by": "tools/mkrevzip.py",
        },
        "context": context_payload(),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="hyphenated archive tag (include a codename at end)")
    ap.add_argument("--outdir", default=".", help="output directory (default: repo root)")
    ap.add_argument("--tz", default="America/New_York", help="IANA timezone for timestamp")
    ap.add_argument("--rev", type=int, default=None, help="override rev instead of inferring")
    ap.add_argument("--stamp", default=None, help="override timestamp (YYYY.MM.DD.HH.MM) for deterministic packaging/tests")
    ap.add_argument(
        "--manifest-name",
        default="MICROMAX-CONTEXT.json",
        help="archive-internal context snapshot filename (default: MICROMAX-CONTEXT.json)",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = (root / str(args.outdir)).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rev = int(args.rev) if args.rev is not None else infer_rev(root)
    stamp = str(args.stamp) if args.stamp else datetime.now(tz=ZoneInfo(str(args.tz))).strftime("%Y.%m.%d.%H.%M")
    name = f"Micromax-rev{rev:04d}-{stamp}-{str(args.tag)}.zip"
    outpath = outdir / name
    manifest_name = str(args.manifest_name).strip() or "MICROMAX-CONTEXT.json"
    manifest = archive_manifest(
        archive_name=name,
        tag=str(args.tag),
        stamp=stamp,
        tz_name=str(args.tz),
        manifest_name=manifest_name,
    )

    with zipfile.ZipFile(outpath, "w", compression=zipfile.ZIP_DEFLATED) as z:
        manifest_rel = Path(manifest_name)
        for p in sorted(root.rglob("*")):
            if p.is_dir():
                continue
            rel = p.relative_to(root)
            if rel == manifest_rel:
                continue
            if should_skip(rel):
                continue
            z.write(p, arcname=str(rel))
        z.writestr(manifest_name, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(str(outpath))


if __name__ == "__main__":
    main()
