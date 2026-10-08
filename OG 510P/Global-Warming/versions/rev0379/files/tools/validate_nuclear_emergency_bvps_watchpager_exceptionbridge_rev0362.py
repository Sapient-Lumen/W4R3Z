#!/usr/bin/env python3
"""Validate watchpager / exception bridge fixtures.

Rev0363 fix: use exact closure-state matching. Negative controls such as
``rejected_closure_attempt`` intentionally contain the word ``closure`` but are
not closure states and must not be counted as automatic readiness closure.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'cube' / 'nuclear-emergency-bvps-pager-acknowledgement-validator-result-rev0362.csv'
ALLOWED_STATES = {
    'rejected_closure_attempt',
    'hold_no_upgrade',
    'candidate_for_adjudication_not_closure',
    'accepted_reopen_signal',
    'context_no_upgrade',
}
FORBIDDEN_CLOSURE_STATES = {
    'auto_closure',
    'automatic_closure',
    'accepted_closure',
    'local_readiness_closure',
    'readiness_closed',
    'closure',
    'closed',
    'closed_ready',
}

def norm(value):
    return (value or '').strip().lower()

with RESULT.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

bad_state = [r for r in rows if norm(r.get('actual_state')) not in ALLOWED_STATES]
bad_pass = [r for r in rows if norm(r.get('pass_fail')) != 'pass']
expected_mismatch = [r for r in rows if norm(r.get('expected_state')) and norm(r.get('expected_state')) != norm(r.get('actual_state'))]
auto_closure = [r for r in rows if norm(r.get('actual_state')) in FORBIDDEN_CLOSURE_STATES]
# Claim boundary is deliberately textual, so check for the positive boundary rather than substring-parsing state names.
boundary_violation = [
    r for r in rows
    if 'automatic readiness closure' not in norm(r.get('claim_boundary'))
    and 'no upgrade' not in norm(r.get('claim_boundary'))
    and 'adjudication only' not in norm(r.get('claim_boundary'))
]

if bad_state or bad_pass or expected_mismatch or auto_closure or boundary_violation:
    print(
        'FAIL '
        f'bad_state={len(bad_state)} bad_pass={len(bad_pass)} '
        f'expected_mismatch={len(expected_mismatch)} auto_closure={len(auto_closure)} '
        f'boundary_violation={len(boundary_violation)}'
    )
    sys.exit(1)
counts = Counter(norm(r.get('actual_state')) for r in rows)
state_summary = ', '.join(f'{k}={counts[k]}' for k in sorted(counts))
print(f'PASS rows={len(rows)} auto_closures=0 states={state_summary}')
