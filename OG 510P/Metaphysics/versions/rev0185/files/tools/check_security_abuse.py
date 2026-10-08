#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def exists(root, rel):
    return bool(rel) and (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    thm = load(root/'SECURITY_THREAT_MODEL.yml')
    abu = load(root/'ABUSE_MISUSE_CASE_REGISTER.yml')
    vul = load(root/'VULNERABILITY_DISCLOSURE_INTAKE.yml')
    hrd = load(root/'SECURITY_HARDENING_BASELINE.yml')
    trb = load(root/'TRUST_BOUNDARY_LEDGER.yml')
    skm = load(root/'SECRET_KEY_MATERIAL_POLICY.yml')
    failures=[]

    if thm.get('public_security_certification_claimed') is not False: failures.append({'threat_model':'public_security_certification_claimed must be false'})
    if thm.get('penetration_test_completed') is not False: failures.append({'threat_model':'penetration_test_completed must be false'})
    if thm.get('production_attack_surface_claimed') is not False: failures.append({'threat_model':'production_attack_surface_claimed must be false'})
    if abu.get('red_team_completed') is not False: failures.append({'abuse_register':'red_team_completed must be false'})
    if abu.get('public_abuse_monitoring_active') is not False: failures.append({'abuse_register':'public_abuse_monitoring_active must be false'})
    if vul.get('public_vulnerability_disclosure_program_active') is not False: failures.append({'vulnerability_intake':'public_vulnerability_disclosure_program_active must be false'})
    if vul.get('bug_bounty_active') is not False: failures.append({'vulnerability_intake':'bug_bounty_active must be false'})
    if vul.get('coordinated_disclosure_service_claimed') is not False: failures.append({'vulnerability_intake':'coordinated_disclosure_service_claimed must be false'})
    if hrd.get('technical_hardening_enforced') is not False: failures.append({'hardening':'technical_hardening_enforced must be false'})
    if hrd.get('sast_completed') is not False: failures.append({'hardening':'sast_completed must be false'})
    if hrd.get('dependency_scan_completed') is not False: failures.append({'hardening':'dependency_scan_completed must be false'})
    if trb.get('external_trust_claimed') is not False: failures.append({'trust_boundary':'external_trust_claimed must be false'})
    if trb.get('production_boundary_claimed') is not False: failures.append({'trust_boundary':'production_boundary_claimed must be false'})
    if skm.get('secrets_present') is not False: failures.append({'secret_policy':'secrets_present must be false'})
    if skm.get('private_keys_present') is not False: failures.append({'secret_policy':'private_keys_present must be false'})
    if skm.get('automated_secret_scan_completed') is not False: failures.append({'secret_policy':'automated_secret_scan_completed must be false'})
    if skm.get('credential_rotation_service_active') is not False: failures.append({'secret_policy':'credential_rotation_service_active must be false'})

    boundary_ids={b.get('boundary_id') for b in trb.get('boundaries', []) or []}
    abuse_ids={a.get('abuse_case_id') for a in abu.get('abuse_cases', []) or []}
    if not boundary_ids: failures.append({'trust_boundary':'no boundaries'})
    if not abuse_ids: failures.append({'abuse_register':'no abuse cases'})
    for b in trb.get('boundaries', []) or []:
        bid=b.get('boundary_id')
        if 'TRB4' not in str(b.get('status','')): failures.append({'boundary_id':bid,'not_checked':b.get('status')})
        for rel in b.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'boundary_id':bid,'missing_evidence_artifact':rel})
    for a in abu.get('abuse_cases', []) or []:
        aid=a.get('abuse_case_id')
        if 'ABU4' not in str(a.get('status','')): failures.append({'abuse_case_id':aid,'not_checked':a.get('status')})
        if not a.get('risk_boundary'): failures.append({'abuse_case_id':aid,'missing_risk_boundary':True})
        for rel in (a.get('linked_controls') or []) + (a.get('evidence_artifacts') or []):
            if not exists(root, rel): failures.append({'abuse_case_id':aid,'missing_artifact':rel})
    for t in thm.get('threat_models', []) or []:
        tid=t.get('threat_model_id')
        if 'THM4' not in str(t.get('status','')): failures.append({'threat_model_id':tid,'not_checked':t.get('status')})
        for ref in t.get('trust_boundary_refs', []) or []:
            if ref not in boundary_ids: failures.append({'threat_model_id':tid,'unknown_trust_boundary_ref':ref})
        for ref in t.get('abuse_case_refs', []) or []:
            if ref not in abuse_ids: failures.append({'threat_model_id':tid,'unknown_abuse_case_ref':ref})
        for rel in t.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'threat_model_id':tid,'missing_evidence_artifact':rel})
    if not thm.get('threat_models'): failures.append({'threat_model':'no threat models'})

    for v in vul.get('intake_rows', []) or []:
        vid=v.get('intake_id')
        if 'VUL4' not in str(v.get('status','')): failures.append({'intake_id':vid,'not_checked':v.get('status')})
        if 'public' in str(v.get('routing','')).lower() and 'do not publish as public' not in str(v.get('routing','')).lower(): failures.append({'intake_id':vid,'unsafe_public_routing':v.get('routing')})
        for rel in v.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'intake_id':vid,'missing_evidence_artifact':rel})
    if not vul.get('intake_rows'): failures.append({'vulnerability_intake':'no intake rows'})

    for c in hrd.get('baseline_controls', []) or []:
        cid=c.get('control_id')
        if 'HRD4' not in str(c.get('status','')): failures.append({'control_id':cid,'not_checked':c.get('status')})
        for rel in c.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'control_id':cid,'missing_evidence_artifact':rel})
    if not hrd.get('baseline_controls'): failures.append({'hardening':'no baseline controls'})

    for s in skm.get('secret_classes', []) or []:
        sid=s.get('secret_class_id')
        if 'SKM4' not in str(s.get('status','')): failures.append({'secret_class_id':sid,'not_checked':s.get('status')})
        if not s.get('handling_rule'): failures.append({'secret_class_id':sid,'missing_handling_rule':True})
        for rel in s.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'secret_class_id':sid,'missing_evidence_artifact':rel})
    if not skm.get('secret_classes'): failures.append({'secret_policy':'no secret classes'})

    summary={'threat_models':len(thm.get('threat_models',[]) or []),'abuse_cases':len(abu.get('abuse_cases',[]) or []),'vulnerability_intake_rows':len(vul.get('intake_rows',[]) or []),'hardening_controls':len(hrd.get('baseline_controls',[]) or []),'trust_boundaries':len(trb.get('boundaries',[]) or []),'secret_classes':len(skm.get('secret_classes',[]) or []),'failures':len(failures)}
    reports={
      'security_threat_model_report': {'security_threat_model_report_version':f'{version}-security-threat-model-report-v1','archive_version':version,'status':'THM4_threat_model_checked; THM5_security_certification_absent' if not failures else 'THM7_unsafe_threat_model_claim','summary':summary,'failures':failures},
      'abuse_misuse_case_report': {'abuse_misuse_case_report_version':f'{version}-abuse-misuse-case-report-v1','archive_version':version,'status':'ABU4_abuse_cases_checked; ABU5_red_team_absent' if not failures else 'ABU7_unsafe_abuse_case_claim','summary':summary,'failures':failures},
      'vulnerability_disclosure_report': {'vulnerability_disclosure_report_version':f'{version}-vulnerability-disclosure-report-v1','archive_version':version,'status':'VUL4_vulnerability_intake_checked; VUL5_public_vdp_absent' if not failures else 'VUL7_unsafe_vulnerability_claim','summary':summary,'failures':failures},
      'security_hardening_report': {'security_hardening_report_version':f'{version}-security-hardening-report-v1','archive_version':version,'status':'HRD4_hardening_baseline_checked; HRD5_security_scan_absent' if not failures else 'HRD7_unsafe_hardening_claim','summary':summary,'failures':failures},
      'trust_boundary_report': {'trust_boundary_report_version':f'{version}-trust-boundary-report-v1','archive_version':version,'status':'TRB4_trust_boundaries_checked; TRB5_production_boundary_absent' if not failures else 'TRB7_unsafe_trust_boundary_claim','summary':summary,'failures':failures},
      'secret_key_material_report': {'secret_key_material_report_version':f'{version}-secret-key-material-report-v1','archive_version':version,'status':'SKM4_secret_key_material_checked; SKM5_automated_secret_scan_absent' if not failures else 'SKM7_unsafe_secret_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__':
    raise SystemExit(main())
