#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROUTE=ROOT/'cube/nuclear-emergency-bvps-records-route-verification-rev0370.csv'
ADAMS=ROOT/'cube/nuclear-emergency-bvps-adams-access-transition-audit-rev0370.csv'

def read(p):
    with p.open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))

def fail(msg): print('FAIL '+msg); sys.exit(1)
routes=read(ROUTE); adams=read(ADAMS)
needed=['FEMA','Pennsylvania','Beaver County','Ohio','NRC','ADAMS']
text='\n'.join(str(r) for r in routes+adams).lower()
for n in needed:
    if n.lower() not in text: fail('missing_route_topic='+n)
if 'web-based adams retired' not in text: fail('missing_adams_retirement')
for r in routes:
    if 'not_evidence' not in r['route_status'] and 'needs_current_route_verification' not in r['route_status']: fail('bad_route_status='+r['route_id'])
    if 'readiness_closure' in r['claim_effect'] and 'no_readiness_closure' not in r['claim_effect']: fail('bad_claim_effect='+r['route_id'])
for r in adams:
    if 'closure' not in r['claim_effect']: fail('missing_adams_claim_effect='+r['audit_id'])
print(f'PASS route_verification_rev0370 routes={len(routes)} adams_rows={len(adams)}')
