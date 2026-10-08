#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def exists(root, rel): return bool(rel) and (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    roles = load(root/'ROLE_AUTHORITY_MATRIX.yml')
    assign = load(root/'ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml')
    sod = load(root/'SEGREGATION_OF_DUTIES_POLICY.yml')
    deleg = load(root/'DELEGATION_HANDOFF_LEDGER.yml')
    approval = load(root/'APPROVAL_CONSENT_LEDGER.yml')
    review = load(root/'ACCOUNTABILITY_REVIEW_LEDGER.yml')
    failures=[]

    role_rows = roles.get('roles', []) or []
    role_ids = {r.get('role_id') for r in role_rows}
    if len(role_ids) != len(role_rows): failures.append({'role_authority':'duplicate role_id'})
    if roles.get('public_authority_granted') is not False: failures.append({'role_authority':'public_authority_granted must be false'})
    if roles.get('external_approval_authority_present') is not False: failures.append({'role_authority':'external_approval_authority_present must be false'})
    if not any(r.get('accountability_scope') for r in role_rows): failures.append({'role_authority':'no accountability scopes'})
    for r in role_rows:
        rid = r.get('role_id')
        if r.get('public_authority_granted') is not False: failures.append({'role_id':rid,'public_authority_granted_not_false':r.get('public_authority_granted')})
        if not r.get('forbidden_authority'): failures.append({'role_id':rid,'missing_forbidden_authority':True})
        for rel in r.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'role_id':rid,'missing_evidence_artifact':rel})

    assignment_ids=set()
    for a in assign.get('assignments', []) or []:
        aid=a.get('assignment_id'); assignment_ids.add(aid)
        for key in ['accountable_role','responsible_role']:
            if a.get(key) not in role_ids: failures.append({'assignment_id':aid,'unknown_'+key:a.get(key)})
        for key in ['consulted_roles','informed_roles']:
            for rid in a.get(key, []) or []:
                if rid not in role_ids: failures.append({'assignment_id':aid,'unknown_'+key:rid})
        for rel in a.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'assignment_id':aid,'missing_evidence_artifact':rel})
    if assign.get('unassigned_critical_surfaces') not in ([], None): failures.append({'assignments':'unassigned critical surfaces present'})
    if 'scripts' not in str(assign.get('non_role_rule','')).lower(): failures.append({'assignments':'non-role rule must mention scripts/tools/reports cannot be accountable'})

    for p in sod.get('prohibited_combinations', []) or []:
        if p.get('role_a') not in role_ids: failures.append({'pair_id':p.get('pair_id'),'unknown_role_a':p.get('role_a')})
        if p.get('role_b') not in role_ids: failures.append({'pair_id':p.get('pair_id'),'unknown_role_b':p.get('role_b')})
    if sod.get('independence_claimed') is not False: failures.append({'segregation':'independence_claimed must be false'})
    if sod.get('violations') not in ([], None): failures.append({'segregation':'violations present'})
    for obs in sod.get('observed_combinations', []) or []:
        for rid in obs.get('roles', []) or []:
            if rid not in role_ids: failures.append({'sod_observation':obs.get('observation_id'),'unknown_role':rid})
        if 'SOD4' not in str(obs.get('segregation_status','')): failures.append({'sod_observation':obs.get('observation_id'),'not_checked':obs.get('segregation_status')})

    for d in deleg.get('delegations', []) or []:
        did=d.get('delegation_id')
        for key in ['from_role','to_role','retained_accountability']:
            if d.get(key) not in role_ids: failures.append({'delegation_id':did,'unknown_'+key:d.get(key)})
        if not d.get('nondelegable_duties'): failures.append({'delegation_id':did,'missing_nondelegable_duties':True})
        if 'DLG4' not in str(d.get('delegation_state','')): failures.append({'delegation_id':did,'not_checked':d.get('delegation_state')})
        for rel in d.get('handoff_evidence', []) or []:
            if not exists(root, rel): failures.append({'delegation_id':did,'missing_handoff_evidence':rel})

    if approval.get('external_approval_present') is not False: failures.append({'approval':'external_approval_present must be false'})
    if approval.get('public_consent_collected') is not False: failures.append({'approval':'public_consent_collected must be false'})
    if approval.get('legal_consent_collected') is not False: failures.append({'approval':'legal_consent_collected must be false'})
    if approval.get('downstream_reliance_authorized') is not False: failures.append({'approval':'downstream_reliance_authorized must be false'})
    approval_ids=set()
    for ap in approval.get('approval_rows', []) or []:
        apid=ap.get('approval_id'); approval_ids.add(apid)
        if ap.get('approving_role') not in role_ids: failures.append({'approval_id':apid,'unknown_approving_role':ap.get('approving_role')})
        if 'APC4' not in str(ap.get('approval_status','')): failures.append({'approval_id':apid,'not_checked':ap.get('approval_status')})
        for rel in ap.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'approval_id':apid,'missing_evidence_artifact':rel})
    for c in approval.get('consent_rows', []) or []:
        if 'no_public_consent' not in str(c.get('consent_status','')).lower(): failures.append({'consent_id':c.get('consent_id'),'unsafe_consent_status':c.get('consent_status')})
        for rel in c.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'consent_id':c.get('consent_id'),'missing_evidence_artifact':rel})

    for rv in review.get('review_cases', []) or []:
        rid=rv.get('review_id')
        if rv.get('assignment_ref') not in assignment_ids: failures.append({'review_id':rid,'unknown_assignment_ref':rv.get('assignment_ref')})
        if rv.get('approval_ref') not in approval_ids: failures.append({'review_id':rid,'unknown_approval_ref':rv.get('approval_ref')})
        for rr in rv.get('role_refs', []) or []:
            if rr not in role_ids: failures.append({'review_id':rid,'unknown_role_ref':rr})
        if 'ACR4' not in str(rv.get('review_status','')): failures.append({'review_id':rid,'not_checked':rv.get('review_status')})
        ev=rv.get('evidence_artifacts', []) or []
        if not ev: failures.append({'review_id':rid,'missing_review_evidence':True})
        for rel in ev:
            if not exists(root, rel): failures.append({'review_id':rid,'missing_evidence_artifact':rel})

    summary={'roles':len(role_rows),'assignments':len(assign.get('assignments',[]) or []),'prohibited_pairings':len(sod.get('prohibited_combinations',[]) or []),'delegations':len(deleg.get('delegations',[]) or []),'approvals':len(approval.get('approval_rows',[]) or []),'consent_rows':len(approval.get('consent_rows',[]) or []),'review_cases':len(review.get('review_cases',[]) or []),'failures':len(failures)}
    reports={
      'role_authority_report': {'role_authority_report_version':f'{version}-role-authority-report-v1','archive_version':version,'status':'RAR4_role_authority_checked; RAR5_external_authority_absent' if not failures else 'RAR7_unsafe_role_authority_claim','summary':summary,'failures':failures},
      'accountability_assignment_report': {'accountability_assignment_report_version':f'{version}-accountability-assignment-report-v1','archive_version':version,'status':'AAS4_assignments_checked; AAS5_non_role_accountability_blocked' if not failures else 'AAS7_unsafe_assignment_claim','summary':summary,'failures':failures},
      'segregation_duties_report': {'segregation_duties_report_version':f'{version}-segregation-duties-report-v1','archive_version':version,'status':'SOD4_duty_segregation_checked; SOD5_independence_absence_declared' if not failures else 'SOD7_unsafe_segregation_claim','summary':summary,'failures':failures},
      'delegation_handoff_report': {'delegation_handoff_report_version':f'{version}-delegation-handoff-report-v1','archive_version':version,'status':'DLG4_delegations_checked; DLG5_nondelegable_duties_declared' if not failures else 'DLG7_unsafe_delegation_claim','summary':summary,'failures':failures},
      'approval_consent_report': {'approval_consent_report_version':f'{version}-approval-consent-report-v1','archive_version':version,'status':'APC4_approval_consent_checked; APC5_no_public_consent_collected' if not failures else 'APC7_unsafe_approval_consent_claim','summary':summary,'failures':failures},
      'accountability_review_report': {'accountability_review_report_version':f'{version}-accountability-review-report-v1','archive_version':version,'status':'ACR4_accountability_review_checked; ACR5_external_review_absent' if not failures else 'ACR7_unsafe_accountability_review_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__': raise SystemExit(main())
