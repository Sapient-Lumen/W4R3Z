#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "docs/EXPERIMENT_CATALOG.md",
    "docs/TRANCHES_SUMMARY.md",
    "docs/COMMAND_INVENTORY.md",
    "docs/VALIDATOR_INVENTORY.md",
    "docs/POLICY_INVENTORY.md",
    "docs/SCHEMA_INVENTORY.md",
    "docs/ARTIFACT_BUCKETS.md",
    "docs/CLAIM_MATRIX.md",
    "docs/CLAIM_REGISTER.md",
    "docs/RISK_REGISTER.md",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [p for p in REQUIRED if not (root / p).exists()]
    if missing:
        for p in missing:
            print(f"generated-docs: missing {p}", file=sys.stderr)
        return 1

    print(f"generated-docs: ok ({len(REQUIRED)} docs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
