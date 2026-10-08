from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

READINESS_SPEC = importlib.util.spec_from_file_location('readiness_report_script', ROOT / 'scripts' / 'readiness_report.py')
assert READINESS_SPEC and READINESS_SPEC.loader
READINESS_MODULE = importlib.util.module_from_spec(READINESS_SPEC)
READINESS_SPEC.loader.exec_module(READINESS_MODULE)

build_readiness_report = READINESS_MODULE.build_readiness_report
capture_readiness_report = READINESS_MODULE.capture_readiness_report
summarize_capture_history = READINESS_MODULE.summarize_capture_history


def _doctor_report(*, validation_complete: bool = False, validation_captured: bool = False) -> dict:
    validation_summary = {
        'path': 'validation/latest/report.json',
        'complete': validation_complete,
        'running_step_name': None if validation_complete else 'pytest_cli',
        'required_failed_step': None if validation_complete else 'pytest_cli',
        'latest_completed_step': 'extension_typecheck',
    }
    latest_validation_capture = {
        'report_path': 'validation/latest/report.json',
        'running_step_name': validation_summary['running_step_name'],
        'latest_completed_step': validation_summary['latest_completed_step'],
    } if validation_captured else None
    return {
        'project': 'GlassTTY',
        'validation': {
            'latest_report': {'exists': True, 'summary': validation_summary},
            'capture_history': {'capture_count': 1 if validation_captured else 0, 'latest_capture': latest_validation_capture},
            'commands': {
                'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume',
                'capture_latest': 'python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture',
                'capture_history': 'python scripts/validate-release-capture.py history --pretty',
            },
        },
        'fixture_lab': {
            'latest_smoke_report': {'exists': True, 'summary': {'report_path': 'validation/latest/e2e-fixturelab.json', 'report_timestamp': '2026-03-18T00:00:00Z', 'ok': True}},
            'smoke_capture_history': {'capture_count': 0, 'latest_capture': None},
            'commands': {
                'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture',
                'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty',
            },
        },
        'profiles': {
            'triage': {
                'best_profile': {
                    'name': 'main',
                    'tier': 'attach-ready',
                    'score': 91,
                    'attach_ready': True,
                    'next_command': './scripts/glasstty-profile.sh resume-proof main',
                    'commands': {'resume_proof': './scripts/glasstty-profile.sh resume-proof main'},
                },
                'commands': {
                    'fleet_capture': './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture',
                    'fleet_captures': './scripts/glasstty-profile.sh fleet-captures --pretty',
                },
            },
            'fleet_capture_history': {'capture_count': 0, 'latest_capture': None},
        },
        'playwright': {
            'available': True,
            'extension_launch_plan': {'skip_reason': None},
        },
        'hints': [],
    }


