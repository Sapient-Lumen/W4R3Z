#!/usr/bin/env python3
import csv, sys
from pathlib import Path

def classify(row):
    public = row.get("is_public_context","").lower() == "true"
    closure = row.get("closure_claim_requested","").lower() == "true"
    complete = row.get("complete_local_packet","").lower() == "true"
    counter = row.get("is_counterevidence","").lower() == "true"
    missing = (row.get("missing_fields") or "").strip()
    if public and closure:
        return "rejected_closure_attempt", "public/context artifact requested local closure"
    if closure and not complete:
        return "rejected_closure_attempt", "closure requested without complete local packet"
    if counter:
        return "accepted_reopen_signal", "counterevidence must reopen or cap the dose/PAR decision state"
    if complete:
        return "candidate_for_adjudication", "complete packet still requires adjudication, CAP/retest/verifier and claim gate"
    if missing:
        return "hold_no_upgrade", "required fields missing: " + missing
    if public:
        return "context_no_upgrade", "public context only; no local closure"
    return "hold_no_upgrade", "insufficient evidence for upgrade"

def main(root):
    root=Path(root)
    inp=root/"cube"/"nuclear-emergency-bvps-dose-field-validator-fixture-rev0332.csv"
    out=root/"cube"/"nuclear-emergency-bvps-dose-field-validator-result-rev0332.csv"
    rows=list(csv.DictReader(inp.open(newline="", encoding="utf-8")))
    fieldnames=["test_id","artifact_type","observed_class","expected_class","pass","auto_closure","reason"]
    failures=0
    with out.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader()
        for r in rows:
            obs,reason=classify(r)
            ok=obs==r.get("expected_class","")
            failures += 0 if ok else 1
            w.writerow({"test_id":r.get("test_id",""),"artifact_type":r.get("artifact_type",""),"observed_class":obs,"expected_class":r.get("expected_class",""),"pass":"true" if ok else "false","auto_closure":"no","reason":reason})
    return failures

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "."))
