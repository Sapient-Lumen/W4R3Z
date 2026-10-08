#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-public-records-request-queue-rev0368.csv'
required=['fema','pema','beaver county','columbiana','vistra','nrc','ohio','west virginia']
errors=[]
rows=list(csv.DictReader(P.open(newline='', encoding='utf-8')))
if len(rows)<10: errors.append('too_few_records_queue_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for term in required:
    if term not in text: errors.append('missing_custodian_or_scope:'+term)
if sum(1 for r in rows if r.get('priority')=='P0')<6: errors.append('too_few_P0_requests')
for r in rows:
    rid=r.get('request_id','?')
    if 'no_readiness_closure' not in r.get('claim_effect','').lower(): errors.append('bad_claim_effect:'+rid)
    if not r.get('target_artifacts') or not r.get('privacy_redaction') or not r.get('why_needed'): errors.append('missing_request_detail:'+rid)
    if 'ssn' in text or 'social security' in text: errors.append('pii_overrequest')
if errors:
    print('FAIL public_records_queue_rev0368 ' + ';'.join(errors[:30])); sys.exit(1)
print(f'PASS public_records_queue_rev0368 rows={len(rows)} P0={sum(1 for r in rows if r.get("priority")=="P0")}')
