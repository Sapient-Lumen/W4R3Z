#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "artifacts",
    "artifacts/timing",
    "artifacts/security",
    "artifacts/process",
    "artifacts/release",
    "artifacts/formal",
    "artifacts/reports",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing: list[str] = []
    for rel in REQUIRED:
        p = root / rel
        if not p.exists() or not p.is_dir():
            missing.append(rel)

    if missing:
        for m in missing:
            print(f"artifact-layout: missing {m}", file=sys.stderr)
        return 1

    print(f"artifact-layout: ok ({len(REQUIRED)} directories)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
