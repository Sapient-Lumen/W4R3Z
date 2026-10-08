#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-eof-repair-admissibility-matrix-rev0367.csv'
required_fragments=['root cause','restored','compensatory','june 2026','communications','offsite','retest','reportability']
errors=[]
with P.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<8: errors.append('too_few_eof_gate_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for frag in required_fragments:
    if frag not in text:
        errors.append('missing_fragment:'+frag)
for r in rows:
    if r.get('claim_effect')!='no_readiness_closure_until_real_evidence':
        errors.append('bad_claim_effect:'+r.get('gate_id','?'))
    if 'readiness_closure' in r.get('minimum_admissible_artifacts','').lower():
        errors.append('bad_artifact_text:'+r.get('gate_id','?'))
    if not r.get('linked_artifact_class'):
        errors.append('missing_artifact_class:'+r.get('gate_id','?'))
if errors:
    print('FAIL eof_repair_gate_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS eof_repair_gate_rev0367 rows={len(rows)}')
