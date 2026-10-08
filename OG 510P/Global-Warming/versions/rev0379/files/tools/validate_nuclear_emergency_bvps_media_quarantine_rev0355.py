#!/usr/bin/env python3
"""Validate BVPS media-quarantine classifications.
Returns non-zero if any test auto-closes or mismatches expected categories."""
from pathlib import Path
import csv, sys
ROOT = Path(__file__).resolve().parents[1]
fix = ROOT / 'cube/nuclear-emergency-bvps-media-quarantine-validator-fixture-rev0355.csv'
res = ROOT / 'cube/nuclear-emergency-bvps-media-quarantine-validator-result-rev0355.csv'
fixtures = {r['test_id']: r for r in csv.DictReader(open(fix, newline='', encoding='utf-8'))}
errors=[]
counts={}
for r in csv.DictReader(open(res, newline='', encoding='utf-8')):
    exp=fixtures[r['test_id']]['expected_classification']
    obs=r['observed_classification']
    counts[obs]=counts.get(obs,0)+1
    if exp!=obs: errors.append(f"{r['test_id']} expected {exp} observed {obs}")
    if r.get('auto_closure','').lower()!='no': errors.append(f"{r['test_id']} auto-closure not allowed")
required={'rejected_closure_attempt':16,'hold_no_upgrade':14,'candidate_for_adjudication_not_closure':10,'accepted_reopen_signal':6,'context_no_upgrade':8}
for k,v in required.items():
    if counts.get(k,0)!=v: errors.append(f"{k} count {counts.get(k,0)} != {v}")
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('media quarantine validator passed', counts)
