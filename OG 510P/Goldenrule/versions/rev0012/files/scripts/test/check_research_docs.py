#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


DOCS = [
    "docs/RESEARCH_SOURCES.md",
    "docs/RESEARCH_AGENDA.md",
    "docs/RESEARCH_TRANCHE_MATRIX.md",
    "docs/RESEARCH_OPINIONS.md",
    "docs/CLAIM_TAXONOMY.md",
    "docs/CLAIM_REGISTER.md",
    "docs/CLAIM_WORKFLOW.md",
    "docs/FORMAL_OBLIGATION_TABLE.md",
    "docs/BENCHMARK_PROGRAM.md",
    "docs/EXECUTION_RHYTHM.md",
    "docs/RESEARCH_RISK_REGISTER.md",
    "docs/RISK_REGISTER.md",
    "docs/CLAIM_MATRIX.md",
]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    missing = [d for d in DOCS if not (root / d).exists()]
    if missing:
        for d in missing:
            print(f"research-docs: missing {d}", file=sys.stderr)
        return 1

    index = (root / "docs" / "README.md").read_text(encoding="utf-8")
    not_indexed = [d for d in DOCS[:-1] if d not in index]
    if not_indexed:
        for d in not_indexed:
            print(f"research-docs: not indexed in docs/README.md -> {d}", file=sys.stderr)
        return 1

    print(f"research-docs: ok ({len(DOCS)} docs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
