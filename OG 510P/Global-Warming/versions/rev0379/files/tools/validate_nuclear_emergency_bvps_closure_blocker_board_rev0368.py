#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-closure-blocker-board-rev0368.csv'
required=['preliminary findings','siren','alert','eof','afn','crc','dose','field monitoring','public communications']
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<12: errors.append('too_few_blockers')
if sum(1 for r in rows if r.get('priority')=='P0')<10: errors.append('too_few_P0_blockers')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in required:
    if term not in text: errors.append('missing_blocker_term:'+term)
for r in rows:
    bid=r.get('blocker_id','?')
    if r.get('current_state')!='open_missing_real_or_lawfully_anonymized_evidence': errors.append('bad_state:'+bid)
    if r.get('claim_effect')!='no_readiness_closure': errors.append('bad_claim_effect:'+bid)
    if not r.get('minimum_evidence_to_unblock') or not r.get('next_action'): errors.append('missing_unblock_or_action:'+bid)
if errors:
    print('FAIL closure_blocker_board_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS closure_blocker_board_rev0368 rows={len(rows)}')
