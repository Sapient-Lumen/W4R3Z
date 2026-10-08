#!/usr/bin/env python3
"""Validate rev0343 BVPS event-day evidence packout fixture.
This validator intentionally has no auto-close state. Complete packets can only become candidate_for_adjudication_not_closure.
"""
import csv, sys
from pathlib import Path

def classify(r):
    if r.get('uses_public_context_as_closure') == 'yes':
        return 'rejected_closure_attempt'
    if r.get('case_type') == 'counterevidence_or_conflict':
        return 'accepted_reopen_signal'
    if r.get('case_type') == 'public_context_no_upgrade':
        return 'context_no_upgrade'
    required = ['has_artifact_id','has_original_hash','has_surrogate_hash','has_owner','has_capture_time','has_custody_event','has_counterevidence_path']
    if any(r.get(k) != 'yes' for k in required):
        return 'hold_no_upgrade'
    return 'candidate_for_adjudication_not_closure'

def main(base):
    base = Path(base)
    src = base/'cube/nuclear-emergency-bvps-eventday-packout-validator-fixture-rev0343.csv'
    dst = base/'cube/nuclear-emergency-bvps-eventday-packout-validator-result-rev0343.csv'
    with src.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    out=[]
    for r in rows:
        actual = classify(r)
        out.append({'test_id':r['test_id'],'case_type':r['case_type'],'packet_id':r['packet_id'],'expected_classification':r['expected_classification'],'actual_classification':actual,'pass':str(actual==r['expected_classification']),'auto_closure':'no','claim_boundary':'validator never returns a closure state'})
    with dst.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    if not all(r['pass']=='True' for r in out):
        sys.exit(1)
if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else '.')
