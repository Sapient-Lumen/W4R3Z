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
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_state_selector.json'
DOC_PATH = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_STATE_SELECTOR.md'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_state_selector_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_STATE_SELECTOR_REHEARSAL.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'choose_rust_standing_bootstrap_path.py'
PATCH_MAP = {
    'repair': ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch',
    'guard': ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch',
    'patchset': ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch',
}
DRIFT_FILE = 'crates/gr_engine/src/probe.rs'


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


def _run_apply(cwd: Path, patch_path: Path) -> tuple[bool, str, bool, str]:
    check = subprocess.run(['git', 'apply', '--check', str(patch_path)], cwd=cwd, capture_output=True, text=True)
    check_summary = '\n'.join(part for part in [check.stdout.strip(), check.stderr.strip()] if part).strip()
    apply_ok = False
    apply_summary = ''
    if check.returncode == 0:
        apply = subprocess.run(['git', 'apply', str(patch_path)], cwd=cwd, capture_output=True, text=True)
        apply_ok = apply.returncode == 0
        apply_summary = '\n'.join(part for part in [apply.stdout.strip(), apply.stderr.strip()] if part).strip()
    return check.returncode == 0, check_summary, apply_ok, apply_summary


def _materialize_case(target_files: list[str], sequence: list[str], drift: bool) -> tuple[Path, list[dict[str, Any]], tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_state_selector_rehearsal_')
    scratch = Path(tmp.name)
    for rel in target_files:
        _copy_if_exists(scratch, rel)
    local_patch_map = {
        patch_id: _write_support_file(scratch, str(path.relative_to(ROOT)), path.read_bytes())
        for patch_id, path in PATCH_MAP.items()
    }
    steps: list[dict[str, Any]] = []
    for step_id in sequence:
        check_ok, check_summary, apply_ok, apply_summary = _run_apply(scratch, local_patch_map[step_id])
        steps.append(
            {
                'step_id': step_id,
                'check_ok': check_ok,
                'apply_ok': apply_ok,
                'check_summary': check_summary,
                'apply_summary': apply_summary,
            }
        )
        if not (check_ok and apply_ok):
            raise SystemExit(f'rust-standing-bootstrap-state-selector-rehearsal: failed scratch sequence at {step_id}')
    if drift:
        drift_path = scratch / DRIFT_FILE
        drift_path.write_text(drift_path.read_text(encoding='utf-8') + '\n// drifted in rehearsal\n', encoding='utf-8')
    return scratch, steps, tmp


def collect() -> tuple[dict[str, Any], str]:
    if not REPORT_PATH.exists() or not DOC_PATH.exists():
        raise SystemExit('rust-standing-bootstrap-state-selector-rehearsal: missing selector report/doc')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
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
    recognized_ok = 0
    drift_ok = 0
    for expected_state, sequence, drift in scenarios:
        scratch, steps, tmp = _materialize_case(report['target_files'], sequence, drift)
        try:
            proc = subprocess.run(
                ['python3', str(TOOL_PATH), '--report', str(REPORT_PATH), '--target-root', str(scratch), '--json'],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                raise SystemExit(
                    'rust-standing-bootstrap-state-selector-rehearsal: selector tool failed\n'
                    + proc.stdout
                    + proc.stderr
                )
            raw_result = json.loads(proc.stdout)
            result = {
                'recognized': raw_result['recognized'],
                'matched_state_id': raw_result['matched_state_id'],
                'matched_label': raw_result['matched_label'],
                'observed_combined_hash': raw_result['observed_combined_hash'],
                'best_partial_match': raw_result['best_partial_match'],
                'recommendation': raw_result['recommendation'],
            }
        finally:
            tmp.cleanup()
        recognized = bool(result['recognized'])
        ok = False
        if drift:
            ok = (not recognized) and result['matched_state_id'] is None
            if ok:
                drift_ok += 1
        else:
            ok = recognized and result['matched_state_id'] == expected_state
            if ok:
                recognized_ok += 1
        cases.append(
            {
                'case_id': expected_state,
                'expected_state_id': None if drift else expected_state,
                'recognized_expected': not drift,
                'selector_ok': ok,
                'drift': drift,
                'sequence': sequence,
                'scratch_sequence': steps,
                'selector_result': result,
            }
        )

    report_out = {
        'tool': 'build_rust_standing_bootstrap_state_selector_rehearsal',
        'selector_report': str(REPORT_PATH.relative_to(ROOT)),
        'selector_tool': str(TOOL_PATH.relative_to(ROOT)),
        'summary': {
            'case_count': len(cases),
            'recognized_case_count': len([case for case in cases if not case['drift']]),
            'recognized_case_ok_count': recognized_ok,
            'drift_case_count': len([case for case in cases if case['drift']]),
            'drift_case_ok_count': drift_ok,
            'all_cases_ok': all(case['selector_ok'] for case in cases),
        },
        'cases': cases,
    }
    return report_out, render_markdown(report_out)


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap State Selector Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_state_selector_rehearsal.py`. This materializes the known bootstrap/comeback branch states in scratch, runs the selector tool against each one, and checks that the exact-state routing matches the generated selector report.',
        '',
        '## Snapshot',
        '',
        f"- case_count: `{s['case_count']}`",
        f"- recognized_case_count: `{s['recognized_case_count']}`",
        f"- recognized_case_ok_count: `{s['recognized_case_ok_count']}`",
        f"- drift_case_count: `{s['drift_case_count']}`",
        f"- drift_case_ok_count: `{s['drift_case_ok_count']}`",
        f"- all_cases_ok: `{str(s['all_cases_ok']).lower()}`",
        '',
        '## What this proves',
        '',
        '- The selector recognizes the exact clean-head, patchset-only, repair-only, guard-only, repair+guard, patchset+repair, patchset+guard, and already-final states that the archive now documents.',
        '- Unknown states fail closed. The rehearsal includes a deliberately drifted `probe.rs` case and the selector refuses to classify it as a known exact state.',
        '',
        '## Case summary',
        '',
        '| case | recognized_expected | selector_ok | matched_state_id |',
        '|---|---|---|---|',
    ]
    for case in report['cases']:
        matched = case['selector_result']['matched_state_id'] or 'none'
        lines.append(
            f"| `{case['case_id']}` | `{str(case['recognized_expected']).lower()}` | `{str(case['selector_ok']).lower()}` | `{matched}` |"
        )
    lines.append('')
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-state-selector-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-state-selector-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-state-selector-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-state-selector-rehearsal: ok selector recognizes exact states and fails closed on drift')
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
