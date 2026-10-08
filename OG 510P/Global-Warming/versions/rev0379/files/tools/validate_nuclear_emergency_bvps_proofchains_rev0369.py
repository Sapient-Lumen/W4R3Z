#!/usr/bin/env python3
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[ROOT/'cube/nuclear-emergency-bvps-eof-corrective-action-proofchain-rev0369.csv', ROOT/'cube/nuclear-emergency-bvps-alerting-proofchain-rev0369.csv']
errors=[]
required={'eof':['restoral','root_cause','post_maintenance_test','LER_or_no_LER','exercise_scope'], 'alert':['current_siren_inventory','decommissioning_approval','delivery_failure_logs','EAS_follow_on','AFN_language_access']}
for p in files:
    rows=list(csv.DictReader(p.open(newline='', encoding='utf-8')))
    kind='eof' if 'eof' in p.name else 'alert'
    stages={r.get('stage','') for r in rows}
    for req in required[kind]:
        if req not in stages: errors.append('missing_stage:'+kind+':'+req)
    if sum(1 for r in rows if r.get('priority')=='P0')<7: errors.append('too_few_P0:'+kind)
    for r in rows:
        if 'readiness_closure' in ' '.join(r.values()).lower().replace('no_readiness_closure',''):
            errors.append('forbidden_closure_phrase:'+r.get('proofchain_id','?'))
        if not r.get('minimum_artifacts') or not r.get('claim_effect'): errors.append('missing_artifacts_or_effect:'+r.get('proofchain_id','?'))
if errors:
    print('FAIL proofchains_rev0369 ' + ';'.join(errors[:50])); sys.exit(1)
print('PASS proofchains_rev0369 files=2')
