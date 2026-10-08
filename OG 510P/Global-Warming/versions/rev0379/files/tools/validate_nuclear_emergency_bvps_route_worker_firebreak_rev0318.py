#!/usr/bin/env python3
"""Validate rev0318 Beaver Valley route/worker firebreak results."""
import csv, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
fixture = root / "cube/nuclear-emergency-bvps-route-worker-firebreak-test-fixture-rev0318.csv"
result = root / "cube/nuclear-emergency-bvps-route-worker-firebreak-test-result-rev0318.csv"
with fixture.open(newline='', encoding='utf-8') as f:
    fx = {r['test_id']: r for r in csv.DictReader(f)}
with result.open(newline='', encoding='utf-8') as f:
    rs = list(csv.DictReader(f))
failures=[]
for r in rs:
    exp = fx[r['test_id']]['expected_decision']
    if r['actual_decision'] != exp or r['status'] != 'pass':
        failures.append((r['test_id'], exp, r['actual_decision'], r['status']))
leaks=[r for r in rs if r['actual_decision']=='accept' and 'complete current kld' not in fx[r['test_id']]['submitted_evidence_claim'].lower()]
if failures or leaks:
    print('FAIL', failures, leaks)
    sys.exit(1)
print('PASS rev0318 route/worker firebreak: %d tests, %d rejects, %d holds, %d reopen, %d conditional accepts' % (len(rs), sum(1 for r in rs if r['actual_decision']=='reject'), sum(1 for r in rs if r['actual_decision']=='hold'), sum(1 for r in rs if r['actual_decision']=='reopen'), sum(1 for r in rs if r['actual_decision'].startswith('accept'))))
