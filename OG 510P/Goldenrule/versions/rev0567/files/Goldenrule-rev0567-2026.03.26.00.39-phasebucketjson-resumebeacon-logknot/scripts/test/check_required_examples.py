#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "examples/gauntlet/gauntlet_v2.json",
    "examples/holdouts/holdout_v1.json",
    "examples/probes/registry_smoke.json",
    "examples/probes/suites/smoke.json",
    "examples/scorecards/registry_smoke.json",
    "examples/snapshots/smoke.json",
    "examples/strategies/tft.json",
    "examples/strategies/extortion_chi3.json",
    "examples/worlds/ipd_long.json",
    "examples/worlds/ipd_noisy.json",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        for p in missing:
            print(f"required-examples: missing {p}", file=sys.stderr)
        return 1

    print(f"required-examples: ok ({len(REQUIRED)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
