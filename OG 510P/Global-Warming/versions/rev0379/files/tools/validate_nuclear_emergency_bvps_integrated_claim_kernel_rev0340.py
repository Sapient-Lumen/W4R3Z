#!/usr/bin/env python3
import csv, sys
from pathlib import Path
OUT={"rejected_closure_attempt","hold_no_upgrade","candidate_for_adjudication","accepted_reopen_signal","context_no_upgrade"}
FORBID={"ready","green","passed","closed","safe","sufficient","certified","demonstrated","complete"}
def yes(v): return str(v).strip().lower() in {"yes","true","1","y"}
def classify(r):
    if yes(r.get('counterevidence_signal')): return 'accepted_reopen_signal'
    txt=(r.get('attempted_public_claim','') or '').lower(); closure=any(w in txt for w in FORBID) or yes(r.get('claims_closure'))
    unresolved=int(r.get('unresolved_p0_count') or 0)
    if closure and (yes(r.get('public_context')) or unresolved>0 or yes(r.get('duplicate_source_only')) or yes(r.get('exercise_no_credit'))): return 'rejected_closure_attempt'
    if yes(r.get('public_context')) and not closure: return 'context_no_upgrade'
    complete=all(yes(r.get(k)) for k in ['has_owner','has_verifier','has_hash','has_scope','has_raw_observation','has_cap_retest','has_counterevidence_path','has_branch_coverage'])
    if complete and unresolved==0 and not yes(r.get('exercise_no_credit')): return 'candidate_for_adjudication'
    return 'hold_no_upgrade'
def main():
    src,dst=Path(sys.argv[1]),Path(sys.argv[2]); rows=list(csv.DictReader(src.open(newline='',encoding='utf-8'))); out=[]; ok=True
    for r in rows:
        c=classify(r); e=r.get('expected_outcome',''); p=(c==e and c in OUT); ok=ok and p
        out.append({'test_id':r.get('test_id',''),'artifact_type':r.get('artifact_type',''),'computed_outcome':c,'expected_outcome':e,'test_pass':'yes' if p else 'no','local_closure_effect':'none','reason':'integrated claim kernel allows reject/hold/candidate/reopen/context only; no auto-closure'})
    with dst.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['test_id','artifact_type','computed_outcome','expected_outcome','test_pass','local_closure_effect','reason']); w.writeheader(); w.writerows(out)
    return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
