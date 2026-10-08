#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys
import yaml

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()

def exists(root, rel):
    return (root / rel).exists()

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    build = load(root / 'BUILD_REPRODUCIBILITY_LEDGER.yml')
    att = load(root / 'ATTESTATION_BOUNDARY_LEDGER.yml')
    custody = load(root / 'EVIDENCE_CHAIN_CUSTODY.yml')
    exe = load(root / 'EXECUTION_LOG_LEDGER.yml')
    rollback = load(root / 'ROLLBACK_RETRACTION_PLAN.yml')
    pub = load(root / 'PUBLIC_RELEASE_ATTESTATION.yml')
    failures = []

    for b in build.get('builds', []) or []:
        for rel in (b.get('input_artifacts') or []) + (b.get('generated_artifacts') or []):
            if not exists(root, rel):
                failures.append({'build_id': b.get('build_id'), 'missing_build_artifact': rel})
        if 'independent' in str(b.get('rebuild_status', '')).lower():
            failures.append({'build_id': b.get('build_id'), 'unsafe_rebuild_status': b.get('rebuild_status')})
    if not build.get('builds'):
        failures.append({'build_ledger': 'no build rows'})

    if att.get('cryptographic_signature_present') is not False:
        failures.append({'attestation_boundary': 'cryptographic_signature_present must be false for rev0170'})
    if att.get('transparency_log_present') is not False:
        failures.append({'attestation_boundary': 'transparency_log_present must be false for rev0170'})
    for a in att.get('attestations', []) or []:
        if not exists(root, a.get('predicate_artifact', '')):
            failures.append({'attestation_id': a.get('attestation_id'), 'missing_predicate': a.get('predicate_artifact')})
        if 'signature_absence' not in str(a.get('signature_state', '')):
            failures.append({'attestation_id': a.get('attestation_id'), 'signature_boundary_not_explicit': a.get('signature_state')})
        for rel in a.get('evidence_refs', []) or []:
            if not exists(root, rel):
                failures.append({'attestation_id': a.get('attestation_id'), 'missing_evidence_ref': rel})

    for item in custody.get('evidence_items', []) or []:
        rel = item.get('artifact')
        if not rel or not exists(root, rel):
            failures.append({'custody_item': item.get('evidence_id'), 'missing_artifact': rel})
            continue
        expected = item.get('sha256')
        if expected and digest(root / rel) != expected:
            failures.append({'custody_item': item.get('evidence_id'), 'digest_mismatch': rel})
    if not custody.get('evidence_items'):
        failures.append({'custody_ledger': 'no evidence items'})

    for step in exe.get('execution_steps', []) or []:
        tool = step.get('tool')
        report = step.get('report')
        if tool and not exists(root, tool):
            failures.append({'execution_step': step.get('step_id'), 'missing_tool': tool})
        if report and report.endswith('.yml') and not exists(root, report):
            failures.append({'execution_step': step.get('step_id'), 'missing_report': report})
    if not exe.get('execution_steps'):
        failures.append({'execution_log': 'no execution steps'})

    if not rollback.get('triggers') or not rollback.get('retraction_targets'):
        failures.append({'rollback_plan': 'missing triggers or retraction targets'})
    for rel in rollback.get('retraction_targets', []) or []:
        if not exists(root, rel):
            failures.append({'rollback_plan': 'missing retraction target', 'target': rel})

    for rel in pub.get('evidence_refs', []) or []:
        if not exists(root, rel):
            failures.append({'public_attestation': 'missing evidence ref', 'ref': rel})
    neg = ' '.join(str(x).lower() for x in pub.get('negative_assertions', []) or [])
    if 'no signed attestation' not in neg:
        failures.append({'public_attestation': 'missing explicit no signed attestation assertion'})
    if 'signature_absence' not in str(pub.get('signature_state', '')):
        failures.append({'public_attestation': 'signature boundary not explicit'})

    summary = {
        'build_rows': len(build.get('builds', []) or []),
        'attestations': len(att.get('attestations', []) or []),
        'custody_items': len(custody.get('evidence_items', []) or []),
        'execution_steps': len(exe.get('execution_steps', []) or []),
        'rollback_triggers': len(rollback.get('triggers', []) or []),
        'public_evidence_refs': len(pub.get('evidence_refs', []) or []),
        'failures': len(failures),
    }
    reports = {
      'build_reproducibility_report': {'build_reproducibility_report_version': f'{version}-build-reproducibility-report-v1', 'archive_version': version, 'status': 'BLD4_local_rebuild_recipe_checked; BLD5_determinism_boundary_declared' if not failures else 'BLD7_unsafe_reproducibility_claim', 'summary': summary, 'failures': failures},
      'attestation_boundary_report': {'attestation_boundary_report_version': f'{version}-attestation-boundary-report-v1', 'archive_version': version, 'status': 'ATT4_signature_absence_explicit' if not failures else 'ATT7_unsafe_attestation_claim', 'summary': summary, 'failures': failures},
      'evidence_custody_report': {'evidence_custody_report_version': f'{version}-evidence-custody-report-v1', 'archive_version': version, 'status': 'CUS4_evidence_chain_custody_checked' if not failures else 'CUS7_unsafe_custody_claim', 'summary': summary, 'failures': failures},
      'execution_log_report': {'execution_log_report_version': f'{version}-execution-log-report-v1', 'archive_version': version, 'status': 'EXE4_execution_log_checked' if not failures else 'EXE7_unsafe_execution_log_claim', 'summary': summary, 'failures': failures},
      'rollback_retraction_report': {'rollback_retraction_report_version': f'{version}-rollback-retraction-report-v1', 'archive_version': version, 'status': 'ROL4_rollback_retraction_plan_checked' if not failures else 'ROL7_unsafe_rollback_claim', 'summary': summary, 'failures': failures},
      'public_release_attestation_report': {'public_release_attestation_report_version': f'{version}-public-release-attestation-report-v1', 'archive_version': version, 'status': 'PAT4_public_release_attestation_packet_checked' if not failures else 'PAT7_unsafe_public_attestation_claim', 'summary': summary, 'failures': failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
