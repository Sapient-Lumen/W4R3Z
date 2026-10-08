#!/usr/bin/env python3
"""Audit the active MA contractor/resident-harm/enforcement bridge.

Rev0378 refactor: resolve the newest revisioned bridge when the current release has advanced. The bridge remains an upstream guardrail; it should not fail merely because a later bridge is now current.
"""
from pathlib import Path
import json, sys, re
ROOT=Path(__file__).resolve().parents[1]
REQUIRED_METRICS={
    'navihealth_processed_share_of_snf_requests':0.50,
    'navihealth_snf_denial_rate':0.14,
    'internal_mao_snf_denial_rate':0.11,
    'other_contractor_snf_denial_rate':0.09,
    'navihealth_appealed_denial_overturn_rate':0.97,
    'nursing_home_resident_snf_denial_rate':0.40,
    'all_other_enrollees_snf_denial_rate':0.11,
}
REQUIRED_SOURCES={'S579','S597','S598','S599'}
REQUIRED_FIELDS={'contractor_or_delegated_entity_id','enrollee_residence_or_institutional_status','approved_authorization_reopened_flag','concurrent_decision_flag','program_audit_result_id','cms_enforcement_action_id','beneficiary_restoration_status','provider_payment_restoration_status'}

def resolve_bridge():
    candidates=sorted((ROOT/'cases').glob('social-security-medicare-claim-security-rev0318-ma-contractor-resident-harm-enforcement-bridge-rev*.json'))
    if not candidates:
        return ROOT/'cases/social-security-medicare-claim-security-rev0318-ma-contractor-resident-harm-enforcement-bridge-rev0375.json'
    def key(p):
        m=re.search(r'rev(\d{4})', p.name)
        return int(m.group(1)) if m else -1
    return sorted(candidates, key=key)[-1]

def main():
    p=resolve_bridge(); issues=[]
    if not p.exists(): issues.append(f'missing bridge file: {p.relative_to(ROOT)}')
    else:
        data=json.loads(p.read_text(encoding='utf-8'))
        if data.get('certification_status_after_rev0375')!='not_certified_current': issues.append('bridge must remain noncertifying')
        blob=json.dumps(data, sort_keys=True)
        for k,v in REQUIRED_METRICS.items():
            if f'"{k}": {v}' not in blob: issues.append(f'missing OIG metric {k}={v}')
        seen=set()
        for rec in data.get('substantive_records') or []: seen.update(rec.get('source_ids') or [])
        if REQUIRED_SOURCES-seen: issues.append('missing required sources: '+', '.join(sorted(REQUIRED_SOURCES-seen)))
        missing=REQUIRED_FIELDS-set(data.get('new_required_row_fields') or [])
        if missing: issues.append('missing required bridge fields: '+', '.join(sorted(missing)))
        if len(data.get('false_pass_blocks') or [])<6: issues.append('false_pass_blocks too short')
        if data.get('certified_current_case_count_after')!=0: issues.append('certified_current_case_count_after must be zero')
    if issues:
        for issue in issues: print('ERROR:', issue)
        print(f'FAILED: {len(issues)} MA contractor/resident/enforcement bridge issue(s)')
        return 1
    print('PASSED: MA contractor/resident-harm/enforcement bridge audit')
    return 0
if __name__=='__main__': sys.exit(main())

# rev0378 live-surface exposure: this earlier bridge audit remains part of the current MA audit chain under rev0378.

# Retained in the rev0379 live-surface contract as an upstream MA guardrail audit.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
