#!/usr/bin/env python3
"""Validate proof-obligation references across the archive.

Ensures:
  - Every PO referenced by claims/hazards exists in the PO registry.
  - PO registry IDs are unique.
"""

from __future__ import annotations

from pathlib import Path
import csv
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

PO_CSV = ROOT / "artifacts" / "proof_obligations" / "proof-obligations.csv"
CLAIMS_CSV = ROOT / "artifacts" / "claims" / "claim-evidence-matrix.csv"
HAZARDS_CSV = ROOT / "artifacts" / "hazards" / "hazard-register.csv"

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def is_track_a(track: str) -> bool:
    t = (track or "").strip().lower()
    return t == "a" or t.startswith("a ") or t.startswith("a(")


def split_ids(s: str) -> list[str]:
    if not s:
        return []
    return [x.strip() for x in re.split(r"[;,]", s) if x.strip()]

def main() -> int:
    errs: list[str] = []

    po_rows = read_csv(PO_CSV)
    po_ids = [r.get("ProofObligationID","").strip() for r in po_rows]
    po_set = set(po_ids)
    if "" in po_set:
        errs.append("PO registry contains empty ProofObligationID")
    if len(po_ids) != len(po_set):
        # find duplicates
        seen=set()
        dups=set()
        for p in po_ids:
            if p in seen:
                dups.add(p)
            seen.add(p)
        errs.append(f"Duplicate PO IDs in registry: {', '.join(sorted(dups))}")

    # Claims
    for row in read_csv(CLAIMS_CSV):
        cid = row.get("ClaimID","").strip()
        claim_pos = split_ids(row.get("ProofObligations",""))
        if is_track_a(row.get("Track","")) and not claim_pos:
            errs.append(f"Track A claim {cid} has no ProofObligations")
        for po in claim_pos:
            if po not in po_set:
                errs.append(f"Claim {cid} references unknown PO {po}")

    # Hazards
    for row in read_csv(HAZARDS_CSV):
        hid = row.get("HazardID","").strip()
        hazard_pos = split_ids(row.get("LinkedProofObligations",""))
        if is_track_a(row.get("Track","")) and not hazard_pos:
            errs.append(f"Track A hazard {hid} has no LinkedProofObligations")
        for po in hazard_pos:
            if po not in po_set:
                errs.append(f"Hazard {hid} references unknown PO {po}")

    if errs:
        print("Proof obligation reference errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
