#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "artifacts/.gitkeep",
    "artifacts/timing/.gitkeep",
    "artifacts/security/.gitkeep",
    "artifacts/process/.gitkeep",
    "artifacts/release/.gitkeep",
    "artifacts/formal/.gitkeep",
    "artifacts/reports/.gitkeep",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        for p in missing:
            print(f"artifact-gitkeep: missing {p}", file=sys.stderr)
        return 1

    print(f"artifact-gitkeep: ok ({len(REQUIRED)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
