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
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_verification_ladder.json'
DOC_PATH = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'emit_rust_standing_bootstrap_verification_ladder.py'
EXECUTION_REHEARSAL = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_execution_rehearsal.json'
PATCH_ROOT = ROOT / 'artifacts' / 'patches'
TARGET_FILES = [
    'crates/gr_engine/src/probe.rs',
    'crates/gr_engine/tests/metamorphic_suite.rs',
    'crates/gr_engine/tests/probe_run.rs',
    'crates/gr_engine/tests/probe_standing_bootstrap.rs',
]
DRIFT_FILE = 'crates/gr_engine/src/probe.rs'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_verification_ladder_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_VERIFICATION_LADDER_REHEARSAL.md'


def _materialize_case(sequence: list[str], drift: bool) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_verify_ladder_')
    scratch = Path(tmp.name)
    for rel in TARGET_FILES:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = scratch / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    patch_map = {
        'repair': PATCH_ROOT / 'rust_standing_bootstrap_repair.patch',
        'guard': PATCH_ROOT / 'rust_standing_bootstrap_guard.patch',
        'patchset': PATCH_ROOT / 'rust_external_test_patchset.patch',
    }
    for step in sequence:
        patch = patch_map[step]
        copied = scratch / patch.relative_to(ROOT)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(patch, copied)
        proc = subprocess.run(['git', 'apply', str(copied.relative_to(scratch))], cwd=scratch, capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit('rust-standing-bootstrap-verification-ladder-rehearsal: failed to materialize scratch state\n' + proc.stderr)
    if drift:
        path = scratch / DRIFT_FILE
        path.write_text(path.read_text(encoding='utf-8') + '\n// drifted in verification rehearsal\n', encoding='utf-8')
    return scratch, tmp


def _inspect(target_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ['python3', str(TOOL_PATH), '--report', str(REPORT_PATH), '--target-root', str(target_root), '--json'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit('rust-standing-bootstrap-verification-ladder-rehearsal: tool failed\n' + proc.stdout + proc.stderr)
    return json.loads(proc.stdout)


def collect() -> tuple[dict[str, Any], str]:
    if not REPORT_PATH.exists() or not DOC_PATH.exists():
        raise SystemExit('rust-standing-bootstrap-verification-ladder-rehearsal: missing ladder report/doc')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    execution_rehearsal = json.loads(EXECUTION_REHEARSAL.read_text(encoding='utf-8'))
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
    exact_stage = next(stage for stage in report['stages'] if stage['stage_id'] == 'standing_affected_probe_rows')
    cases: list[dict[str, Any]] = []
    for case_id, sequence, drift in scenarios:
        scratch, tmp = _materialize_case(sequence, drift)
        try:
            observed = _inspect(scratch)
            ok = False
            if case_id == 'final_full':
                ok = (
                    observed['precondition_satisfied']
                    and observed['matched_state_id'] == 'final_full'
                    and len(observed['verification_stages']) == len(report['stages'])
                    and observed['verification_stages'][1]['commands'] == exact_stage['commands']
                    and observed['expected_final_combined_hash'] == report['summary']['expected_final_combined_hash']
                )
            else:
                ok = (
                    not observed['precondition_satisfied']
                    and observed['matched_state_id'] != 'final_full'
                    and len(observed['verification_stages']) == 0
                )
                if not drift:
                    matched = next(case for case in execution_rehearsal['cases'] if case['case_id'] == case_id)
                    expected_apply = matched['initial_plan']['plan']['apply_commands']
                    ok = ok and observed['apply_first_commands'] == expected_apply
            cases.append(
                {
                    'case_id': case_id,
                    'drift': drift,
                    'sequence': sequence,
                    'ok': ok,
                    'precondition_satisfied': observed['precondition_satisfied'],
                    'matched_state_id': observed['matched_state_id'],
                    'apply_first_commands': observed['apply_first_commands'],
                    'verification_stage_count': len(observed['verification_stages']),
                }
            )
        finally:
            tmp.cleanup()
    out = {
        'tool': 'build_rust_standing_bootstrap_verification_ladder_rehearsal',
        'verification_ladder_report': str(REPORT_PATH.relative_to(ROOT)),
        'verification_ladder_tool': str(TOOL_PATH.relative_to(ROOT)),
        'summary': {
            'case_count': len(cases),
            'successful_case_count': len([case for case in cases if case['ok']]),
            'final_state_case_count': len([case for case in cases if case['case_id'] == 'final_full']),
            'nonfinal_or_drift_case_count': len([case for case in cases if case['case_id'] != 'final_full']),
            'all_cases_ok': all(case['ok'] for case in cases),
        },
        'cases': cases,
    }
    return out, render_markdown(out)


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Verification Ladder Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_verification_ladder_rehearsal.py`. This materializes the known bootstrap branch states in scratch and proves the verification-ladder tool only emits the staged ladder after the checkout reaches the exact proved `final_full` state; earlier or drifted states are routed back to apply sequencing instead.',
        '',
        '## Snapshot',
        '',
        f"- case_count: `{s['case_count']}`",
        f"- successful_case_count: `{s['successful_case_count']}`",
        f"- final_state_case_count: `{s['final_state_case_count']}`",
        f"- nonfinal_or_drift_case_count: `{s['nonfinal_or_drift_case_count']}`",
        f"- all_cases_ok: `{str(s['all_cases_ok']).lower()}`",
        '',
        '## What this proves',
        '',
        '- The verification ladder is gated on the exact proved final bootstrap/comeback state instead of being emitted too early on partial or drifted branches.',
        '- Every known non-final state is routed back to the execution-plan apply commands before verification sequencing is offered.',
        '- The final state emits the full staged ladder, including the three exact affected `probe_run` witnesses and no broader commands ahead of them.',
        '',
        '## Case summary',
        '',
        '| case | ok | precondition_satisfied | matched_state_id | apply cmds | stages |',
        '|---|---|---|---|---:|---:|',
    ]
    for case in report['cases']:
        lines.append(
            f"| `{case['case_id']}` | `{str(case['ok']).lower()}` | `{str(case['precondition_satisfied']).lower()}` | `{case['matched_state_id'] or 'none'}` | {len(case['apply_first_commands'])} | {case['verification_stage_count']} |"
        )
    lines.append('')
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-verification-ladder-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-verification-ladder-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-verification-ladder-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-verification-ladder-rehearsal: ok ladder only emits after final_full and otherwise routes back to apply sequencing')
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
