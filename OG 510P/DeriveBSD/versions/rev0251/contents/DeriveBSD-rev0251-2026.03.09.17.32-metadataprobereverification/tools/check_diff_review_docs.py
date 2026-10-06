#!/usr/bin/env python3
"""Guardrail: ensure diff review-surface docs stay crisp and consistently wired.

Why:
  - Diff artifacts are stable reviewer-facing surfaces.
  - We have many per-diff docs (e.g., *-diff-as-*-surface.md). Small drift across them
    causes amnesia and undermines the "stable diff surfaces" pillar.

Scope:
  - Docs in docs/ matching '*diff-as-*surface*.md'.

Rules (conservative, format-agnostic): each doc must:
  - Mention a Tier placement (Tier A–E).
  - Mention the canonical pattern token 'Registry→Diff→Gate'.
  - Mention at least one backticked '*.diff' kind.
  - Mention the schema path for that kind ('spec/<kind>.schema.json').
  - Mention at least one example path under 'spec/examples/'.

Usage:
  python3 tools/check_diff_review_docs.py

Exit codes:
  0: ok
  1: at least one doc violates the guardrail
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

DIFF_DOC_GLOB = "*diff-as-*surface*.md"

TIER_RE = re.compile(r"\bTier\b[^A-Za-z0-9]{0,6}[:*\s]*\b(?P<tier>[ABCDE])\b")
DIFF_KIND_RE = re.compile(r"`(?P<kind>[a-zA-Z0-9_.-]+\.diff)`")


def _check_doc(path: Path) -> list[str]:
    issues: list[str] = []
    txt = path.read_text(encoding="utf-8", errors="replace")

    if not TIER_RE.search(txt):
        issues.append("missing Tier placement (e.g., 'Tier B')")

    if "Registry→Diff→Gate" not in txt:
        issues.append("missing 'Registry→Diff→Gate' pattern token")

    kinds = [m.group("kind") for m in DIFF_KIND_RE.finditer(txt)]
    if not kinds:
        issues.append("missing backticked '*.diff' kind")
        return issues

    kind = kinds[0]
    schema_path = f"spec/{kind}.schema.json"
    if schema_path not in txt:
        issues.append(f"missing schema path '{schema_path}'")

    if "spec/examples/" not in txt:
        issues.append("missing example path under 'spec/examples/'")

    return issues


def main() -> int:
    if not DOCS.exists():
        print("Missing docs/ directory")
        return 1

    candidates = sorted(DOCS.glob(DIFF_DOC_GLOB))
    if not candidates:
        print("No diff review-surface docs found (pattern '*diff-as-*surface*.md')")
        return 0

    failures: list[tuple[Path, list[str]]] = []
    for p in candidates:
        issues = _check_doc(p)
        if issues:
            failures.append((p, issues))

    if failures:
        print("Diff review-surface docs check FAILED. Fix the following docs:\n")
        for p, issues in failures:
            rel = p.relative_to(ROOT)
            print(f"- {rel}:")
            for i in issues:
                print(f"  - {i}")
        print("")
        return 1

    print("Diff review-surface docs check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
