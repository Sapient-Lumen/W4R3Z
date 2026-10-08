#!/usr/bin/env python3
"""tools/surface_anomaly_codes.py

Stable, publishable anomaly codes for public-surface monitoring artifacts.

These codes are intended for *notes fields* in small, publishable monitoring payloads
(e.g., `PublicSurfaceParitySnapshot.observations[].notes` and
`LivenessBeacon.observations[].notes`).

Design goals:
- Codes are short and stable (comparable across implementations).
- Context MAY follow after ':' for local debugging, but publishable artifacts
  SHOULD be able to publish only the codes.
- Severity is coarse: FAIL vs WARN.

Source of truth:
- artifacts/registries/surface-anomaly-codes.csv

Normative-ish references:
- docs/201 (Public surface parity snapshots)
- docs/210 (Liveness beacons)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnomalyCode:
    code: str
    severity: str  # 'FAIL' | 'WARN'
    summary: str


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "artifacts" / "registries" / "surface-anomaly-codes.csv"


def _load_registry() -> dict[str, AnomalyCode]:
    """Load the surface anomaly-code registry.

    This is intentionally strict: anomaly codes are a publishable interoperability surface.
    If the registry is missing or malformed, tools should fail closed.
    """

    if not REGISTRY.exists():
        raise RuntimeError(f"Missing surface anomaly-code registry: {REGISTRY}")

    out: dict[str, AnomalyCode] = {}
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
                raise RuntimeError(f"Duplicate surface anomaly code: {code}")
            out[code] = AnomalyCode(code=code, severity=sev, summary=summary)

    if "unknown_surface_anomaly_code" not in out:
        raise RuntimeError("Registry must include 'unknown_surface_anomaly_code' (anti-drift).")
    return out


# Source of truth.
# Keep this list small; add new codes only when necessary.
CODES: dict[str, AnomalyCode] = _load_registry()


def code_of(note: str) -> str:
    """Return the leading code from a note string (everything before first ':')."""
    if not isinstance(note, str):
        return ""
    s = note.strip()
    if not s:
        return ""
    return s.split(":", 1)[0]


def is_known(code: str) -> bool:
    return code in CODES


def severity(code: str) -> str:
    ac = CODES.get(code)
    return ac.severity if ac else "FAIL"


def all_codes_sorted() -> list[AnomalyCode]:
    return [CODES[k] for k in sorted(CODES.keys())]
