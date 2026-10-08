#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-columbiana-plan-crosswalk-rev0367.csv'
need=['certification','concept','public warning','exercises','protective action']
errors=[]
with P.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
text=' '.join(' '.join(r.values()).lower() for r in rows)
if len(rows)<6: errors.append('too_few_crosswalk_rows')
for n in need:
    if n not in text: errors.append('missing_crosswalk_topic:'+n)
for r in rows:
    if r.get('claim_effect')!='no_readiness_closure': errors.append('bad_claim_effect:'+r.get('crosswalk_id','?'))
    if r.get('boundary_use')!='public_plan_context_not_evaluated_performance': errors.append('bad_boundary:'+r.get('crosswalk_id','?'))
if errors:
    print('FAIL columbiana_plan_boundary_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS columbiana_plan_boundary_rev0367 rows={len(rows)}')
