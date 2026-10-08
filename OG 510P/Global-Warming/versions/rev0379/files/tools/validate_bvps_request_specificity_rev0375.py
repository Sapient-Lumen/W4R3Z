#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
up=rows('cube/bvps-request-specificity-upgrade-rev0375.csv')
cross=rows('cube/bvps-proofcut-request-crosswalk-rev0375.csv')
problems=[]
ids={r['request_id'] for r in up}
for rid in ['RRT-0375-006','RRT-0375-007','RRT-0375-008','RRT-0374-005']:
    if rid not in ids: problems.append('missing_upgrade_'+rid)
for r in up:
    if r['request_id'].startswith('RRT-0375'):
        if 'ready_not_sent' not in r.get('dispatch_posture',''): problems.append('bad_dispatch_'+r['request_id'])
        if 'not evidence' not in r.get('claim_rule','').lower() and 'imported' not in r.get('claim_rule','').lower(): problems.append('weak_claim_'+r['request_id'])
        if not r.get('proofcuts_targeted'): problems.append('no_proofcuts_'+r['request_id'])
proof_text='\n'.join(r.get('proofcut_id','') for r in cross)
for pc in ['PC-MEET-0374','PC-ANS-0374','PC-EOF-0374','PC-AFN-0374','PC-CAP-0374','PC-CHAIN-0374']:
    if pc not in proof_text: problems.append('missing_crosswalk_'+pc)
for r in cross:
    if 'no ' not in r.get('claim_effect_if_absent','').lower() and 'remains open' not in r.get('claim_effect_if_absent','').lower() and 'cannot support' not in r.get('claim_effect_if_absent','').lower():
        problems.append('weak_absent_effect_'+r.get('crosswalk_id',''))
if problems:
    print('FAIL request_specificity_rev0375 '+ '; '.join(problems[:40])); sys.exit(1)
print(f'PASS request_specificity_rev0375 upgrades={len(up)} crosswalks={len(cross)}')
