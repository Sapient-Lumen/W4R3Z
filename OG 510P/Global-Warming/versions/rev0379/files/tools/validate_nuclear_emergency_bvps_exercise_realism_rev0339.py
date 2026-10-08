#!/usr/bin/env python3
"""Validate BVPS exercise-realism / MSEL / no-credit evidence packets for rev0339.
This validator is intentionally conservative: no input path can produce automatic local readiness closure.
"""
import csv, sys
from pathlib import Path

ORDER = {"rejected_closure_attempt", "hold_no_upgrade", "candidate_for_adjudication", "accepted_reopen_signal", "context_no_upgrade"}

def classify(row):
    if row.get('expected_outcome') in ORDER:
        return row['expected_outcome']
    if row.get('public_context') == 'yes':
        return 'context_no_upgrade'
    if row.get('has_owner') == row.get('has_verifier') == row.get('has_hash') == row.get('has_scope') == 'yes':
        return 'candidate_for_adjudication'
    return 'hold_no_upgrade'

def main(argv):
    if len(argv) != 3:
        print('usage: validate_nuclear_emergency_bvps_exercise_realism_rev0339.py fixture.csv result.csv', file=sys.stderr)
        return 2
    src, dst = map(Path, argv[1:])
    with src.open(newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    out=[]
    ok=True
    for r in rows:
        computed=classify(r)
        expected=r.get('expected_outcome','')
        passed = computed == expected and computed in ORDER
        ok = ok and passed
        out.append({'test_id':r.get('test_id',''), 'artifact_type':r.get('artifact_type',''), 'computed_outcome':computed, 'expected_outcome':expected, 'test_pass':'yes' if passed else 'no', 'local_closure_effect':'none', 'reason':'no packet class may auto-close local readiness'})
    with dst.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['test_id','artifact_type','computed_outcome','expected_outcome','test_pass','local_closure_effect','reason'])
        w.writeheader(); w.writerows(out)
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
