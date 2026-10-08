#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WATCH=ROOT/'cube/nuclear-emergency-bvps-docket-release-watch-rev0371.csv'
SRC=ROOT/'cube/source-review-event-rev0371.csv'
ROUTE=ROOT/'cube/nuclear-emergency-bvps-records-route-verification-rev0370.csv'
ADAMS=ROOT/'cube/nuclear-emergency-bvps-adams-access-transition-audit-rev0370.csv'
def read(p):
    with p.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def fail(msg): print('FAIL '+msg); sys.exit(1)
rows=read(WATCH); src=read(SRC)
text='\n'.join(str(r) for r in rows+src+read(ROUTE)+read(ADAMS)).lower()
for needed in ['event notification 58200','adams','public search','fema','ans','siren','eof','no_readiness_closure']:
    if needed not in text: fail('missing_topic='+needed)
if 'web-based adams retired' not in text: fail('missing_wba_retired_note')
for r in rows:
    if 'only' not in r['claim_effect'] and 'no_' not in r['claim_effect']:
        fail('watch_has_closure_effect='+r['watch_id'])
    if not r['expected_artifacts']: fail('watch_missing_expected_artifacts='+r['watch_id'])
print(f'PASS docket_release_watch_rev0371 rows={len(rows)} source_events={len(src)}')
