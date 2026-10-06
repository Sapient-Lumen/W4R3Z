#!/usr/bin/env python3
"""Ensure the canonical diff surface registry stays aligned with spec/*.diff.schema.json.

Why:
  - Diff artifacts are stable reviewer-facing surfaces.
  - Adding a new *.diff without wiring it into a canonical list creates amnesia drift.

Rule:
  - Enumerate `spec/*.diff.schema.json` and derive the expected diff kinds from filenames.
  - Require each kind to appear in `docs/430-diff-surface-registry.md` as a backticked token.
  - Reject extra backticked `*.diff` entries in the registry that do not have a schema.

Usage:
  python3 tools/check_diff_surface_registry.py

Exit codes:
  0: ok
  1: registry missing entries or contains unknown entries
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
REG = ROOT / "docs" / "430-diff-surface-registry.md"

BACKTICK_DIFF_RE = re.compile(r"`(?P<kind>[a-zA-Z0-9_.-]+\.diff)`")


def _expected_kinds() -> set[str]:
    kinds: set[str] = set()
    for p in SPEC.glob("*.diff.schema.json"):
        # Filename base is the canonical kind (e.g. authority.diff).
        kinds.add(p.name[: -len(".schema.json")])
    return kinds


def _listed_kinds(txt: str) -> set[str]:
    return {m.group("kind") for m in BACKTICK_DIFF_RE.finditer(txt)}


def main() -> int:
    if not REG.exists():
        print("Missing docs/430-diff-surface-registry.md")
        return 1

    expected = _expected_kinds()
    listed = _listed_kinds(REG.read_text(encoding="utf-8", errors="replace"))

    missing = sorted(expected - listed)
    extra = sorted(listed - expected)

    if missing or extra:
        print("Diff surface registry check FAILED. Fix docs/430-diff-surface-registry.md:\n")
        if missing:
            print("Missing diff kinds (have schemas but are not listed):")
            for k in missing:
                print(f"- {k}")
            print("")
        if extra:
            print("Unknown diff kinds (listed but no schema exists):")
            for k in extra:
                print(f"- {k}")
            print("")
        return 1

    print("Diff surface registry check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
