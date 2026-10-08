#!/usr/bin/env python3
"""scripts/gen_verifier_profiles.py

Generate docs/VERIFIER_PROFILES.md from artifacts/registries/verifier-profiles.csv.

Rationale:
- Profiles are intended to be *small and stable* strings that verifiers can claim in
  `hfv.verifier.report` for comparability.
- This generator keeps a compact human-readable index without duplicating long prose.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "verifier-profiles.csv"
OUT = ROOT / "docs" / "VERIFIER_PROFILES.md"


def sha256_prefixed(p: Path) -> str:
    b = p.read_bytes()
    return "sha256:" + hashlib.sha256(b).hexdigest()


def main() -> int:
    if not REG.exists():
        raise SystemExit(f"Missing registry: {REG}")

    rows = []
    with REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            pid = (row.get("profile_id") or "").strip()
            summary = (row.get("summary") or "").strip()
            kinds = [(k.strip()) for k in (row.get("required_kinds") or "").split(";") if k.strip()]
            rows.append((pid, summary, kinds))

    rows.sort(key=lambda x: x[0])

    lines: list[str] = []
    lines.append("# Verifier profiles (stable capability claims)\n\n")
    lines.append(
        "This document indexes **verifier profile IDs** from `artifacts/registries/verifier-profiles.csv`. "
        "Verifiers MAY claim these IDs in `hfv.verifier.report.supported_profiles` so independent observers can compare what implementations actually support.\n\n"
    )

    lines.append("## Registry digest\n\n")
    lines.append(f"- `artifacts/registries/verifier-profiles.csv` — `{sha256_prefixed(REG)}`\n\n")

    lines.append("## Profiles\n\n")
    for pid, summary, kinds in rows:
        lines.append(f"### `{pid}`\n\n")
        if summary:
            lines.append(f"{summary}\n\n")
        lines.append("Required envelope kinds:\n\n")
        for k in kinds:
            lines.append(f"- `{k}`\n")
        lines.append("\n")

    lines.append("## Notes\n\n")
    lines.append(
        "- Profiles are intentionally **small**. When you need to communicate additional constraints (e.g., receipt tiers, transport, or UI expectations), do so in a publishable verifier narrative, not by proliferating profile IDs.\n"
    )
    lines.append(
        "- Kind semantics and schemas live in `docs/EVIDENCE_OBJECT_CATALOG.md` (generated) and the underlying registries/schemas.\n"
    )

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
