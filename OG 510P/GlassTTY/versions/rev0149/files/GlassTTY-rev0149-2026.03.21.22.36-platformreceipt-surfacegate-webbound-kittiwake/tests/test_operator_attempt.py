from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_SPEC = importlib.util.spec_from_file_location('operator_attempt_script', ROOT / 'scripts' / 'operator_attempt.py')
assert MODULE_SPEC and MODULE_SPEC.loader
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)

finish_attempt = MODULE.finish_attempt
start_attempt = MODULE.start_attempt
summarize_capture_history = MODULE.summarize_capture_history
summarize_current_attempt = MODULE.summarize_current_attempt


def _doctor_report(*, validation_complete: bool = False, readiness_grade: str | None = None) -> dict:
    validation_summary = {
        'path': 'validation/latest/report.json',
        'complete': validation_complete,
        'running_step_name': None if validation_complete else 'pytest_cli',
        'required_failed_step': None if validation_complete else 'pytest_cli',
        'latest_completed_step': 'extension_typecheck',
    }
    best_profile = {
        'name': 'main',
        'tier': 'attach-ready' if validation_complete else 'reopen-debug',
        'score': 95 if validation_complete else 80,
        'attach_ready': validation_complete,
        'next_command': './scripts/glasstty-profile.sh resume-proof main' if validation_complete else './scripts/glasstty-profile.sh reopen main',
        'commands': {
            'resume_proof': './scripts/glasstty-profile.sh resume-proof main',
        },
    }
    if readiness_grade is None:
        readiness_grade = 'live-lane-ready' if validation_complete else 'blocked-by-validation'
    return {
        'project': 'GlassTTY',
        'validation': {
            'latest_report': {'exists': True, 'summary': validation_summary},
            'capture_history': {'capture_count': 1 if validation_complete else 0, 'latest_capture': None},
            'commands': {
                'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume',
                'capture_latest': 'python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture',
                'capture_history': 'python scripts/validate-release-capture.py history --pretty',
            },
        },
        'fixture_lab': {
            'latest_smoke_report': {'exists': True, 'summary': {'report_timestamp': '2026-03-18T01:00:00Z', 'ok': True}},
            'smoke_capture_history': {'capture_count': 1, 'latest_capture': {'output_dir': 'validation/latest/e2e-fixturelab-capture'}},
            'commands': {
                'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture',
                'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty',
            },
        },
        'profiles': {
            'triage': {
                'best_profile': best_profile,
                'commands': {
                    'fleet_capture': './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture',
                    'fleet_captures': './scripts/glasstty-profile.sh fleet-captures --pretty',
                },
            },
            'fleet_capture_history': {'capture_count': 1, 'latest_capture': {'output_dir': 'validation/latest/profile-fleet-capture'}},
        },
        'playwright': {'available': True, 'extension_launch_plan': {'skip_reason': None}},
        'readiness': {'commands': {'report': 'python scripts/readiness-report.py --pretty'}},
        'operator_handoff': {'commands': {'capture_latest': 'python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff'}},
        'hints': ['hint-a', 'hint-b'],
    }


