#!/usr/bin/env python3
from pathlib import Path
import json, collections, sys
ROOT = Path(__file__).resolve().parents[1]
REV = "rev0366"
CASE = "stablecoins-money-market-treasury-liquidity-backstop-rev0319"
ledger = json.loads((ROOT/"cases"/"VERIFIED_CLAIM_EDGE_LEDGER.json").read_text(encoding="utf-8"))
rows = [r for r in ledger.get("verified_claim_edges", []) if r.get("case_id") == CASE]
new_rows = [r for r in rows if r.get("created_revision") == REV]
packet = json.loads((ROOT/"cases"/f"{CASE}-claim-packet.json").read_text(encoding="utf-8"))
mapdoc = json.loads((ROOT/"cases"/f"{CASE}-treasury-basis-repo-clearing-map.json").read_text(encoding="utf-8"))
required_sources = {"S359","S557","S558","S559","S560","S561","S562"}
source_union = set().union(*(set(r.get("source_ids", [])) for r in new_rows)) if new_rows else set()
problems=[]
if len(new_rows) < 16: problems.append("expected_at_least_16_rev0366_treasury_edges")
if not required_sources.issubset(source_union): problems.append("missing_required_treasury_source_coverage")
if packet.get("case_certification_status_after") == "certified_current": problems.append("packet_overcertifies_case")
if mapdoc.get("certification_status") != "not_certified_current": problems.append("map_does_not_preserve_noncertification")
if len(mapdoc.get("perimeter_layers") or []) < 6: problems.append("map_missing_six_layer_perimeter")
for r in new_rows:
    for k in ["verified_claim_edge_id","bounded_claim","relationship_code","source_ids","exact_locator","does_not_prove","contrary_or_qualifying_evidence_needed","reversal_rule"]:
        if not r.get(k): problems.append(f"{r.get('verified_claim_edge_id')} missing {k}")
out = {
  "revision_current": REV,
  "case_id": CASE,
  "new_edge_count": len(new_rows),
  "total_case_edge_count": len(rows),
  "relationship_counts": dict(collections.Counter(r.get("relationship_code") for r in new_rows)),
  "source_union": sorted(source_union, key=lambda s:int(s[1:])),
  "certification_status": packet.get("case_certification_status_after"),
  "problem_count": len(problems),
  "problems": problems,
}
print(json.dumps(out, indent=2))
sys.exit(1 if problems else 0)
