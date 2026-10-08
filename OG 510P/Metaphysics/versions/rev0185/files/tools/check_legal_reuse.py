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
    lic = load(root/'LICENSE_REUSE_POLICY.yml')
    atb = load(root/'ATTRIBUTION_CITATION_LEDGER.yml')
    tpc = load(root/'THIRD_PARTY_CONTENT_REGISTER.yml')
    cpn = load(root/'CONTRIBUTOR_PROVENANCE_LEDGER.yml')
    der = load(root/'DERIVATIVE_REDISTRIBUTION_POLICY.yml')
    cbl = load(root/'COMPLIANCE_BOUNDARY_LEDGER.yml')
    roles = load(root/'ROLE_AUTHORITY_MATRIX.yml')
    role_ids = {r.get('role_id') for r in roles.get('roles', []) or []}
    failures=[]

    false_checks = [
      (lic, ['public_license_grant_claimed','legal_review_completed','lawyer_review_claimed','license_compliance_claimed','copyright_clearance_completed'], 'license_reuse'),
      (atb, ['endorsement_claim_allowed','sponsorship_claim_allowed','official_status_claim_allowed','legal_attribution_service_claimed'], 'attribution_citation'),
      (tpc, ['complete_third_party_inventory_claimed','third_party_clearance_completed','external_content_republished','copyright_clearance_claimed'], 'third_party_content'),
      (cpn, ['external_contributor_claimed','contributor_assignment_collected','contributor_license_agreement_collected','developer_certificate_origin_claimed','authorship_warranty_claimed'], 'contributor_provenance'),
      (der, ['public_redistribution_permission_claimed','derivative_permission_granted','downstream_compliance_guaranteed','derivative_support_obligation_accepted','compatibility_guaranteed'], 'derivative_redistribution'),
      (cbl, ['legal_advice_claimed','regulatory_compliance_claimed','jurisdictional_review_completed','standards_conformance_claimed','warranty_claimed','indemnity_claimed'], 'compliance_boundary')]
    for obj, keys, label in false_checks:
        for k in keys:
            if obj.get(k) is not False:
                failures.append({label:f'{k} must be false'})

    if lic.get('spdx_expression_declared') not in ('NOASSERTION', None):
        failures.append({'license_reuse':'non-NOASSERTION SPDX expression requires real legal/license review'})
    if not lic.get('license_rows'): failures.append({'license_reuse':'no license rows'})
    for row in lic.get('license_rows', []) or []:
        rid=row.get('license_id')
        if 'LIC4' not in str(row.get('license_state','')): failures.append({'license_id':rid,'not_checked':row.get('license_state')})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'license_id':rid,'missing_evidence_artifact':rel})

    if not atb.get('citation_rows'): failures.append({'attribution_citation':'no citation rows'})
    for row in atb.get('citation_rows', []) or []:
        rid=row.get('citation_id')
        if 'ATB4' not in str(row.get('attribution_state','')): failures.append({'citation_id':rid,'not_checked':row.get('attribution_state')})
        if 'endorse' in str(row.get('recommended_citation','')).lower() and 'do not' not in str(row.get('recommended_citation','')).lower(): failures.append({'citation_id':rid,'unsafe_endorsement_language':True})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'citation_id':rid,'missing_evidence_artifact':rel})

    if not tpc.get('third_party_rows'): failures.append({'third_party_content':'no third-party rows'})
    for row in tpc.get('third_party_rows', []) or []:
        rid=row.get('third_party_id')
        if 'TPC4' not in str(row.get('clearance_state','')): failures.append({'third_party_id':rid,'not_checked':row.get('clearance_state')})
        for rel in row.get('source_artifacts', []) or []:
            if not exists(root, rel): failures.append({'third_party_id':rid,'missing_source_artifact':rel})

    if not cpn.get('contributor_rows'): failures.append({'contributor_provenance':'no contributor rows'})
    for row in cpn.get('contributor_rows', []) or []:
        rid=row.get('contributor_id')
        if row.get('role_ref') not in role_ids: failures.append({'contributor_id':rid,'unknown_role_ref':row.get('role_ref')})
        if 'CPN4' not in str(row.get('provenance_state','')): failures.append({'contributor_id':rid,'not_checked':row.get('provenance_state')})
        assignment=str(row.get('assignment_state','')).lower()
        if ('assignment' in assignment or 'cla' in assignment or 'dco' in assignment or 'warranty' in assignment) and 'no ' not in assignment:
            failures.append({'contributor_id':rid,'unsafe_assignment_state':row.get('assignment_state')})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'contributor_id':rid,'missing_evidence_artifact':rel})

    if not der.get('derivative_rows'): failures.append({'derivative_redistribution':'no derivative rows'})
    for row in der.get('derivative_rows', []) or []:
        rid=row.get('derivative_id')
        if 'DER4' not in str(row.get('redistribution_state','')): failures.append({'derivative_id':rid,'not_checked':row.get('redistribution_state')})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'derivative_id':rid,'missing_evidence_artifact':rel})

    if not cbl.get('compliance_rows'): failures.append({'compliance_boundary':'no compliance rows'})
    for row in cbl.get('compliance_rows', []) or []:
        rid=row.get('boundary_id')
        if 'CBL4' not in str(row.get('boundary_state','')): failures.append({'boundary_id':rid,'not_checked':row.get('boundary_state')})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'boundary_id':rid,'missing_evidence_artifact':rel})

    summary={'license_rows':len(lic.get('license_rows',[]) or []),'citation_rows':len(atb.get('citation_rows',[]) or []),'third_party_rows':len(tpc.get('third_party_rows',[]) or []),'contributor_rows':len(cpn.get('contributor_rows',[]) or []),'derivative_rows':len(der.get('derivative_rows',[]) or []),'compliance_rows':len(cbl.get('compliance_rows',[]) or []),'failures':len(failures)}
    reports={
      'license_reuse_report': {'license_reuse_report_version':f'{version}-license-reuse-report-v1','archive_version':version,'status':'LIC4_license_reuse_checked; LIC5_legal_advice_absent' if not failures else 'LIC7_unsafe_license_claim','summary':summary,'failures':failures},
      'attribution_citation_report': {'attribution_citation_report_version':f'{version}-attribution-citation-report-v1','archive_version':version,'status':'ATB4_attribution_citation_checked; ATB5_no_endorsement_boundary_declared' if not failures else 'ATB7_unsafe_attribution_claim','summary':summary,'failures':failures},
      'third_party_content_report': {'third_party_content_report_version':f'{version}-third-party-content-report-v1','archive_version':version,'status':'TPC4_third_party_content_checked; TPC5_clearance_absent' if not failures else 'TPC7_unsafe_third_party_claim','summary':summary,'failures':failures},
      'contributor_provenance_report': {'contributor_provenance_report_version':f'{version}-contributor-provenance-report-v1','archive_version':version,'status':'CPN4_contributor_provenance_checked; CPN5_assignment_absent' if not failures else 'CPN7_unsafe_contributor_claim','summary':summary,'failures':failures},
      'derivative_redistribution_report': {'derivative_redistribution_report_version':f'{version}-derivative-redistribution-report-v1','archive_version':version,'status':'DER4_derivative_redistribution_checked; DER5_permission_absent' if not failures else 'DER7_unsafe_derivative_claim','summary':summary,'failures':failures},
      'compliance_boundary_report': {'compliance_boundary_report_version':f'{version}-compliance-boundary-report-v1','archive_version':version,'status':'CBL4_compliance_boundary_checked; CBL5_legal_advice_absent' if not failures else 'CBL7_unsafe_compliance_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__':
    raise SystemExit(main())
