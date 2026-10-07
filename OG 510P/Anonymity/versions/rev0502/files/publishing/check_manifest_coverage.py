#!/usr/bin/env python3
"""Verify that MANIFEST.sha256 covers the shipped archive surface fail-closed."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ALLOWED_UNLISTED = {"MANIFEST.sha256"}


def manifest_paths(path: pathlib.Path) -> list[str]:
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise ValueError(f"malformed MANIFEST.sha256 line: {line!r}")
        out.append(parts[1])
    return out


def file_paths(root: pathlib.Path) -> list[str]:
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
    )


def check(root: pathlib.Path) -> dict:
    listed = manifest_paths(root / "MANIFEST.sha256")
    files = file_paths(root)
    listed_set = set(listed)
    files_set = set(files)

    unlisted = sorted(files_set - listed_set)
    missing = sorted(listed_set - files_set)
    duplicates = sorted(path for path in listed_set if listed.count(path) > 1)
    unexpected_unlisted = sorted(p for p in unlisted if p not in ALLOWED_UNLISTED)

    ok = not missing and not duplicates and not unexpected_unlisted
    return {
        "status": "pass" if ok else "fail",
        "checked_root": ".",
        "manifest_path": "MANIFEST.sha256",
        "allowed_unlisted_paths": sorted(ALLOWED_UNLISTED),
        "unexpected_unlisted_paths": unexpected_unlisted,
        "missing_paths": missing,
        "duplicate_entries": duplicates,
        "summary": {
            "listed_entry_count": len(listed),
            "file_count": len(files),
            "unlisted_file_count": len(unlisted),
            "missing_path_count": len(missing),
            "duplicate_entry_count": len(duplicates),
        },
        "fail_closed_rule": "If coverage fails, default to no publication and regenerate MANIFEST.sha256 so every shipped file is either listed or explicitly allowed as unlisted.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
