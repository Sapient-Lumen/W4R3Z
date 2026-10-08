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
        for po in split_ids(row.get("ProofObligations","")):
            if po not in po_set:
                errs.append(f"Claim {cid} references unknown PO {po}")

    # Hazards
    for row in read_csv(HAZARDS_CSV):
        hid = row.get("HazardID","").strip()
        for po in split_ids(row.get("LinkedProofObligations","")):
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
