#!/usr/bin/env python3
"""Reject stale explicit current-stack range labels in bounded maintainer docs."""

from __future__ import annotations

import re
from pathlib import Path

from _shared.special_case_control_stack import current_special_case_control_stack_range_label

ROOT = Path(__file__).resolve().parents[1]
CURRENT_LABEL = current_special_case_control_stack_range_label()
RANGE_RE = re.compile(r"\b344[–-](\d+)\b")

TARGETS = [
    "docs/13-artifact-index.md",
    "docs/162-release-and-ci-evidence-pipeline.md",
    "docs/242-audience-reading-paths-and-what-to-ignore.md",
    "docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md",
    "docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md",
    "docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md",
    "docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md",
    "docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md",
    "docs/START_HERE.md",
]


def main() -> int:
    errors: list[str] = []
    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            errors.append(f"missing target doc {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        found = sorted(set(m.group(0) for m in RANGE_RE.finditer(text)))
        bad = [label for label in found if label != CURRENT_LABEL]
        if bad:
            rendered = ", ".join(bad)
            errors.append(f"{rel} carries stale explicit current-stack range label(s): {rendered}; expected {CURRENT_LABEL}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 2
    print(f"PASS: special-case current-stack range labels match {CURRENT_LABEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
