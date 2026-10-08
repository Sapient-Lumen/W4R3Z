#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-public-meeting-evidence-packout-rev0368.csv'
required=['preliminary findings','ans demonstration','siren decommissioning','eof power','protective action','afn','crc','ems','field monitoring','corrective actions']
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<14: errors.append('too_few_packout_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in required:
    if term not in text: errors.append('missing_term:'+term)
for r in rows:
    iid=r.get('item_id','?')
    if 'readiness_closure' in r.get('claim_effect','').lower() and 'no_readiness_closure' not in r.get('claim_effect','').lower(): errors.append('bad_claim_effect:'+iid)
    if not r.get('exact_question_or_action') or not r.get('minimum_artifact'): errors.append('missing_question_or_artifact:'+iid)
if errors:
    print('FAIL public_meeting_packout_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS public_meeting_packout_rev0368 rows={len(rows)}')
