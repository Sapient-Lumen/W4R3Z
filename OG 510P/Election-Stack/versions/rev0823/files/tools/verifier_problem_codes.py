#!/usr/bin/env python3
"""tools/verifier_problem_codes.py

Stable, publishable problem codes for offline evidence packet verification.

Design goals:
- Codes are short and stable (comparable across implementations).
- Context MAY follow after ':' for local debugging, but publishable reports SHOULD
  be able to omit context and share only the codes.
- Severity is deliberately coarse: FAIL vs WARN.

Source of truth:
- artifacts/registries/verifier-problem-codes.csv

Normative-ish references:
- docs/179 (evidence API surface)
- docs/193 (publishable verifier reports)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProblemCode:
    code: str
    severity: str  # 'FAIL' | 'WARN'
    summary: str


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"


def _load_registry() -> dict[str, ProblemCode]:
    """Load the verifier problem-code registry.

    This is intentionally strict: problem codes are a public interoperability surface.
    If the registry is missing or malformed, tools should fail closed.
    """

    if not REGISTRY.exists():
        raise RuntimeError(f"Missing verifier problem-code registry: {REGISTRY}")

    out: dict[str, ProblemCode] = {}
    with REGISTRY.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            code = (row.get("code") or "").strip()
            sev = (row.get("severity") or "").strip().upper()
            summary = (row.get("summary") or "").strip()
            if not code:
                continue
            if sev not in {"FAIL", "WARN"}:
                raise RuntimeError(f"Invalid severity for {code}: {sev!r}")
            if code in out:
                raise RuntimeError(f"Duplicate verifier problem code: {code}")
            out[code] = ProblemCode(code=code, severity=sev, summary=summary)

    if "unknown_problem_code" not in out:
        raise RuntimeError("Registry must include 'unknown_problem_code' (anti-drift).")
    return out


# Source of truth.
# Keep this list small; add new codes only when necessary.
CODES: dict[str, ProblemCode] = _load_registry()


def code_of(problem: str) -> str:
    """Return the leading code from a problem string (everything before first ':')."""
    if not isinstance(problem, str):
        return ""
    s = problem.strip()
    if not s:
        return ""
    return s.split(":", 1)[0]


def is_known(code: str) -> bool:
    return code in CODES


def severity(code: str) -> str:
    pc = CODES.get(code)
    return pc.severity if pc else "FAIL"


def all_codes_sorted() -> list[ProblemCode]:
    return [CODES[k] for k in sorted(CODES.keys())]
