#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

StepSpec = dict[str, Any]




def _pytest_argv(*, test_path: str, extra_args: list[str] | None = None, faulthandler_timeout: float | None = None, durations: int | None = None) -> list[str]:
    argv = [sys.executable, '-m', 'pytest', '-q', test_path]
    if extra_args:
        argv.extend(extra_args)
    if faulthandler_timeout and faulthandler_timeout > 0:
        argv.extend(['-o', f'faulthandler_timeout={faulthandler_timeout}'])
    if durations and durations > 0:
        argv.extend(['--durations', str(durations)])
    return argv


def sanitize(name: str) -> str:
    return ''.join(ch if ch.isalnum() or ch in ('-', '_') else '-' for ch in name)


def _write_step_artifacts(*, artifacts_dir: Path, stem: str, step: dict[str, Any], stdout: str, stderr: str) -> dict[str, Any]:
    stdout_path = artifacts_dir / f'{stem}.stdout.txt'
    stderr_path = artifacts_dir / f'{stem}.stderr.txt'
    stdout_path.write_text(stdout, encoding='utf-8')
    stderr_path.write_text(stderr, encoding='utf-8')
    step['stdout_path'] = str(stdout_path)
    step['stderr_path'] = str(stderr_path)
    (artifacts_dir / f'{stem}.json').write_text(json.dumps(step, indent=2) + '\n', encoding='utf-8')
    return step