def test_start_attempt_writes_before_bundle_and_in_progress_summary(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'operator-attempt'
    history_path = tmp_path / 'validation' / 'operator-attempts.json'

    payload = start_attempt(
        output_dir=output_dir,
        history_path=history_path,
        doctor_report=_doctor_report(validation_complete=False),
        label='live-try-1',
        planned_command='python scripts/validate-release.py --out-dir validation/latest --resume',
        notes='before a resumed validation pass',
        root=tmp_path,
    )
    assert payload['status'] == 'in-progress'
    assert payload['before']['readiness_grade'] == 'blocked-by-validation'
    assert (output_dir / 'doctor-before.json').exists()
    assert (output_dir / 'readiness-before.json').exists()
    assert (output_dir / 'operator-handoff-before.json').exists()
    assert (output_dir / 'artifact-index-before.json').exists()
    summary = summarize_current_attempt(output_dir)
    assert summary['exists'] is True
    assert summary['status'] == 'in-progress'
    assert summary['planned_command'] == 'python scripts/validate-release.py --out-dir validation/latest --resume'


def test_finish_attempt_writes_after_state_attempt_diff_and_history(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'operator-attempt'
    history_path = tmp_path / 'validation' / 'operator-attempts.json'

    start_attempt(
        output_dir=output_dir,
        history_path=history_path,
        doctor_report=_doctor_report(validation_complete=False),
        label='live-try-2',
        planned_command='python scripts/validate-release.py --out-dir validation/latest --resume',
        root=tmp_path,
    )
    payload = finish_attempt(
        output_dir=output_dir,
        history_path=history_path,
        doctor_report=_doctor_report(validation_complete=True),
        outcome='success',
        notes='validation resumed cleanly',
        root=tmp_path,
    )
    assert payload['status'] == 'finished'
    assert payload['after']['readiness_grade'] == 'live-lane-ready'
    assert 'readiness_grade' in payload['attempt_diff']['changed_fields']
    assert 'validation_complete' in payload['attempt_diff']['changed_fields']
    assert (output_dir / 'doctor-after.json').exists()
    assert (output_dir / 'attempt-diff.json').exists()
    assert (output_dir / 'history-update.json').exists()
    assert (output_dir / 'history-diff.json').exists()
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    assert history['latest_capture']['outcome'] == 'success'


def test_doctor_exposes_operator_attempt_commands_and_in_progress_hint(tmp_path: Path) -> None:
    attempt_dir = ROOT / 'validation' / 'latest' / 'operator-attempt'
    history_path = ROOT / 'validation' / 'operator-attempts.json'
    backup_dir = tmp_path / 'operator-attempt-backup'
    backup_history = history_path.read_text(encoding='utf-8') if history_path.exists() else None
    had_attempt_dir = attempt_dir.exists()
    if had_attempt_dir:
        subprocess.check_call(['cp', '-R', str(attempt_dir), str(backup_dir)])
    try:
        if attempt_dir.exists():
            subprocess.check_call(['rm', '-rf', str(attempt_dir)])
        attempt_dir.mkdir(parents=True, exist_ok=True)
        attempt_payload = {
            'schema_version': 1,
            'label': 'live-run',
            'status': 'in-progress',
            'started_at': '2026-03-18T01:00:00Z',
            'finished_at': None,
            'outcome': None,
            'planned_command': './scripts/glasstty-profile.sh resume-proof main',
            'history_path': str(history_path),
            'relative_output_dir': 'validation/latest/operator-attempt',
            'commands': {
                'report': 'python scripts/operator-attempt.py --pretty',
                'start_latest': 'python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt',
                'finish_latest': 'python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome success',
                'history': 'python scripts/operator-attempt.py history --pretty',
            },
            'before': {'readiness_grade': 'live-lane-ready'},
            'after': None,
        }
        (attempt_dir / 'attempt.json').write_text(json.dumps(attempt_payload, indent=2) + '\n', encoding='utf-8')
        history_path.write_text(json.dumps({'schema_version': 1, 'capture_count': 0, 'entries': []}, indent=2) + '\n', encoding='utf-8')
        output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
        assert output['operator_attempt']['commands']['start_latest'] == 'python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt'
        assert output['operator_attempt']['current_attempt']['status'] == 'in-progress'
        assert any('operator attempt is already in progress' in hint.lower() and 'python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome success' in hint for hint in output['hints'])
    finally:
        if attempt_dir.exists():
            subprocess.check_call(['rm', '-rf', str(attempt_dir)])
        if had_attempt_dir:
            subprocess.check_call(['cp', '-R', str(backup_dir), str(attempt_dir)])
        if backup_history is None:
            history_path.unlink(missing_ok=True)
        else:
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(backup_history, encoding='utf-8')
