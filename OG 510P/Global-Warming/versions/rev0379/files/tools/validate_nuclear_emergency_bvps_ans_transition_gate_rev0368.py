#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-ans-transition-admissibility-matrix-rev0368.csv'
required_terms=['official approval','siren','ans','eas','ens','ipaws','wea','delivery','failure','route alerting','access-and-functional-needs','cross-jurisdiction']
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<10: errors.append('too_few_ans_transition_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in required_terms:
    if term not in text: errors.append('missing_term:'+term)
if sum(1 for r in rows if r.get('priority')=='P0')<7: errors.append('too_few_P0_rows')
for r in rows:
    gid=r.get('gate_id','?')
    ce=r.get('claim_effect','').lower()
    if 'no_readiness_closure' not in ce: errors.append('bad_claim_effect:'+gid)
    if 'readiness_closure' in r.get('automatic_rejection','').lower() and 'no_readiness_closure' not in ce: errors.append('closure_rejection_mismatch:'+gid)
    for col in ['evidence_question','minimum_admissible_artifacts','automatic_rejection','blocks_claim','next_action']:
        if not r.get(col): errors.append('missing_'+col+':'+gid)
    if 'success' in r.get('claim_effect','').lower(): errors.append('success_claim_effect:'+gid)
if errors:
    print('FAIL ans_transition_gate_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS ans_transition_gate_rev0368 rows={len(rows)} P0={sum(1 for r in rows if r.get("priority")=="P0")}')
