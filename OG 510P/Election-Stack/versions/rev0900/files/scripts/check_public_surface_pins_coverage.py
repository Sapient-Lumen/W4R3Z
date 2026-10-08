#!/usr/bin/env python3
"""scripts/check_public_surface_pins_coverage.py

Release-gate drift firewall: ensure `tools/public_surface_pins.py` remains a
complete + correct pin printer for small, stable registry bytes.

Rationale:
- Publishable verifier outputs may include optional sha256 pins for comparability.
- The pin tool is the operator-facing helper for copying those pins.
- If the tool silently stops emitting an important registry pin (or emits a
  wrong digest), published reports become ambiguous and hard to compare.

Policy:
- stdlib-only
- bounded: validate the tool's JSON output against a small expected map of
  registry files *when those files exist* in this archive.

What we enforce:
- `public_surface_pins.py --all --json` must emit pins for each expected
  registry file present in this archive.
- Each emitted pin must exactly match the sha256 of the raw registry bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "public_surface_pins.py"

PIN_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

EXPECTED: dict[str, Path] = {
    # Core comparability pins used by verifier outputs.
    "envelope_kinds_sha256": ROOT / "artifacts" / "registries" / "envelope-kinds.csv",
    "verifier_problem_codes_sha256": ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv",
    "verifier_profiles_sha256": ROOT / "artifacts" / "registries" / "verifier-profiles.csv",
    # Additional stable registries printed under --all.
    "official_channels_sha256": ROOT / "artifacts" / "registries" / "official-channels.csv",
    "publication_triggers_sha256": ROOT / "artifacts" / "registries" / "publication-triggers.csv",
    "receipt_profiles_sha256": ROOT / "artifacts" / "registries" / "receipt-profiles.csv",
    "envelope_attachment_requirements_sha256": ROOT
    / "artifacts"
    / "registries"
    / "envelope-attachment-requirements.csv",
    "tool_maturity_sha256": ROOT / "artifacts" / "registries" / "tool-maturity.csv",
    "surface_anomaly_codes_sha256": ROOT / "artifacts" / "registries" / "surface-anomaly-codes.csv",
}


def sha256_prefixed_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def run_tool() -> dict[str, str]:
    if not TOOL.exists():
        raise SystemExit(f"missing tool: {TOOL}")
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--all", "--json"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit("public_surface_pins.py failed")
    try:
        obj = json.loads(proc.stdout)
    except Exception as e:
        raise SystemExit(f"public_surface_pins.py did not emit valid JSON: {e}")
    if not isinstance(obj, dict):
        raise SystemExit("public_surface_pins.py JSON must be an object")
    out: dict[str, str] = {}
    for k, v in obj.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v
    return out


def main() -> int:
    pins = run_tool()
    failures: list[str] = []

    # Validate expected pins.
    for k, p in EXPECTED.items():
        if not p.exists():
            continue
        want = sha256_prefixed_bytes(p.read_bytes())
        got = pins.get(k)
        if not got:
            failures.append(f"missing pin key: {k} (file present: {p.relative_to(ROOT)})")
            continue
        if got != want:
            failures.append(f"pin mismatch for {k}: got {got} want {want}")

    # Basic hygiene: all emitted pins should be sha256-prefixed.
    for k, v in sorted(pins.items()):
        if k.endswith("_sha256") and not PIN_RE.match(v):
            failures.append(f"invalid pin format for {k}: {v!r}")

    if failures:
        for f in failures:
            print("ERROR:", f, file=sys.stderr)
        return 2

    print("PASS: public_surface_pins coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
