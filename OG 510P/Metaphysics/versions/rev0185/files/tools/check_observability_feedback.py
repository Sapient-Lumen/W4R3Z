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
    obs = load(root / 'OBSERVABILITY_MONITORING_PLAN.yml')
    aud = load(root / 'AUDIT_SAMPLING_PLAN.yml')
    fdb = load(root / 'FEEDBACK_INTAKE_LEDGER.yml')
    rel = load(root / 'DOWNSTREAM_RELIANCE_LEDGER.yml')
    drf = load(root / 'DRIFT_ANOMALY_LEDGER.yml')
    drl = load(root / 'EXERCISE_INCIDENT_DRILL_LEDGER.yml')
    failures = []

    signals = obs.get('signals', []) or []
    if not signals:
        failures.append({'observability': 'no signals'})
    if obs.get('public_monitoring_active') is not False:
        failures.append({'observability': 'public_monitoring_active must be false for local package'})
    for s in signals:
        sid = s.get('signal_id')
        for a in s.get('source_artifacts', []) or []:
            if not exists(root, a): failures.append({'signal_id': sid, 'missing_source_artifact': a})
        if 'OBS4' not in str(s.get('status', '')):
            failures.append({'signal_id': sid, 'signal_not_checked': s.get('status')})

    samples = aud.get('samples', []) or []
    if not samples:
        failures.append({'audit': 'no samples'})
    for s in samples:
        sid = s.get('sample_id')
        for a in s.get('target_artifacts', []) or []:
            if not exists(root, a): failures.append({'sample_id': sid, 'missing_target_artifact': a})
        if 'AUD4' not in str(s.get('result_status', '')):
            failures.append({'sample_id': sid, 'sample_not_checked': s.get('result_status')})

    if fdb.get('public_feedback_channel_active') is not False:
        failures.append({'feedback': 'public_feedback_channel_active must be false unless new public duty gate is added'})
    if fdb.get('response_sla_present') is not False:
        failures.append({'feedback': 'response_sla_present must be false for rev0171'})
    for ch in fdb.get('channels', []) or []:
        if ch.get('public_channel') is True:
            failures.append({'channel_id': ch.get('channel_id'), 'public_channel_active': True})
    for item in fdb.get('feedback_items', []) or []:
        for a in item.get('related_artifacts', []) or []:
            if not exists(root, a): failures.append({'feedback_id': item.get('feedback_id'), 'missing_related_artifact': a})

    if int(rel.get('known_operational_uses_count', 0) or 0) != 0:
        failures.append({'reliance': 'known_operational_uses_count must be zero for local release'})
    for row in rel.get('reliance_rows', []) or []:
        for a in row.get('evidence_artifacts', []) or []:
            if not exists(root, a): failures.append({'reliance_id': row.get('reliance_id'), 'missing_evidence_artifact': a})
        if row.get('known_external_party') is True and not row.get('boundary'):
            failures.append({'reliance_id': row.get('reliance_id'), 'external_reliance_without_boundary': True})

    if drf.get('continuous_monitoring_active') is not False:
        failures.append({'drift': 'continuous_monitoring_active must be false for rev0171'})
    for chk in drf.get('checks', []) or []:
        for a in chk.get('target_artifacts', []) or []:
            if not exists(root, a): failures.append({'check_id': chk.get('check_id'), 'missing_target_artifact': a})
        if 'DRF4' not in str(chk.get('status', '')):
            failures.append({'check_id': chk.get('check_id'), 'check_not_passed': chk.get('status')})
    for anom in drf.get('anomalies', []) or []:
        if anom.get('blocking') is True and 'closed' not in str(anom.get('disposition', '')).lower():
            failures.append({'anomaly_id': anom.get('anomaly_id'), 'open_blocking_anomaly': True})

    drills = drl.get('drills', []) or []
    if not drills:
        failures.append({'drills': 'no drill rows'})
    for d in drills:
        did = d.get('drill_id')
        for a in (d.get('runbook_refs', []) or []) + (d.get('evidence_artifacts', []) or []):
            if not exists(root, a): failures.append({'drill_id': did, 'missing_artifact': a})
        if 'DRL4' not in str(d.get('status', '')):
            failures.append({'drill_id': did, 'drill_not_checked': d.get('status')})

    summary = {
        'signals': len(signals), 'samples': len(samples), 'channels': len(fdb.get('channels', []) or []),
        'feedback_items': len(fdb.get('feedback_items', []) or []), 'reliance_rows': len(rel.get('reliance_rows', []) or []),
        'drift_checks': len(drf.get('checks', []) or []), 'anomalies': len(drf.get('anomalies', []) or []),
        'drills': len(drills), 'failures': len(failures)
    }
    reports = {
      'observability_report': {'observability_report_version': f'{version}-observability-report-v1', 'archive_version': version, 'status': 'OBS4_observability_boundary_checked' if not failures else 'OBS7_unsafe_observability_claim', 'summary': summary, 'failures': failures},
      'audit_sampling_report': {'audit_sampling_report_version': f'{version}-audit-sampling-report-v1', 'archive_version': version, 'status': 'AUD4_audit_samples_checked' if not failures else 'AUD7_unsafe_audit_claim', 'summary': summary, 'failures': failures},
      'feedback_intake_report': {'feedback_intake_report_version': f'{version}-feedback-intake-report-v1', 'archive_version': version, 'status': 'FDB4_feedback_intake_checked' if not failures else 'FDB7_unsafe_feedback_claim', 'summary': summary, 'failures': failures},
      'downstream_reliance_report': {'downstream_reliance_report_version': f'{version}-downstream-reliance-report-v1', 'archive_version': version, 'status': 'REL4_downstream_reliance_checked' if not failures else 'REL7_unsafe_reliance_claim', 'summary': summary, 'failures': failures},
      'drift_anomaly_report': {'drift_anomaly_report_version': f'{version}-drift-anomaly-report-v1', 'archive_version': version, 'status': 'DRF4_drift_anomaly_checked' if not failures else 'DRF7_unsafe_drift_claim', 'summary': summary, 'failures': failures},
      'exercise_drill_report': {'exercise_drill_report_version': f'{version}-exercise-drill-report-v1', 'archive_version': version, 'status': 'DRL4_exercise_drill_checked' if not failures else 'DRL7_unsafe_drill_claim', 'summary': summary, 'failures': failures},
    }
    print(yaml.safe_dump(reports, sort_keys=False, allow_unicode=True).rstrip())
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
