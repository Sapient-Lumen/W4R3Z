#!/usr/bin/env python3
"""Minimal ENR drift detector (example).

This is intentionally small and auditable. It:
- loads a canonical CRO JSON file and hashes TBS(CRO) canonical bytes (RFC8785-JCS; docs/235)
- loads one or more observed JSON responses and compares declared cro_hash fields
- emits a DriftAlert JSON if mismatch is found

NOT production code.
"""

import argparse
import hashlib
import json
from jcs import dump_bytes as jcs_bytes
from datetime import datetime, timezone


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--election-id", required=True)
    ap.add_argument("--cro", required=True, help="Path to canonical results object (JSON)")
    ap.add_argument("--observed", nargs="+", required=True, help="Observed API/UI JSON files")
    ap.add_argument("--out", required=True, help="Write DriftAlert JSON here if drift detected")
    args = ap.parse_args()

    cro = load_json(args.cro)

    # Track A contract (docs/235): cro_hash is computed over TBS(CRO) = CRO with cro_hash omitted.
    tbs = dict(cro) if isinstance(cro, dict) else {}
    tbs.pop("cro_hash", None)
    computed_hash = sha256_hex(jcs_bytes(tbs))

    declared_hash = cro.get("cro_hash") if isinstance(cro, dict) else None
    expected_hash = declared_hash or computed_hash

    observed_hashes = []
    drift = False

    # If the CRO's declared hash does not match the TBS(CRO) computed hash, fail loud.
    cro_declared_mismatch = False
    if declared_hash and declared_hash != computed_hash:
        cro_declared_mismatch = True
        drift = True
        expected_hash = computed_hash  # prefer computed TBS hash for comparisons
    for p in args.observed:
        obs = load_json(p)
        h = obs.get("cro_hash")
        if not h:
            # Treat missing as drift (presentation drift)
            h = "(missing)"
            drift = True
        observed_hashes.append(h)
        if h != expected_hash:
            drift = True

    if not drift:
        return 0

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    alert = {
        "alert_id": f"alert_{now}_0001",
        "election_id": args.election_id,
        "severity": "CRITICAL",
        "detected_at": now,
        "class": "presentation_drift",
        "expected_cro_hash": expected_hash,
        "declared_cro_hash": declared_hash,
        "computed_cro_hash": computed_hash,
        "cro_declared_mismatch": cro_declared_mismatch,
        "observed_hashes": observed_hashes,
        "evidence": {
            "snapshots": [
                {"kind": "observed_json", "uri": p, "content_hash": sha256_hex(open(p, 'rb').read())}
                for p in args.observed
            ],
            "pbb_anchor": {}
        },
        "suggested_actions": [
            "Compare ENR UI/API derivation to CRO",
            "Check CDN/cache rules",
            "Publish signed incident statement"
        ]
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(alert, f, indent=2)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
