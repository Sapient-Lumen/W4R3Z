#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED = [
    "make doctor",
    "make test-quick",
    "make test-full",
    "make gate",
    "make gate-strict",
    "make test-tranches",
    "make test-release-manifest-schema",
    "make report-repro-bundle",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(["make", "help"], cwd=str(root), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print("make-help: 'make help' failed", file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return 1

    out = proc.stdout
    missing = [s for s in REQUIRED if s not in out]
    if missing:
        for s in missing:
            print(f"make-help: missing '{s}'", file=sys.stderr)
        return 1

    print(f"make-help: ok ({len(REQUIRED)} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
