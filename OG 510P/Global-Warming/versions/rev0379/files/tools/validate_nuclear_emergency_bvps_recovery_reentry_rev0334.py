#!/usr/bin/env python3
"""Validate rev0334 recovery/reentry/cleanup/waste/claims evidence firebreak fixtures.

The validator intentionally has no auto-closure state. A complete packet is only a
candidate for adjudication; it must still pass CAP/retest/verifier and public-claim gates.
"""
import csv, sys
from pathlib import Path

VALID = {"rejected_closure_attempt", "hold_no_upgrade", "candidate_for_adjudication", "accepted_reopen_signal", "context_no_upgrade"}

def classify(row):
    if row.get('input_type') == 'counterevidence':
        return 'accepted_reopen_signal'
    if row.get('input_type') == 'public_context':
        return 'context_no_upgrade'
    if row.get('public_source_only') == 'yes' and row.get('closure_requested') == 'yes':
        return 'rejected_closure_attempt'
    if row.get('has_local_hash') == 'yes' and row.get('has_verifier') == 'yes' and row.get('has_cap_retest') == 'yes':
        return 'candidate_for_adjudication'
    if row.get('closure_requested') == 'yes':
        return 'hold_no_upgrade'
    return 'context_no_upgrade'

def main(base='.'):
    base = Path(base)
    src = base/'cube/nuclear-emergency-bvps-recovery-validator-fixture-rev0334.csv'
    out = base/'cube/nuclear-emergency-bvps-recovery-validator-result-rev0334.csv'
    with src.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) + ['actual_status','auto_closure','pass','reason']
    failures = 0
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            actual = classify(row)
            ok = actual == row.get('expected_status') and actual in VALID
            failures += 0 if ok else 1
            row.update({
                'actual_status': actual,
                'auto_closure': 'no',
                'pass': 'yes' if ok else 'no',
                'reason': 'no automatic closure; complete packets remain adjudication candidates'
            })
            w.writerow(row)
    return failures

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
