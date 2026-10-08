from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('validate_release_script', ROOT / 'scripts' / 'validate-release.py')
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

run_step = MODULE.run_step
sanitize = MODULE.sanitize
package_check_paths = MODULE.package_check_paths
write_report_artifacts = MODULE.write_report_artifacts
write_running_step_artifact = MODULE.write_running_step_artifact
build_step_specs = MODULE.build_step_specs
package_zip_proof = MODULE.package_zip_proof
select_steps = MODULE.select_steps
pending_steps_for_resume = MODULE.pending_steps_for_resume
maybe_reinsert_package_release = MODULE.maybe_reinsert_package_release


def test_sanitize_preserves_safe_chars() -> None:
    assert sanitize('alpha beta/gamma') == 'alpha-beta-gamma'


def test_run_step_records_timeout(tmp_path: Path) -> None:
    step = run_step(
        'timeout-case',
        [sys.executable, '-c', 'import time; time.sleep(0.3)'],
        artifacts_dir=tmp_path,
        timeout=0.05,
        check=False,
    )
    assert step['ok'] is False
    assert step['timed_out'] is True
    assert step['returncode'] is None
    assert Path(step['stdout_path']).exists()
    assert Path(step['stderr_path']).exists()


SPEC2 = importlib.util.spec_from_file_location('refresh_archive_script', ROOT / 'scripts' / 'refresh-archive.py')
assert SPEC2 and SPEC2.loader
MODULE2 = importlib.util.module_from_spec(SPEC2)
SPEC2.loader.exec_module(MODULE2)
parse_archive_name = MODULE2.parse_archive_name


def test_parse_archive_name_extracts_revision_and_slug() -> None:
    parsed = parse_archive_name(Path('GlassTTY-rev0062-2026.03.09.12.32-runtimeexperiment-dynamicregister-coverageflight-skylark'))
    assert parsed['archive_revision'] == 62
    assert parsed['archive_created_at_from_name'] == '2026.03.09.12.32'
    assert parsed['archive_slug'] == 'runtimeexperiment-dynamicregister-coverageflight-skylark'


def test_package_check_paths_use_temp_path_outside_requested_out_dir(tmp_path: Path) -> None:
    out_dir = tmp_path / 'validation' / 'latest'
    temp_path, final_path = package_check_paths(out_dir)
    assert final_path == out_dir / 'package-check.zip'
    assert temp_path.name == 'package-check.zip'
    assert temp_path.parent != out_dir
    assert out_dir not in temp_path.parents


def test_write_report_artifacts_marks_partial_state(tmp_path: Path) -> None:
    report = {
        'timestamp': '2026-03-16T00:00:00Z',
        'ok': False,
        'complete': False,
        'steps': [
            {
                'name': 'example',
                'ok': True,
                'timed_out': False,
                'returncode': 0,
                'seconds': 0.1,
                'stdout_path': str(tmp_path / 'example.stdout.txt'),
                'stderr_path': str(tmp_path / 'example.stderr.txt'),
            }
        ],
    }
    (tmp_path / 'example.stdout.txt').write_text('ok\n', encoding='utf-8')
    (tmp_path / 'example.stderr.txt').write_text('', encoding='utf-8')
    json_path, md_path = write_report_artifacts(report, out_dir=tmp_path)
    assert json_path.exists()
    assert md_path.exists()
    summary = md_path.read_text(encoding='utf-8')
    assert '- complete: False' in summary
    assert '| example | yes | no | 0 | 0.1 |' in summary


def test_package_zip_proof_includes_digest_and_retention_flag(tmp_path: Path) -> None:
    temp_zip = tmp_path / 'package-check.zip'
    temp_zip.write_bytes(b'zip-bytes')
    proof = package_zip_proof(temp_zip, retained=False, final_path=tmp_path / 'final.zip')
    assert proof is not None
    assert proof['retained'] is False
    assert proof['path'].endswith('final.zip')
    assert proof['size_bytes'] == len(b'zip-bytes')
    assert len(proof['sha256']) == 64


