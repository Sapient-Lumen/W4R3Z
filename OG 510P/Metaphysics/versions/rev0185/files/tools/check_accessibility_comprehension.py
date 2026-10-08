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
    version = (root/'VERSION').read_text(encoding='utf-8').strip()
    acy = load(root/'ACCESSIBILITY_REVIEW_PLAN.yml')
    rpl = load(root/'READABILITY_PLAIN_LANGUAGE_LEDGER.yml')
    dnm = load(root/'DISCOVERABILITY_NAVIGATION_MAP.yml')
    ltb = load(root/'LOCALIZATION_TRANSLATION_BOUNDARY.yml')
    ugo = load(root/'USER_GUIDANCE_ONBOARDING_LEDGER.yml')
    iar = load(root/'INCLUSIVE_ACCESS_RISK_REGISTER.yml')
    apa = load(root/'AFFECTED_PARTY_ANALYSIS.yml')
    failures=[]
    false_checks = [
      (acy, ['wcag_conformance_claimed','accessibility_certification_claimed','assistive_technology_testing_completed','legal_accessibility_compliance_claimed'], 'accessibility'),
      (rpl, ['plain_language_certification_claimed','comprehension_testing_completed','controlled_language_conformance_claimed','legal_plain_language_compliance_claimed'], 'readability_plain_language'),
      (dnm, ['information_architecture_certification_claimed','user_testing_completed','search_index_service_claimed','complete_findability_claimed'], 'discoverability_navigation'),
      (ltb, ['official_translation_claimed','localization_completed','multilingual_support_claimed','i18n_conformance_claimed'], 'localization_translation'),
      (ugo, ['training_program_claimed','public_support_claimed','complete_user_documentation_claimed','tutorial_completeness_claimed'], 'user_guidance'),
      (iar, ['equitable_access_proven','access_barrier_eliminated','accessibility_impact_assessment_completed','public_accommodation_claimed'], 'inclusive_access'),
    ]
    for obj, keys, surface in false_checks:
        for k in keys:
            if obj.get(k) is not False:
                failures.append({surface:f'{k} must be false'})
    guidance_ids={r.get('guidance_id') for r in ugo.get('guidance_rows',[]) or []}
    risk_ids={r.get('access_risk_id') for r in iar.get('access_risk_rows',[]) or []}
    affected_ids={r.get('affected_party_id') for r in apa.get('affected_party_rows',[]) or []}
    def check_artifacts(rows, id_key, status_token, surface):
        if not rows: failures.append({surface:'no rows'})
        for row in rows or []:
            rid=row.get(id_key)
            if status_token not in str(row.get('status','')):
                failures.append({id_key:rid,'not_checked':row.get('status')})
            for rel in row.get('evidence_artifacts',[]) or row.get('mitigation_artifacts',[]) or []:
                if not exists(root, rel): failures.append({id_key:rid,'missing_evidence_artifact':rel})
    check_artifacts(acy.get('accessibility_rows',[]),'accessibility_review_id','ACY4','accessibility')
    for row in acy.get('accessibility_rows',[]) or []:
        rid=row.get('accessibility_review_id')
        for ref in row.get('guidance_refs',[]) or []:
            if ref not in guidance_ids: failures.append({'accessibility_review_id':rid,'unknown_guidance_ref':ref})
        for ref in row.get('risk_refs',[]) or []:
            if ref not in risk_ids: failures.append({'accessibility_review_id':rid,'unknown_access_risk_ref':ref})
    check_artifacts(rpl.get('readability_rows',[]),'readability_id','RPL4','readability')
    check_artifacts(dnm.get('navigation_rows',[]),'navigation_id','DNM4','discoverability')
    for row in dnm.get('navigation_rows',[]) or []:
        rid=row.get('navigation_id')
        for rel in row.get('routes_to',[]) or []:
            if not exists(root, rel): failures.append({'navigation_id':rid,'missing_route_target':rel})
    check_artifacts(ltb.get('translation_boundary_rows',[]),'translation_boundary_id','LTB4','localization')
    check_artifacts(ugo.get('guidance_rows',[]),'guidance_id','UGO4','guidance')
    check_artifacts(iar.get('access_risk_rows',[]),'access_risk_id','IAR4','inclusive_access')
    for row in iar.get('access_risk_rows',[]) or []:
        rid=row.get('access_risk_id')
        for ref in row.get('affected_party_refs',[]) or []:
            if ref not in affected_ids: failures.append({'access_risk_id':rid,'unknown_affected_party_ref':ref})
    summary={'accessibility_rows':len(acy.get('accessibility_rows',[]) or []),'readability_rows':len(rpl.get('readability_rows',[]) or []),'navigation_rows':len(dnm.get('navigation_rows',[]) or []),'translation_boundary_rows':len(ltb.get('translation_boundary_rows',[]) or []),'guidance_rows':len(ugo.get('guidance_rows',[]) or []),'access_risk_rows':len(iar.get('access_risk_rows',[]) or []),'failures':len(failures)}
    reports={
      'accessibility_review_report': {'accessibility_review_report_version':f'{version}-accessibility-review-report-v1','archive_version':version,'status':'ACY4_accessibility_boundary_checked; ACY5_accessibility_certification_absent' if not failures else 'ACY7_unsafe_accessibility_claim','summary':summary,'failures':failures},
      'readability_plain_language_report': {'readability_plain_language_report_version':f'{version}-readability-plain-language-report-v1','archive_version':version,'status':'RPL4_plain_language_boundary_checked; RPL5_comprehension_testing_absent' if not failures else 'RPL7_unsafe_plain_language_claim','summary':summary,'failures':failures},
      'discoverability_navigation_report': {'discoverability_navigation_report_version':f'{version}-discoverability-navigation-report-v1','archive_version':version,'status':'DNM4_discoverability_boundary_checked; DNM5_public_discovery_absent' if not failures else 'DNM7_unsafe_discoverability_claim','summary':summary,'failures':failures},
      'localization_translation_report': {'localization_translation_report_version':f'{version}-localization-translation-report-v1','archive_version':version,'status':'LTB4_localization_boundary_checked; LTB5_official_translation_absent' if not failures else 'LTB7_unsafe_localization_claim','summary':summary,'failures':failures},
      'user_guidance_onboarding_report': {'user_guidance_onboarding_report_version':f'{version}-user-guidance-onboarding-report-v1','archive_version':version,'status':'UGO4_guidance_boundary_checked; UGO5_public_support_absent' if not failures else 'UGO7_unsafe_guidance_claim','summary':summary,'failures':failures},
      'inclusive_access_risk_report': {'inclusive_access_risk_report_version':f'{version}-inclusive-access-risk-report-v1','archive_version':version,'status':'IAR4_inclusive_access_boundary_checked; IAR5_equitable_access_not_proved' if not failures else 'IAR7_unsafe_inclusive_access_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__':
    raise SystemExit(main())
