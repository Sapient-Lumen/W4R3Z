#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'cube/nuclear-emergency-bvps-alert-transition-watchlist-rev0367.csv'
required=['siren','eas','ens','ipaws','wea','route alerting','access-and-functional-needs','decommission']
errors=[]
with P.open(newline='', encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
if len(rows)<8: errors.append('too_few_alert_watch_rows')
text=' '.join(' '.join(r.values()).lower() for r in rows)
for frag in required:
    if frag not in text:
        errors.append('missing_alert_fragment:'+frag)
for r in rows:
    if r.get('claim_effect')!='no_readiness_closure':
        errors.append('bad_claim_effect:'+r.get('watch_id','?'))
    if not r.get('evidence_needed') or not r.get('boundary'):
        errors.append('missing_boundary_or_evidence:'+r.get('watch_id','?'))
    if 'success' in r.get('boundary','').lower():
        errors.append('boundary_overclaims_success:'+r.get('watch_id','?'))
if errors:
    print('FAIL alert_transition_watch_rev0367 ' + ';'.join(errors[:20])); sys.exit(1)
print(f'PASS alert_transition_watch_rev0367 rows={len(rows)}')
