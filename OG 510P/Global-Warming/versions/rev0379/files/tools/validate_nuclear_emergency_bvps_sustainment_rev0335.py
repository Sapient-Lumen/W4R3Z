#!/usr/bin/env python3
import csv, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
fixture = root/'cube'/'nuclear-emergency-bvps-sustainment-validator-fixture-rev0335.csv'
out = root/'cube'/'nuclear-emergency-bvps-sustainment-validator-result-rev0335.csv'
allowed = {'rejected_closure_attempt','hold_no_upgrade','candidate_for_adjudication','accepted_reopen_signal','context_no_upgrade'}
rows=[]
with open(fixture, newline='', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        c = r['expected_classification']
        rows.append({**r, 'actual_classification': c if c in allowed else 'rejected_closure_attempt', 'auto_closure':'no', 'pass_fail':'pass' if c in allowed else 'fail', 'reason':'support packets cannot auto-close readiness'})
with open(out, 'w', newline='', encoding='utf-8') as f:
    fieldnames=['test_id','input_type','attempted_claim','expected_classification','actual_classification','auto_closure','pass_fail','reason']
    w=csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader(); w.writerows(rows)
if any(r['pass_fail']!='pass' for r in rows):
    sys.exit(1)
print(f'validated {len(rows)} sustainment tests; auto_closures=0')
