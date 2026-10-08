#!/usr/bin/env python3
"""Validate rev0364 real-evidence gate keeps local readiness claims blocked."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
critical = list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-real-evidence-critical-path-rev0364.csv', newline='', encoding='utf-8')))
requests = list(csv.DictReader(open(ROOT/'cube/nuclear-emergency-bvps-evidence-request-packet-rev0364.csv', newline='', encoding='utf-8')))
errors=[]
if len(critical) < 12:
    errors.append(f'critical_rows<{12}:{len(critical)}')
if len(requests) < 10:
    errors.append(f'request_rows<{10}:{len(requests)}')
required_priorities={'P0','P1'}
if not required_priorities.issubset({(r.get('gap_id','').split('-') or [''])[0] for r in critical}):
    errors.append('missing_P0_or_P1_gap_ids')
for r in critical:
    text=' '.join((r.get(k,'') or '').lower() for k in r)
    if any(phrase in text for phrase in ['readiness closure','proved ready','passed exercise','certified ready','local readiness proved']):
        errors.append('forbidden_readiness_phrase:'+r.get('gap_id',''))
    if 'claim_freeze' not in (r.get('public_claim_effect','') or '') and 'no_' not in (r.get('public_claim_effect','') or '') and 'context_only' not in (r.get('public_claim_effect','') or ''):
        errors.append('weak_claim_effect:'+r.get('gap_id',''))
    if not r.get('artifact_needed') or not r.get('minimum_acceptance_test') or not r.get('owner_role'):
        errors.append('missing_required_field:'+r.get('gap_id',''))
for r in requests:
    if r.get('hash_required') != 'yes':
        errors.append('hash_not_required:'+r.get('request_id',''))
    if 'candidate' not in (r.get('claim_boundary','') or '') or 'no_readiness_closure' not in (r.get('claim_boundary','') or ''):
        errors.append('bad_claim_boundary:'+r.get('request_id',''))
if errors:
    print('FAIL evidence_gate ' + ';'.join(errors[:20]))
    sys.exit(1)
print(f'PASS evidence_gate critical_rows={len(critical)} request_rows={len(requests)} claim_freeze=unchanged')
