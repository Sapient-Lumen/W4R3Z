#!/usr/bin/env python3
import csv, sys
from pathlib import Path

def as_bool(v):
    return str(v).strip().lower() in {'true','1','yes'}

def classify(row):
    public = as_bool(row.get('is_public_context'))
    local = as_bool(row.get('has_local_or_anonymized_packet'))
    h = as_bool(row.get('has_hash'))
    verifier = as_bool(row.get('has_independent_verifier'))
    retest = as_bool(row.get('has_retest_or_CAP_link'))
    counter = as_bool(row.get('is_counterevidence'))
    typ = row.get('artifact_type','')
    if counter:
        return 'accepted_reopen_signal'
    if public and typ in {'public_summary','public_meeting'}:
        return 'context_no_upgrade'
    if public:
        return 'rejected_closure_attempt'
    if not local:
        return 'rejected_closure_attempt'
    if local and h and verifier and retest:
        return 'candidate_for_adjudication'
    return 'hold_no_upgrade'

def main():
    root = Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    inp = root/'cube'/'nuclear-emergency-bvps-crc-decon-validator-fixture-rev0330.csv'
    out = root/'cube'/'nuclear-emergency-bvps-crc-decon-validator-result-rev0330.csv'
    rows=[]
    with open(inp, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            observed=classify(r)
            rows.append({**r,'observed_class':observed,'test_status':'pass' if observed==r['expected_class'] else 'fail','auto_closure':'no'})
    with open(out,'w',newline='',encoding='utf-8') as f:
        fieldnames=list(rows[0].keys())
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)
    fails=[r for r in rows if r['test_status']!='pass']
    print(f"validated {len(rows)} tests; failures={len(fails)}")
    return 1 if fails else 0
if __name__=='__main__':
    raise SystemExit(main())
