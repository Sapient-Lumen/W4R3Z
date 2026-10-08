#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def exists(root, rel): return bool(rel) and (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    tri = load(root / 'REMEDIATION_TRIAGE_POLICY.yml')
    sev = load(root / 'SEVERITY_CLASSIFICATION_MATRIX.yml')
    obj = load(root / 'SERVICE_OBJECTIVE_LEDGER.yml')
    car = load(root / 'CORRECTIVE_ACTION_REGISTER.yml')
    esc = load(root / 'COMMUNICATION_ESCALATION_LEDGER.yml')
    clv = load(root / 'CLOSURE_VERIFICATION_LEDGER.yml')
    failures=[]
    sev_ids={s.get('severity_id') for s in sev.get('levels',[]) or []}
    obj_ids={o.get('objective_id') for o in obj.get('objectives',[]) or []}
    tri_ids={t.get('triage_id') for t in tri.get('triage_cases',[]) or []}
    act_ids={a.get('action_id') for a in car.get('actions',[]) or []}
    close_ids={c.get('closure_id') for c in clv.get('closure_cases',[]) or []}
    if tri.get('public_sla_active') is not False: failures.append({'triage':'public_sla_active must be false'})
    if tri.get('public_support_channel_active') is not False: failures.append({'triage':'public_support_channel_active must be false'})
    if not tri.get('triage_cases'): failures.append({'triage':'no triage cases'})
    for t in tri.get('triage_cases',[]) or []:
        tid=t.get('triage_id')
        if t.get('severity_id') not in sev_ids: failures.append({'triage_id':tid,'unknown_severity':t.get('severity_id')})
        if t.get('objective_ref') not in obj_ids: failures.append({'triage_id':tid,'unknown_objective':t.get('objective_ref')})
        if t.get('corrective_action_ref') not in act_ids: failures.append({'triage_id':tid,'unknown_action':t.get('corrective_action_ref')})
        if t.get('closure_ref') not in close_ids: failures.append({'triage_id':tid,'unknown_closure':t.get('closure_ref')})
        if 'REM4' not in str(t.get('status','')): failures.append({'triage_id':tid,'triage_not_checked':t.get('status')})
        for rel in t.get('source_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'triage_id':tid,'missing_source_artifact':rel})
    if not any(s.get('blocking') for s in sev.get('levels',[]) or []): failures.append({'severity':'no blocking severity level'})
    for s in sev.get('levels',[]) or []:
        if s.get('objective_ref') not in obj_ids: failures.append({'severity_id':s.get('severity_id'),'unknown_objective':s.get('objective_ref')})
    if obj.get('public_sla_active') is not False: failures.append({'objectives':'public_sla_active must be false'})
    if obj.get('public_response_commitment') is not False: failures.append({'objectives':'public_response_commitment must be false'})
    for o in obj.get('objectives',[]) or []:
        for rel in o.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'objective_id':o.get('objective_id'),'missing_evidence_artifact':rel})
    if car.get('closure_required') is not True: failures.append({'corrective_action':'closure_required must be true'})
    for a in car.get('actions',[]) or []:
        aid=a.get('action_id')
        if a.get('triage_ref') not in tri_ids: failures.append({'action_id':aid,'unknown_triage':a.get('triage_ref')})
        if not a.get('owner_role'): failures.append({'action_id':aid,'missing_owner_role':True})
        for rel in a.get('verification_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'action_id':aid,'missing_verification_artifact':rel})
    if esc.get('public_notification_duty') is not False: failures.append({'communication':'public_notification_duty must be false'})
    if esc.get('legal_notice_duty') is not False: failures.append({'communication':'legal_notice_duty must be false'})
    if esc.get('customer_alerting_active') is not False: failures.append({'communication':'customer_alerting_active must be false'})
    for e in esc.get('escalation_paths',[]) or []:
        for rel in e.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'path_id':e.get('path_id'),'missing_evidence_artifact':rel})
    if clv.get('evidence_required') is not True: failures.append({'closure':'evidence_required must be true'})
    for c in clv.get('closure_cases',[]) or []:
        cid=c.get('closure_id')
        if c.get('triage_ref') not in tri_ids: failures.append({'closure_id':cid,'unknown_triage':c.get('triage_ref')})
        if c.get('corrective_action_ref') not in act_ids: failures.append({'closure_id':cid,'unknown_action':c.get('corrective_action_ref')})
        ev=c.get('evidence_artifacts',[]) or []
        if not ev: failures.append({'closure_id':cid,'missing_closure_evidence':True})
        for rel in ev:
            if not exists(root, rel): failures.append({'closure_id':cid,'missing_evidence_artifact':rel})
        if not c.get('residual_debt'): failures.append({'closure_id':cid,'missing_residual_debt':True})
    summary={'triage_cases':len(tri.get('triage_cases',[]) or []),'severity_levels':len(sev.get('levels',[]) or []),'objectives':len(obj.get('objectives',[]) or []),'corrective_actions':len(car.get('actions',[]) or []),'escalation_paths':len(esc.get('escalation_paths',[]) or []),'closure_cases':len(clv.get('closure_cases',[]) or []),'failures':len(failures)}
    reports={
      'remediation_triage_report': {'remediation_triage_report_version':f'{version}-remediation-triage-report-v1','archive_version':version,'status':'REM4_remediation_triage_checked' if not failures else 'REM7_unsafe_remediation_claim','summary':summary,'failures':failures},
      'severity_classification_report': {'severity_classification_report_version':f'{version}-severity-classification-report-v1','archive_version':version,'status':'SEV4_blocking_class_declared' if not failures else 'SEV7_unsafe_severity_claim','summary':summary,'failures':failures},
      'service_objective_report': {'service_objective_report_version':f'{version}-service-objective-report-v1','archive_version':version,'status':'OBJ4_public_sla_absent' if not failures else 'OBJ7_unsafe_service_objective_claim','summary':summary,'failures':failures},
      'corrective_action_report': {'corrective_action_report_version':f'{version}-corrective-action-report-v1','archive_version':version,'status':'CAR4_corrective_actions_checked' if not failures else 'CAR7_unsafe_corrective_action_claim','summary':summary,'failures':failures},
      'communication_escalation_report': {'communication_escalation_report_version':f'{version}-communication-escalation-report-v1','archive_version':version,'status':'ESC4_communication_escalation_checked' if not failures else 'ESC7_unsafe_communication_claim','summary':summary,'failures':failures},
      'closure_verification_report': {'closure_verification_report_version':f'{version}-closure-verification-report-v1','archive_version':version,'status':'CLV4_closure_verification_checked' if not failures else 'CLV7_unsafe_closure_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__': raise SystemExit(main())
