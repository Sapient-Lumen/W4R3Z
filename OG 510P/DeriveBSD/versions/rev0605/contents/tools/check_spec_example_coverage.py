#!/usr/bin/env python3
"""Check that key artifact schemas have matching examples.

Goal:
  Prevent schema drift where critical artifact shapes exist without a concrete example.

Coverage (strict):
  - *.plan.schema.json
  - *.receipt.schema.json
  - *.event.schema.json
  - *.report.schema.json
  - *.registry.schema.json
  - *.diff.schema.json

Rule:
  For each covered schema `spec/<name>.schema.json`, require `spec/examples/<name>.json`.

Usage:
  python3 tools/check_spec_example_coverage.py

Exit codes:
  0: ok
  1: missing examples
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
EX = SPEC / "examples"

COVER_SUFFIXES = [
    ".plan.schema.json",
    ".receipt.schema.json",
    ".event.schema.json",
    ".report.schema.json",
    ".registry.schema.json",
    ".diff.schema.json",
]


def main() -> int:
    missing: list[str] = []
    for p in sorted(SPEC.glob("*.schema.json")):
        if not any(p.name.endswith(s) for s in COVER_SUFFIXES):
            continue
        ex_name = p.name.replace(".schema.json", ".json")
        ex_path = EX / ex_name
        if not ex_path.exists():
            missing.append(f"spec/examples/{ex_name} (for {p.name})")

    if missing:
        print("Missing required examples for artifact schemas:")
        for m in missing:
            print(f"- {m}")
        return 1

    print("Spec example coverage: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
