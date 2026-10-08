from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALIDATE_SPEC = importlib.util.spec_from_file_location('validate_release_script', ROOT / 'scripts' / 'validate-release.py')
assert VALIDATE_SPEC and VALIDATE_SPEC.loader
VALIDATE_MODULE = importlib.util.module_from_spec(VALIDATE_SPEC)
VALIDATE_SPEC.loader.exec_module(VALIDATE_MODULE)

CAPTURE_SPEC = importlib.util.spec_from_file_location('validate_release_capture_script', ROOT / 'scripts' / 'validate_release_capture.py')
assert CAPTURE_SPEC and CAPTURE_SPEC.loader
CAPTURE_MODULE = importlib.util.module_from_spec(CAPTURE_SPEC)
CAPTURE_SPEC.loader.exec_module(CAPTURE_MODULE)

build_step_specs = VALIDATE_MODULE.build_step_specs
capture_validate_release = CAPTURE_MODULE.capture_validate_release
summarize_report_file = CAPTURE_MODULE.summarize_report_file


def _write_validate_report(source_dir: Path, *, running_step: str | None = 'pytest_cli', ok: bool = False, complete: bool = False) -> None:
    steps_dir = source_dir / 'steps'
    steps_dir.mkdir(parents=True, exist_ok=True)
    (steps_dir / 'pytest_cli.stdout.txt').write_text('stdout\n', encoding='utf-8')
    (steps_dir / 'pytest_cli.stderr.txt').write_text('stderr\n', encoding='utf-8')
    report = {
        'project': 'GlassTTY',
        'root': str(ROOT),
        'timestamp': '2026-03-18T00:00:00Z',
        'ok': ok,
        'complete': complete,
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
        'pytest_diagnostics': {'faulthandler_timeout': 45.0, 'durations': 10},
    }
    if running_step is not None:
        report['running_step'] = {'name': running_step, 'argv': ['python', '-m', 'pytest', '-q', 'tests/test_cli.py'], 'cwd': str(ROOT), 'required': True, 'started_at': '2026-03-18T00:01:00Z'}
        (source_dir / 'current_step.json').write_text(json.dumps(report['running_step']), encoding='utf-8')
    else:
        report['running_step'] = None
    (steps_dir / 'extension_typecheck.stdout.txt').write_text('ok\n', encoding='utf-8')
    (steps_dir / 'extension_typecheck.stderr.txt').write_text('', encoding='utf-8')
    (source_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (source_dir / 'SUMMARY.md').write_text('# partial\n', encoding='utf-8')


def test_build_step_specs_adds_pytest_diagnostics_flags(tmp_path: Path) -> None:
    steps = build_step_specs(root=ROOT, package_zip_temp=tmp_path / 'package-check.zip', out_dir=tmp_path, pytest_faulthandler_timeout=33.0, pytest_durations=7)
    pytest_cli = next(step for step in steps if step['name'] == 'pytest_cli')
    assert ['-o', 'faulthandler_timeout=33.0'] == pytest_cli['argv'][-4:-2]
    assert pytest_cli['argv'][-2:] == ['--durations', '7']


def test_validate_release_capture_writes_bundle_history_and_diff(tmp_path: Path) -> None:
    source_dir = tmp_path / 'validation' / 'latest'
    output_dir = source_dir / 'validate-release-capture'
    history_path = tmp_path / 'validation' / 'validate-release-captures.json'
    _write_validate_report(source_dir)

    bundle = capture_validate_release(source_dir=source_dir, output_dir=output_dir, history_path=history_path)
    assert bundle['validation_summary']['running_step_name'] == 'pytest_cli'
    assert bundle['validation_summary']['required_failed_step'] == 'pytest_cli'
    assert bundle['validation_summary']['timed_out_step_count'] == 1
    assert (output_dir / 'report.json').exists()
    assert (output_dir / 'steps' / 'pytest_cli.stdout.txt').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    assert bundle['history_update']['capture_count_after_write'] == 1
    history = json.loads(history_path.read_text(encoding='utf-8'))
    assert history['capture_count'] == 1
    assert history['entries'][0]['resume_command'].endswith('--resume')

    _write_validate_report(source_dir, running_step=None, ok=True, complete=True)
    bundle2 = capture_validate_release(source_dir=source_dir, output_dir=output_dir, history_path=history_path)
    diff = json.loads((output_dir / 'capture-diff.json').read_text(encoding='utf-8'))
    assert bundle2['history_update']['capture_count_after_write'] == 2
    assert diff['complete_changed'] is True
    assert 'complete' in diff['changed_fields']


def test_doctor_surfaces_validate_release_resume_and_capture_hints(tmp_path: Path) -> None:
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
        if source_dir.exists():
            for child in ['report.json', 'SUMMARY.md', 'current_step.json']:
                (source_dir / child).unlink(missing_ok=True)
            if (source_dir / 'steps').exists():
                subprocess.check_call(['rm', '-rf', str(source_dir / 'steps')])
        history_path.unlink(missing_ok=True)
        _write_validate_report(source_dir)
        output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
        assert any('validate-release report is still incomplete' in hint and 'python scripts/validate-release.py --out-dir validation/latest --resume' in hint for hint in output['hints'])
        assert any('freeze it with `python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture`' in hint for hint in output['hints'])
        assert output['validation']['latest_report']['summary']['running_step_name'] == 'pytest_cli'
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


def test_summarize_report_file_reports_resume_and_focus_commands(tmp_path: Path) -> None:
    source_dir = tmp_path / 'validation' / 'latest'
    _write_validate_report(source_dir)
    summary = summarize_report_file(source_dir)
    assert summary['exists'] is True
    assert summary['summary']['resume_command'].endswith('--resume')
    assert '--start-at pytest_cli --end-at pytest_cli' in summary['summary']['focus_command']
