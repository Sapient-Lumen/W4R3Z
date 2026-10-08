#!/usr/bin/env python3
"""rev0375 active in current release. Audit the MA appeal-burden public pilot without requiring a same-revision copy.

Rev0375 refactor: the public pilot was created in rev0374 and remains active, but
future revisions should resolve the newest revisioned pilot file rather than
silently treating the absence of a same-revision copy as a substantive failure.
"""
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    'prior_authorization_determinations_millions':52.8,
    'fully_or_partially_denied_millions':4.1,
    'denial_rate':0.077,
    'appeal_share_of_denials':0.115,
    'overturn_share_of_appeals':0.807,
    'snf_request_denial_rate':0.12,
    'appeal_share_of_snf_denials':0.18,
    'overturn_share_of_appealed_snf_denials':0.95,
    'ltch_overturn_share_of_appealed_denials':0.36,
    'irf_overturn_share_of_appealed_denials':0.43,
}

def resolve_pilot():
    rev=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
    cur=ROOT/'cases'/f'social-security-medicare-claim-security-rev0318-ma-appeal-burden-public-pilot-{rev}.json'
    if cur.exists():
        return cur
    candidates=sorted((ROOT/'cases').glob('social-security-medicare-claim-security-rev0318-ma-appeal-burden-public-pilot-rev*.json'))
    if not candidates:
        return cur
    def key(p):
        m=re.search(r'rev(\d{4})', p.name)
        return int(m.group(1)) if m else -1
    return sorted(candidates, key=key)[-1]

def main():
    path=resolve_pilot()
    issues=[]
    if not path.exists():
        issues.append(f'missing MA appeal-burden pilot: {path.relative_to(ROOT)}')
    else:
        data=json.loads(path.read_text(encoding='utf-8'))
        if data.get('certification_status_after_rev0374')!='not_certified_current':
            issues.append('pilot must remain noncertifying')
        blob=json.dumps(data, sort_keys=True)
        for key,val in EXPECTED.items():
            if f'"{key}": {val}' not in blob:
                issues.append(f'missing expected public metric {key}={val}')
        if 'A high overturn rate is not a self-correction pass' not in blob:
            issues.append('appeal-burden inference rule missing')
        if len(data.get('false_pass_blocks') or []) < 6:
            issues.append('false_pass_blocks too short')
        if data.get('certified_current_case_count_after') != 0:
            issues.append('certified_current_case_count_after must be zero')
    if issues:
        for issue in issues:
            print('ERROR:', issue)
        print(f'FAILED: {len(issues)} MA appeal-burden pilot issue(s)')
        return 1
    print('PASSED: MA appeal-burden public pilot audit')
    return 0
if __name__=='__main__':
    sys.exit(main())

# rev0376 note: retained as upstream prerequisite for the MA equity-disaggregation and beneficiary-experience bridge.

# Retained in the rev0377 live-surface contract as an upstream MA guardrail audit.

# Retained in the rev0378 live-surface contract as an upstream MA guardrail audit.

# Retained in the rev0379 live-surface contract as an upstream MA guardrail audit.

# current_release_anchor: rev0380 retains this upstream bridge audit as active; do not clone same-revision boilerplate.
