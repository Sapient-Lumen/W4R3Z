#!/usr/bin/env python3
"""Reject stale root-level hygiene/check log dumps in linked revision zips.

Structured ledgers under session-reviews/ replaced the old pattern of dropping
many hygiene_rNNN.log files in the archive root.  Root log dumps inflate every
revision, bury the source tree front door, and become stale evidence almost
immediately.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {"check_run.log", "checks_tail.log", "hygiene_full.log"}
FORBIDDEN_PREFIXES = ("hygiene_r",)
FORBIDDEN_SUFFIX = ".log"


def main() -> int:
    offenders: list[str] = []
    for path in sorted(ROOT.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name in FORBIDDEN_NAMES or (name.startswith(FORBIDDEN_PREFIXES) and name.endswith(FORBIDDEN_SUFFIX)):
            offenders.append(name)
    if offenders:
        print("Root hygiene log dump check FAILED.")
        print("Move durable run evidence under session-reviews/*.json or validation/, not root text logs.")
        for name in offenders:
            print(f"- {name}")
        return 1
    print("Root hygiene log dump check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
