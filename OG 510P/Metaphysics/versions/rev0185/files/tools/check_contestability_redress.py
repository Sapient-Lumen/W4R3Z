#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def exists(root, rel): return bool(rel) and (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    cnt = load(root/'CONTESTATION_INTAKE_LEDGER.yml')
    apl = load(root/'APPEAL_REVIEW_POLICY.yml')
    dst = load(root/'DISSENT_MINORITY_REPORT_LEDGER.yml')
    hir = load(root/'HARM_IMPACT_REVIEW_LEDGER.yml')
    rdr = load(root/'REDRESS_REVERSAL_LEDGER.yml')
    chl = load(root/'STAKEHOLDER_CHALLENGE_REGISTER.yml')
    roles = {r.get('role_id') for r in load(root/'ROLE_AUTHORITY_MATRIX.yml').get('roles', []) or []}
    severity_ids = {l.get('severity_id') for l in load(root/'SEVERITY_CLASSIFICATION_MATRIX.yml').get('levels', []) or []}
    remediation_ids = {t.get('triage_id') for t in load(root/'REMEDIATION_TRIAGE_POLICY.yml').get('triage_cases', []) or []}
    failures=[]

    if cnt.get('public_complaint_channel_active') is not False: failures.append({'contestation':'public_complaint_channel_active must be false'})
    if cnt.get('legal_grievance_procedure_active') is not False: failures.append({'contestation':'legal_grievance_procedure_active must be false'})
    challenge_ids={s.get('stakeholder_id') for s in chl.get('stakeholder_classes', []) or []}
    contest_ids=set()
    for c in cnt.get('contestations', []) or []:
        cid=c.get('contestation_id'); contest_ids.add(cid)
        if c.get('stakeholder_ref') not in challenge_ids: failures.append({'contestation_id':cid,'unknown_stakeholder_ref':c.get('stakeholder_ref')})
        if 'CNT4' not in str(c.get('intake_status','')): failures.append({'contestation_id':cid,'not_checked':c.get('intake_status')})
        for rel in c.get('source_artifacts', []) or []:
            if not exists(root, rel): failures.append({'contestation_id':cid,'missing_source_artifact':rel})
    if not contest_ids: failures.append({'contestation':'no contestation rows'})

    if apl.get('external_appeal_authority_present') is not False: failures.append({'appeal':'external_appeal_authority_present must be false'})
    if apl.get('public_appeal_channel_active') is not False: failures.append({'appeal':'public_appeal_channel_active must be false'})
    appeal_ids=set()
    for a in apl.get('appeals', []) or []:
        aid=a.get('appeal_id'); appeal_ids.add(aid)
        if a.get('contestation_ref') not in contest_ids: failures.append({'appeal_id':aid,'unknown_contestation_ref':a.get('contestation_ref')})
        if a.get('reviewing_role') not in roles: failures.append({'appeal_id':aid,'unknown_reviewing_role':a.get('reviewing_role')})
        for r in a.get('consulted_roles', []) or []:
            if r not in roles: failures.append({'appeal_id':aid,'unknown_consulted_role':r})
        if 'APL4' not in str(a.get('appeal_status','')): failures.append({'appeal_id':aid,'not_checked':a.get('appeal_status')})
        for rel in a.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'appeal_id':aid,'missing_evidence_artifact':rel})
    if not appeal_ids: failures.append({'appeal':'no appeal rows'})

    if dst.get('dissent_suppression_allowed') is not False: failures.append({'dissent':'dissent_suppression_allowed must be false'})
    dissent_ids=set()
    for d in dst.get('dissent_reports', []) or []:
        did=d.get('dissent_id'); dissent_ids.add(did)
        if d.get('related_contestation') not in contest_ids: failures.append({'dissent_id':did,'unknown_contestation_ref':d.get('related_contestation')})
        if d.get('dissent_preserved') is not True: failures.append({'dissent_id':did,'dissent_not_preserved':d.get('dissent_preserved')})
        if 'DST4' not in str(d.get('dissent_status','')): failures.append({'dissent_id':did,'not_checked':d.get('dissent_status')})
        for rel in d.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'dissent_id':did,'missing_evidence_artifact':rel})

    if hir.get('legal_harm_review_completed') is not False: failures.append({'harm':'legal_harm_review_completed must be false'})
    if hir.get('operational_safety_assessment_completed') is not False: failures.append({'harm':'operational_safety_assessment_completed must be false'})
    harm_ids=set()
    for h in hir.get('harm_cases', []) or []:
        hid=h.get('harm_id'); harm_ids.add(hid)
        if h.get('contestation_ref') not in contest_ids: failures.append({'harm_id':hid,'unknown_contestation_ref':h.get('contestation_ref')})
        if h.get('stakeholder_ref') not in challenge_ids: failures.append({'harm_id':hid,'unknown_stakeholder_ref':h.get('stakeholder_ref')})
        if h.get('severity_ref') not in severity_ids: failures.append({'harm_id':hid,'unknown_severity_ref':h.get('severity_ref')})
        if h.get('remediation_ref') not in remediation_ids: failures.append({'harm_id':hid,'unknown_remediation_ref':h.get('remediation_ref')})
        if 'HIR4' not in str(h.get('harm_status','')): failures.append({'harm_id':hid,'not_checked':h.get('harm_status')})
        for rel in h.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'harm_id':hid,'missing_evidence_artifact':rel})

    if rdr.get('legal_remedy_available') is not False: failures.append({'redress':'legal_remedy_available must be false'})
    if rdr.get('downstream_recall_authority_present') is not False: failures.append({'redress':'downstream_recall_authority_present must be false'})
    if rdr.get('compensation_process_active') is not False: failures.append({'redress':'compensation_process_active must be false'})
    redress_ids=set()
    for r in rdr.get('redress_rows', []) or []:
        rid=r.get('redress_id'); redress_ids.add(rid)
        if r.get('contestation_ref') not in contest_ids: failures.append({'redress_id':rid,'unknown_contestation_ref':r.get('contestation_ref')})
        if r.get('appeal_ref') not in appeal_ids: failures.append({'redress_id':rid,'unknown_appeal_ref':r.get('appeal_ref')})
        if r.get('harm_ref') not in harm_ids: failures.append({'redress_id':rid,'unknown_harm_ref':r.get('harm_ref')})
        if 'RDR4' not in str(r.get('redress_status','')): failures.append({'redress_id':rid,'not_checked':r.get('redress_status')})
        if not r.get('changed_artifacts'): failures.append({'redress_id':rid,'missing_changed_artifacts':True})
        if not r.get('evidence_artifacts'): failures.append({'redress_id':rid,'missing_redress_evidence':True})
        for rel in (r.get('changed_artifacts', []) or []) + (r.get('evidence_artifacts', []) or []):
            if not exists(root, rel): failures.append({'redress_id':rid,'missing_artifact':rel})
        if not r.get('residual_boundary'): failures.append({'redress_id':rid,'missing_residual_boundary':True})

    if chl.get('stakeholder_consultation_completed') is not False: failures.append({'challenge':'stakeholder_consultation_completed must be false'})
    if chl.get('public_consent_collected') is not False: failures.append({'challenge':'public_consent_collected must be false'})
    if chl.get('stakeholder_representation_claimed') is not False: failures.append({'challenge':'stakeholder_representation_claimed must be false'})
    for s in chl.get('stakeholder_classes', []) or []:
        sid=s.get('stakeholder_id')
        if not s.get('standing_boundary'): failures.append({'stakeholder_id':sid,'missing_standing_boundary':True})
        for rel in s.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'stakeholder_id':sid,'missing_evidence_artifact':rel})
    for ch in chl.get('challenge_channels', []) or []:
        if ch.get('public_channel') is True: failures.append({'channel_id':ch.get('channel_id'),'public_channel_active':True})
        for rel in ch.get('routes_to', []) or []:
            if not exists(root, rel): failures.append({'channel_id':ch.get('channel_id'),'missing_route_artifact':rel})

    summary={'contestations':len(contest_ids),'appeals':len(appeal_ids),'dissent_reports':len(dissent_ids),'harm_cases':len(harm_ids),'redress_rows':len(redress_ids),'stakeholder_classes':len(challenge_ids),'failures':len(failures)}
    reports={
      'contestation_intake_report': {'contestation_intake_report_version':f'{version}-contestation-intake-report-v1','archive_version':version,'status':'CNT4_contestation_checked' if not failures else 'CNT7_unsafe_contestation_claim','summary':summary,'failures':failures},
      'appeal_review_report': {'appeal_review_report_version':f'{version}-appeal-review-report-v1','archive_version':version,'status':'APL4_appeal_review_checked' if not failures else 'APL7_unsafe_appeal_claim','summary':summary,'failures':failures},
      'dissent_report': {'dissent_report_version':f'{version}-dissent-report-v1','archive_version':version,'status':'DST4_dissent_ledger_checked' if not failures else 'DST7_unsafe_dissent_claim','summary':summary,'failures':failures},
      'harm_impact_report': {'harm_impact_report_version':f'{version}-harm-impact-report-v1','archive_version':version,'status':'HIR4_harm_impact_checked' if not failures else 'HIR7_unsafe_harm_claim','summary':summary,'failures':failures},
      'redress_reversal_report': {'redress_reversal_report_version':f'{version}-redress-reversal-report-v1','archive_version':version,'status':'RDR4_redress_reversal_checked' if not failures else 'RDR7_unsafe_redress_claim','summary':summary,'failures':failures},
      'stakeholder_challenge_report': {'stakeholder_challenge_report_version':f'{version}-stakeholder-challenge-report-v1','archive_version':version,'status':'CHL4_stakeholder_challenge_checked' if not failures else 'CHL7_unsafe_challenge_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__': raise SystemExit(main())
