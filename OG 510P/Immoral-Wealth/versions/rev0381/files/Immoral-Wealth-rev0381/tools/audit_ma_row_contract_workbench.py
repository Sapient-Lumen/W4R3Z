#!/usr/bin/env python3
"""rev0375 active in current release. Audit the MA row-contract workbench without hardcoding the current filename.

Rev0374 refactor (rev0374): the row contract was created in rev0373 and remains substantively
active, but future revisions should not fail merely because there is not a same-revision
copy of the workbench. Resolve the current file if present, otherwise the newest
revisioned workbench file.
"""
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
 'contract_id','report_year','service_category','monthly_enrollment','request_count','adverse_or_partially_adverse_count','appeal_count','overturn_count','criteria_id','delegated_entity','delay_days','beneficiary_harm_flag','beneficiary_remedy_type','star_rating_contract','radv_overpayment_amount','radv_recovery_status','integrated_denial_notice_issued','source_ids'
}

def resolve_workbench():
    rev=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    cur=ROOT/'cases'/f'social-security-medicare-claim-security-rev0318-ma-contract-claim-security-workbench-{rev}.json'
    if cur.exists():
        return cur
    candidates=sorted((ROOT/'cases').glob('social-security-medicare-claim-security-rev0318-ma-contract-claim-security-workbench-rev*.json'))
    if not candidates:
        return cur
    def key(p):
        m=re.search(r'rev(\d{4})', p.name)
        return int(m.group(1)) if m else -1
    return sorted(candidates, key=key)[-1]

def main():
    path=resolve_workbench()
    issues=[]
    if not path.exists():
        issues.append(f'workbench missing: {path.relative_to(ROOT)}')
    else:
        data=json.loads(path.read_text(encoding='utf-8'))
        status=str(data.get('certification_status_after_rev0373') or data.get('certification_status') or data.get('status'))
        if 'not_certified_current' not in status:
            issues.append('workbench must remain noncertifying')
        cols=set(data.get('required_columns') or [])
        missing=sorted(REQUIRED-cols)
        if missing: issues.append('required columns missing: '+', '.join(missing))
        if len(data.get('false_pass_blocks') or [])<6:
            issues.append('false_pass_blocks too short')
        if not data.get('minimum_viable_pilot'):
            issues.append('minimum_viable_pilot missing')
    if issues:
        for i in issues: print('ERROR:', i)
        return 1
    print('PASSED: MA row-contract workbench audit')
    return 0
if __name__=='__main__': sys.exit(main())

# rev0376 note: retained as upstream prerequisite for the MA equity-disaggregation and beneficiary-experience bridge.

# Retained in the rev0377 live-surface contract as an upstream MA guardrail audit.

# Retained in the rev0378 live-surface contract as an upstream MA guardrail audit.

# Retained in the rev0379 live-surface contract as an upstream MA guardrail audit.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
