#!/usr/bin/env python3
import csv, sys
from pathlib import Path

def classify(row):
    if row.get('requests_local_closure') == 'true':
        return 'reject'
    basis = row.get('basis_class','')
    if basis == 'counterevidence':
        return 'reopen_signal'
    if basis == 'complete_local_candidate':
        return 'candidate_not_closure'
    if basis == 'incomplete_local':
        return 'hold_no_upgrade'
    if basis == 'public_context':
        return 'context_no_upgrade'
    return 'hold_no_upgrade'

def main(base):
    base = Path(base)
    in_path = base/'cube'/'nuclear-emergency-bvps-receiver-sentinel-validator-fixture-rev0328.csv'
    out_path = base/'cube'/'nuclear-emergency-bvps-receiver-sentinel-validator-result-rev0328.csv'
    rows = list(csv.DictReader(open(in_path, newline='', encoding='utf-8')))
    out = []
    ok = True
    for r in rows:
        actual = classify(r)
        auto_closure = 'false'
        passed = (actual == r['expected_classification'] and auto_closure == 'false')
        ok = ok and passed
        out.append({
            'test_id': r['test_id'],
            'artifact_type': r['artifact_type'],
            'expected_classification': r['expected_classification'],
            'actual_classification': actual,
            'auto_closure': auto_closure,
            'closure_effect': r['expected_closure_effect'],
            'pass': 'true' if passed else 'false',
            'notes': 'packet may route/cap/reopen/contextualize only; no local readiness auto-closure'
        })
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(out[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(out)
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
