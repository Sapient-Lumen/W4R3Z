#!/usr/bin/env python3
"""Validate BVPS rev0347 live-intake quarantine fixture.
This validator intentionally has no auto-closure state.
"""
import csv, sys
from pathlib import Path
base = Path(__file__).resolve().parents[1]
path = base / 'cube' / 'nuclear-emergency-bvps-live-intake-validator-result-rev0347.csv'
allowed = {'rejected_closure_attempt','hold_no_upgrade','candidate_for_adjudication_not_closure','accepted_reopen_signal','context_no_upgrade'}
errors=[]
with path.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
for r in rows:
    if r['actual_classification'] not in allowed:
        errors.append(f"bad classification {r['test_id']}: {r['actual_classification']}")
    if r['auto_closure_allowed'].lower() != 'no':
        errors.append(f"auto closure leak {r['test_id']}")
    if r['closure_leak_detected'].lower() != 'no':
        errors.append(f"closure leak {r['test_id']}")
if len(rows) != 54:
    errors.append(f"expected 54 tests, found {len(rows)}")
if errors:
    for e in errors:
        print(e)
    sys.exit(1)
print('rev0347 live-intake quarantine validator passed: 54 tests, 0 auto-closures')
