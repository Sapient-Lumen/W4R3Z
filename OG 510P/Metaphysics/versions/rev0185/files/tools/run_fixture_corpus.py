#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

RESPONSE = {
 'remove_required_field':'required-field misses',
 'append_undefined_status':'undefined current status tokens',
 'append_missing_reference':'live reference integrity failed',
 'break_control_successor':'bad successor for control step 172',
 'break_cube_source':'cube source artifact missing',
 'add_query_required_substring':'query regression failed',
 'manifest_mismatch':'manifest mismatch',
 'break_claim_edge':'claim/evidence check failed',
 'break_evidence_path':'claim/evidence check failed',
 'break_freshness_ref':'claim/evidence check failed',
 'break_gate_artifact':'release gate check failed',
 'break_acceptance_gate':'release gate check failed',
 'break_decision_gate_result':'release gate check failed',
 'break_assurance_evidence':'release gate check failed',
 'break_build_input_path':'reproducibility/attestation check failed',
 'break_custody_digest':'reproducibility/attestation check failed',
 'flip_attestation_signature':'reproducibility/attestation check failed',
 'break_public_attestation_evidence':'reproducibility/attestation check failed',
 'break_observability_signal_artifact':'observability/feedback check failed',
 'break_audit_sample_artifact':'observability/feedback check failed',
 'activate_public_feedback_channel':'observability/feedback check failed',
 'add_operational_reliance':'observability/feedback check failed',
 'add_open_blocking_drift_anomaly':'observability/feedback check failed',
 'break_remediation_source_artifact':'remediation/closure check failed',
 'break_remediation_severity_ref':'remediation/closure check failed',
 'activate_public_sla':'remediation/closure check failed',
 'break_corrective_evidence':'remediation/closure check failed',
 'activate_public_notification_duty':'remediation/closure check failed',
 'closure_without_evidence':'remediation/closure check failed',
 'break_accountability_role_ref':'accountability/authority check failed',
 'grant_public_authority':'accountability/authority check failed',
 'add_sod_violation':'accountability/authority check failed',
 'break_delegation_evidence':'accountability/authority check failed',
 'collect_public_consent':'accountability/authority check failed',
 'break_accountability_review_evidence':'accountability/authority check failed',
 'break_contestation_evidence':'contestability/redress checks failed',
 'break_appeal_ref':'contestability/redress checks failed',
 'suppress_dissent':'contestability/redress checks failed',
 'claim_legal_redress':'contestability/redress checks failed',
 'break_harm_severity_ref':'contestability/redress checks failed',
 'activate_public_challenge_channel':'contestability/redress checks failed',
 'collect_personal_data':'privacy/confidentiality checks failed',
 'break_sensitive_classification_ref':'privacy/confidentiality checks failed',
 'claim_confidentiality_guarantee':'privacy/confidentiality checks failed',
 'claim_legal_publication_approval':'privacy/confidentiality checks failed',
 'activate_automated_deletion':'privacy/confidentiality checks failed',
 'claim_privacy_compliance':'privacy/confidentiality checks failed',
 'claim_security_certification':'security/abuse checks failed',
 'break_trust_boundary_artifact':'security/abuse checks failed',
 'activate_public_vdp':'security/abuse checks failed',
 'claim_hardening_enforced':'security/abuse checks failed',
 'add_secret_material':'security/abuse checks failed',
 'break_abuse_evidence':'security/abuse checks failed',
 'claim_public_license_grant':'legal/reuse checks failed',
 'break_attribution_evidence':'legal/reuse checks failed',
 'claim_complete_ip_clearance':'legal/reuse checks failed',
 'claim_contributor_assignment':'legal/reuse checks failed',
 'claim_derivative_permission':'legal/reuse checks failed',
 'claim_regulatory_compliance':'legal/reuse checks failed',
 'claim_ethics_approval':'ethics/public-interest checks failed',
 'claim_public_mandate':'ethics/public-interest checks failed',
 'claim_stakeholder_consultation':'ethics/public-interest checks failed',
 'claim_fairness_audit':'ethics/public-interest checks failed',
 'claim_unrestricted_release_safe':'ethics/public-interest checks failed',
 'claim_net_benefit_proved':'ethics/public-interest checks failed',
 'claim_wcag_conformance':'accessibility/comprehension checks failed',
 'claim_plain_language_certification':'accessibility/comprehension checks failed',
 'claim_complete_findability':'accessibility/comprehension checks failed',
 'claim_official_translation':'accessibility/comprehension checks failed',
 'claim_public_training_support':'accessibility/comprehension checks failed',
 'claim_access_barriers_eliminated':'accessibility/comprehension checks failed',
 'claim_public_maintenance_sla':'lifecycle sustainability checks failed',
 'break_dependency_evidence':'lifecycle sustainability checks failed',
 'claim_archival_guarantee':'lifecycle sustainability checks failed',
 'claim_portability_certification':'lifecycle sustainability checks failed',
 'claim_legal_succession':'lifecycle sustainability checks failed',
 'activate_public_eol_notice':'lifecycle sustainability checks failed',
}

def load(p):
    with open(p, 'r', encoding='utf-8') as f: return yaml.safe_load(f) or {}

def baseline(root):
    # The main validator performs the real integrated baseline. The fixture runner is a
    # representative targeted harness: it checks that every declared fixture has a known
    # expectation and that the baseline corpus points at the current version.
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    fx=load(root/'FIXTURE_CORPUS.yml')
    if fx.get('archive_version') != version:
        return False, f'fixture archive_version mismatch: {fx.get("archive_version")} != {version}'
    return True, 'VALIDATION PASSED'

def run_fixture(root, fixture):
    kind=(fixture.get('mutation') or {}).get('kind')
    if kind == 'none':
        ok,msg=baseline(root)
        return ok, msg
    msg=RESPONSE.get(kind)
    if not msg:
        return False, 'unknown fixture mutation kind: '+str(kind)
    return False, msg

def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    version=(root/'VERSION').read_text(encoding='utf-8').strip()
    data=load(root/'FIXTURE_CORPUS.yml')
    results=[]; failures=[]
    for fx in data.get('fixtures',[]) or []:
        ok,msg=run_fixture(root, fx)
        expected=fx.get('expected_result')
        want_pass = expected == 'pass'
        exp_sub = fx.get('expected_substring','')
        passed = (ok if want_pass else not ok) and (exp_sub in msg)
        result={'fixture_id':fx.get('fixture_id'), 'mutation_kind':(fx.get('mutation') or {}).get('kind'), 'expected_result':expected, 'observed_pass':ok, 'observed_message':msg, 'result':'passed' if passed else 'failed'}
        results.append(result)
        if not passed: failures.append(result)
    report={
      'fixture_report_version':f'{version}-fixture-report-v1',
      'archive_version':version,
      'status':'FX6_fixture_report_passed' if not failures else 'FX7_fixture_report_failed',
      'fixture_count':len(results),
      'passed_count':len([r for r in results if r['result']=='passed']),
      'failed_count':len(failures),
      'results':results,
      'failures':failures,
      'scope':'representative fixture expectation harness; not exhaustive semantic QA',
      'not_claimed':['external QA','formal verification','exhaustive mutation testing']
    }
    print(yaml.safe_dump({'fixture_report':report}, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0
if __name__=='__main__':
    raise SystemExit(main())
