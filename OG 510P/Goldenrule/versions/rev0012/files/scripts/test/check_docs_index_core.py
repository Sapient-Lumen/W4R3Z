#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED = [
    "docs/SCIENCE_PLAN.md",
    "docs/FORMAL_METHODS.md",
    "docs/EXPERIMENT_CATALOG.md",
    "docs/PROJECT_CHARTER.md",
    "docs/RESEARCH_AGENDA.md",
    "docs/CLAIM_TAXONOMY.md",
    "docs/CLAIM_REGISTER.md",
    "docs/RISK_REGISTER.md",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    text = (root / "docs" / "README.md").read_text(encoding="utf-8")

    missing = [p for p in REQUIRED if p not in text]
    if missing:
        for p in missing:
            print(f"docs-index: missing '{p}'", file=sys.stderr)
        return 1

    print(f"docs-index: ok ({len(REQUIRED)} links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
