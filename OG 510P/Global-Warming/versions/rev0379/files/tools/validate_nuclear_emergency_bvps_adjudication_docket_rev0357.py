#!/usr/bin/env python3
"""Validate rev0357 adjudication docket: no state may auto-close readiness."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
queue = ROOT / 'cube' / 'nuclear-emergency-bvps-forensic-dropbox-to-adjudication-queue-rev0357.csv'
allowed = {'reject_do_not_promote','hold_pending_missing_fields','candidate_for_two_reviewer_adjudication','accepted_reopen_counterevidence','context_only_no_upgrade'}
failures = []
with queue.open(newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['adjudication_state'] not in allowed:
            failures.append((row['docket_id'], 'bad_state', row['adjudication_state']))
        if row.get('auto_closure') != 'no':
            failures.append((row['docket_id'], 'auto_closure_not_no', row.get('auto_closure')))
        if not row.get('sha256') or len(row['sha256']) != 64:
            failures.append((row['docket_id'], 'bad_hash', row.get('sha256')))
if failures:
    print('FAIL')
    for f in failures:
        print(f)
    sys.exit(1)
print('PASS: rev0357 adjudication docket has no auto-closure states')
