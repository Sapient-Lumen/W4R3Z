#!/usr/bin/env python3
"""Validate that rev0348 live-intake console has no auto-closure state."""
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
console=ROOT/'cube/nuclear-emergency-bvps-live-intake-console-rev0348.csv'
validator=ROOT/'cube/nuclear-emergency-bvps-live-console-validator-result-rev0348.csv'
errors=[]
with console.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)!=60:
    errors.append(f'expected 60 console rows, found {len(rows)}')
for r in rows:
    if r.get('auto_closure_allowed') != 'no':
        errors.append(f"auto closure allowed for {r.get('packet_id')}")
    if r.get('loss_cap_active') != 'yes':
        errors.append(f"loss cap not active for {r.get('packet_id')}")
with validator.open(newline='', encoding='utf-8') as f:
    tests=list(csv.DictReader(f))
if len(tests)!=54:
    errors.append(f'expected 54 validator tests, found {len(tests)}')
for t in tests:
    if t.get('auto_closure_observed') != 'no' or t.get('pass_fail') != 'pass':
        errors.append(f"validator failed or auto-closed: {t.get('test_id')}")
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('rev0348 live-intake console validator: ok')
