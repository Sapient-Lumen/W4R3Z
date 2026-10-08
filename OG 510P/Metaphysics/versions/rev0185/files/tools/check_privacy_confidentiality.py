#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def exists(root, rel): return bool(rel) and (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    pmn = load(root/'PRIVACY_MINIMIZATION_POLICY.yml')
    caf = load(root/'CONFIDENTIALITY_ACCESS_MATRIX.yml')
    dsp = load(root/'DISCLOSURE_PUBLICATION_REVIEW.yml')
    rtn = load(root/'RETENTION_DELETION_LEDGER.yml')
    sdc = load(root/'SENSITIVE_DATA_CLASSIFICATION.yml')
    prr = load(root/'PRIVACY_RISK_REVIEW_LEDGER.yml')
    roles = {r.get('role_id') for r in load(root/'ROLE_AUTHORITY_MATRIX.yml').get('roles', []) or []}
    failures=[]

    if pmn.get('personal_data_collection_intended') is not False: failures.append({'privacy_minimization':'personal_data_collection_intended must be false'})
    if pmn.get('public_user_tracking_active') is not False: failures.append({'privacy_minimization':'public_user_tracking_active must be false'})
    if pmn.get('data_subject_request_service_active') is not False: failures.append({'privacy_minimization':'data_subject_request_service_active must be false'})

    class_ids={c.get('class_id') for c in sdc.get('classification_classes', []) or []}
    if sdc.get('special_category_data_present') is not False: failures.append({'sensitive_classification':'special_category_data_present must be false'})
    if sdc.get('secrets_detected') is not False: failures.append({'sensitive_classification':'secrets_detected must be false'})
    if sdc.get('personal_data_inventory_claimed_complete') is not False: failures.append({'sensitive_classification':'personal_data_inventory_claimed_complete must be false'})
    for c in sdc.get('classification_classes', []) or []:
        cid=c.get('class_id')
        if 'SDC4' not in str(c.get('status','')): failures.append({'class_id':cid,'not_checked':c.get('status')})
        if not c.get('handling_rule'): failures.append({'class_id':cid,'missing_handling_rule':True})
        for rel in c.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'class_id':cid,'missing_evidence_artifact':rel})

    minimization_ids=set()
    for m in pmn.get('minimization_cases', []) or []:
        mid=m.get('minimization_id'); minimization_ids.add(mid)
        if m.get('classification_ref') not in class_ids: failures.append({'minimization_id':mid,'unknown_classification_ref':m.get('classification_ref')})
        if 'PMN4' not in str(m.get('minimization_status','')): failures.append({'minimization_id':mid,'not_checked':m.get('minimization_status')})
        if not m.get('data_elements_forbidden'): failures.append({'minimization_id':mid,'missing_forbidden_elements':True})
        for rel in m.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'minimization_id':mid,'missing_evidence_artifact':rel})
    if not minimization_ids: failures.append({'privacy_minimization':'no minimization cases'})

    if caf.get('public_confidentiality_guarantee_claimed') is not False: failures.append({'access':'public_confidentiality_guarantee_claimed must be false'})
    if caf.get('secrets_present') is not False: failures.append({'access':'secrets_present must be false'})
    if caf.get('access_control_system_active') is not False: failures.append({'access':'access_control_system_active must be false'})
    access_ids=set()
    for a in caf.get('access_rows', []) or []:
        aid=a.get('access_id'); access_ids.add(aid)
        if a.get('role_ref') not in roles: failures.append({'access_id':aid,'unknown_role_ref':a.get('role_ref')})
        if a.get('classification_ref') not in class_ids: failures.append({'access_id':aid,'unknown_classification_ref':a.get('classification_ref')})
        if 'CAF4' not in str(a.get('access_status','')): failures.append({'access_id':aid,'not_checked':a.get('access_status')})
        if 'guarantee' not in str(a.get('access_boundary','')).lower() and 'may not' not in str(a.get('access_boundary','')).lower(): failures.append({'access_id':aid,'boundary_not_explicit':a.get('access_boundary')})
        for rel in a.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'access_id':aid,'missing_evidence_artifact':rel})

    if dsp.get('external_disclosure_approval_claimed') is not False: failures.append({'disclosure':'external_disclosure_approval_claimed must be false'})
    if dsp.get('public_safe_publication_certified') is not False: failures.append({'disclosure':'public_safe_publication_certified must be false'})
    disclosure_ids=set()
    for d in dsp.get('disclosure_rows', []) or []:
        did=d.get('disclosure_id'); disclosure_ids.add(did)
        for cid in d.get('classification_refs', []) or []:
            if cid not in class_ids: failures.append({'disclosure_id':did,'unknown_classification_ref':cid})
        if 'DSP4' not in str(d.get('disclosure_status','')): failures.append({'disclosure_id':did,'not_checked':d.get('disclosure_status')})
        if not d.get('prohibited_disclosure'): failures.append({'disclosure_id':did,'missing_prohibited_disclosure':True})
        for rel in d.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'disclosure_id':did,'missing_evidence_artifact':rel})

    if rtn.get('legal_retention_schedule_claimed') is not False: failures.append({'retention':'legal_retention_schedule_claimed must be false'})
    if rtn.get('automated_deletion_active') is not False: failures.append({'retention':'automated_deletion_active must be false'})
    retention_ids=set()
    for r in rtn.get('retention_rows', []) or []:
        rid=r.get('retention_id'); retention_ids.add(rid)
        if r.get('classification_ref') not in class_ids: failures.append({'retention_id':rid,'unknown_classification_ref':r.get('classification_ref')})
        if 'RTN4' not in str(r.get('retention_status','')): failures.append({'retention_id':rid,'not_checked':r.get('retention_status')})
        if not r.get('review_trigger'): failures.append({'retention_id':rid,'missing_review_trigger':True})
        for rel in r.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'retention_id':rid,'missing_evidence_artifact':rel})

    if prr.get('legal_privacy_compliance_claimed') is not False: failures.append({'privacy_risk':'legal_privacy_compliance_claimed must be false'})
    if prr.get('privacy_impact_assessment_completed') is not False: failures.append({'privacy_risk':'privacy_impact_assessment_completed must be false'})
    if prr.get('public_dpia_claimed') is not False: failures.append({'privacy_risk':'public_dpia_claimed must be false'})
    review_ids=set()
    for r in prr.get('risk_reviews', []) or []:
        rid=r.get('risk_id'); review_ids.add(rid)
        if r.get('classification_ref') not in class_ids: failures.append({'risk_id':rid,'unknown_classification_ref':r.get('classification_ref')})
        if r.get('minimization_ref') not in minimization_ids: failures.append({'risk_id':rid,'unknown_minimization_ref':r.get('minimization_ref')})
        if r.get('access_ref') not in access_ids: failures.append({'risk_id':rid,'unknown_access_ref':r.get('access_ref')})
        if r.get('disclosure_ref') not in disclosure_ids: failures.append({'risk_id':rid,'unknown_disclosure_ref':r.get('disclosure_ref')})
        if r.get('retention_ref') not in retention_ids: failures.append({'risk_id':rid,'unknown_retention_ref':r.get('retention_ref')})
        if 'PRR4' not in str(r.get('risk_status','')): failures.append({'risk_id':rid,'not_checked':r.get('risk_status')})
        for rel in r.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'risk_id':rid,'missing_evidence_artifact':rel})

    summary={'minimization_cases':len(minimization_ids),'classification_classes':len(class_ids),'access_rows':len(access_ids),'disclosure_rows':len(disclosure_ids),'retention_rows':len(retention_ids),'privacy_risk_reviews':len(review_ids),'failures':len(failures)}
    reports={
      'privacy_minimization_report': {'privacy_minimization_report_version':f'{version}-privacy-minimization-report-v1','archive_version':version,'status':'PMN4_minimization_checked' if not failures else 'PMN7_unsafe_privacy_minimization_claim','summary':summary,'failures':failures},
      'confidentiality_access_report': {'confidentiality_access_report_version':f'{version}-confidentiality-access-report-v1','archive_version':version,'status':'CAF4_confidentiality_access_checked' if not failures else 'CAF7_unsafe_confidentiality_access_claim','summary':summary,'failures':failures},
      'disclosure_publication_report': {'disclosure_publication_report_version':f'{version}-disclosure-publication-report-v1','archive_version':version,'status':'DSP4_disclosure_publication_checked' if not failures else 'DSP7_unsafe_disclosure_claim','summary':summary,'failures':failures},
      'retention_deletion_report': {'retention_deletion_report_version':f'{version}-retention-deletion-report-v1','archive_version':version,'status':'RTN4_retention_deletion_checked' if not failures else 'RTN7_unsafe_retention_claim','summary':summary,'failures':failures},
      'sensitive_data_classification_report': {'sensitive_data_classification_report_version':f'{version}-sensitive-data-classification-report-v1','archive_version':version,'status':'SDC4_sensitive_data_classification_checked' if not failures else 'SDC7_unsafe_sensitive_data_claim','summary':summary,'failures':failures},
      'privacy_risk_review_report': {'privacy_risk_review_report_version':f'{version}-privacy-risk-review-report-v1','archive_version':version,'status':'PRR4_privacy_risk_checked' if not failures else 'PRR7_unsafe_privacy_risk_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__': raise SystemExit(main())
