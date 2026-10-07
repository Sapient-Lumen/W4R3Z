#!/usr/bin/env python3
"""Conservative preflight checks for a prospective new Anonymity release.

This does not publish anything. It validates naming and warns about risky sources.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
PREFIX = "Anonymity: "


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--title", required=True, help="Title without the 'Anonymity: ' prefix")
    parser.add_argument("--source", required=True, help="Source .tex path to freeze")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    src = (root / args.source).resolve()

    problems: list[str] = []
    warnings: list[str] = []

    if not DATE_RE.match(args.date):
        problems.append("date must match YYYY.MM.DD")
    if args.title.startswith(PREFIX):
        problems.append("title should omit the 'Anonymity: ' prefix")
    if not src.exists():
        problems.append(f"source does not exist: {args.source}")
    elif src.suffix != ".tex":
        problems.append("source must be a .tex file")

    if src.exists():
        rel = src.relative_to(root).as_posix()
        if rel.startswith("published/"):
            problems.append("source is already under published/")
        if rel.startswith("series/synthesis/"):
            m = re.match(r"series/synthesis/paper(\d+)_", rel)
            if m and int(m.group(1)) >= 31:
                warnings.append("late synthesis paper: default posture is defer unless a recorded stabilization reason exists")
            if rel.startswith("series/synthesis/paper17_"):
                warnings.append("worked example has been repeatedly revised; verify it is truly a freeze target")

    dirname = f"{args.date} - {PREFIX}{args.title.strip()}"
    target = root / "published" / dirname
    if target.exists():
        problems.append(f"target already exists: {target.relative_to(root)}")

    if not list((root / "release_queue" / "decisions").glob("*.md")):
        warnings.append("no decision notes found; repo should usually record one before release")

    print(f"prospective published name: [[{dirname}]]")
    print(f"source: {args.source}")
    if warnings:
        print("warnings:")
        for item in warnings:
            print(f" - {item}")
    if problems:
        print("problems:", file=sys.stderr)
        for item in problems:
            print(f" - {item}", file=sys.stderr)
        return 1

    print("preflight: PASS (no hard blockers found)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
