#!/usr/bin/env python3
"""Validate rev0350 live-drop red-team results. No case may auto-close local readiness."""
from pathlib import Path
import csv, sys
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
result = root/'cube'/'nuclear-emergency-bvps-live-drop-redteam-validator-result-rev0350.csv'
rows=list(csv.DictReader(open(result, newline='', encoding='utf-8')))
allowed={'rejected_closure_attempt','hold_no_upgrade','candidate_for_adjudication_not_closure','accepted_reopen_signal','context_no_upgrade'}
fail=[]
for r in rows:
    if r.get('classification') not in allowed: fail.append((r.get('test_id'),'bad classification'))
    if r.get('auto_closure_allowed') != 'no': fail.append((r.get('test_id'),'auto closure allowed'))
    if r.get('closure_effect') == 'closure': fail.append((r.get('test_id'),'closure effect'))
if len(rows)!=54: fail.append(('row_count',f'expected 54 got {len(rows)}'))
if fail:
    for f in fail: print('FAIL', f)
    sys.exit(1)
print('PASS rev0350 live-drop red-team validator: 54 tests, 0 auto-closures')
