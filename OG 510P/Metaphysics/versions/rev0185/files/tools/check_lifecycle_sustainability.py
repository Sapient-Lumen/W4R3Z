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
    mtn = load(root/'MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml')
    dup = load(root/'DEPENDENCY_UPDATE_POLICY.yml')
    prs = load(root/'PRESERVATION_ARCHIVAL_PLAN.yml')
    por = load(root/'PORTABILITY_INTEROPERABILITY_MATRIX.yml')
    suc = load(root/'SUCCESSION_CONTINUITY_PLAN.yml')
    eol = load(root/'SUNSET_END_OF_LIFE_LEDGER.yml')
    roles = load(root/'ROLE_AUTHORITY_MATRIX.yml')
    role_ids = {r.get('role_id') for r in roles.get('roles', []) or []}
    failures=[]

    if mtn.get('public_maintenance_commitment_claimed') is not False: failures.append({'maintainership':'public_maintenance_commitment_claimed must be false'})
    if mtn.get('support_sla_claimed') is not False: failures.append({'maintainership':'support_sla_claimed must be false'})
    if mtn.get('external_maintainer_claimed') is not False: failures.append({'maintainership':'external_maintainer_claimed must be false'})
    if dup.get('automated_dependency_scanning_active') is not False: failures.append({'dependency_update':'automated_dependency_scanning_active must be false'})
    if dup.get('external_update_service_active') is not False: failures.append({'dependency_update':'external_update_service_active must be false'})
    if dup.get('vulnerability_monitoring_claimed') is not False: failures.append({'dependency_update':'vulnerability_monitoring_claimed must be false'})
    if prs.get('archival_guarantee_claimed') is not False: failures.append({'preservation':'archival_guarantee_claimed must be false'})
    if prs.get('public_repository_claimed') is not False: failures.append({'preservation':'public_repository_claimed must be false'})
    if prs.get('long_term_hosting_claimed') is not False: failures.append({'preservation':'long_term_hosting_claimed must be false'})
    if por.get('portability_certification_claimed') is not False: failures.append({'portability':'portability_certification_claimed must be false'})
    if por.get('interoperability_profile_claimed') is not False: failures.append({'portability':'interoperability_profile_claimed must be false'})
    if por.get('migration_service_claimed') is not False: failures.append({'portability':'migration_service_claimed must be false'})
    if suc.get('legal_successor_designated') is not False: failures.append({'succession':'legal_successor_designated must be false'})
    if suc.get('succession_authority_claimed') is not False: failures.append({'succession':'succession_authority_claimed must be false'})
    if suc.get('business_continuity_certification_claimed') is not False: failures.append({'succession':'business_continuity_certification_claimed must be false'})
    if eol.get('public_eol_notice_service_active') is not False: failures.append({'sunset_eol':'public_eol_notice_service_active must be false'})
    if eol.get('decommission_authority_claimed') is not False: failures.append({'sunset_eol':'decommission_authority_claimed must be false'})
    if eol.get('downstream_migration_guaranteed') is not False: failures.append({'sunset_eol':'downstream_migration_guaranteed must be false'})

    for row in mtn.get('maintainership_rows', []) or []:
        rid=row.get('maintainership_id')
        if row.get('role_ref') not in role_ids: failures.append({'maintainership_id':rid,'unknown_role_ref':row.get('role_ref')})
        if 'MTN4' not in str(row.get('status','')): failures.append({'maintainership_id':rid,'not_checked':row.get('status')})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'maintainership_id':rid,'missing_evidence_artifact':rel})
    if not mtn.get('maintainership_rows'): failures.append({'maintainership':'no maintainership rows'})

    for row in dup.get('dependency_rows', []) or []:
        rid=row.get('dependency_id')
        if 'DUP4' not in str(row.get('status','')): failures.append({'dependency_id':rid,'not_checked':row.get('status')})
        if not row.get('update_trigger'): failures.append({'dependency_id':rid,'missing_update_trigger':True})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'dependency_id':rid,'missing_evidence_artifact':rel})
    if not dup.get('dependency_rows'): failures.append({'dependency_update':'no dependency rows'})

    for row in prs.get('preservation_targets', []) or []:
        rid=row.get('preservation_id')
        if 'PRS4' not in str(row.get('status','')): failures.append({'preservation_id':rid,'not_checked':row.get('status')})
        for rel in (row.get('artifacts') or []) + (row.get('evidence_artifacts') or []):
            if not exists(root, rel): failures.append({'preservation_id':rid,'missing_artifact':rel})
    if not prs.get('preservation_targets'): failures.append({'preservation':'no preservation targets'})

    for row in por.get('export_surfaces', []) or []:
        rid=row.get('surface_id')
        if 'POR4' not in str(row.get('status','')): failures.append({'surface_id':rid,'not_checked':row.get('status')})
        if not row.get('consumer_boundary'): failures.append({'surface_id':rid,'missing_consumer_boundary':True})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'surface_id':rid,'missing_evidence_artifact':rel})
    if not por.get('export_surfaces'): failures.append({'portability':'no export surfaces'})

    for row in suc.get('continuity_rows', []) or []:
        rid=row.get('continuity_id')
        for key in ['from_role','to_role']:
            if row.get(key) not in role_ids: failures.append({'continuity_id':rid,'unknown_'+key:row.get(key)})
        if 'SUC4' not in str(row.get('status','')): failures.append({'continuity_id':rid,'not_checked':row.get('status')})
        for rel in row.get('handoff_artifacts', []) or []:
            if not exists(root, rel): failures.append({'continuity_id':rid,'missing_handoff_artifact':rel})
    if not suc.get('continuity_rows'): failures.append({'succession':'no continuity rows'})

    for row in eol.get('sunset_rows', []) or []:
        rid=row.get('sunset_id')
        if 'EOL4' not in str(row.get('status','')): failures.append({'sunset_id':rid,'not_checked':row.get('status')})
        if not row.get('trigger') or not row.get('action'): failures.append({'sunset_id':rid,'missing_trigger_or_action':True})
        for rel in row.get('evidence_artifacts', []) or []:
            if not exists(root, rel): failures.append({'sunset_id':rid,'missing_evidence_artifact':rel})
    if not eol.get('sunset_rows'): failures.append({'sunset_eol':'no sunset rows'})

    summary={'maintainership_rows':len(mtn.get('maintainership_rows',[]) or []),'dependency_rows':len(dup.get('dependency_rows',[]) or []),'preservation_targets':len(prs.get('preservation_targets',[]) or []),'export_surfaces':len(por.get('export_surfaces',[]) or []),'continuity_rows':len(suc.get('continuity_rows',[]) or []),'sunset_rows':len(eol.get('sunset_rows',[]) or []),'failures':len(failures)}
    reports={
      'maintainership_stewardship_report': {'maintainership_stewardship_report_version':f'{version}-maintainership-stewardship-report-v1','archive_version':version,'status':'MTN4_maintainership_checked; MTN5_public_support_absent' if not failures else 'MTN7_unsafe_maintainership_claim','summary':summary,'failures':failures},
      'dependency_update_report': {'dependency_update_report_version':f'{version}-dependency-update-report-v1','archive_version':version,'status':'DUP4_dependency_update_checked; DUP5_automated_scanning_absent' if not failures else 'DUP7_unsafe_dependency_update_claim','summary':summary,'failures':failures},
      'preservation_archival_report': {'preservation_archival_report_version':f'{version}-preservation-archival-report-v1','archive_version':version,'status':'PRS4_preservation_checked; PRS5_archival_guarantee_absent' if not failures else 'PRS7_unsafe_preservation_claim','summary':summary,'failures':failures},
      'portability_interoperability_report': {'portability_interoperability_report_version':f'{version}-portability-interoperability-report-v1','archive_version':version,'status':'POR4_portability_checked; POR5_certification_absent' if not failures else 'POR7_unsafe_portability_claim','summary':summary,'failures':failures},
      'succession_continuity_report': {'succession_continuity_report_version':f'{version}-succession-continuity-report-v1','archive_version':version,'status':'SUC4_succession_checked; SUC5_legal_successor_absent' if not failures else 'SUC7_unsafe_succession_claim','summary':summary,'failures':failures},
      'sunset_eol_report': {'sunset_eol_report_version':f'{version}-sunset-eol-report-v1','archive_version':version,'status':'EOL4_sunset_eol_checked; EOL5_public_eol_service_absent' if not failures else 'EOL7_unsafe_sunset_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__':
    raise SystemExit(main())