def _write_validate_report(source_dir: Path) -> None:
    steps_dir = source_dir / 'steps'
    steps_dir.mkdir(parents=True, exist_ok=True)
    (steps_dir / 'pytest_cli.stdout.txt').write_text('stdout\n', encoding='utf-8')
    (steps_dir / 'pytest_cli.stderr.txt').write_text('stderr\n', encoding='utf-8')
    report = {
        'project': 'GlassTTY',
        'root': str(ROOT),
        'timestamp': '2026-03-18T00:00:00Z',
        'ok': False,
        'complete': False,
        'resume_requested': False,
        'selection': {'start_at': None, 'end_at': None, 'run_e2e': False},
        'planned_steps': ['extension_typecheck', 'pytest_cli', 'verify_package'],
        'steps': [
            {
                'name': 'extension_typecheck',
                'ok': True,
                'timed_out': False,
                'returncode': 0,
                'seconds': 1.2,
                'required': True,
                'stdout_path': str(steps_dir / 'extension_typecheck.stdout.txt'),
                'stderr_path': str(steps_dir / 'extension_typecheck.stderr.txt'),
            },
            {
                'name': 'pytest_cli',
                'ok': False,
                'timed_out': True,
                'returncode': None,
                'seconds': 45.0,
                'required': True,
                'stdout_path': str(steps_dir / 'pytest_cli.stdout.txt'),
                'stderr_path': str(steps_dir / 'pytest_cli.stderr.txt'),
            },
        ],
        'running_step': {'name': 'pytest_cli', 'argv': ['python', '-m', 'pytest', '-q'], 'cwd': str(ROOT), 'required': True, 'started_at': '2026-03-18T00:01:00Z'},
        'pytest_diagnostics': {'faulthandler_timeout': 45.0, 'durations': 10},
    }
    (steps_dir / 'extension_typecheck.stdout.txt').write_text('ok\n', encoding='utf-8')
    (steps_dir / 'extension_typecheck.stderr.txt').write_text('', encoding='utf-8')
    (source_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (source_dir / 'SUMMARY.md').write_text('# partial\n', encoding='utf-8')
    (source_dir / 'current_step.json').write_text(json.dumps(report['running_step']), encoding='utf-8')


def test_build_readiness_report_prioritizes_validation_resume() -> None:
    report = build_readiness_report(doctor_report=_doctor_report())
    readiness = report['readiness']
    assert readiness['readiness_grade'] == 'blocked-by-validation'
    assert readiness['primary_next_kind'] == 'resume_validate_release'
    assert readiness['primary_next_command'].endswith('--resume')
    assert readiness['actions'][1]['kind'] == 'capture_validate_release'
    assert any(action['kind'] == 'capture_mv3_resume_proof' for action in readiness['actions'])


def test_capture_readiness_report_writes_bundle_history_and_diff(tmp_path: Path) -> None:
    output_dir = tmp_path / 'validation' / 'latest' / 'readiness-report-capture'
    history_path = tmp_path / 'validation' / 'readiness-report-captures.json'

    bundle = capture_readiness_report(output_dir=output_dir, history_path=history_path, doctor_report=_doctor_report())
    assert bundle['readiness']['primary_next_kind'] == 'resume_validate_release'
    assert (output_dir / 'readiness-report.json').exists()
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    assert bundle['history_update']['capture_count_after_write'] == 1

    bundle2 = capture_readiness_report(output_dir=output_dir, history_path=history_path, doctor_report=_doctor_report(validation_complete=True, validation_captured=True))
    diff = json.loads((output_dir / 'capture-diff.json').read_text(encoding='utf-8'))
    history = summarize_capture_history(history_path)
    assert bundle2['readiness']['readiness_grade'] == 'live-lane-ready'
    assert 'readiness_grade' in diff['changed_fields']
    assert 'primary_next_command' in diff['changed_fields']
    assert history['capture_count'] == 2


def test_doctor_exposes_readiness_commands_and_hint(tmp_path: Path) -> None:
    source_dir = ROOT / 'validation' / 'latest'
    history_path = ROOT / 'validation' / 'validate-release-captures.json'
    source_dir.mkdir(parents=True, exist_ok=True)
    backup_report = (source_dir / 'report.json').read_text(encoding='utf-8') if (source_dir / 'report.json').exists() else None
    backup_summary = (source_dir / 'SUMMARY.md').read_text(encoding='utf-8') if (source_dir / 'SUMMARY.md').exists() else None
    backup_current = (source_dir / 'current_step.json').read_text(encoding='utf-8') if (source_dir / 'current_step.json').exists() else None
    backup_steps_dir = tmp_path / 'steps-backup'
    had_steps = (source_dir / 'steps').exists()
    if had_steps:
        subprocess.check_call(['cp', '-R', str(source_dir / 'steps'), str(backup_steps_dir)])
    backup_history = history_path.read_text(encoding='utf-8') if history_path.exists() else None
    try:
        for child in ['report.json', 'SUMMARY.md', 'current_step.json']:
            (source_dir / child).unlink(missing_ok=True)
        if (source_dir / 'steps').exists():
            subprocess.check_call(['rm', '-rf', str(source_dir / 'steps')])
        history_path.unlink(missing_ok=True)
        _write_validate_report(source_dir)
        output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
        assert output['readiness']['commands']['report'] == 'python scripts/readiness-report.py --pretty'
        assert any('Condense the current profile/smoke/validation state into one next-action board' in hint and 'python scripts/readiness-report.py --pretty' in hint for hint in output['hints'])
    finally:
        for child in ['report.json', 'SUMMARY.md', 'current_step.json']:
            (source_dir / child).unlink(missing_ok=True)
        if (source_dir / 'steps').exists():
            subprocess.check_call(['rm', '-rf', str(source_dir / 'steps')])
        if backup_report is not None:
            (source_dir / 'report.json').write_text(backup_report, encoding='utf-8')
        if backup_summary is not None:
            (source_dir / 'SUMMARY.md').write_text(backup_summary, encoding='utf-8')
        if backup_current is not None:
            (source_dir / 'current_step.json').write_text(backup_current, encoding='utf-8')
        if had_steps:
            subprocess.check_call(['cp', '-R', str(backup_steps_dir), str(source_dir / 'steps')])
        if backup_history is None:
            history_path.unlink(missing_ok=True)
        else:
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(backup_history, encoding='utf-8')
