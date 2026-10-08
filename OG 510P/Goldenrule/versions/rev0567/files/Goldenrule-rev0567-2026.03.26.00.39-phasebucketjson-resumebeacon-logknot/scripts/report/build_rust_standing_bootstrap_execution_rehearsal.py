#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_card.json'
DOC_PATH = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_EXECUTION_CARD.md'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_EXECUTION_REHEARSAL.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_execution_plan.py'
PATCH_PATHS = [
    ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch',
    ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch',
    ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch',
    ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_comeback_bundle.patch',
    ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_post_patchset_bundle.patch',
]
DRIFT_FILE = 'crates/gr_engine/src/probe.rs'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _hash_path(path: Path) -> str:
    if not path.exists():
        return 'MISSING'
    return _sha256_bytes(path.read_bytes())


def _copy_if_exists(root: Path, relpath: str) -> None:
    src = ROOT / relpath
    if not src.exists():
        return
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _write_support_file(root: Path, relpath: str, data: bytes) -> Path:
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst


def _run_apply_command(cwd: Path, command: str) -> dict[str, Any]:
    check_parts = command.split()
    if check_parts[:2] != ['git', 'apply'] or len(check_parts) != 3:
        raise SystemExit(f'rust-standing-bootstrap-execution-rehearsal: unsupported apply command {command!r}')
    patch_rel = check_parts[2]
    check = subprocess.run(['git', 'apply', '--check', patch_rel], cwd=cwd, capture_output=True, text=True)
    apply_ok = False
    apply_summary = ''
    if check.returncode == 0:
        apply = subprocess.run(['git', 'apply', patch_rel], cwd=cwd, capture_output=True, text=True)
        apply_ok = apply.returncode == 0
        apply_summary = '\n'.join(part for part in [apply.stdout.strip(), apply.stderr.strip()] if part).strip()
    return {
        'command': command,
        'check_ok': check.returncode == 0,
        'apply_ok': apply_ok,
        'check_summary': '\n'.join(part for part in [check.stdout.strip(), check.stderr.strip()] if part).strip(),
        'apply_summary': apply_summary,
    }


def _materialize_case(target_files: list[str], sequence: list[str], drift: bool) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_execution_rehearsal_')
    scratch = Path(tmp.name)
    for rel in target_files:
        _copy_if_exists(scratch, rel)
    patch_map = {
        path.relative_to(ROOT).as_posix(): _write_support_file(scratch, str(path.relative_to(ROOT)), path.read_bytes())
        for path in PATCH_PATHS
        if path.exists()
    }
    state_to_patch = {
        'repair': 'artifacts/patches/rust_standing_bootstrap_repair.patch',
        'guard': 'artifacts/patches/rust_standing_bootstrap_guard.patch',
        'patchset': 'artifacts/patches/rust_external_test_patchset.patch',
    }
    for step in sequence:
        rel = state_to_patch[step]
        if rel not in patch_map:
            raise SystemExit(f'rust-standing-bootstrap-execution-rehearsal: missing copied patch {rel}')
        apply = subprocess.run(['git', 'apply', rel], cwd=scratch, capture_output=True, text=True)
        if apply.returncode != 0:
            raise SystemExit('rust-standing-bootstrap-execution-rehearsal: failed to materialize scratch state\n' + apply.stderr)
    if drift:
        drift_path = scratch / DRIFT_FILE
        drift_path.write_text(drift_path.read_text(encoding='utf-8') + '\n// drifted in rehearsal\n', encoding='utf-8')
    return scratch, tmp


