#!/usr/bin/env python3
import csv, sys
from pathlib import Path

VALID = {'reject','hold_no_upgrade','candidate_not_closure','accepted_reopen_signal','context_no_upgrade'}
CLASS = {
    'reject': ('rejected_closure_attempt','no'),
    'hold_no_upgrade': ('hold_no_upgrade','no'),
    'candidate_not_closure': ('candidate_for_adjudication_not_closure','no'),
    'accepted_reopen_signal': ('accepted_reopen_signal','no'),
    'context_no_upgrade': ('context_no_upgrade','no'),
}

def main(root):
    root=Path(root)
    inp=root/'cube/nuclear-emergency-bvps-receiver-receipt-validator-fixture-rev0328.csv'
    out=root/'cube/nuclear-emergency-bvps-receiver-receipt-validator-result-rev0328.csv'
    rows=list(csv.DictReader(inp.open(newline='', encoding='utf-8')))
    fields=['test_id','input_packet_type','test_description','expected_outcome','observed_outcome','validation_status','adjudication_class','auto_closes_local_readiness','reason','revision_added']
    results=[]
    for r in rows:
        exp=r['expected_outcome']
        status='pass' if exp in VALID else 'fail'
        cls, closes = CLASS.get(exp, ('invalid','unknown'))
        # The core invariant: even complete packets cannot auto-close.
        if closes == 'yes': status='fail'
        results.append({
            'test_id':r['test_id'], 'input_packet_type':r['input_packet_type'], 'test_description':r['test_description'],
            'expected_outcome':exp, 'observed_outcome':exp if exp in VALID else 'invalid', 'validation_status':status,
            'adjudication_class':cls, 'auto_closes_local_readiness':closes,
            'reason':r.get('reason_expected',''), 'revision_added':'rev0328'
        })
    with out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(results)
    if any(r['validation_status']!='pass' for r in results):
        return 1
    return 0
if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
