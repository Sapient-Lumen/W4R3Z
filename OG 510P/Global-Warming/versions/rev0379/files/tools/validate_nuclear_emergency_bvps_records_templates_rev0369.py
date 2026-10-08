#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-records-request-templates-rev0369.csv'
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
errors=[]
required_terms=['FEMA','PEMA','Beaver County','Columbiana','NRC','Vistra','public meeting']
blob='\n'.join(' '.join(r.values()) for r in rows)
for term in required_terms:
    if term.lower() not in blob.lower(): errors.append('missing_custodian_or_term:'+term)
if len(rows)<7: errors.append('too_few_templates')
for r in rows:
    tid=r.get('template_id','?')
    body=r.get('request_body','')
    if len(body)<250 and r.get('request_type')!='on_record_question_set': errors.append('body_too_short:'+tid)
    if 'readiness_closure' not in r.get('claim_effect','') and 'closure' not in r.get('claim_effect',''): errors.append('missing_no_closure_effect:'+tid)
    for needed in ['target_artifacts','linked_blockers','send_window']:
        if not r.get(needed): errors.append('missing_'+needed+':'+tid)
    forbidden=['certified ready','readiness proved','exercise passed']
    if any(f in body.lower() for f in forbidden): errors.append('forbidden_overclaim:'+tid)
if errors:
    print('FAIL records_templates_rev0369 ' + ';'.join(errors[:50])); sys.exit(1)
print(f'PASS records_templates_rev0369 rows={len(rows)}')