def _plan_for(target_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ['python3', str(TOOL_PATH), '--report', str(REPORT_PATH), '--target-root', str(target_root), '--json'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit('rust-standing-bootstrap-execution-rehearsal: execution-plan tool failed\n' + proc.stdout + proc.stderr)
    raw = json.loads(proc.stdout)
    return {
        'recognized': raw['recognized'],
        'matched_state_id': raw['matched_state_id'],
        'matched_label': raw['matched_label'],
        'observed_combined_hash': raw['observed_combined_hash'],
        'best_partial_match': raw['best_partial_match'],
        'plan': raw['plan'],
    }


def _snapshot_hash(target_root: Path, target_files: list[str]) -> str:
    snapshot = {rel: _hash_path(target_root / rel) for rel in target_files}
    return _combined_hash(snapshot)


def collect() -> tuple[dict[str, Any], str]:
    if not REPORT_PATH.exists() or not DOC_PATH.exists():
        raise SystemExit('rust-standing-bootstrap-execution-rehearsal: missing execution card/doc')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    target_files = report['target_files']
    expected_final_hash = report['summary']['canonical_final_combined_hash']
    scenarios = [
        ('clean_head', [], False),
        ('repair_only', ['repair'], False),
        ('guard_only', ['guard'], False),
        ('repair_guard', ['repair', 'guard'], False),
        ('patchset_only', ['patchset'], False),
        ('patchset_repair', ['patchset', 'repair'], False),
        ('patchset_guard', ['patchset', 'guard'], False),
        ('final_full', ['patchset', 'repair', 'guard'], False),
        ('drifted_probe_file', ['repair'], True),
    ]
    cases: list[dict[str, Any]] = []
    success_count = 0
    drift_success_count = 0
    for case_id, sequence, drift in scenarios:
        scratch, tmp = _materialize_case(target_files, sequence, drift)
        try:
            initial_plan = _plan_for(scratch)
            execution_steps: list[dict[str, Any]] = []
            final_plan = initial_plan
            final_hash = initial_plan['observed_combined_hash']
            if not drift and case_id != 'final_full':
                for command in initial_plan['plan']['apply_commands']:
                    step = _run_apply_command(scratch, command)
                    execution_steps.append(step)
                    if not (step['check_ok'] and step['apply_ok']):
                        break
                final_hash = _snapshot_hash(scratch, target_files)
                final_plan = _plan_for(scratch)
            elif not drift and case_id == 'final_full':
                final_hash = _snapshot_hash(scratch, target_files)
            plan_ok = False
            if drift:
                plan_ok = (
                    not initial_plan['recognized']
                    and initial_plan['matched_state_id'] is None
                    and initial_plan['plan']['action_kind'] == report['unknown_policy']['action_kind']
                    and not initial_plan['plan']['apply_commands']
                )
                if plan_ok:
                    drift_success_count += 1
            else:
                applys_ok = all(step['check_ok'] and step['apply_ok'] for step in execution_steps)
                if case_id == 'final_full':
                    plan_ok = (
                        initial_plan['recognized']
                        and initial_plan['matched_state_id'] == 'final_full'
                        and final_hash == expected_final_hash
                        and not initial_plan['plan']['apply_commands']
                    )
                else:
                    plan_ok = (
                        initial_plan['recognized']
                        and initial_plan['matched_state_id'] == case_id
                        and applys_ok
                        and final_hash == expected_final_hash
                        and final_plan['recognized']
                        and final_plan['matched_state_id'] == 'final_full'
                        and not final_plan['plan']['apply_commands']
                    )
                if plan_ok:
                    success_count += 1
            cases.append(
                {
                    'case_id': case_id,
                    'drift': drift,
                    'sequence': sequence,
                    'plan_ok': plan_ok,
                    'initial_plan': initial_plan,
                    'execution_steps': execution_steps,
                    'final_plan': final_plan,
                    'final_combined_hash': final_hash,
                }
            )
        finally:
            tmp.cleanup()

    report_out = {
        'tool': 'build_rust_standing_bootstrap_execution_rehearsal',
        'execution_card_report': str(REPORT_PATH.relative_to(ROOT)),
        'execution_plan_tool': str(TOOL_PATH.relative_to(ROOT)),
        'summary': {
            'case_count': len(cases),
            'recognized_case_count': len([case for case in cases if not case['drift']]),
            'recognized_case_ok_count': success_count,
            'drift_case_count': len([case for case in cases if case['drift']]),
            'drift_case_ok_count': drift_success_count,
            'canonical_final_combined_hash': expected_final_hash,
            'all_cases_ok': all(case['plan_ok'] for case in cases),
        },
        'cases': cases,
    }
    return report_out, render_markdown(report_out)


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Execution Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_execution_rehearsal.py`. This materializes each known bootstrap branch state in scratch, runs the execution-plan tool against it, follows the emitted apply commands, and checks that every recognized non-final state converges to the same proved final 4-file hash.',
        '',
        '## Snapshot',
        '',
        f"- case_count: `{s['case_count']}`",
        f"- recognized_case_count: `{s['recognized_case_count']}`",
        f"- recognized_case_ok_count: `{s['recognized_case_ok_count']}`",
        f"- drift_case_count: `{s['drift_case_count']}`",
        f"- drift_case_ok_count: `{s['drift_case_ok_count']}`",
        f"- canonical_final_combined_hash: `{s['canonical_final_combined_hash']}`",
        f"- all_cases_ok: `{str(s['all_cases_ok']).lower()}`",
        '',
        '## What this proves',
        '',
        '- The execution-plan tool is not only classifying states; its emitted apply commands are sufficient to land the exact final bootstrap/comeback state from every recognized non-final branch state.',
        '- The already-final case is idempotent at the planning layer: it emits no further apply commands and already matches the proved final hash.',
        '- Unknown drift still fails closed; the deliberate drift case receives no apply plan.',
        '',
        '## Case summary',
        '',
        '| case | plan_ok | initial_state | final_state | final hash | apply steps |',
        '|---|---|---|---|---|---:|',
    ]
    for case in report['cases']:
        initial_state = case['initial_plan']['matched_state_id'] or 'none'
        final_state = case['final_plan']['matched_state_id'] or 'none'
        lines.append(
            f"| `{case['case_id']}` | `{str(case['plan_ok']).lower()}` | `{initial_state}` | `{final_state}` | `{case['final_combined_hash']}` | {len(case['execution_steps'])} |"
        )
    lines.append('')
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-execution-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-execution-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-execution-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-execution-rehearsal: ok execution plan lands final hash from every known exact state and fails closed on drift')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report, markdown = collect()
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown)


if __name__ == '__main__':
    raise SystemExit(main())
