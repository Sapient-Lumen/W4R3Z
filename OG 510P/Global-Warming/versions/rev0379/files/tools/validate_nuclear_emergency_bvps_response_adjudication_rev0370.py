#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUB=ROOT/'cube/nuclear-emergency-bvps-response-adjudication-rubric-rev0370.csv'

def read(p):
    with p.open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def fail(msg): print('FAIL '+msg); sys.exit(1)
rows=read(RUB)
if len(rows)<7: fail('too_few_rubric_rows')
required_fields={'minimum_to_credit','automatic_rejection','allowed_credit','forbidden_credit','claim_effect'}
missing=required_fields-set(rows[0].keys())
if missing: fail('missing_fields='+','.join(sorted(missing)))
for r in rows:
    for field in required_fields:
        if not r.get(field,'').strip(): fail('blank_'+field+'_'+r['rubric_id'])
    joined=' '.join(r.values()).lower()
    for token in ['hash','custodian']:
        if token not in joined: fail('rubric_missing_'+token+'_'+r['rubric_id'])
    if 'candidate' not in r['allowed_credit'].lower() and 'route' not in r['allowed_credit'].lower() and 'lead' not in r['allowed_credit'].lower(): fail('bad_allowed_credit='+r['rubric_id'])
    if 'closure' not in r['claim_effect']: fail('missing_claim_effect='+r['rubric_id'])
print(f'PASS response_adjudication_rev0370 rows={len(rows)}')
