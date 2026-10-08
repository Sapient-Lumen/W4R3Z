#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'cube/bvps-public-meeting-acquisition-status-rev0373.csv'
with path.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
ids={r['control_id']:r for r in rows}
required={f'PMW-0373-{i:03d}' for i in range(1,7)}
problems=[]
if set(ids)!=required:
    problems.append('control_ids_mismatch')
for r in rows:
    rule=(r.get('claim_rule') or '').lower()
    status=(r.get('observed_status') or '').lower()
    if 'no_readiness' not in rule and 'cannot close' not in rule and 'must_be_imported' not in rule and 'not evidence' not in rule:
        problems.append('weak_claim_rule_'+r.get('control_id',''))
    if r.get('control_id') in {'PMW-0373-002','PMW-0373-003','PMW-0373-004'} and 'not_imported' not in status:
        problems.append('missing_not_imported_'+r.get('control_id',''))
front=(ROOT/'580-nuclear-emergency-preparedness-meetingwatch-sourcegraph-activesurface-refactor-compact-canon.md').read_text(encoding='utf-8').lower()
for phrase in ['no real beaver valley exercise response packet has been imported','no records request has been sent','no local readiness conclusion']:
    if phrase not in front:
        problems.append('front_missing_'+phrase.replace(' ','_'))
if problems:
    print('FAIL public_meeting_acquisition_rev0373 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS public_meeting_acquisition_rev0373 controls={len(rows)}')
