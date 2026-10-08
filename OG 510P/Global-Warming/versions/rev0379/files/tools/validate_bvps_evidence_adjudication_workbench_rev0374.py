#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(rel):
    with (ROOT/rel).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
proof=rows('cube/bvps-proofcut-minimum-evidence-thresholds-rev0374.csv')
work=rows('cube/bvps-evidence-adjudication-workbench-rev0374.csv')
problems=[]
expected={'PC-MEET-0374','PC-ANS-0374','PC-EOF-0374','PC-AFN-0374','PC-CAP-0374','PC-CHAIN-0374'}
proof_ids={r['proofcut_id'] for r in proof}
if expected-proof_ids: problems.append('missing_proofcuts='+','.join(sorted(expected-proof_ids)))
if len(work)<15: problems.append('workbench_too_small')
for r in proof:
    if 'open' not in r.get('adjudication_state',''): problems.append('proofcut_not_open_'+r.get('proofcut_id',''))
    if 'no_readiness' not in r.get('claim_rule','') and 'gate_open' not in r.get('claim_rule','') and 'trigger' not in r.get('claim_rule',''):
        problems.append('weak_claim_rule_'+r.get('proofcut_id',''))
for r in work:
    if r.get('proofcut_id') not in proof_ids: problems.append('workbench_unknown_proofcut_'+r.get('workbench_id',''))
    if r.get('claim_effect')!='no_readiness_closure': problems.append('bad_claim_effect_'+r.get('workbench_id',''))
if problems:
    print('FAIL evidence_adjudication_workbench_rev0374 '+ '; '.join(problems[:30])); sys.exit(1)
print(f'PASS evidence_adjudication_workbench_rev0374 proofcuts={len(proof)} workbench_rows={len(work)}')
