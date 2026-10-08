#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECOVERY_CARD = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
PLAN_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_rustup_plan.json'
FETCH_SURFACE = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_fetch_surface.json'
COMPILE_SURFACE = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_compile_surface.json'
OFFLINE_LADDER = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_offline_proof_ladder.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_failure_resume_card.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _plan_phase(plan: dict[str, Any], phase_id: str) -> dict[str, Any]:
    for phase in plan.get('phases') or []:
        if phase.get('phase_id') == phase_id:
            return dict(phase)
    raise KeyError(f'missing plan phase {phase_id!r}')


def _offline_phase(ladder: dict[str, Any], phase_id: str) -> dict[str, Any]:
    for phase in ladder.get('phases') or []:
        if phase.get('phase_id') == phase_id:
            return dict(phase)
    raise KeyError(f'missing ladder phase {phase_id!r}')


def _json_variant(command: str) -> str:
    cargo_prefix = 'cargo test '
    if not command.startswith(cargo_prefix):
        raise ValueError(f'unsupported cargo command for json capture: {command!r}')
    head, sep, tail = command.partition(' -- ')
    if sep:
        return f"{head} --message-format=json-render-diagnostics{sep}{tail}"
    return f"{command} --message-format=json-render-diagnostics"


def build_report() -> dict[str, Any]:
    recovery = _load_json(RECOVERY_CARD)
    plan_report = _load_json(PLAN_REPORT)
    fetch = _load_json(FETCH_SURFACE)
    compile_surface = _load_json(COMPILE_SURFACE)
    ladder = _load_json(OFFLINE_LADDER)

    plan = plan_report.get('plan') or {}
    bootstrap_phase = _plan_phase(plan, 'bootstrap')
    toolchain_phase = _plan_phase(plan, 'toolchain')
    warm_cache_phase = _plan_phase(plan, 'warm_cache')
    env_phase = _plan_phase(plan, 'env')
    cleanup_phase = _plan_phase(plan, 'cleanup')

    offline_compile = _offline_phase(ladder, 'offline_compile')
    offline_exact = _offline_phase(ladder, 'offline_exact_witness')
    offline_lane_smoke = _offline_phase(ladder, 'offline_lane_smoke')
    apply_quick = _offline_phase(ladder, 'apply_quick_foothold')

    commands = {
        'env_exports': list(env_phase.get('commands') or []),
        'bootstrap': str((bootstrap_phase.get('commands') or [''])[0]),
        'toolchain_install': str((toolchain_phase.get('commands') or ['', ''])[-1]),
        'warm_cache': str((warm_cache_phase.get('commands') or [''])[0]),
        'patch_apply': str(apply_quick.get('command') or ''),
        'offline_compile': str(offline_compile.get('command') or ''),
        'offline_exact_witness': str(offline_exact.get('command') or ''),
        'offline_lane_smoke': str(offline_lane_smoke.get('command') or ''),
        'cleanup': str((cleanup_phase.get('commands') or [''])[0]),
    }
    if not all(commands[k] for k in ['bootstrap', 'toolchain_install', 'warm_cache', 'patch_apply', 'offline_compile', 'offline_exact_witness', 'offline_lane_smoke', 'cleanup']):
        raise ValueError('missing one or more required commands for failure-resume card')

    json_capture = {
        'offline_compile': _json_variant(commands['offline_compile']),
        'offline_exact_witness': _json_variant(commands['offline_exact_witness']),
        'offline_lane_smoke': _json_variant(commands['offline_lane_smoke']),
    }

    exact_test_name = 'lift_fsm_strategy_family_lift_first_seed'
    classes = [
        {
            'class_id': 'bootstrap_command_missing',
            'phase_id': 'bootstrap',
            'resume_phase_id': 'env',
            'resume_command_key': 'bootstrap',
            'resume_command': commands['bootstrap'],
            'summary': 'The later machine does not yet have the repo-local rustup/Cargo toolchain on PATH.',
            'markers': [
                'rustup: command not found',
                'cargo: command not found',
                'no such file or directory (os error 2)',
                'command not found',
            ],
            'next_step': 'Re-export the repo-local env roots, bootstrap rustup again, then continue to toolchain install before retrying Cargo.',
            'capture_hint': 'No JSON rerun needed yet; this is still a bootstrap/path failure before Cargo itself can emit structured diagnostics.',
        },
        {
            'class_id': 'toolchain_unresolved',
            'phase_id': 'toolchain',
            'resume_phase_id': 'toolchain',
            'resume_command_key': 'toolchain_install',
            'resume_command': commands['toolchain_install'],
            'summary': 'rustup exists, but the repo-pinned toolchain/components are not fully installed or selected yet.',
            'markers': [
                'toolchain',
                'is not installed',
                'no default toolchain configured',
                'override toolchain',
                'component',
                'rustfmt',
            ],
            'next_step': 'Resume from the toolchain-install phase rather than from fetch or patch apply.',
            'capture_hint': 'Run `rustup show` immediately after reinstalling to confirm the override resolved before spending another fetch attempt.',
        },
        {
            'class_id': 'warm_cache_transport_or_registry',
            'phase_id': 'warm_cache',
            'resume_phase_id': 'warm_cache',
            'resume_command_key': 'warm_cache',
            'resume_command': commands['warm_cache'],
            'summary': 'The brief egress window failed during dependency staging.',
            'markers': [
                'spurious network error',
                'failed to download',
                'could not resolve host',
                'timed out',
                'failed to get',
                'updating crates.io index',
            ],
            'next_step': 'Spend the next egress window on `cargo fetch --locked` again before trusting any offline compile or test output.',
            'capture_hint': 'If the failure text is noisy, rerun the exact warm-cache command with `-vv` and keep the log with the later-machine note.',
        },
        {
            'class_id': 'offline_cache_incomplete_or_lock_drift',
            'phase_id': 'offline_compile',
            'resume_phase_id': 'warm_cache',
            'resume_command_key': 'warm_cache',
            'resume_command': commands['warm_cache'],
            'summary': 'The offline compile/test step is still asking for network access or wants to rewrite the lockfile.',
            'markers': [
                'attempting to make an http request, but --offline was specified',
                'failed to load source for dependency',
                'lock file cargo.lock needs to be updated but --locked was passed',
                'unable to update registry',
                'but --offline was specified',
            ],
            'next_step': 'Treat this as a return to warm-cache or lockfile reconciliation, not as a semantic test failure.',
            'capture_hint': f"Prefer the structured rerun `{json_capture['offline_compile']}` if you want Cargo/rustc diagnostics separated from later test output.",
        },
        {
            'class_id': 'patch_apply_mismatch',
            'phase_id': 'apply_quick_foothold',
            'resume_phase_id': 'apply_quick_foothold',
            'resume_command_key': 'patch_apply',
            'resume_command': commands['patch_apply'],
            'summary': 'The quick-foothold patch no longer applies cleanly to the checked-out tree.',
            'markers': [
                'patch failed',
                'does not apply',
                'corrupt patch',
                'error: patch fragment without header',
                'rejected hunk',
            ],
            'next_step': 'Refresh the comeback execution card on that later machine, inspect branch drift, and re-evaluate whether the quick foothold is still the right shard.',
            'capture_hint': 'Keep the raw `git apply` stderr; this failure is branch-state drift, not Cargo drift.',
        },
        {
            'class_id': 'compile_surface_failure',
            'phase_id': 'offline_compile',
            'resume_phase_id': 'offline_compile',
            'resume_command_key': 'offline_compile',
            'resume_command': commands['offline_compile'],
            'summary': 'The later machine reached compilation, but build/codegen/linking still failed before the exact witness could run.',
            'markers': [
                'could not compile',
                'cannot find derive macro',
                'proc-macro derive panicked',
                'failed to run custom build command',
                'linking with',
                'error[e',
            ],
            'next_step': 'Resume at the offline compile checkpoint; do not spend time rerunning the exact witness until this compiles cleanly.',
            'capture_hint': f"For machine-readable triage, rerun `{json_capture['offline_compile']}` and feed that log to `scripts/tools/classify_cloudtainer_userspace_failure.py --command-key offline_compile`.",
        },
        {
            'class_id': 'exact_witness_semantic_failure',
            'phase_id': 'offline_exact_witness',
            'resume_phase_id': 'offline_exact_witness',
            'resume_command_key': 'offline_exact_witness',
            'resume_command': commands['offline_exact_witness'],
            'summary': 'Compile succeeded; the smallest exact witness failed on semantics/assertions.',
            'markers': [
                exact_test_name,
                'assertion failed',
                'panicked at',
                'test result: failed',
                'failures:',
            ],
            'next_step': 'Stay on the exact witness first; do not broaden back to full probe_run smoke until the smallest witness is understood.',
            'capture_hint': f"If you need structured compiler plus test context, rerun `{json_capture['offline_exact_witness']}`; Cargo emits JSON until build-finished, then the test binary may add plain text.",
        },
        {
            'class_id': 'lane_smoke_semantic_failure',
            'phase_id': 'offline_lane_smoke',
            'resume_phase_id': 'offline_lane_smoke',
            'resume_command_key': 'offline_lane_smoke',
            'resume_command': commands['offline_lane_smoke'],
            'summary': 'The exact witness passed or was skipped, but the wider touched probe_run target still failed.',
            'markers': [
                'test result: failed',
                'panicked at',
                'assertion failed',
                'failures:',
                'probe_run',
            ],
            'next_step': 'Treat this as a still-localized target-level failure; widen only after understanding which additional probe_run cases joined the failure set.',
            'capture_hint': f"The structured rerun is `{json_capture['offline_lane_smoke']}`; pass `--command-key offline_lane_smoke` to the classifier so semantic failures do not fall back to the compile bucket.",
        },
    ]

    precedence = [row['class_id'] for row in classes]
    implications = [
        'This card closes the operational gap between the offline proof ladder and the first real later-machine failure: instead of reopening the whole comeback stack, the inheritor now gets one small phase-scoped resume map.',
        'The resume commands stay narrow on purpose: network trouble resumes from warm-cache, compile/codegen trouble resumes from offline compile, and semantic test failures stay pinned to the exact witness or the wider probe_run smoke phase.',
        'The emitted JSON capture variants are optional but useful because Cargo can emit line-delimited JSON messages with compiler diagnostics, artifacts, and build-script results before any later plain test-binary output begins.',
    ]
    tripwires = [
        'If the quick foothold patch path or exact witness name changes, regenerate this card before trusting the semantic-failure buckets.',
        'If the fetch surface stops being registry-only, expect the offline-cache-incomplete bucket to widen into git or alternate-registry rescue work.',
        'If the compile surface stops being direct_derive_no_native_build, treat compile-surface failures as potentially requiring new host packages rather than only proc-macro/codegen repair.',
    ]

    return {
        'tool': 'build_cloudtainer_userspace_failure_resume_card',
        'summary': {
            'current_state_code': recovery.get('summary', {}).get('current_state_code'),
            'fetch_surface_code': fetch.get('summary', {}).get('fetch_surface_code'),
            'compile_surface_code': compile_surface.get('summary', {}).get('compile_surface_code'),
            'offline_ladder_code': ladder.get('summary', {}).get('offline_ladder_code'),
            'failure_resume_code': 'phase_scoped_resume_tripwire',
            'class_count': len(classes),
            'json_capture_variant_count': len(json_capture),
            'exact_witness_test_name': exact_test_name,
            'quick_foothold_target': ladder.get('summary', {}).get('quick_foothold_target'),
            'env_export_count': len(commands['env_exports']),
            'transient_roots': list((plan_report.get('summary') or {}).get('transient_roots') or []),
        },
        'command_precedence': precedence,
        'commands': commands,
        'json_capture_commands': json_capture,
        'classes': classes,
        'implications': implications,
        'tripwires': tripwires,
    }


