#!/usr/bin/env python3
import csv, sys
from pathlib import Path
def classify(r):
    if r.get("artifact_type")=="counterevidence" or (r.get("has_counterevidence")=="yes" and "reopen" in r.get("attempted_claim","")): return "accepted_reopen_signal"
    if r.get("public_context")=="yes":
        if "close" in r.get("attempted_claim","") or "green" in r.get("attempted_claim","") or r.get("artifact_type")=="public_context_or_incomplete_form": return "rejected_closure_attempt"
        return "context_no_upgrade"
    if all(r.get(k)=="yes" for k in ["has_owner","has_verifier","has_hash","has_timestamp","has_scope","has_retest","has_counterevidence"]): return "candidate_for_adjudication_not_closure"
    return "hold_no_upgrade"
def main(root):
    root=Path(root); inp=root/"cube/nuclear-emergency-bvps-cop-validator-fixture-rev0338.csv"; out=root/"cube/nuclear-emergency-bvps-cop-validator-result-rev0338.csv"; rows=[]
    with inp.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            o=classify(r); rows.append({"test_id":r["test_id"],"artifact_type":r["artifact_type"],"computed_outcome":o,"expected_outcome":r["expected_outcome"],"test_pass":"yes" if o==r["expected_outcome"] else "no","local_closure_effect":"none","reason":"public context and packet candidates cannot auto-close local readiness evidence"})
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    fails=[r for r in rows if r["test_pass"]!="yes"]
    print(f"tests={len(rows)} failures={len(fails)}")
    return 1 if fails else 0
if __name__=="__main__": sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "."))
