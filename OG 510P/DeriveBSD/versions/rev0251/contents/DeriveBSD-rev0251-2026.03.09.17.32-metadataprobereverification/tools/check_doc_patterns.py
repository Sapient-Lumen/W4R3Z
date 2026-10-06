#!/usr/bin/env python3
"""Check that high-leverage docs declare which DeriveBSD patterns they use.

Rationale:
- "Patterns are law" only works if new work *explicitly* maps to the catalog.
- A tiny metadata field creates a stable review surface and reduces amnesia.

Rule (intentionally narrow):
- Docs with numeric prefix >= 397 MUST include, near the top:
    - **Patterns:**

Exception:
- Generated navigation surfaces are exempt (doc catalog, artifact index, context pack,
  product profile matrix, risk register index). These are detected by the presence
  of "This page is generated" or "(generated)" in the header block.

Validation (lightweight):
- Patterns must be a comma-separated list.
- Each entry must match one of the allowed canonical patterns (with flexible
  whitespace and arrow formatting).

Allowed patterns (canonical names):
- Plan→Apply→Receipt
- Broker→Lease→Receipt
- Registry→Diff→Gate
- Quarantine→Promote
- Observation→Suggestion→Review→Enforce
- Capsule
- Bundles
- Adapter→Shadow→Replace

Usage:
  python3 tools/check_doc_patterns.py

Exit codes:
  0: OK
  1: At least one doc missing Patterns metadata or has invalid values
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

DOC_RE = re.compile(r"^(?P<num>\d+)-.+\.md$")
PATTERNS_RE = re.compile(r"^\*\*Patterns:\*\*\s*(?P<val>.+?)\s*$")

ALLOWED_CANONICAL = [
    "Plan→Apply→Receipt",
    "Broker→Lease→Receipt",
    "Registry→Diff→Gate",
    "Quarantine→Promote",
    "Observation→Suggestion→Review→Enforce",
    "Capsule",
    "Bundles",
    "Adapter→Shadow→Replace",
]

# Normalized keys -> canonical display
CANONICAL_MAP = {
    "plan→apply→receipt": "Plan→Apply→Receipt",
    "plan→receipt": "Plan→Apply→Receipt",
    "broker→lease→receipt": "Broker→Lease→Receipt",
    "broker→lease": "Broker→Lease→Receipt",
    "registry→diff→gate": "Registry→Diff→Gate",
    "registry→diff": "Registry→Diff→Gate",
    "quarantine→promote": "Quarantine→Promote",
    "quarantine→promote→": "Quarantine→Promote",
    "observation→suggestion→review→enforce": "Observation→Suggestion→Review→Enforce",
    "observe→suggest→review→enforce": "Observation→Suggestion→Review→Enforce",
    "capsule": "Capsule",
    "bundles": "Bundles",
    "bundlescomposedriftsurfaces": "Bundles",
    "adapter→shadow→replace": "Adapter→Shadow→Replace",
    "adapter→shadow": "Adapter→Shadow→Replace",
}


def _top_lines(txt: str, max_lines: int = 60) -> list[str]:
    return [ln.rstrip("\n") for ln in txt.splitlines()[:max_lines]]


def _is_generated(top: list[str]) -> bool:
    for ln in top[:30]:
        low = ln.lower()
        if "this page is generated" in low:
            return True
        if "(generated)" in low:
            return True
        if low.strip().startswith("> generated"):
            return True
        if "generated from" in low:
            return True
        if "do not hand-edit" in low:
            return True
    return False


def _split_csv(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def _normalize_item(raw: str) -> str:
    s = raw.strip()
    # unify arrows
    s = s.replace("->", "→")
    # drop spaces
    s = re.sub(r"\s+", "", s)
    return s.lower()


def main() -> int:
    problems: list[str] = []

    for p in sorted(DOCS.glob("*.md")):
        m = DOC_RE.match(p.name)
        if not m:
            continue
        n = int(m.group("num"))
        if n < 397:
            continue

        txt = p.read_text(encoding="utf-8", errors="replace")
        top = _top_lines(txt)
        if _is_generated(top):
            continue

        pat_line = ""
        for ln in top:
            mm = PATTERNS_RE.match(ln.strip())
            if mm:
                pat_line = mm.group("val").strip()
                break

        if not pat_line:
            problems.append(f"{p.name}: missing **Patterns:** metadata")
            continue

        items = _split_csv(pat_line)
        if not items:
            problems.append(f"{p.name}: empty Patterns list")
            continue

        bad: list[str] = []
        canonical: list[str] = []
        for it in items:
            key = _normalize_item(it)
            if key in CANONICAL_MAP:
                canonical.append(CANONICAL_MAP[key])
            else:
                bad.append(it)

        if bad:
            problems.append(
                f"{p.name}: invalid Patterns entries {bad} (allowed: {ALLOWED_CANONICAL})"
            )
            continue

        # duplicates after normalization are a smell
        if len(set(canonical)) != len(canonical):
            problems.append(f"{p.name}: duplicate Patterns after normalization {canonical}")

    if problems:
        print("Doc patterns check FAILED. Add a Patterns metadata line near the top:\n")
        for pr in problems:
            print(f"- {pr}")
        print("\nTemplate:\n")
        print(
            "  **Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate\n\n"
            "Allowed patterns:\n"
            + "\n".join([f"- {x}" for x in ALLOWED_CANONICAL])
        )
        return 1

    print("Doc patterns check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