def test_write_running_step_artifact_round_trip(tmp_path: Path) -> None:
    running_step = {
        'name': 'pytest_cli',
        'argv': ['python', '-m', 'pytest', '-q', 'tests/test_cli.py'],
        'cwd': str(tmp_path),
        'required': True,
        'started_at': '2026-03-16T00:00:00Z',
    }
    path = write_running_step_artifact(running_step, out_dir=tmp_path)
    assert path.exists()
    assert path.name == 'current_step.json'
    assert 'pytest_cli' in path.read_text(encoding='utf-8')
    write_running_step_artifact(None, out_dir=tmp_path)
    assert not path.exists()


def test_write_report_artifacts_records_running_step(tmp_path: Path) -> None:
    report = {
        'timestamp': '2026-03-16T00:00:00Z',
        'ok': False,
        'complete': False,
        'running_step': {
            'name': 'pytest_cli',
            'argv': ['python', '-m', 'pytest', '-q', 'tests/test_cli.py'],
            'cwd': str(tmp_path),
            'required': True,
            'started_at': '2026-03-16T00:00:00Z',
        },
        'steps': [],
    }
    _json_path, md_path = write_report_artifacts(report, out_dir=tmp_path)
    summary = md_path.read_text(encoding='utf-8')
    assert '- running_step: pytest_cli' in summary


def test_write_report_artifacts_records_package_zip_proof(tmp_path: Path) -> None:
    report = {
        'timestamp': '2026-03-16T00:00:00Z',
        'ok': True,
        'complete': True,
        'package_zip_proof': {
            'path': str(tmp_path / 'validation' / 'package-check.zip'),
            'retained': False,
            'size_bytes': 123,
            'sha256': 'a' * 64,
        },
        'steps': [],
    }
    _json_path, md_path = write_report_artifacts(report, out_dir=tmp_path)
    summary = md_path.read_text(encoding='utf-8')
    assert '- package_zip_retained: False' in summary
    assert '- package_zip_size_bytes: 123' in summary
    assert f"- package_zip_sha256: {'a' * 64}" in summary



def test_select_steps_honors_start_and_end_filters(tmp_path: Path) -> None:
    package_zip_temp = tmp_path / 'package-check.zip'
    steps = build_step_specs(root=ROOT, package_zip_temp=package_zip_temp, out_dir=tmp_path, run_e2e=True)
    selected = select_steps(steps, start_at='pytest_cli', end_at='native_message_budget')
    assert selected[0]['name'] == 'pytest_cli'
    assert selected[-1]['name'] == 'native_message_budget'
    assert all(step['name'] != 'package_release' for step in selected)


def test_pending_steps_for_resume_skips_successful_steps(tmp_path: Path) -> None:
    package_zip_temp = tmp_path / 'package-check.zip'
    steps = build_step_specs(root=ROOT, package_zip_temp=package_zip_temp, out_dir=tmp_path)
    report = {
        'steps': [
            {'name': 'extension_typecheck', 'ok': True},
            {'name': 'extension_build', 'ok': False},
        ]
    }
    pending = pending_steps_for_resume(steps[:3], report)
    assert [step['name'] for step in pending] == ['extension_build', 'receiver_inventory_check']


def test_resume_reinserts_package_release_when_verify_needs_missing_temp_zip(tmp_path: Path) -> None:
    package_zip_temp = tmp_path / 'missing-package-check.zip'
    steps = build_step_specs(root=ROOT, package_zip_temp=package_zip_temp, out_dir=tmp_path)
    selected = select_steps(steps, start_at='verify_package', end_at='verify_package')
    report = {'steps': [{'name': 'package_release', 'ok': True}]}
    resumed = maybe_reinsert_package_release(selected, steps, report=report, package_zip_temp=package_zip_temp)
    assert [step['name'] for step in resumed] == ['package_release', 'verify_package']
