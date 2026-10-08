#!/usr/bin/env python3
"""Audit locator-bound verified claim edges without external dependencies."""
from pathlib import Path
import json, collections, sys
ROOT = Path(__file__).resolve().parents[1]
ledger = json.loads((ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json").read_text(encoding="utf-8"))
rows = ledger.get("verified_claim_edges", [])
required = ["verified_claim_edge_id","case_id","bounded_claim","relationship_code","source_ids","exact_locator","does_not_prove","contrary_or_qualifying_evidence_needed","reversal_rule","verification_status"]
missing=[]
for row in rows:
    for key in required:
        if not row.get(key):
            missing.append((row.get("verified_claim_edge_id"), key))
print(f"verified_claim_edges={len(rows)}")
print("case_counts=" + json.dumps(collections.Counter(r.get("case_id") for r in rows), sort_keys=True))
print("relationship_counts=" + json.dumps(collections.Counter(r.get("relationship_code") for r in rows), sort_keys=True))
if missing:
    print("missing_required_fields=" + json.dumps(missing))
    sys.exit(1)
print("missing_required_fields=0")
