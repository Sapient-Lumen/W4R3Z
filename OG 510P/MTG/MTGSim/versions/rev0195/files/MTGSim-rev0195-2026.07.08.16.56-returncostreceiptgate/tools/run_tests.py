#!/usr/bin/env python3
"""Compatibility wrapper for the rev0002 timed harness."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["debug", "release", "sanitize", "profile"], default="release")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--jobs", default="auto")
    parser.add_argument("--budget-sec", type=float, default=None)
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args(argv)

    cmd = [sys.executable, "tools/harness.py", "test", "--mode", args.mode, "--jobs", args.jobs]
    if args.no_build:
        cmd.append("--skip-build")
    if args.budget_sec is not None:
        cmd.extend(["--budget-sec", str(args.budget_sec)])
    if args.keep_going:
        cmd.append("--keep-going")
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