def emit_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    commands = report['commands']
    json_capture = report['json_capture_commands']
    lines = [
        '# Cloudtainer userspace failure resume card',
        '',
        'Generated by `scripts/report/build_cloudtainer_userspace_failure_resume_card.py`.',
        '',
        'This card is the later-machine companion to `docs/CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md`: once the first real Rust-capable machine produces a failure log, it preserves the smallest phase-scoped answer to **where to resume** and **which command to rerun** without reopening the whole comeback stack.',
        '',
        '## Summary',
        '',
        f"- current recovery state: `{summary['current_state_code']}`",
        f"- upstream fetch surface: `{summary['fetch_surface_code']}`",
        f"- upstream compile surface: `{summary['compile_surface_code']}`",
        f"- upstream offline ladder: `{summary['offline_ladder_code']}`",
        f"- failure resume code: `{summary['failure_resume_code']}`",
        f"- failure classes: `{summary['class_count']}`",
        f"- JSON capture variants: `{summary['json_capture_variant_count']}`",
        f"- exact witness name anchor: `{summary['exact_witness_test_name']}`",
        f"- quick foothold target: `{summary['quick_foothold_target']}`",
        f"- repo-local env exports carried in: `{summary['env_export_count']}`",
        f"- transient prune roots still protected: `{', '.join(summary['transient_roots'])}`",
        '',
        '## Sources carried into this card',
        '',
        '- `RS-GR-565`: Cargo offline/frozen guidance is why “network requested during offline compile” routes back to warm-cache instead of to semantic test debugging.',
        '- `RS-GR-566`: Cargo says `--message-format=json` emits line-delimited JSON messages that distinguish compiler diagnostics, produced artifacts, and build-script results with a `reason` field.',
        '- `RS-GR-567`: `cargo test` itself accepts the same `--message-format` family, so the later-machine compile/exact/smoke reruns can stay on the real test commands rather than switching to a different Cargo verb for log capture.',
        '',
        '## Core commands carried forward',
        '',
        f"- bootstrap: `{commands['bootstrap']}`",
        f"- toolchain install: `{commands['toolchain_install']}`",
        f"- warm cache: `{commands['warm_cache']}`",
        f"- patch apply: `{commands['patch_apply']}`",
        f"- offline compile: `{commands['offline_compile']}`",
        f"- offline exact witness: `{commands['offline_exact_witness']}`",
        f"- offline lane smoke: `{commands['offline_lane_smoke']}`",
        f"- cleanup: `{commands['cleanup']}`",
        '',
        '## Optional structured reruns',
        '',
        '| command key | rerun | why |',
        '| --- | --- | --- |',
        f"| `offline_compile` | `{json_capture['offline_compile']}` | keeps compile/codegen/linking diagnostics in Cargo JSON before any test-binary output exists |",
        f"| `offline_exact_witness` | `{json_capture['offline_exact_witness']}` | keeps the exact witness on the real later-machine command while still exposing compiler/build-script messages as structured lines |",
        f"| `offline_lane_smoke` | `{json_capture['offline_lane_smoke']}` | preserves the target-level smoke command while giving the classifier a cleaner Cargo diagnostic prefix |",
        '',
        '## Failure classes',
        '',
        '| class | resume from | rerun | matching markers (examples) |',
        '| --- | --- | --- | --- |',
    ]
    for row in report['classes']:
        markers = ', '.join(f'`{marker}`' for marker in row['markers'][:4])
        lines.append(
            f"| `{row['class_id']}` | `{row['resume_phase_id']}` | `{row['resume_command']}` | {markers} |"
        )
    lines.extend([
        '',
        '## Why this is worth preserving',
        '',
    ])
    for item in report['implications']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Resume details',
        '',
    ])
    for row in report['classes']:
        lines.append(f"### `{row['class_id']}`")
        lines.append('')
        lines.append(f"- phase that failed: `{row['phase_id']}`")
        lines.append(f"- resume from: `{row['resume_phase_id']}`")
        lines.append(f"- rerun command: `{row['resume_command']}`")
        lines.append(f"- interpretation: {row['summary']}")
        lines.append(f"- next step: {row['next_step']}")
        lines.append(f"- capture hint: {row['capture_hint']}")
        lines.append(f"- marker set: {', '.join(f'`{marker}`' for marker in row['markers'])}")
        lines.append('')
    lines.extend([
        '## Classifier usage',
        '',
        '```bash',
        'python3 scripts/tools/classify_cloudtainer_userspace_failure.py \\\n  --command-key offline_compile \\\n  --input later_machine_failure.log',
        '```',
        '',
        '```bash',
        f"{json_capture['offline_exact_witness']} 2>&1 | tee later_machine_failure.log",
        'python3 scripts/tools/classify_cloudtainer_userspace_failure.py \\\n  --command-key offline_exact_witness \\\n  --input later_machine_failure.log --format text',
        '```',
        '',
        '## Tripwires',
        '',
    ])
    for item in report['tripwires']:
        lines.append(f'- {item}')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the later-machine userspace failure resume card.')
    parser.add_argument('--write', action='store_true', help='write the generated JSON and markdown outputs')
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report, indent=2, sort_keys=True) + '\n'
    markdown = emit_markdown(report)

    if args.write:
        OUT_JSON.write_text(payload, encoding='utf-8')
        OUT_MD.write_text(markdown, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
    else:
        print(payload, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
