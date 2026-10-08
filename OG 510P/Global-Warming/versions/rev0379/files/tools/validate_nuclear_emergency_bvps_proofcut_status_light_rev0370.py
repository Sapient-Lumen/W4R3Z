#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'cube/nuclear-emergency-bvps-proofcut-status-rev0366.csv'
errors=[]
with TARGET.open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<12:
    errors.append('too_few_proofcut_rows')
real_total=sum(int(r.get('real_candidate_rows','0') or 0) for r in rows)
fixture_total=sum(int(r.get('fixture_rows','0') or 0) for r in rows)
if real_total!=0:
    errors.append(f'unexpected_real_candidate_rows={real_total}')
if fixture_total<3:
    errors.append(f'fixture_rows_not_seen={fixture_total}')
for r in rows:
    blob=((r.get('claim_effect','')+' '+r.get('forbidden_statement','')).lower())
    if 'readiness_closure' not in blob:
        errors.append('missing_no_closure_marker:'+r.get('artifact_class',''))
    if r.get('fixture_rows')!='0' and r.get('real_candidate_rows')!='0':
        errors.append('fixture_counted_as_real:'+r.get('artifact_class',''))
if errors:
    print('FAIL proofcut_status_light_rev0370 '+';'.join(errors[:20])); sys.exit(1)
print(f'PASS proofcut_status_light_rev0370 rows={len(rows)} real_candidate_rows={real_total} fixture_rows={fixture_total}')
