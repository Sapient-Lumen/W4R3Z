#!/usr/bin/env python3
"""scripts/check_verifier_problem_codes_registry.py

Drift firewall for artifacts/registries/verifier-problem-codes.csv.

Problem codes are a publishable interoperability surface. This check enforces:
- exact column set
- stable formatting (no leading/trailing spaces)
- valid code format + severity
- uniqueness
- required sentinel: unknown_problem_code
- deterministic order (sorted by code)
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"

CODE_RE = re.compile(r"^[a-z0-9_]+$")


def main() -> int:
    if not REG.exists():
        print(f"ERROR: missing verifier problem-code registry: {REG}", file=sys.stderr)
        return 2

    errors: list[str] = []
    codes: list[str] = []
    seen: set[str] = set()

    with REG.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        required = {"code", "severity", "summary"}
        if set(r.fieldnames or []) != required:
            print(
                f"ERROR: verifier-problem-codes.csv columns must be exactly {sorted(required)}; got {r.fieldnames}",
                file=sys.stderr,
            )
            return 2

        for i, row in enumerate(r, start=2):
            raw_code = row.get("code") or ""
            raw_sev = row.get("severity") or ""
            raw_summary = row.get("summary") or ""

            code = raw_code.strip()
            sev = raw_sev.strip().upper()
            summary = raw_summary.strip()

            # Formatting stability: no hidden whitespace.
            if raw_code != raw_code.strip():
                errors.append(f"line {i}: code has leading/trailing whitespace: {raw_code!r}")
            if raw_sev != raw_sev.strip():
                errors.append(f"line {i}: severity has leading/trailing whitespace: {raw_sev!r}")
            if raw_summary != raw_summary.strip():
                errors.append(f"line {i}: summary has leading/trailing whitespace")

            if not code:
                errors.append(f"line {i}: code must be non-empty")
                continue
            if ":" in code or any(c.isspace() for c in code):
                errors.append(f"line {i}: invalid code (no ':' or whitespace): {code}")
            if not CODE_RE.match(code):
                errors.append(f"line {i}: invalid code format (expected [a-z0-9_]+): {code}")

            if sev not in {"FAIL", "WARN"}:
                errors.append(f"line {i}: invalid severity for {code}: {sev!r}")

            if not summary:
                errors.append(f"line {i}: summary must be non-empty for {code}")

            if code in seen:
                errors.append(f"line {i}: duplicate code: {code}")
            seen.add(code)
            codes.append(code)

    if "unknown_problem_code" not in seen:
        errors.append("registry must include 'unknown_problem_code' (anti-drift)")

    # Determinism: require registry already sorted by code.
    if codes != sorted(codes):
        errors.append("registry must be sorted by code (lexicographic)")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
