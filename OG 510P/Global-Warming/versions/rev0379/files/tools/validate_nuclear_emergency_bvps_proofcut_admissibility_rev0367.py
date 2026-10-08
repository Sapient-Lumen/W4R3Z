#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-proofcut-admissibility-tests-rev0367.csv'
CON=ROOT/'cube/nuclear-emergency-bvps-evidence-packet-contract-rev0365.csv'
errors=[]
with P.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
with CON.open(newline='', encoding='utf-8') as f:
    contract=list(csv.DictReader(f))
classes={r['artifact_class'] for r in rows}
contract_classes={r['artifact_class'] for r in contract}
if classes != contract_classes:
    errors.append('artifact_class_mismatch')
if len(rows)<14: errors.append('too_few_admissibility_rows')
for r in rows:
    blob=' '.join(r.values()).lower()
    for token in ['sha256','size_bytes','scope','claim limit','no_readiness_closure']:
        if token not in blob:
            errors.append('missing_'+token.replace(' ','_')+':'+r.get('artifact_class','?'))
    if r.get('claim_effect')!='no_readiness_closure':
        errors.append('bad_claim_effect:'+r.get('artifact_class','?'))
if errors:
    print('FAIL proofcut_admissibility_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS proofcut_admissibility_rev0367 rows={len(rows)} classes={len(classes)}')
