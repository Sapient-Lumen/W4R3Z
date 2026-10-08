#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def exists(root, rel): return bool(rel) and (root/rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root/'VERSION').read_text(encoding='utf-8').strip()
    eia = load(root/'ETHICAL_IMPACT_ASSESSMENT.yml')
    pib = load(root/'PUBLIC_INTEREST_BALANCING_LEDGER.yml')
    apa = load(root/'AFFECTED_PARTY_ANALYSIS.yml')
    fbr = load(root/'FAIRNESS_BIAS_REVIEW_LEDGER.yml')
    msr = load(root/'MISUSE_SENSITIVE_RELEASE_POLICY.yml')
    bhr = load(root/'BENEFIT_HARM_REGISTER.yml')
    abuse = load(root/'ABUSE_MISUSE_CASE_REGISTER.yml')
    failures=[]
    false_checks = [
      (eia, ['institutional_ethics_board_approval_claimed','human_subjects_research_determination_claimed','ethics_certification_claimed','social_license_claimed'], 'ethical_impact'),
      (pib, ['public_authority_claimed','democratic_mandate_claimed','public_interest_override_claimed','policy_approval_claimed'], 'public_interest'),
      (apa, ['stakeholder_consultation_completed','public_participation_claimed','affected_party_consent_collected','representative_body_claimed'], 'affected_party'),
      (fbr, ['fairness_audit_completed','bias_free_claimed','anti_discrimination_certification_claimed','demographic_testing_completed'], 'fairness_bias'),
      (msr, ['unrestricted_release_claimed','dual_use_review_certified','red_team_completed','misuse_impossible_claimed'], 'misuse_sensitive_release'),
      (bhr, ['net_benefit_proven','harm_eliminated','safety_certification_claimed','public_good_guaranteed'], 'benefit_harm'),
    ]
    for obj, keys, surface in false_checks:
        for k in keys:
            if obj.get(k) is not False:
                failures.append({surface:f'{k} must be false'})
    apa_ids={r.get('affected_party_id') for r in apa.get('affected_party_rows',[]) or []}
    bhr_ids={r.get('benefit_harm_id') for r in bhr.get('benefit_harm_rows',[]) or []}
    eia_ids={r.get('impact_id') for r in eia.get('impact_rows',[]) or []}
    abuse_ids={r.get('abuse_case_id') for r in abuse.get('abuse_cases',[]) or []}
    if not apa_ids: failures.append({'affected_party':'no affected-party rows'})
    if not bhr_ids: failures.append({'benefit_harm':'no benefit/harm rows'})
    if not eia_ids: failures.append({'ethical_impact':'no impact rows'})
    for row in eia.get('impact_rows',[]) or []:
        rid=row.get('impact_id')
        if 'EIA4' not in str(row.get('status','')): failures.append({'impact_id':rid,'not_checked':row.get('status')})
        for ref in row.get('affected_party_refs',[]) or []:
            if ref not in apa_ids: failures.append({'impact_id':rid,'unknown_affected_party_ref':ref})
        for ref in row.get('benefit_harm_refs',[]) or []:
            if ref not in bhr_ids: failures.append({'impact_id':rid,'unknown_benefit_harm_ref':ref})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'impact_id':rid,'missing_evidence_artifact':rel})
    for row in pib.get('balancing_rows',[]) or []:
        rid=row.get('balancing_id')
        if 'PIB4' not in str(row.get('status','')): failures.append({'balancing_id':rid,'not_checked':row.get('status')})
        for ref in row.get('impact_refs',[]) or []:
            if ref not in eia_ids: failures.append({'balancing_id':rid,'unknown_impact_ref':ref})
        for ref in row.get('benefit_harm_refs',[]) or []:
            if ref not in bhr_ids: failures.append({'balancing_id':rid,'unknown_benefit_harm_ref':ref})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'balancing_id':rid,'missing_evidence_artifact':rel})
    for row in apa.get('affected_party_rows',[]) or []:
        rid=row.get('affected_party_id')
        if 'APA4' not in str(row.get('status','')): failures.append({'affected_party_id':rid,'not_checked':row.get('status')})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'affected_party_id':rid,'missing_evidence_artifact':rel})
    for row in fbr.get('fairness_review_rows',[]) or []:
        rid=row.get('fairness_review_id')
        if 'FBR4' not in str(row.get('status','')): failures.append({'fairness_review_id':rid,'not_checked':row.get('status')})
        for ref in row.get('affected_party_refs',[]) or []:
            if ref not in apa_ids: failures.append({'fairness_review_id':rid,'unknown_affected_party_ref':ref})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'fairness_review_id':rid,'missing_evidence_artifact':rel})
    for row in msr.get('release_boundary_rows',[]) or []:
        rid=row.get('release_boundary_id')
        if 'MSR4' not in str(row.get('status','')): failures.append({'release_boundary_id':rid,'not_checked':row.get('status')})
        for ref in row.get('abuse_case_refs',[]) or []:
            if ref not in abuse_ids: failures.append({'release_boundary_id':rid,'unknown_abuse_case_ref':ref})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'release_boundary_id':rid,'missing_evidence_artifact':rel})
    for row in bhr.get('benefit_harm_rows',[]) or []:
        rid=row.get('benefit_harm_id')
        if 'BHR4' not in str(row.get('status','')): failures.append({'benefit_harm_id':rid,'not_checked':row.get('status')})
        for rel in row.get('evidence_artifacts',[]) or []:
            if not exists(root, rel): failures.append({'benefit_harm_id':rid,'missing_evidence_artifact':rel})
    summary={'impact_rows':len(eia.get('impact_rows',[]) or []),'balancing_rows':len(pib.get('balancing_rows',[]) or []),'affected_party_rows':len(apa.get('affected_party_rows',[]) or []),'fairness_review_rows':len(fbr.get('fairness_review_rows',[]) or []),'release_boundary_rows':len(msr.get('release_boundary_rows',[]) or []),'benefit_harm_rows':len(bhr.get('benefit_harm_rows',[]) or []),'failures':len(failures)}
    reports={
      'ethical_impact_report': {'ethical_impact_report_version':f'{version}-ethical-impact-report-v1','archive_version':version,'status':'EIA4_ethical_impact_checked; EIA5_ethics_approval_absent' if not failures else 'EIA7_unsafe_ethics_claim','summary':summary,'failures':failures},
      'public_interest_balancing_report': {'public_interest_balancing_report_version':f'{version}-public-interest-balancing-report-v1','archive_version':version,'status':'PIB4_public_interest_boundary_checked; PIB5_public_authority_absent' if not failures else 'PIB7_unsafe_public_interest_claim','summary':summary,'failures':failures},
      'affected_party_analysis_report': {'affected_party_analysis_report_version':f'{version}-affected-party-analysis-report-v1','archive_version':version,'status':'APA4_affected_party_boundary_checked; APA5_consultation_absent' if not failures else 'APA7_unsafe_affected_party_claim','summary':summary,'failures':failures},
      'fairness_bias_review_report': {'fairness_bias_review_report_version':f'{version}-fairness-bias-review-report-v1','archive_version':version,'status':'FBR4_fairness_bias_boundary_checked; FBR5_audit_absent' if not failures else 'FBR7_unsafe_fairness_claim','summary':summary,'failures':failures},
      'misuse_sensitive_release_report': {'misuse_sensitive_release_report_version':f'{version}-misuse-sensitive-release-report-v1','archive_version':version,'status':'MSR4_misuse_release_boundary_checked; MSR5_unrestricted_release_not_cleared' if not failures else 'MSR7_unsafe_misuse_release_claim','summary':summary,'failures':failures},
      'benefit_harm_report': {'benefit_harm_report_version':f'{version}-benefit-harm-report-v1','archive_version':version,'status':'BHR4_benefit_harm_boundary_checked; BHR5_net_benefit_not_proved' if not failures else 'BHR7_unsafe_benefit_harm_claim','summary':summary,'failures':failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__ == '__main__':
    raise SystemExit(main())
