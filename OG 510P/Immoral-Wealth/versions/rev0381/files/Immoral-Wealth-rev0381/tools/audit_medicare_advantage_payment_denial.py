#!/usr/bin/env python3
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
CASE="social-security-medicare-claim-security-rev0318"
REV="rev0370"
req={"S578","S579","S580","S581","S582","S583"}
ledger=json.loads((ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.json").read_text())
rows=[r for r in ledger.get("verified_claim_edges",[]) if r.get("case_id")==CASE]
new=[r for r in rows if r.get("created_revision")==REV]
seen=set(s for r in new for s in r.get("source_ids",[]))
problems=[]
if len(new)!=16: problems.append(f"expected 16 rev0370 edges, found {len(new)}")
if not req.issubset(seen): problems.append(f"missing required source ids {sorted(req-seen)}")
for r in new:
    for k in ["bounded_claim","relationship_code","source_ids","exact_locator","does_not_prove","contrary_or_qualifying_evidence_needed","reversal_rule"]:
        if not r.get(k): problems.append(f"{r.get('verified_claim_edge_id')} missing {k}")
packet=json.loads((ROOT/f"cases/{CASE}-claim-packet.json").read_text())
if packet.get("case_certification_status_after") == "certified_current": problems.append("claim packet must remain noncertifying")
mp=json.loads((ROOT/f"cases/{CASE}-medicare-advantage-payment-denial-map.json").read_text())
if mp.get("certification_status") != "not_certified_current" or len(mp.get("layers",[])) < 5: problems.append("MA map must preserve noncertification and five layers")
print(json.dumps({"revision_current":REV,"case_id":CASE,"new_edge_count":len(new),"total_case_edge_count":len(rows),"source_ids":sorted(seen),"problem_count":len(problems),"problems":problems}, indent=2))
if problems: sys.exit(1)
