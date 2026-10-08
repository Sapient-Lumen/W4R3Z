#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHECKPOINTS_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints.json'
VERIFIER_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoint_verifier.json'
VERIFIER_DOC = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'verify_rust_standing_bootstrap_checkpoint.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoint_verifier_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER_REHEARSAL.md'
PATCH_ROOT = ROOT / 'artifacts' / 'patches'
TARGET_FILES = [
    'crates/gr_engine/src/probe.rs',
    'crates/gr_engine/tests/metamorphic_suite.rs',
    'crates/gr_engine/tests/probe_run.rs',
    'crates/gr_engine/tests/probe_standing_bootstrap.rs',
]
PATCH_MAP = {
    'repair': PATCH_ROOT / 'rust_standing_bootstrap_repair.patch',
    'guard': PATCH_ROOT / 'rust_standing_bootstrap_guard.patch',
    'patchset': PATCH_ROOT / 'rust_external_test_patchset.patch',
}


def _materialize(sequence: list[str], drift: bool = False) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_checkpoint_verifier_rehearsal_')
    scratch = Path(tmp.name)
    for rel in TARGET_FILES:
        src = ROOT / rel
        if src.exists():
            dst = scratch / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for patch in PATCH_MAP.values():
        dst = scratch / patch.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(patch, dst)
    for step in sequence:
        proc = subprocess.run(
            ['git', 'apply', str(PATCH_MAP[step].relative_to(ROOT))],
            cwd=scratch,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(
                'rust-standing-bootstrap-checkpoint-verifier-rehearsal: failed to materialize scratch state\n'
                + proc.stderr
            )
    if drift:
        path = scratch / 'crates/gr_engine/src/probe.rs'
        path.write_text(path.read_text(encoding='utf-8') + '\n// drifted in checkpoint verifier rehearsal\n', encoding='utf-8')
    return scratch, tmp


def _run(target_root: Path, *args: str) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(
        ['python3', str(TOOL_PATH), '--report', str(CHECKPOINTS_REPORT), '--target-root', str(target_root), '--json', *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, payload, proc.stderr.strip()


def collect() -> tuple[dict[str, Any], str]:
    missing = [path for path in [CHECKPOINTS_REPORT, VERIFIER_REPORT, VERIFIER_DOC, TOOL_PATH] if not path.exists()]
    if missing:
        raise SystemExit(
            'rust-standing-bootstrap-checkpoint-verifier-rehearsal: missing prerequisites\n'
            + '\n'.join(str(path.relative_to(ROOT)) for path in missing)
        )
    checkpoints = json.loads(CHECKPOINTS_REPORT.read_text(encoding='utf-8'))
    by_state = {state['state_id']: state for state in checkpoints['state_checkpoints']}
    cases: list[dict[str, Any]] = []

    def add_case(case: dict[str, Any]) -> None:
        case['ok'] = bool(case['ok'])
        cases.append(case)

    rc, payload, stderr = _run(ROOT, '--expect-state-id', 'clean_head', '--expect-combined-hash', by_state['clean_head']['observed_combined_hash'])
    add_case({
        'case_id': 'live_clean_head_direct',
        'mode': 'direct',
        'expect_success': True,
        'ok': rc == 0 and payload is not None and payload['verified'] and payload['matched_state_id'] == 'clean_head' and payload['observed_combined_hash'] == by_state['clean_head']['observed_combined_hash'],
        'returncode': rc,
        'verified': None if payload is None else payload['verified'],
        'recognized': None if payload is None else payload['recognized'],
        'matched_state_id': None if payload is None else payload['matched_state_id'],
        'observed_combined_hash': None if payload is None else payload['observed_combined_hash'],
        'stderr': stderr,
        'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root . --expect-state-id clean_head --expect-combined-hash ' + by_state['clean_head']['observed_combined_hash'] + ' --json',
    })

    scratch, tmp = _materialize(['repair'])
    try:
        rc, payload, stderr = _run(scratch, '--expect-state-id', 'repair_only', '--expect-combined-hash', by_state['repair_only']['observed_combined_hash'])
        add_case({
            'case_id': 'scratch_repair_only_direct',
            'mode': 'direct',
            'expect_success': True,
            'ok': rc == 0 and payload is not None and payload['verified'] and payload['matched_state_id'] == 'repair_only' and payload['observed_combined_hash'] == by_state['repair_only']['observed_combined_hash'],
            'returncode': rc,
            'verified': None if payload is None else payload['verified'],
            'recognized': None if payload is None else payload['recognized'],
            'matched_state_id': None if payload is None else payload['matched_state_id'],
            'observed_combined_hash': None if payload is None else payload['observed_combined_hash'],
            'stderr': stderr,
            'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root <scratch> --expect-state-id repair_only --expect-combined-hash ' + by_state['repair_only']['observed_combined_hash'] + ' --json',
        })
        cp = by_state['repair_only']['checkpoints'][0]
        apply_proc = subprocess.run(cp['apply_command'].split(), cwd=scratch, capture_output=True, text=True, check=False)
        if apply_proc.returncode != 0:
            raise SystemExit('rust-standing-bootstrap-checkpoint-verifier-rehearsal: failed to apply repair_only checkpoint step\n' + apply_proc.stderr)
        rc, payload, stderr = _run(scratch, '--from-state-id', 'repair_only', '--step-index', '1')
        add_case({
            'case_id': 'scratch_repair_only_step1_route',
            'mode': 'route-step',
            'expect_success': True,
            'ok': rc == 0 and payload is not None and payload['verified'] and payload['matched_state_id'] == cp['expected_state_id'] and payload['observed_combined_hash'] == cp['expected_combined_hash'] and payload['derived_from_checkpoint'] is not None and payload['derived_from_checkpoint']['from_state_id'] == 'repair_only' and payload['derived_from_checkpoint']['step_index'] == 1,
            'returncode': rc,
            'verified': None if payload is None else payload['verified'],
            'recognized': None if payload is None else payload['recognized'],
            'matched_state_id': None if payload is None else payload['matched_state_id'],
            'observed_combined_hash': None if payload is None else payload['observed_combined_hash'],
            'stderr': stderr,
            'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root <scratch> --from-state-id repair_only --step-index 1 --json',
        })
    finally:
        tmp.cleanup()

    scratch, tmp = _materialize(['patchset', 'repair', 'guard'])
    try:
        rc, payload, stderr = _run(scratch, '--expect-state-id', 'final_full', '--expect-combined-hash', by_state['final_full']['observed_combined_hash'])
        add_case({
            'case_id': 'scratch_final_full_direct',
            'mode': 'direct',
            'expect_success': True,
            'ok': rc == 0 and payload is not None and payload['verified'] and payload['matched_state_id'] == 'final_full' and payload['observed_combined_hash'] == by_state['final_full']['observed_combined_hash'],
            'returncode': rc,
            'verified': None if payload is None else payload['verified'],
            'recognized': None if payload is None else payload['recognized'],
            'matched_state_id': None if payload is None else payload['matched_state_id'],
            'observed_combined_hash': None if payload is None else payload['observed_combined_hash'],
            'stderr': stderr,
            'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root <scratch> --expect-state-id final_full --expect-combined-hash ' + by_state['final_full']['observed_combined_hash'] + ' --json',
        })
    finally:
        tmp.cleanup()

    scratch, tmp = _materialize(['repair'], drift=True)
    try:
        rc, payload, stderr = _run(scratch, '--expect-state-id', 'repair_only')
        add_case({
            'case_id': 'scratch_repair_only_drift_fail_closed',
            'mode': 'direct',
            'expect_success': False,
            'ok': rc != 0 and payload is not None and (not payload['verified']) and (not payload['recognized']),
            'returncode': rc,
            'verified': None if payload is None else payload['verified'],
            'recognized': None if payload is None else payload['recognized'],
            'matched_state_id': None if payload is None else payload['matched_state_id'],
            'observed_combined_hash': None if payload is None else payload['observed_combined_hash'],
            'stderr': stderr,
            'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root <scratch-drifted> --expect-state-id repair_only --json',
            'best_partial_match_state_id': None if payload is None else payload['best_partial_match']['state_id'],
            'best_partial_match_file_count': None if payload is None else payload['best_partial_match']['matched_file_count'],
        })
    finally:
        tmp.cleanup()

    rc, payload, stderr = _run(ROOT, '--from-state-id', 'repair_only', '--step-index', '1', '--expect-state-id', 'final_full')
    add_case({
        'case_id': 'conflicting_expectation_rejected',
        'mode': 'argument-guard',
        'expect_success': False,
        'ok': rc != 0 and payload is None and 'conflicts with derived checkpoint expectation' in stderr,
        'returncode': rc,
        'verified': None,
        'recognized': None,
        'matched_state_id': None,
        'observed_combined_hash': None,
        'stderr': stderr,
        'invocation': 'python3 scripts/tools/verify_rust_standing_bootstrap_checkpoint.py --target-root . --from-state-id repair_only --step-index 1 --expect-state-id final_full --json',
    })

    summary = {
        'case_count': len(cases),
        'successful_case_count': len([case for case in cases if case['ok']]),
        'success_expected_case_count': len([case for case in cases if case['expect_success']]),
        'failure_expected_case_count': len([case for case in cases if not case['expect_success']]),
        'direct_mode_case_count': len([case for case in cases if case['mode'] == 'direct']),
        'route_mode_case_count': len([case for case in cases if case['mode'] == 'route-step']),
        'argument_guard_case_count': len([case for case in cases if case['mode'] == 'argument-guard']),
        'all_cases_ok': all(case['ok'] for case in cases),
    }
    report = {
        'tool': 'build_rust_standing_bootstrap_checkpoint_verifier_rehearsal',
        'source_report': str(CHECKPOINTS_REPORT.relative_to(ROOT)),
        'verifier_report': str(VERIFIER_REPORT.relative_to(ROOT)),
        'verifier_doc': str(VERIFIER_DOC.relative_to(ROOT)),
        'verifier_tool': str(TOOL_PATH.relative_to(ROOT)),
        'summary': summary,
        'cases': cases,
    }
    return report, render_markdown(report)


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Checkpoint Verifier Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_checkpoint_verifier_rehearsal.py`. This scratch-rehearses the checkpoint verifier itself so future inheritors can trust that direct checks, route-step checks, fail-closed drift handling, and conflicting-expectation rejection all behave exactly as advertised before any Rust-capable machine work begins.',
        '',
        '## Snapshot',
        '',
        f"- case_count: `{s['case_count']}`",
        f"- successful_case_count: `{s['successful_case_count']}`",
        f"- success_expected_case_count: `{s['success_expected_case_count']}`",
        f"- failure_expected_case_count: `{s['failure_expected_case_count']}`",
        f"- direct_mode_case_count: `{s['direct_mode_case_count']}`",
        f"- route_mode_case_count: `{s['route_mode_case_count']}`",
        f"- argument_guard_case_count: `{s['argument_guard_case_count']}`",
        f"- all_cases_ok: `{str(s['all_cases_ok']).lower()}`",
        '',
        '## What this proves',
        '',
        '- The verifier succeeds on the live clean head before any bootstrap patch is applied, so it is immediately usable in a fresh archive reopen.',
        '- Direct exact-state checks and route-step checks both work on scratch-materialized bootstrap states, including a post-step transition from `repair_only` to `repair_guard`.',
        '- The verifier fails closed on drifted content and rejects conflicting user-supplied expectations instead of silently accepting an inconsistent request.',
        '',
        '## Rehearsed cases',
        '',
        '| case | mode | expect success | ok | matched state | returncode |',
        '|---|---|---|---|---|---:|',
    ]
    for case in report['cases']:
        lines.append(f"| `{case['case_id']}` | `{case['mode']}` | `{str(case['expect_success']).lower()}` | `{str(case['ok']).lower()}` | `{case['matched_state_id'] or 'none'}` | {case['returncode']} |")
    lines.extend(['', '## Exact invocations exercised', ''])
    for case in report['cases']:
        lines.append(f"- `{case['case_id']}` — `{case['invocation']}`")
    lines.extend(['', '## Operational reading', '', '1. Keep `docs/RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md` as the operator-facing command card.', '2. Use this rehearsal only as the proof surface that the verifier lane itself still behaves honestly after future archive refreshes.', '3. When this rehearsal ever drifts, treat the verifier as suspect until both the tool and the generated card have been reconciled and regenerated together.'])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-checkpoint-verifier-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-checkpoint-verifier-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-checkpoint-verifier-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-checkpoint-verifier-rehearsal: ok verifier direct, route-step, fail-closed, and argument-guard cases remain reproducible')
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
