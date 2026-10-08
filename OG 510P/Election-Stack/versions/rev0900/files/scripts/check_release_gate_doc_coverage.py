#!/usr/bin/env python3
"""scripts/check_release_gate_doc_coverage.py

Drift firewall: the human release-gate control doc must name every child step
that the authoritative release runner executes.

Why this exists:
- `scripts/release_gate_steps.py` is the single source for child-step order.
- `scripts/release_gate.py` executes that inventory.
- `docs/162-*` is how maintainers and reviewers audit the gate without reading
  Python.
- If the runner grows but the control doc does not, CI may still pass while the
  archive's human release checklist becomes incomplete.

This check is stdlib-only and intentionally narrow: it does not require exact
order or duplicate descriptions, only that every child script in the inventory
is represented somewhere in the release-gate control doc.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import release_gate_steps

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "162-release-and-ci-evidence-pipeline.md"
DOC_SCRIPT_RE = re.compile(r"scripts/([A-Za-z0-9_-]+\.py)")


def fail(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)
    raise SystemExit(2)


def release_gate_steps_from_inventory() -> list[str]:
    names = list(release_gate_steps.CHECK_STEP_NAMES)
    if not names:
        fail("release-gate step inventory is empty")
    return names


def documented_scripts() -> set[str]:
    if not DOC.exists():
        fail(f"missing release-gate control doc: {DOC.relative_to(ROOT)}")
    return set(DOC_SCRIPT_RE.findall(DOC.read_text(encoding="utf-8")))


def main() -> int:
    steps = release_gate_steps_from_inventory()
    documented = documented_scripts()
    missing = [s for s in steps if s not in documented]
    if missing:
        print("FAIL: release-gate child scripts missing from docs/162", file=sys.stderr)
        for s in missing:
            print(f"  - scripts/{s}", file=sys.stderr)
        print("hint: update docs/162-release-and-ci-evidence-pipeline.md with the new gate step(s)", file=sys.stderr)
        return 2
    print(f"PASS: docs/162 names all {len(steps)} release-gate child scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
