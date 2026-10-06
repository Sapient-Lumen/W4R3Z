#!/usr/bin/env python3
"""Ensure risk flag metadata stays wired to real review surfaces.

Rationale:
- `risk_flags` are the stable reason codes emitted by diff summaries and used by gates.
- The canonical registry (`risk.flag.registry`) includes `typical_sources` to help UIs and
  reviewers jump to the right diff surface.
- Without a guardrail, `typical_sources` can drift (typos, renamed kinds, phantom diffs).

Rules:
- Load `spec/examples/risk.flag.registry.json`.
- For each entry in `flags[*].typical_sources`:
    - require a matching schema exists: `spec/<kind>.schema.json`
    - if the kind ends with `.diff`, require it is listed in the canonical diff surface
      registry: `docs/430-diff-surface-registry.md`

This check is intentionally conservative and fast.

Usage:
  python3 tools/check_risk_flag_typical_sources.py

Exit codes:
  0: OK
  1: at least one problem found
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
RISK_REGISTRY_EXAMPLE = SPEC / "examples" / "risk.flag.registry.json"
DIFF_REGISTRY = ROOT / "docs" / "430-diff-surface-registry.md"

DIFF_KIND_RE = re.compile(r"`(?P<kind>[a-z0-9][a-z0-9_.-]*\.diff)`")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _diff_kinds() -> set[str]:
    if not DIFF_REGISTRY.exists():
        return set()
    return {m.group("kind") for m in DIFF_KIND_RE.finditer(_read(DIFF_REGISTRY))}


def main() -> int:
    if not RISK_REGISTRY_EXAMPLE.exists():
        print("Missing spec/examples/risk.flag.registry.json")
        return 1

    try:
        reg = json.loads(_read(RISK_REGISTRY_EXAMPLE))
    except Exception as e:  # noqa: BLE001
        print("Failed to parse risk flag registry example:", e)
        return 1

    flags = reg.get("flags")
    if not isinstance(flags, list):
        print("risk.flag.registry example missing 'flags' list")
        return 1

    known_diffs = _diff_kinds()
    problems: list[str] = []

    for f in flags:
        if not isinstance(f, dict):
            continue
        fid = f.get("id", "<unknown>")
        sources = f.get("typical_sources")
        if sources is None:
            continue
        if not isinstance(sources, list):
            problems.append(f"flag {fid}: typical_sources must be a list")
            continue

        for s in sources:
            if not isinstance(s, str) or not s.strip():
                problems.append(f"flag {fid}: invalid typical_sources entry: {s!r}")
                continue

            kind = s.strip()
            schema = SPEC / f"{kind.lower()}.schema.json"
            if not schema.exists():
                problems.append(f"flag {fid}: typical_sources kind '{kind}' has no schema at spec/{kind.lower()}.schema.json")
                continue

            if kind.endswith(".diff") and kind not in known_diffs:
                problems.append(
                    f"flag {fid}: diff kind '{kind}' not listed in docs/430-diff-surface-registry.md"
                )

    if problems:
        print("Risk flag typical_sources check FAILED:\n")
        for p in problems:
            print(f"- {p}")
        print("\nFix by correcting typical_sources, adding missing schemas, or updating docs/430-diff-surface-registry.md.")
        return 1

    print("Risk flag typical_sources check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
