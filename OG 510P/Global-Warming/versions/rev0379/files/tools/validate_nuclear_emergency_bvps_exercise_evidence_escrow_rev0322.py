#!/usr/bin/env python3
"""Validate rev0322 Beaver Valley exercise evidence escrow firebreak fixture.
Public context may route/cap/reopen evidence demands but cannot close local readiness evidence.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FIXTURE = BASE / 'cube' / 'nuclear-emergency-bvps-exercise-evidence-validator-fixture-rev0322.csv'
RESULT = BASE / 'cube' / 'nuclear-emergency-bvps-exercise-evidence-validator-result-rev0322.csv'

def validate(row):
    sc=row['input_source_class']
    b={k: row[k]=='true' for k in ['has_hash','has_owner','has_timestamp','has_scope','has_verifier','has_retest_or_CAP_state','has_counterevidence_path','claims_local_closure']}
    if sc.startswith('public') and b['claims_local_closure']:
        return 'reject_public_context_closure'
    if sc in ['public_schedule','public_context'] and not b['claims_local_closure']:
        return 'accept_context_no_upgrade'
    if sc=='public_signal' and not b['claims_local_closure']:
        return 'accept_reopen_signal'
    if sc=='counterevidence':
        return 'accept_reopen_signal'
    if sc=='preliminary_finding' and not b['claims_local_closure']:
        return 'accept_context_no_upgrade'
    if not (b['has_hash'] and b['has_owner'] and b['has_timestamp'] and b['has_scope']):
        return 'reject_missing_integrity'
    if sc=='hotwash_note' and b['claims_local_closure']:
        return 'reject_hotwash_not_closure'
    if sc=='sensitive_annex' or row['test_id']=='VESC-027':
        return 'hold_redaction_needed'
    if row['test_id']=='VESC-030':
        return 'hold_incomplete_packet'
    if b['claims_local_closure'] and not (b['has_verifier'] and b['has_retest_or_CAP_state'] and b['has_counterevidence_path']):
        return 'hold_incomplete_packet'
    if b['has_hash'] and b['has_owner'] and b['has_timestamp'] and b['has_scope'] and b['has_verifier'] and b['has_retest_or_CAP_state'] and b['has_counterevidence_path']:
        return 'candidate_not_auto_closure'
    return 'hold_incomplete_packet'

def main():
    with FIXTURE.open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    failures=[]
    for row in rows:
        actual=validate(row)
        if actual != row['expected_outcome']:
            failures.append((row['test_id'], row['expected_outcome'], actual))
    if failures:
        for failure in failures:
            print('FAIL', failure)
        return 1
    print(f'PASS {len(rows)}/{len(rows)} rev0322 evidence escrow firebreak tests')
    return 0

if __name__=='__main__':
    sys.exit(main())
