#!/usr/bin/env python3
"""scripts/check_tool_maturity_registry.py

Release-gate drift firewall for tools intent/maturity.

Rationale:
- The archive contains a mix of operator helpers, research prototypes, and explicit skeletons.
- Readers should not confuse *convenience tooling* with normative evidence surfaces.

This check enforces:
- every tools/*.py file is listed exactly once
- strict enums for maturity + evidence-safety
- lexicographic ordering (stable diffs)
- basic invariants (skeletons are not evidence-safe; smoke-tested tools are operator-facing)

Registry: artifacts/registries/tool-maturity.csv
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "tool-maturity.csv"
TOOLS_DIR = ROOT / "tools"

REQUIRED_HEADER = ["tool", "maturity", "evidence_safe", "smoke_tested", "notes"]
ALLOWED_MATURITY = {"operator", "research", "skeleton", "library"}
ALLOWED_EVIDENCE_SAFE = {"yes", "no", "conditional"}
ALLOWED_YN = {"yes", "no"}


def list_tools_py() -> list[str]:
    if not TOOLS_DIR.exists():
        return []
    return sorted([p.name for p in TOOLS_DIR.glob("*.py") if p.is_file()])


def main() -> int:
    errors: list[str] = []

    if not REG.exists():
        print(f"ERROR: missing registry {REG}")
        return 2

    with REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        rows = list(r)

    if not rows:
        print("ERROR: tool-maturity.csv is empty")
        return 2

    header = [c.strip() for c in rows[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header} want {REQUIRED_HEADER}")

    seen: dict[str, int] = {}
    tools_in_csv: list[str] = []

    for i, row in enumerate(rows[1:], start=2):
        if not row or all((c or "").strip() == "" for c in row):
            continue
        if len(row) < len(REQUIRED_HEADER):
            errors.append(f"L{i}: too few columns")
            continue

        tool, maturity, evidence_safe, smoke_tested, notes = [c.strip() for c in row[:5]]
        if not tool:
            errors.append(f"L{i}: missing tool")
            continue

        tools_in_csv.append(tool)
        seen[tool] = seen.get(tool, 0) + 1
        if seen[tool] > 1:
            errors.append(f"L{i}: duplicate tool entry: {tool}")

        if maturity not in ALLOWED_MATURITY:
            errors.append(f"L{i}: invalid maturity for {tool}: {maturity!r}")
        if evidence_safe not in ALLOWED_EVIDENCE_SAFE:
            errors.append(f"L{i}: invalid evidence_safe for {tool}: {evidence_safe!r}")
        if smoke_tested not in ALLOWED_YN:
            errors.append(f"L{i}: invalid smoke_tested for {tool}: {smoke_tested!r}")

        # Invariants
        if maturity == "skeleton" and evidence_safe != "no":
            errors.append(f"L{i}: skeleton must be evidence_safe=no ({tool})")
        if smoke_tested == "yes" and maturity != "operator":
            errors.append(f"L{i}: smoke_tested=yes requires maturity=operator ({tool})")

        # Tool must exist.
        if not (TOOLS_DIR / tool).exists():
            errors.append(f"L{i}: tool file does not exist: tools/{tool}")

    # Ordering firewall (stable diffs)
    tools_sorted = sorted(tools_in_csv)
    if tools_in_csv != tools_sorted:
        errors.append("registry not sorted lexicographically by tool")

    # Completeness: every tools/*.py must be present.
    want = set(list_tools_py())
    got = set(tools_in_csv)
    missing = sorted(want - got)
    extra = sorted(got - want)
    if missing:
        errors.append("missing tools in registry: " + ", ".join(missing))
    if extra:
        errors.append("extra registry rows for non-existent tools: " + ", ".join(extra))

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: tool maturity registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
