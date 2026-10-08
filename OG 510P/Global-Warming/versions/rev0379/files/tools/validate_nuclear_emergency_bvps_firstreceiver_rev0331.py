#!/usr/bin/env python3
import csv, sys
from pathlib import Path

def classify(row):
    if str(row.get('counterevidence_signal','')).lower() == 'true':
        return 'accepted_reopen_signal'
    if str(row.get('public_context_only','')).lower() == 'true':
        text = row.get('input_summary','').lower()
        if any(word in text for word in ['proves','closes','ready','readiness','worked','handled','proof']):
            return 'rejected_closure_attempt'
        return 'context_no_upgrade'
    if str(row.get('has_local_packet','')).lower() != 'true' or str(row.get('has_hash','')).lower() != 'true':
        return 'rejected_closure_attempt'
    if any(phrase in row.get('input_summary','').lower() for phrase in ['no ', 'without', 'missing', 'exists but no', 'has photos but no']):
        return 'hold_no_upgrade'
    if str(row.get('has_verifier','')).lower() != 'true':
        return 'hold_no_upgrade'
    if str(row.get('has_retest','')).lower() == 'false':
        return 'hold_no_upgrade'
    return 'candidate_for_adjudication'

def main(root):
    root = Path(root)
    inp = root/'cube'/'nuclear-emergency-bvps-firstreceiver-validator-fixture-rev0331.csv'
    out = root/'cube'/'nuclear-emergency-bvps-firstreceiver-validator-result-rev0331.csv'
    rows = list(csv.DictReader(inp.open(newline='', encoding='utf-8')))
    fieldnames = ['test_id','input_summary','expected_class','observed_class','pass','auto_closure']
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        failures = 0
        for row in rows:
            obs = classify(row)
            ok = obs == row['expected_class']
            if not ok: failures += 1
            w.writerow({'test_id':row['test_id'],'input_summary':row['input_summary'],'expected_class':row['expected_class'],'observed_class':obs,'pass':'pass' if ok else 'fail','auto_closure':'no'})
    return failures

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
