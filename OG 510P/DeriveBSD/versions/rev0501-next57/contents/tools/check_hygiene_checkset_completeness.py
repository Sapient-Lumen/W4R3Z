#!/usr/bin/env python3
"""Ensure the hygiene wrapper runs every top-level check_*.py guardrail.

Why:
  The archive relies on tools/hygiene.py as the one-command validation surface.
  A guardrail script that exists but is not listed there is easy to miss, and a
  stale hygiene entry for a deleted/renamed check makes the wrapper brittle.

Rule:
  - Every top-level check_*.py script must be referenced exactly once in
    tools/hygiene.py.
  - Every check_*.py path referenced by tools/hygiene.py must exist.
  - Non-check helpers such as lint_spec_schemas.py and validate_spec_examples.py
    are allowed but are outside this completeness rule.

Usage:
  python3 tools/check_hygiene_checkset_completeness.py

Exit codes:
  0: ok
  1: the hygiene wrapper is missing, duplicating, or referencing stale checks
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
HYGIENE = TOOLS / "hygiene.py"
CHECK_RE = re.compile(r"check_[A-Za-z0-9_]+\.py")


def main() -> int:
    if not HYGIENE.exists():
        print("Hygiene checkset completeness FAILED.")
        print("- missing tools/hygiene.py")
        return 1

    expected = {p.name for p in TOOLS.glob("check_*.py") if p.is_file()}
    text = HYGIENE.read_text(encoding="utf-8", errors="replace")
    referenced = CHECK_RE.findall(text)
    counts = Counter(referenced)
    referenced_set = set(referenced)

    missing = sorted(expected - referenced_set)
    stale = sorted(name for name in referenced_set - expected if name.startswith("check_"))
    duplicates = sorted(name for name, count in counts.items() if count > 1)

    errors: list[str] = []
    if missing:
        errors.append("missing from tools/hygiene.py: " + ", ".join(missing))
    if stale:
        errors.append("referenced by tools/hygiene.py but not present: " + ", ".join(stale))
    if duplicates:
        errors.append("referenced more than once by tools/hygiene.py: " + ", ".join(duplicates))

    if errors:
        print("Hygiene checkset completeness FAILED.")
        print("tools/hygiene.py must enumerate every top-level check_*.py guardrail exactly once.")
        for error in errors:
            print("-", error)
        print(f"Expected check scripts: {len(expected)}; referenced check scripts: {len(referenced_set)}")
        return 1

    print(f"Hygiene checkset completeness OK ({len(expected)} check scripts referenced exactly once)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