def run_step(
    name: str,
    argv: list[str],
    *,
    artifacts_dir: Path,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    timeout: float = 180.0,
    check: bool = True,
) -> dict[str, Any]:
    started = time.time()
    stem = sanitize(name)
    base = {
        'name': name,
        'argv': argv,
        'cwd': str(cwd),
        'required': check,
        'timeout_seconds': timeout,
    }
    try:
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False)
        step = {
            **base,
            'returncode': result.returncode,
            'seconds': round(time.time() - started, 3),
            'ok': result.returncode == 0,
            'timed_out': False,
        }
        return _write_step_artifacts(artifacts_dir=artifacts_dir, stem=stem, step=step, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout if isinstance(error.stdout, str) else (error.stdout.decode('utf-8', errors='replace') if error.stdout else '')
        stderr = error.stderr if isinstance(error.stderr, str) else (error.stderr.decode('utf-8', errors='replace') if error.stderr else '')
        step = {
            **base,
            'returncode': None,
            'seconds': round(time.time() - started, 3),
            'ok': False,
            'timed_out': True,
            'error': f'timed out after {timeout} seconds',
        }
        if stderr:
            stderr = f'{stderr}\n\n[validate-release] timed out after {timeout} seconds\n'
        else:
            stderr = f'[validate-release] timed out after {timeout} seconds\n'
        return _write_step_artifacts(artifacts_dir=artifacts_dir, stem=stem, step=step, stdout=stdout, stderr=stderr)


def package_check_paths(out_dir: Path, existing_temp_path: str | None = None) -> tuple[Path, Path]:
    final_path = out_dir / 'package-check.zip'
    if existing_temp_path:
        return Path(existing_temp_path), final_path
    temp_dir = Path(tempfile.mkdtemp(prefix='glasstty-package-check-'))
    temp_path = temp_dir / final_path.name
    return temp_path, final_path


def package_zip_proof(path: Path, *, retained: bool, final_path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return {
        'path': str(final_path),
        'retained': retained,
        'sha256': digest.hexdigest(),
        'size_bytes': path.stat().st_size,
    }


def maybe_copy_json_output(step: dict[str, Any], destination: Path) -> None:
    stdout_path = Path(step['stdout_path'])
    try:
        data = json.loads(stdout_path.read_text(encoding='utf-8'))
    except Exception:
        return
    destination.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def write_running_step_artifact(running_step: dict[str, Any] | None, *, out_dir: Path) -> Path:
    path = out_dir / 'current_step.json'
    if running_step is None:
        path.unlink(missing_ok=True)
        return path
    path.write_text(json.dumps(running_step, indent=2) + '\n', encoding='utf-8')
    return path


def write_report_artifacts(report: dict[str, Any], *, out_dir: Path, package_zip_final: Path | None = None) -> tuple[Path, Path]:
    json_path = out_dir / 'report.json'
    md_path = out_dir / 'SUMMARY.md'
    if package_zip_final is not None:
        report['package_zip'] = str(package_zip_final) if package_zip_final.exists() else None
    json_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# GlassTTY validation summary',
        '',
        f"- timestamp: {report['timestamp']}",
        f"- overall_ok: {report['ok']}",
        f"- complete: {report.get('complete', False)}",
        f"- steps_recorded: {len(report.get('steps', []))}",
    ]
    planned_steps = report.get('planned_steps') or []
    if planned_steps:
        lines.append(f"- planned_steps: {', '.join(planned_steps)}")
    if report.get('resume_requested'):
        lines.append('- resume_requested: True')
    package_proof = report.get('package_zip_proof')
    if isinstance(package_proof, dict):
        lines.append(f"- package_zip_retained: {bool(package_proof.get('retained'))}")
        if package_proof.get('size_bytes') is not None:
            lines.append(f"- package_zip_size_bytes: {package_proof['size_bytes']}")
        if package_proof.get('sha256'):
            lines.append(f"- package_zip_sha256: {package_proof['sha256']}")
    running_step = report.get('running_step')
    if isinstance(running_step, dict) and running_step.get('name'):
        lines.append(f"- running_step: {running_step['name']}")
    lines.extend([
        '',
        '| step | ok | timed_out | returncode | seconds | stdout | stderr |',
        '|---|---:|---:|---:|---:|---|---|',
    ])
    for step in report.get('steps', []):
        lines.append(
            f"| {step['name']} | {'yes' if step['ok'] else 'no'} | {'yes' if step.get('timed_out') else 'no'} | {step['returncode']} | {step['seconds']} | {Path(step['stdout_path']).name} | {Path(step['stderr_path']).name} |"
        )
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return json_path, md_path


def build_step_specs(*, root: Path = ROOT, package_zip_temp: Path, out_dir: Path, run_e2e: bool = False, pytest_faulthandler_timeout: float | None = 45.0, pytest_durations: int | None = 10) -> list[StepSpec]:
    steps: list[StepSpec] = [
        {'name': 'extension_typecheck', 'argv': ['npm', 'run', 'typecheck'], 'cwd': root / 'extension', 'required': True},
        {'name': 'extension_build', 'argv': ['npm', 'run', 'build'], 'cwd': root / 'extension', 'required': True},
        {'name': 'receiver_inventory_check', 'argv': ['node', 'scripts/receiver-inventory-check.mjs'], 'cwd': root / 'extension', 'required': True},
        {'name': 'receiver_priming_check', 'argv': ['node', 'scripts/receiver-priming-check.mjs'], 'cwd': root / 'extension', 'required': True},
        {'name': 'content_script_experiment_check', 'argv': ['node', 'scripts/content-script-experiment-check.mjs'], 'cwd': root / 'extension', 'required': True},
        {'name': 'pytest_protocol', 'argv': _pytest_argv(test_path='tests/test_protocol.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_state', 'argv': _pytest_argv(test_path='tests/test_state.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_broker', 'argv': _pytest_argv(test_path='tests/test_broker.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_cli', 'argv': _pytest_argv(test_path='tests/test_cli.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_fixture_tools', 'argv': _pytest_argv(test_path='tests/test_fixture_tools.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_coverage_experiment_tools', 'argv': _pytest_argv(test_path='tests/test_coverage_experiment_tools.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_package_release', 'argv': _pytest_argv(test_path='tests/test_package_release.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_dev_tools', 'argv': _pytest_argv(test_path='tests/test_dev_tools.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_e2e_helper', 'argv': _pytest_argv(test_path='tests/test_e2e_fixturelab.py', extra_args=['-k', 'not fixturelab_e2e_smoke'], faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'pytest_cdp_inspect', 'argv': _pytest_argv(test_path='tests/test_cdp_inspect.py', faulthandler_timeout=pytest_faulthandler_timeout, durations=pytest_durations), 'cwd': root, 'required': True},
        {'name': 'doctor_pretty', 'argv': [sys.executable, 'scripts/doctor.py', '--pretty'], 'cwd': root, 'required': True},
        {'name': 'seed_fixture_corpus', 'argv': [sys.executable, 'scripts/seed-fixture-corpus.py', 'fixtures/corpus', '--force'], 'cwd': root, 'required': True},
        {'name': 'index_fixture_corpus', 'argv': [sys.executable, 'scripts/index-fixtures.py', 'fixtures/corpus', '--pretty'], 'cwd': root, 'required': True},
        {'name': 'compare_fixture_examples', 'argv': [sys.executable, 'scripts/compare-fixtures.py', 'fixtures/corpus/fixturelab-home.json', 'fixtures/corpus/fixturelab-thread.json', '--pretty'], 'cwd': root, 'required': True},
        {'name': 'compare_coverage_experiments', 'argv': [sys.executable, 'scripts/compare-coverage-experiments.py', 'fixtures/coverage-experiments/about-blank-before-probe.json', 'fixtures/coverage-experiments/about-blank-after-probe.json', '--pretty'], 'cwd': root, 'required': True},
        {'name': 'native_message_budget', 'argv': [sys.executable, 'scripts/native-message-budget.py', 'fixtures/corpus', '--pretty'], 'cwd': root, 'required': True},
        {'name': 'package_release', 'argv': ['bash', 'scripts/package-release.sh', str(root), str(package_zip_temp)], 'cwd': root, 'required': True},
        {'name': 'verify_package', 'argv': [sys.executable, 'scripts/verify-package.py', str(package_zip_temp), '--pretty'], 'cwd': root, 'required': True},
    ]
    if run_e2e:
        e2e_path = out_dir / 'e2e-fixturelab.json'
        steps.append({'name': 'e2e_fixturelab', 'argv': [sys.executable, 'scripts/e2e-fixturelab.py', '--output', str(e2e_path)], 'cwd': root, 'required': False})
    return steps


def select_steps(steps: list[StepSpec], *, start_at: str | None = None, end_at: str | None = None) -> list[StepSpec]:
    if not steps:
        return []
    names = [step['name'] for step in steps]
    if start_at and start_at not in names:
        raise ValueError(f'unknown start step: {start_at}')
    if end_at and end_at not in names:
        raise ValueError(f'unknown end step: {end_at}')
    start_index = names.index(start_at) if start_at else 0
    end_index = names.index(end_at) if end_at else len(steps) - 1
    if start_index > end_index:
        raise ValueError(f'start step {start_at} occurs after end step {end_at}')
    return steps[start_index : end_index + 1]


def load_existing_report(out_dir: Path) -> dict[str, Any] | None:
    report_path = out_dir / 'report.json'
    if not report_path.exists():
        return None
    data = json.loads(report_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{report_path} is not a JSON object')
    return data


def completed_ok_step_names(report: dict[str, Any]) -> set[str]:
    return {step.get('name') for step in report.get('steps', []) if isinstance(step, dict) and step.get('ok') and isinstance(step.get('name'), str)}


def pending_steps_for_resume(steps: list[StepSpec], report: dict[str, Any]) -> list[StepSpec]:
    completed = completed_ok_step_names(report)
    return [step for step in steps if step['name'] not in completed]


def maybe_reinsert_package_release(steps: list[StepSpec], all_steps: list[StepSpec], *, report: dict[str, Any], package_zip_temp: Path) -> list[StepSpec]:
    names = [step['name'] for step in steps]
    completed = completed_ok_step_names(report)
    if 'verify_package' not in names or 'package_release' not in completed or package_zip_temp.exists():
        return steps
    package_step = next((step for step in all_steps if step['name'] == 'package_release'), None)
    if package_step is None:
        return steps
    verify_index = names.index('verify_package')
    return steps[:verify_index] + [package_step] + steps[verify_index:]


def upsert_step(report: dict[str, Any], step: dict[str, Any]) -> None:
    steps = report.setdefault('steps', [])
    for index, existing in enumerate(steps):
        if isinstance(existing, dict) and existing.get('name') == step.get('name'):
            steps[index] = step
            return
    steps.append(step)


def compute_report_ok(report: dict[str, Any], *, planned_steps: list[str] | None = None) -> bool:
    by_name = {step.get('name'): step for step in report.get('steps', []) if isinstance(step, dict) and isinstance(step.get('name'), str)}
    if planned_steps:
        relevant = [by_name[name] for name in planned_steps if name in by_name]
    else:
        relevant = list(by_name.values())
    required = [step for step in relevant if step.get('required')]
    return bool(relevant) and all(step.get('ok') for step in required)


def should_keep_package_temp(report: dict[str, Any], package_zip_temp: Path) -> bool:
    if not package_zip_temp.exists():
        return False
    if report.get('complete'):
        return False
    return any(isinstance(step, dict) and step.get('name') == 'package_release' and step.get('ok') for step in report.get('steps', []))


def main() -> None:
    parser = argparse.ArgumentParser(description='Run a reproducible GlassTTY release-validation pass and save JSON/Markdown artifacts.')
    parser.add_argument('--out-dir', default='validation/latest')
    parser.add_argument('--run-e2e', action='store_true', help='Also run the best-effort real-browser fixture-lab smoke')
    parser.add_argument('--start-at', help='Run starting at this named step')
    parser.add_argument('--end-at', help='Stop after this named step')
    parser.add_argument('--resume', action='store_true', help='Resume a prior partial run in the same out-dir by skipping already successful steps')
    parser.add_argument('--keep-package-zip', action='store_true', help='Retain validation/package-check.zip after verify_package succeeds')
    parser.add_argument('--pytest-faulthandler-timeout', type=float, default=45.0, help='Add pytest faulthandler timeout diagnostics (seconds) to validation pytest steps; set 0 to disable')
    parser.add_argument('--pytest-durations', type=int, default=10, help='Record the N slowest pytest tests in validation step output; set 0 to disable')
    args = parser.parse_args()

    out_dir = (ROOT / args.out_dir).resolve()
    artifacts_dir = out_dir / 'steps'
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'daemon' / 'src') + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')

    existing_report = load_existing_report(out_dir) if args.resume else None
    if args.resume and existing_report is None:
        raise SystemExit(f'--resume requested but no report.json exists under {out_dir}')

    package_zip_temp, package_zip_final = package_check_paths(out_dir, existing_temp_path=(existing_report or {}).get('package_zip_temp'))
    all_steps = build_step_specs(root=ROOT, package_zip_temp=package_zip_temp, out_dir=out_dir, run_e2e=args.run_e2e, pytest_faulthandler_timeout=args.pytest_faulthandler_timeout, pytest_durations=args.pytest_durations)
    try:
        selected_steps = select_steps(all_steps, start_at=args.start_at, end_at=args.end_at)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    planned_steps = [step['name'] for step in selected_steps]

    if existing_report is not None:
        report = existing_report
        report.setdefault('project', 'GlassTTY')
        report.setdefault('root', str(ROOT))
        report.setdefault('steps', [])
        report['complete'] = False
        report['ok'] = False
        report['running_step'] = None
    else:
        report = {'project': 'GlassTTY', 'root': str(ROOT), 'steps': [], 'complete': False, 'ok': False, 'running_step': None}
    report['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    report['resume_requested'] = args.resume
    report['selection'] = {'start_at': args.start_at, 'end_at': args.end_at, 'run_e2e': args.run_e2e}
    report['pytest_diagnostics'] = {'faulthandler_timeout': args.pytest_faulthandler_timeout, 'durations': args.pytest_durations}
    report['planned_steps'] = planned_steps
    report['package_zip_temp'] = str(package_zip_temp)
    report['package_zip_retained'] = args.keep_package_zip

    if args.resume:
        selected_steps = pending_steps_for_resume(selected_steps, report)
        selected_steps = maybe_reinsert_package_release(selected_steps, all_steps, report=report, package_zip_temp=package_zip_temp)

    try:
        for spec in selected_steps:
            name = spec['name']
            argv = spec['argv']
            cwd = spec['cwd']
            required = spec['required']
            print(f'[validate-release] running {name}: {" ".join(argv)}', file=sys.stderr)
            report['running_step'] = {'name': name, 'argv': argv, 'cwd': str(cwd), 'required': required, 'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
            write_running_step_artifact(report['running_step'], out_dir=out_dir)
            write_report_artifacts(report, out_dir=out_dir, package_zip_final=package_zip_final)
            step = run_step(name, argv, artifacts_dir=artifacts_dir, cwd=cwd, env=env, check=required)
            upsert_step(report, step)
            report['running_step'] = None
            write_running_step_artifact(None, out_dir=out_dir)
            if name == 'doctor_pretty':
                maybe_copy_json_output(step, out_dir / 'doctor_pretty.json')
            elif name == 'index_fixture_corpus':
                maybe_copy_json_output(step, out_dir / 'index_fixture_corpus.json')
            elif name == 'compare_fixture_examples':
                maybe_copy_json_output(step, out_dir / 'compare_fixture_examples.json')
            elif name == 'native_message_budget':
                maybe_copy_json_output(step, out_dir / 'native_message_budget.json')
            elif name == 'seed_fixture_corpus':
                (out_dir / 'seed_fixture_corpus.log').write_text(Path(step['stdout_path']).read_text(encoding='utf-8'), encoding='utf-8')
            write_report_artifacts(report, out_dir=out_dir, package_zip_final=package_zip_final)

        verify_step = next((step for step in report['steps'] if step['name'] == 'verify_package'), None)
        if verify_step and verify_step.get('ok') and package_zip_temp.exists():
            report['package_zip_proof'] = package_zip_proof(package_zip_temp, retained=args.keep_package_zip, final_path=package_zip_final)
            if args.keep_package_zip:
                shutil.copy2(package_zip_temp, package_zip_final)
        report['ok'] = compute_report_ok(report, planned_steps=planned_steps)
        report['complete'] = all(any(step.get('name') == name for step in report['steps']) for name in planned_steps)
        json_path, md_path = write_report_artifacts(report, out_dir=out_dir, package_zip_final=package_zip_final)
        print(json.dumps({'ok': report['ok'], 'json': str(json_path), 'markdown': str(md_path), 'steps_dir': str(artifacts_dir), 'package_zip': str(package_zip_final) if package_zip_final.exists() else None, 'package_zip_proof': report.get('package_zip_proof')}, indent=2))
        raise SystemExit(0 if report['ok'] else 1)
    finally:
        report['running_step'] = None
        write_running_step_artifact(None, out_dir=out_dir)
        if 'package_zip_temp' in locals() and not should_keep_package_temp(report, package_zip_temp):
            shutil.rmtree(package_zip_temp.parent, ignore_errors=True)


if __name__ == '__main__':
    main()
