#!/usr/bin/env python3
"""scripts/check_no_hedging_in_public_templates.py

Release-gate drift firewall: prevent hedge-language from sneaking into
public-facing templates and adopter-facing Track A narrative docs.

Rationale:
- Hedge words ("likely", "appears", "seems", ...) are a common way to smuggle
  uncertainty into authoritative statements without being accountable.
- Public-facing artifacts should use explicit epistemic tags (docs/218) and
  uncertainty-safe update mechanics (docs/219) instead.

Scope (intentionally narrow to avoid false positives in technical docs):
- artifacts/templates/*.md
- docs/track-a/*.md
- observer-kit/README.md

This check ignores fenced code blocks and explicit "do not hedge" / "avoid
hedges" instructional lines.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "artifacts" / "templates",
    ROOT / "docs" / "track-a",
]

EXTRA_FILES = [
    ROOT / "observer-kit" / "README.md",
]

BANNED_RE = re.compile(r"\b(likely|probably|appears|seems|apparently)\b", re.IGNORECASE)

# Lines that explicitly *discuss* hedging (instructions / examples) are allowed.
ALLOW_LINE_RE = re.compile(
    r"(do not hedge|\bavoid\b|avoid(\s+bespoke)?\s+hedg|replace\s+\"?appears\"?|replace\s+\"?likely\"?)",
    re.IGNORECASE,
)


def iter_md_files() -> list[Path]:
    files: list[Path] = []
    for base in TARGETS:
        if not base.exists():
            continue
        files.extend(sorted(p for p in base.rglob("*.md") if p.is_file()))
    for p in EXTRA_FILES:
        if p.exists() and p.is_file():
            files.append(p)
    # De-dup
    uniq: list[Path] = []
    seen: set[Path] = set()
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            uniq.append(p)
            seen.add(rp)
    return uniq


def check_file(path: Path) -> list[str]:
    failures: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"{path}: cannot read ({e})"]

    in_fence = False
    fence_token: str | None = None

    for i, line in enumerate(text.splitlines(), start=1):
        s = line.rstrip("\n")

        # Fence tracking (``` or ~~~). Only treat as a fence when it starts the line.
        if s.startswith("```") or s.startswith("~~~"):
            token = s[:3]
            if not in_fence:
                in_fence = True
                fence_token = token
            elif fence_token == token:
                in_fence = False
                fence_token = None
            continue

        if in_fence:
            continue

        if not BANNED_RE.search(s):
            continue

        # Allow explicit instructional lines that talk about hedging.
        if ALLOW_LINE_RE.search(s):
            continue

        failures.append(f"{path.relative_to(ROOT)}:{i}: hedge-language in public-facing doc: {s.strip()}")

    return failures


def main() -> int:
    failures: list[str] = []
    for p in iter_md_files():
        failures.extend(check_file(p))

    if failures:
        print("FAIL check_no_hedging_in_public_templates")
        for f in failures[:200]:
            print(f)
        if len(failures) > 200:
            print(f"... ({len(failures) - 200} more)")
        return 2

    print("PASS check_no_hedging_in_public_templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
