#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "artifacts/timing/timing_full.tsv",
    "artifacts/timing/seed_full.json",
    "artifacts/timing/env_full.json",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        for p in missing:
            print(f"timing-artifacts: missing {p}", file=sys.stderr)
        return 1

    print(f"timing-artifacts: ok ({len(REQUIRED)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
