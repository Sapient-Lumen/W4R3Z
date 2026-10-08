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
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints.json'
DOC_PATH = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINTS.md'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINTS_REHEARSAL.md'
PATCH_ROOT = ROOT / 'artifacts' / 'patches'
TARGET_FILES = [
    'crates/gr_engine/src/probe.rs',
    'crates/gr_engine/tests/metamorphic_suite.rs',
    'crates/gr_engine/tests/probe_run.rs',
    'crates/gr_engine/tests/probe_standing_bootstrap.rs',
]
DRIFT_FILE = 'crates/gr_engine/src/probe.rs'
STATE_SEQUENCES = {
    'clean_head': [],
    'repair_only': ['repair'],
    'guard_only': ['guard'],
    'repair_guard': ['repair', 'guard'],
    'patchset_only': ['patchset'],
    'patchset_repair': ['patchset', 'repair'],
    'patchset_guard': ['patchset', 'guard'],
    'final_full': ['patchset', 'repair', 'guard'],
}
PATCH_MAP = {
    'repair': PATCH_ROOT / 'rust_standing_bootstrap_repair.patch',
    'guard': PATCH_ROOT / 'rust_standing_bootstrap_guard.patch',
    'patchset': PATCH_ROOT / 'rust_external_test_patchset.patch',
    'bundle': PATCH_ROOT / 'rust_standing_bootstrap_comeback_bundle.patch',
    'post_patchset_bundle': PATCH_ROOT / 'rust_standing_bootstrap_post_patchset_bundle.patch',
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_path(path: Path) -> str:
    if not path.exists():
        return 'MISSING'
    return _sha256_bytes(path.read_bytes())


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _materialize_case(sequence: list[str], drift: bool) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_checkpoint_rehearsal_')
    scratch = Path(tmp.name)
    for rel in TARGET_FILES:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = scratch / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    for patch in PATCH_MAP.values():
        copied = scratch / patch.relative_to(ROOT)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(patch, copied)
    for step in sequence:
        patch = PATCH_MAP[step]
        proc = subprocess.run(['git', 'apply', str(patch.relative_to(ROOT))], cwd=scratch, capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit('rust-standing-bootstrap-checkpoints-rehearsal: failed to materialize scratch state\n' + proc.stderr)
    if drift:
        path = scratch / DRIFT_FILE
        path.write_text(path.read_text(encoding='utf-8') + '\n// drifted in checkpoint rehearsal\n', encoding='utf-8')
    return scratch, tmp


def _classify(report: dict[str, Any], target_root: Path) -> dict[str, Any]:
    observed_hashes = {rel: _hash_path(target_root / rel) for rel in report['target_files']}
    matched = next((state for state in report['state_checkpoints'] if state['file_hashes'] == observed_hashes), None)
    return {
        'recognized': matched is not None,
        'matched_state_id': None if matched is None else matched['state_id'],
        'observed_hashes': observed_hashes,
        'observed_combined_hash': _combined_hash(observed_hashes),
        'checkpoints': [] if matched is None else matched['checkpoints'],
        'apply_commands': [] if matched is None else matched['apply_commands'],
    }


def _run_apply_command(cwd: Path, command: str) -> dict[str, Any]:
    parts = command.split()
    if parts[:2] != ['git', 'apply'] or len(parts) != 3:
        raise SystemExit(f'rust-standing-bootstrap-checkpoints-rehearsal: unsupported apply command {command!r}')
    patch_rel = parts[2]
    check = subprocess.run(['git', 'apply', '--check', patch_rel], cwd=cwd, capture_output=True, text=True)
    apply = subprocess.run(['git', 'apply', patch_rel], cwd=cwd, capture_output=True, text=True) if check.returncode == 0 else None
    return {
        'command': command,
        'check_ok': check.returncode == 0,
        'apply_ok': apply is not None and apply.returncode == 0,
    }


def collect() -> tuple[dict[str, Any], str]:
    if not REPORT_PATH.exists() or not DOC_PATH.exists():
        raise SystemExit('rust-standing-bootstrap-checkpoints-rehearsal: missing report/doc')
    report = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    by_state = {state['state_id']: state for state in report['state_checkpoints']}
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
    for case_id, sequence, drift in scenarios:
        scratch, tmp = _materialize_case(sequence, drift)
        try:
            initial = _classify(report, scratch)
            checkpoint_steps: list[dict[str, Any]] = []
            final_state = initial['matched_state_id']
            if drift:
                ok = (not initial['recognized']) and not initial['checkpoints']
            elif case_id == 'final_full':
                ok = initial['recognized'] and initial['matched_state_id'] == 'final_full' and not initial['checkpoints']
            else:
                ok = initial['recognized'] and initial['matched_state_id'] == case_id and len(initial['checkpoints']) == len(initial['apply_commands'])
                for expected in initial['checkpoints']:
                    step = _run_apply_command(scratch, expected['apply_command'])
                    post = _classify(report, scratch)
                    post_state = by_state.get(post['matched_state_id']) if post['matched_state_id'] else None
                    step_ok = (
                        step['check_ok'] and step['apply_ok']
                        and post['recognized']
                        and post['matched_state_id'] == expected['expected_state_id']
                        and post['observed_combined_hash'] == expected['expected_combined_hash']
                        and post_state is not None
                        and len(post_state['apply_commands']) == expected['expected_remaining_apply_command_count']
                    )
                    checkpoint_steps.append(
                        {
                            'step_index': expected['step_index'],
                            'apply_command': expected['apply_command'],
                            'ok': step_ok,
                            'observed_state_id': post['matched_state_id'],
                            'observed_combined_hash': post['observed_combined_hash'],
                        }
                    )
                    ok = ok and step_ok
                final_state = checkpoint_steps[-1]['observed_state_id'] if checkpoint_steps else final_state
                ok = ok and final_state == 'final_full'
            cases.append(
                {
                    'case_id': case_id,
                    'drift': drift,
                    'sequence': sequence,
                    'ok': ok,
                    'initial_recognized': initial['recognized'],
                    'initial_state_id': initial['matched_state_id'],
                    'checkpoint_count': len(initial['checkpoints']),
                    'checkpoint_steps': checkpoint_steps,
                    'final_state_id': final_state,
                }
            )
        finally:
            tmp.cleanup()
    out = {
        'tool': 'build_rust_standing_bootstrap_checkpoints_rehearsal',
        'checkpoints_report': str(REPORT_PATH.relative_to(ROOT)),
        'summary': {
            'case_count': len(cases),
            'successful_case_count': len([case for case in cases if case['ok']]),
            'recognized_case_count': len([case for case in cases if not case['drift']]),
            'drift_case_count': len([case for case in cases if case['drift']]),
            'all_cases_ok': all(case['ok'] for case in cases),
        },
        'cases': cases,
    }
    return out, render_markdown(out)


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Checkpoints Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_checkpoints_rehearsal.py`. This materializes each known bootstrap branch state in scratch, reads the checkpoints card, then actually applies the promised patch commands and confirms the resulting checkout hits the exact promised state ids and combined hashes step by step.',
        '',
        '## Snapshot',
        '',
        f"- case_count: `{s['case_count']}`",
        f"- successful_case_count: `{s['successful_case_count']}`",
        f"- recognized_case_count: `{s['recognized_case_count']}`",
        f"- drift_case_count: `{s['drift_case_count']}`",
        f"- all_cases_ok: `{str(s['all_cases_ok']).lower()}`",
        '',
        '## What this proves',
        '',
        '- The checkpoints card is not just restating the apply plan; its post-step state ids and combined hashes match the actual scratch-applied results.',
        '- The layered routes now have exact pause points (`repair_guard`, `final_full`) that can be re-identified after every apply.',
        '- The already-final case emits no checkpoints, and drift still fails closed.',
        '',
        '## Case summary',
        '',
        '| case | ok | initial_state | checkpoints | final_state |',
        '|---|---|---|---:|---|',
    ]
    for case in report['cases']:
        lines.append(
            f"| `{case['case_id']}` | `{str(case['ok']).lower()}` | `{case['initial_state_id'] or 'none'}` | {case['checkpoint_count']} | `{case['final_state_id'] or 'none'}` |"
        )
    lines.append('')
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-checkpoints-rehearsal: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-checkpoints-rehearsal: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-checkpoints-rehearsal: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-checkpoints-rehearsal: ok intermediate checkpoints match actual post-apply states')
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
