#!/usr/bin/env python3
import csv, sys
from pathlib import Path

DEFAULT_IN = Path('cube/nuclear-emergency-bvps-lifeline-validator-fixture-rev0337.csv')
DEFAULT_OUT = Path('cube/nuclear-emergency-bvps-lifeline-validator-result-rev0337.csv')

def classify(row):
    if row.get('attempted_auto_closure') == 'yes':
        return 'rejected_closure_attempt'
    et = row.get('evidence_type','')
    if et == 'incomplete_local_packet':
        return 'hold_no_upgrade'
    if et == 'local_packet_complete':
        return 'candidate_for_adjudication'
    if et == 'counterevidence':
        return 'accepted_reopen_signal'
    return 'context_no_upgrade'

def main(inp=DEFAULT_IN, out=DEFAULT_OUT):
    inp, out = Path(inp), Path(out)
    rows=[]
    with inp.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            observed = classify(row)
            expected = row.get('expected_classification','')
            rows.append({
                'test_id': row.get('test_id',''),
                'evidence_type': row.get('evidence_type',''),
                'expected_classification': expected,
                'observed_classification': observed,
                'auto_closure_allowed': 'no',
                'validator_status': 'pass' if observed == expected else 'fail',
                'claim_gate': 'no_auto_closure_candidate_only' if observed == 'candidate_for_adjudication' else observed,
                'notes': row.get('notes','')
            })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', newline='', encoding='utf-8') as f:
        fields=['test_id','evidence_type','expected_classification','observed_classification','auto_closure_allowed','validator_status','claim_gate','notes']
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    if any(r['validator_status'] != 'pass' for r in rows):
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
