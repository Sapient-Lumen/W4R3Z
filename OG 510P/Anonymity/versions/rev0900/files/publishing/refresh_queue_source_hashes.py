#!/usr/bin/env python3
"""Refresh Queue-bound source SHA-256 lines in active queue notes.

This is a maintenance helper, not a publication command. It updates Candidate,
Published-ready, and Hold queue notes so each human governance note names the
current source bytes for its `Source paper` path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

SOURCE_RE = re.compile(r"^- Source paper: `([^`]+)`$", re.MULTILINE)
HASH_LINE_RE = re.compile(r"^- Queue-bound source SHA-256: `sha256:[0-9a-f]{64}`$")
QUEUE_DIRS = ["release_queue/candidates", "release_queue/published_ready", "release_queue/hold"]


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def update_note(root: pathlib.Path, path: pathlib.Path, *, dry_run: bool = False) -> dict[str, Any]:
    rel_note = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8")
    source_match = SOURCE_RE.search(text)
    if not source_match:
        return {"note": rel_note, "status": "skip", "reason": "missing Source paper line"}

    source_rel = source_match.group(1)
    source_path = root / source_rel
    if not source_path.exists():
        return {"note": rel_note, "status": "fail", "reason": "missing source", "source_tex": source_rel}

    digest = sha256_file(source_path)
    wanted = f"- Queue-bound source SHA-256: `sha256:{digest}`"
    lines = text.splitlines()
    out: list[str] = []
    inserted_or_replaced = False
    changed = False

    for idx, line in enumerate(lines):
        if HASH_LINE_RE.match(line):
            if line != wanted:
                changed = True
            out.append(wanted)
            inserted_or_replaced = True
            continue
        out.append(line)
        if line == source_match.group(0) and not inserted_or_replaced:
            next_line = lines[idx + 1] if idx + 1 < len(lines) else ""
            if not HASH_LINE_RE.match(next_line):
                out.append(wanted)
                inserted_or_replaced = True
                changed = True

    if not inserted_or_replaced:
        out.append(wanted)
        changed = True

    if changed and not dry_run:
        path.write_text("\n".join(out) + "\n", encoding="utf-8")

    return {
        "note": rel_note,
        "status": "updated" if changed else "unchanged",
        "source_tex": source_rel,
        "source_sha256": digest,
    }


def refresh(root: pathlib.Path, *, dry_run: bool = False) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for rel_dir in QUEUE_DIRS:
        directory = root / rel_dir
        for path in sorted(directory.glob("*.md")):
            rows.append(update_note(root, path, dry_run=dry_run))
    failures = [row for row in rows if row["status"] == "fail"]
    return {
        "status": "fail" if failures else "pass",
        "dry_run": dry_run,
        "queue_dirs": QUEUE_DIRS,
        "summary": {
            "notes_checked": len(rows),
            "updated": sum(1 for row in rows if row["status"] == "updated"),
            "unchanged": sum(1 for row in rows if row["status"] == "unchanged"),
            "skipped": sum(1 for row in rows if row["status"] == "skip"),
            "failed": len(failures),
        },
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = refresh(root, dry_run=args.dry_run)
    sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
