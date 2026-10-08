#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'cube/bvps-public-meeting-acquisition-status-rev0374.csv'
with path.open(newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
problems=[]
if len(rows)<8: problems.append('too_few_controls')
text='\n'.join(r.get('topic','')+' '+r.get('source_basis','')+' '+r.get('next_action','') for r in rows).lower()
for needle in ['11:00','columbiana','ans/ipaws','en58200','final report']:
    if needle not in text: problems.append('missing_'+needle.replace(':',''))
for r in rows:
    if r.get('status')!='open': problems.append('non_open_'+r.get('control_id',''))
    if 'no_readiness' not in r.get('claim_rule','') and 'cannot close readiness' not in r.get('claim_rule','') and 'not evidence' not in r.get('claim_rule',''):
        problems.append('weak_claim_rule_'+r.get('control_id',''))
if problems:
    print('FAIL public_meeting_acquisition_rev0374 '+ '; '.join(problems)); sys.exit(1)
print(f'PASS public_meeting_acquisition_rev0374 controls={len(rows)}')
