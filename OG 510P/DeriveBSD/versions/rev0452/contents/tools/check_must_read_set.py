#!/usr/bin/env python3
"""Check that the LLM runbook's must-read set contains the archive's required invariants.

Rationale:
  The context pack is generated from the runbook's must-read list.
  If the runbook list drifts (accidentally dropping core docs), humans and automation
  lose the shared refresh path.

Rule:
  docs/99-llm-runbook.md section "## Mandatory refresh before editing" must include
  a required set of repo paths (at least these).

This check is intentionally small and conservative: it enforces only the
"start here" invariants and discovery surfaces.

Usage:
  python3 tools/check_must_read_set.py

Exit codes:
  0: ok
  1: missing required items
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "99-llm-runbook.md"

# Keep this list minimal and high leverage.
REQUIRED = [
    "docs/00-index.md",
    "docs/00-vision.md",
    "docs/01-glossary.md",
    "docs/02-derive-core.md",
    "docs/97-non-negotiable-behaviors.md",
    "docs/229-evidence-spine-overview.md",
    "docs/397-pattern-catalog.md",
    "docs/401-v0-cutline-and-feature-tiers.md",
    "docs/402-adapter-lanes-and-strangler-discipline.md",
    "docs/348-design-review-rubric-and-feature-intake.md",
    "docs/98-archive-hygiene.md",
    "docs/266-open-questions-and-risk-register.md",

    # A–D viability surfaces.
    "docs/411-product-profiles-as-compilation-target.md",
    "docs/412-product-profile-matrix.md",

    # Amnesia resistors / discovery surfaces.
    "docs/420-context-pack.md",
    "docs/414-doc-catalog.md",
    "docs/418-artifact-index.md",
    "docs/415-risk-register-index.md",

    # Invariants registry (stable diff surface for constitution-level rules).
    "docs/422-invariant-registry-and-design-invariants.md",
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_must_read(txt: str) -> list[str]:
    out: list[str] = []
    in_list = False
    for line in txt.splitlines():
        if line.strip() == "## Mandatory refresh before editing":
            in_list = True
            continue
        if in_list:
            if line.startswith("## "):
                break
            if line.strip().startswith("-"):
                hits = re.findall(r"`([^`]+)`", line)
                if hits:
                    out.extend(hits)
    # de-dupe
    seen = set()
    dedup: list[str] = []
    for x in out:
        if x and x not in seen:
            seen.add(x)
            dedup.append(x)
    return dedup


def main() -> int:
    must = set(_extract_must_read(_read(RUNBOOK)))
    missing = [p for p in REQUIRED if p not in must]

    if missing:
        print("Must-read set check FAILED. Add these to docs/99-llm-runbook.md (Mandatory refresh before editing):\n")
        for m in missing:
            print(f"- {m}")
        return 1

    print("Must-read set check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
