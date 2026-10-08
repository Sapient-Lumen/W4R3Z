#!/usr/bin/env python3
from pathlib import Path
import json, sys, collections
ROOT=Path(__file__).resolve().parents[1]
REV='rev0379'
CID='social-security-medicare-claim-security-rev0318'
BRIDGE=ROOT/'cases'/f'{CID}-ma-payment-integrity-rebate-value-risk-coding-waterfall-{REV}.json'
AUDIT=ROOT/'docs/00-meta'/f'ma-payment-integrity-rebate-value-risk-coding-audit-{REV}.json'
REQUIRED_SOURCES={'S580','S581','S588','S589','S615','S616','S617','S618','S619','S620'}
REQUIRED_FIELDS={'contract_id','payment_year','risk_score','diagnosis_source_type','in_home_hra_flag','chart_review_flag','service_record_linkage_flag','county_ratebook_benchmark','plan_bid_amount','rebate_amount','supplemental_benefit_utilization_measure','part_b_premium_effect','taxpayer_cost_effect','ffs_counterfactual_spending','radv_recovery_amount','overpayment_collection_status','denial_access_remedy_bridge_id'}
REQUIRED_FALSE_PHRASES=['No rebate-value pass','No risk-score pass','No HRA/chart-review pass','No RADV-existence pass','No rate-announcement pass','No public-cost pass']
errors=[]
if not BRIDGE.exists(): errors.append(f'missing bridge file: {BRIDGE.relative_to(ROOT)}')
else:
    bridge=json.loads(BRIDGE.read_text(encoding='utf-8'))
    if bridge.get('certification_status_after_rev0379')!='not_certified_current': errors.append('bridge must remain noncertifying')
    missing=REQUIRED_FIELDS-set(bridge.get('required_payment_integrity_fields') or [])
    if missing: errors.append('missing payment-integrity fields: '+', '.join(sorted(missing)))
    if not REQUIRED_SOURCES.issubset(set(bridge.get('source_ids') or [])): errors.append('missing source ids in bridge')
    blob=json.dumps(bridge, sort_keys=True)
    for phrase in REQUIRED_FALSE_PHRASES:
        if phrase not in blob: errors.append(f'missing false-pass phrase: {phrase}')
    if len(bridge.get('false_pass_blocks') or [])<10: errors.append('false_pass_blocks too short')
verified=json.loads((ROOT/'cases/VERIFIED_CLAIM_EDGE_LEDGER.json').read_text(encoding='utf-8'))
rows=verified.get('verified_claim_edges') or []
ids={r.get('verified_claim_edge_id') for r in rows}
required={f'VCEDGE-rev0379-{i:04d}' for i in range(226,236)}
if not required.issubset(ids): errors.append('missing rev0379 evidence ids: '+', '.join(sorted(required-ids)))
rel=collections.Counter(r.get('relationship_code') for r in rows)
if rel.get('contradicts',0)<6: errors.append('expected at least six contradict records after rev0379')
if verified.get('certified_current_case_count')!=0: errors.append('verified ledger must preserve zero certified-current cases')
if AUDIT.exists():
    audit=json.loads(AUDIT.read_text(encoding='utf-8'))
    if audit.get('new_locator_record_count')!=10 or audit.get('new_contradict_record_count')!=2 or audit.get('certified_current_after') is not False:
        errors.append('audit count/certification mismatch')
else: errors.append(f'missing audit file: {AUDIT.relative_to(ROOT)}')
if errors:
    for e in errors: print('ERROR:', e)
    print(f'FAILED: {len(errors)} MA payment-integrity/rebate/risk-coding issue(s)')
    sys.exit(1)
print('PASSED: MA payment-integrity/rebate-value/risk-coding waterfall audit')

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
