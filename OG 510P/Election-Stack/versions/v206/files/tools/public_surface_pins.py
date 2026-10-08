#!/usr/bin/env python3
"""tools/public_surface_pins.py

Print sha256 pins for small, stable "public surface" files.

Why:
- Publishable verifier outputs (`hfv.verifier.report`, `hfv.verifier.packet_verification_report`)
  optionally include sha256 pins for registry bytes so reports remain comparable over time.
- This helper prints those pins in a copy/pasteable format without requiring any network access.

This tool is intentionally stdlib-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]

SURFACES: Dict[str, Path] = {
    "envelope_kinds_sha256": ROOT / "artifacts" / "registries" / "envelope-kinds.csv",
    "verifier_problem_codes_sha256": ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv",
    "verifier_profiles_sha256": ROOT / "artifacts" / "registries" / "verifier-profiles.csv",
    "surface_anomaly_codes_sha256": ROOT / "artifacts" / "registries" / "surface-anomaly-codes.csv",
}


def sha256_prefixed(p: Path) -> str:
    b = p.read_bytes()
    return "sha256:" + hashlib.sha256(b).hexdigest()


def compute_pins(all_surfaces: bool) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for k, p in SURFACES.items():
        if p.exists():
            pins[k] = sha256_prefixed(p)
    if all_surfaces:
        # Emit a few additional high-value pins when present.
        extra = {
            "official_channels_sha256": ROOT / "artifacts" / "registries" / "official-channels.csv",
            "publication_triggers_sha256": ROOT / "artifacts" / "registries" / "publication-triggers.csv",
            "receipt_profiles_sha256": ROOT / "artifacts" / "registries" / "receipt-profiles.csv",
            "tool_maturity_sha256": ROOT / "artifacts" / "registries" / "tool-maturity.csv",
            "envelope_attachment_requirements_sha256": ROOT
            / "artifacts"
            / "registries"
            / "envelope-attachment-requirements.csv",
        }
        for k, p in extra.items():
            if p.exists():
                pins[k] = sha256_prefixed(p)
    return pins


def patch_json(path: Path, pins: Dict[str, str], force: bool) -> None:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise SystemExit("Target JSON must be an object")
    for k, v in pins.items():
        if force or (k not in obj):
            obj[k] = v
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Print sha256 pins for public-surface registry files")
    ap.add_argument("--json", action="store_true", help="emit JSON object")
    ap.add_argument("--all", action="store_true", help="include additional stable registries")
    ap.add_argument("--update", default=None, help="path to a JSON payload file to patch with computed pins")
    ap.add_argument("--force", action="store_true", help="overwrite existing fields when --update is used")
    args = ap.parse_args()

    pins = compute_pins(all_surfaces=bool(args.all))

    if args.update:
        patch_json(Path(args.update), pins, force=bool(args.force))
        return 0

    if args.json:
        print(json.dumps(pins, ensure_ascii=False, sort_keys=True))
        return 0

    for k in sorted(pins.keys()):
        print(f"{k}={pins[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
