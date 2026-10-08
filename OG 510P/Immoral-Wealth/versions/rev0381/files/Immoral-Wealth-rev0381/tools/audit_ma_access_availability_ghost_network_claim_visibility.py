#!/usr/bin/env python3
"""Audit the active rev0378 MA access-availability/ghost-network/claim-visibility bridge.

Rev0379 refactor: this upstream bridge remains active after the current release advances, so the script resolves the rev0378 bridge rather than assuming a same-revision clone.
"""
from pathlib import Path
import json, sys, collections, re
ROOT=Path(__file__).resolve().parents[1]
CID='social-security-medicare-claim-security-rev0318'
REQUIRED_FIELDS={'contract_id','plan_id','county_fips','specialty_or_facility_type','behavioral_health_provider_type','provider_npi','hsd_table_listing_flag','provider_directory_listing_flag','medicare_plan_finder_directory_listing_flag','provider_directory_api_update_timestamp','accepting_new_patients_flag','provider_active_claims_or_encounters_in_period','appointment_offered_date','time_distance_standard_result','automated_criteria_check_pass_fail','zip_code_failed_county_flag','network_exception_requested_flag','access_complaint_id','ghost_provider_flag','encounter_adjustment_code','definitive_denied_claim_indicator_present_flag','claim_denied_indicator','payment_restoration_date','beneficiary_service_restoration_date','clinical_correctness_bridge_id','subgroup_denominator_key'}
REQUIRED_SOURCES={'S609','S610','S611','S612','S613','S614'}
REQUIRED_PHRASES=['No HSD/ACC pass','No provider-directory pass','No ghost-network pass','No encounter-adjustment pass','No remedy pass']
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def resolve_bridge():
    candidates=sorted((ROOT/'cases').glob(f'{CID}-ma-access-availability-ghost-network-claim-visibility-bridge-rev*.json'))
    if not candidates: return ROOT/'cases'/f'{CID}-ma-access-availability-ghost-network-claim-visibility-bridge-rev0378.json'
    def key(p):
        m=re.search(r'rev(\d{4})',p.name); return int(m.group(1)) if m else -1
    return sorted(candidates,key=key)[-1]
errors=[]; BRIDGE=resolve_bridge()
if not BRIDGE.exists(): errors.append(f'missing bridge file: {BRIDGE.relative_to(ROOT)}')
else:
    b=json.loads(BRIDGE.read_text(encoding='utf-8'))
    if b.get('certification_status_after_rev0378')!='not_certified_current': errors.append('bridge must remain noncertifying')
    fields=set(b.get('required_access_availability_fields') or [])
    missing=REQUIRED_FIELDS-fields
    if missing: errors.append(f'bridge missing access fields: {sorted(missing)}')
    if not REQUIRED_SOURCES.issubset(set(b.get('source_ids') or [])): errors.append('bridge missing required sources')
    text=BRIDGE.read_text(encoding='utf-8')
    for phrase in REQUIRED_PHRASES:
        if phrase not in text: errors.append(f'bridge missing phrase {phrase}')
verified=load('cases/VERIFIED_CLAIM_EDGE_LEDGER.json'); rows=verified.get('verified_claim_edges') or []
ids={r.get('verified_claim_edge_id') for r in rows}; req={f'VCEDGE-rev0378-{i:04d}' for i in range(218,226)}
if not req.issubset(ids): errors.append(f'missing rev0378 evidence records {sorted(req-ids)}')
rel=collections.Counter(r.get('relationship_code') for r in rows)
if rel.get('contradicts',0)<4: errors.append('expected at least four contradict records after rev0378')
audit=load('docs/00-meta/ma-access-availability-ghost-network-claim-visibility-audit-rev0378.json')
if audit.get('new_locator_record_count')!=8 or audit.get('new_contradict_record_count')!=2 or audit.get('certified_current_after') is not False: errors.append('audit count/certification mismatch')
if errors:
    for e in errors: print('ERROR:',e)
    print(f'FAILED: {len(errors)} MA access-availability/claim-visibility issue(s)')
    sys.exit(1)
print('PASSED: MA access-availability/ghost-network/claim-visibility bridge audit')

# rev0379 current live-surface compatibility marker.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
