#!/usr/bin/env python3
"""scripts/check_operator_smoke_coverage.py

Release-gate drift firewall: tool-maturity smoke flags must match the actual smoke harness.

Rationale:
- `artifacts/registries/tool-maturity.csv` is an intent surface.
- If a tool is marked `smoke_tested=yes`, the release gate must actually exercise it.
  Otherwise the flag becomes misleading and the operator UX can silently rot.

This check enforces that every `smoke_tested=yes` tool appears as an invoked tool path
in `scripts/check_operator_tools_smoke.py`.

This is intentionally simple (stdlib-only) and avoids trying to interpret control flow.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "tool-maturity.csv"
SMOKE = ROOT / "scripts" / "check_operator_tools_smoke.py"


_TOOL_REF_RE = re.compile(r"TOOLS\s*/\s*\"([^\"]+)\"")


def load_smoke_tools() -> set[str]:
    tools: set[str] = set()
    if not REG.exists():
        return tools
    with REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            tool = (row.get("tool") or "").strip()
            if not tool:
                continue
            if (row.get("smoke_tested") or "").strip() == "yes":
                tools.add(tool)
    return tools


def referenced_in_smoke_harness() -> set[str]:
    refs: set[str] = set()
    if not SMOKE.exists():
        return refs
    text = SMOKE.read_text(encoding="utf-8")
    for m in _TOOL_REF_RE.finditer(text):
        refs.add(m.group(1))
    return refs


def main() -> int:
    want = load_smoke_tools()
    got = referenced_in_smoke_harness()

    missing = sorted(want - got)
    if missing:
        for t in missing:
            print(f"ERROR: tool marked smoke_tested=yes but not invoked in check_operator_tools_smoke.py: {t}")
        return 2

    print("PASS: operator smoke coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
