#!/usr/bin/env python3
"""Audit the active MA medical-necessity/clinical-remedy guardrails.

Rev0378 refactor: keep rev0377 guardrails active while allowing later revisions to advance.
"""
from pathlib import Path
import json, sys, collections, re
ROOT=Path(__file__).resolve().parents[1]
CID='social-security-medicare-claim-security-rev0318'
REQUIRED_FIELDS={'medicare_coverage_authority_type','medicare_coverage_authority_locator','internal_coverage_criteria_used_flag','internal_coverage_criteria_public_url','medical_records_sufficient_flag','physician_or_clinical_reviewer_conclusion','service_would_be_covered_under_original_medicare_flag','denial_cause_taxonomy','algorithm_or_ai_tool_used','human_review_level','effectuation_deadline_date','service_authorized_or_provided_date','provider_payment_restored_date','effectuation_deadline_met_flag','beneficiary_harm_or_abandonment_signal'}
REQUIRED_SOURCES={'S599','S605','S606','S607','S608'}
REQUIRED_PHRASES=['No denial-rate pass','No appeal-overturn pass','No internal-criteria pass','No algorithm/delegation opacity pass','No CY2026-AI-guardrail pass','No remedy pass']
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def resolve_bridge():
    candidates=sorted((ROOT/'cases').glob(f'{CID}-ma-medical-necessity-clinical-remedy-guardrails-rev*.json'))
    if not candidates: return ROOT/'cases'/f'{CID}-ma-medical-necessity-clinical-remedy-guardrails-rev0377.json'
    def key(p):
        m=re.search(r'rev(\d{4})', p.name)
        return int(m.group(1)) if m else -1
    return sorted(candidates, key=key)[-1]
errors=[]; BRIDGE=resolve_bridge()
if not BRIDGE.exists(): errors.append(f'missing bridge file: {BRIDGE.relative_to(ROOT)}')
else:
    b=json.loads(BRIDGE.read_text(encoding='utf-8'))
    if b.get('certification_status_after_rev0377')!='not_certified_current': errors.append('bridge must remain noncertifying')
    missing=REQUIRED_FIELDS-set(b.get('required_clinical_remedy_fields') or [])
    if missing: errors.append(f'bridge missing clinical fields: {sorted(missing)}')
    if not REQUIRED_SOURCES.issubset(set(b.get('source_ids') or [])): errors.append('bridge missing required sources')
    text=BRIDGE.read_text(encoding='utf-8')
    for phrase in REQUIRED_PHRASES:
        if phrase not in text: errors.append(f'bridge missing phrase {phrase}')
verified=load('cases/VERIFIED_CLAIM_EDGE_LEDGER.json'); rows=verified.get('verified_claim_edges') or []
ids={r.get('verified_claim_edge_id') for r in rows}; required={f'VCEDGE-rev0377-{i:04d}' for i in range(210,218)}
if not required.issubset(ids): errors.append(f'missing verified records {sorted(required-ids)}')
rel=collections.Counter(r.get('relationship_code') for r in rows)
if rel.get('contradicts',0)<2: errors.append('expected at least two contradict records')
audit=load('docs/00-meta/ma-medical-necessity-clinical-remedy-guardrails-audit-rev0377.json')
if audit.get('new_locator_record_count')!=8 or audit.get('new_contradict_record_count')!=2 or audit.get('certified_current_after') is not False: errors.append('audit count/certification mismatch')
if errors:
    for e in errors: print('ERROR:',e)
    print(f'FAILED: {len(errors)} MA medical-necessity guardrail issue(s)')
    sys.exit(1)
print('PASSED: MA medical-necessity/clinical-remedy guardrails audit')

# rev0378 live-surface exposure: this earlier bridge audit remains part of the current MA audit chain under rev0378.

# Retained in the rev0379 live-surface contract as an upstream MA guardrail audit.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
