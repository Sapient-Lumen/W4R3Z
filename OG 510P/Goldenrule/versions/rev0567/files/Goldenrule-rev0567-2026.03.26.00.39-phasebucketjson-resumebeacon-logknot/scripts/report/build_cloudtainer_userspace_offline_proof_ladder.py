#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECOVERY_CARD = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
FETCH_SURFACE = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_fetch_surface.json'
COMPILE_SURFACE = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_compile_surface.json'
PLAN_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_rustup_plan.json'
EXECUTION_CARD = ROOT / 'artifacts' / 'reports' / 'rust_comeback_execution_card.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_offline_proof_ladder.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _cargo_test_variant(command: str, *, offline: bool = False, no_run: bool = False) -> str:
    prefix = 'cargo test '
    if not command.startswith(prefix):
        raise ValueError(f'unsupported cargo test command shape: {command!r}')
    flags: list[str] = []
    if offline:
        flags.extend(['--locked', '--offline'])
    if no_run:
        flags.append('--no-run')
    remainder = command[len(prefix):]
    flag_prefix = (' '.join(flags) + ' ') if flags else ''
    return f'cargo test {flag_prefix}{remainder}'


def _plan_phase(plan: dict[str, Any], phase_id: str) -> dict[str, Any]:
    for phase in plan.get('phases') or []:
        if phase.get('phase_id') == phase_id:
            return dict(phase)
    raise KeyError(f'missing plan phase {phase_id!r}')


def _plateau_card(execution: dict[str, Any], label: str) -> dict[str, Any]:
    for card in execution.get('plateau_cards') or []:
        if card.get('label') == label:
            return dict(card)
    raise KeyError(f'missing execution plateau {label!r}')


def build_report() -> dict[str, Any]:
    recovery = _load_json(RECOVERY_CARD)
    fetch = _load_json(FETCH_SURFACE)
    compile_surface = _load_json(COMPILE_SURFACE)
    plan_report = _load_json(PLAN_REPORT)
    execution = _load_json(EXECUTION_CARD)

    summary_recovery = recovery.get('summary') or {}
    summary_fetch = fetch.get('summary') or {}
    summary_compile = compile_surface.get('summary') or {}
    plan = plan_report.get('plan') or {}
    warm_cache_phase = _plan_phase(plan, 'warm_cache')
    cleanup_phase = _plan_phase(plan, 'cleanup')
    quick_foothold = _plateau_card(execution, 'quick_foothold')

    patch_command = str(summary_recovery.get('first_machine_quick_foothold_apply_hint') or quick_foothold.get('apply_hint') or '')
    if not patch_command:
        raise ValueError('missing quick foothold patch command')

    exact_witness_commands = [str(v) for v in (quick_foothold.get('cumulative_exact_witness_commands') or [])]
    if len(exact_witness_commands) != 1:
        raise ValueError(f'unexpected quick foothold exact witness commands: {exact_witness_commands!r}')
    exact_witness_command = exact_witness_commands[0]

    lane_smoke_commands = [str(v) for v in (quick_foothold.get('lane_smoke_commands') or [])]
    if len(lane_smoke_commands) != 1:
        raise ValueError(f'unexpected quick foothold lane smoke commands: {lane_smoke_commands!r}')
    lane_smoke_command = lane_smoke_commands[0]

    offline_compile_command = _cargo_test_variant(lane_smoke_command, offline=True, no_run=True)
    offline_exact_command = _cargo_test_variant(exact_witness_command, offline=True)
    offline_lane_smoke_command = _cargo_test_variant(lane_smoke_command, offline=True)

    phases = [
        {
            'phase_id': 'warm_cache',
            'network_required': True,
            'command': str((warm_cache_phase.get('commands') or [''])[0]),
            'intent': 'download the locked dependency graph while HTTPS egress still exists',
        },
        {
            'phase_id': 'health_check',
            'network_required': False,
            'commands': ['rustup show', 'make doctor', 'make update-rust-comeback-execution-card'],
            'intent': 'confirm the toolchain resolved correctly and refresh the current patch/test card before editing',
        },
        {
            'phase_id': 'apply_quick_foothold',
            'network_required': False,
            'command': patch_command,
            'intent': 'land the smallest external Rust witness without widening to later shards',
        },
        {
            'phase_id': 'offline_compile',
            'network_required': False,
            'command': offline_compile_command,
            'intent': 'compile the touched probe_run target without running it; if this fails, the issue is build/cache state rather than test semantics',
        },
        {
            'phase_id': 'offline_exact_witness',
            'network_required': False,
            'command': offline_exact_command,
            'intent': 'run the smallest exact witness after compile succeeds, while still forbidding network access',
        },
        {
            'phase_id': 'offline_lane_smoke',
            'network_required': False,
            'command': offline_lane_smoke_command,
            'intent': 'broaden to the full touched test target only after the exact witness passes',
        },
        {
            'phase_id': 'cleanup',
            'network_required': False,
            'command': str((cleanup_phase.get('commands') or [''])[0]),
            'intent': 'delete transient userspace toolchain/build roots before the next retained archive cut',
        },
    ]

    interpretations = [
        {
            'phase_id': 'warm_cache',
            'if_it_fails': 'Treat failure here as bootstrap or egress trouble: the later machine still cannot fully stage the locked dependency graph.',
        },
        {
            'phase_id': 'offline_compile',
            'if_it_fails': 'If Cargo complains about missing downloads or network access at this step, the warmed cache is incomplete or the lockfile/toolchain surface drifted after fetch.',
        },
        {
            'phase_id': 'offline_exact_witness',
            'if_it_fails': 'If compile succeeded but the exact witness fails, the problem moved past bootstrap and into patch/test semantics or model behavior.',
        },
        {
            'phase_id': 'offline_lane_smoke',
            'if_it_fails': 'If the exact witness passes but lane smoke fails, the blast radius is still confined to the current probe_run target rather than the whole workspace.',
        },
    ]

    implications = [
        'This ladder preserves one disciplined answer to “did the warmed cache really buy me offline execution?” instead of assuming that a successful fetch implies the first compile/test witness will stay network-free.',
        'The inserted offline compile step uses the same quick-foothold target as the recovery card, but stops before execution so the inheritor can separate build/cache trouble from semantic test trouble.',
        'The emitted commands stay explicit with --locked --offline instead of collapsing to --frozen, so later-machine logs make it obvious which reproducibility and network guards were intended.',
        'Cleanup remains the full .local cargo/rustup/target prune from the userspace-rustup plan, so this proof ladder does not weaken the archive-size discipline established in the previous passes.',
    ]
    tripwires = [
        'If the quick foothold stops being shard prefix 1, refresh this ladder before trusting the emitted exact witness commands.',
        'If the later-machine fetch surface stops being registry_only_single_workspace, treat the offline compile step as a stronger stress test and widen the egress/debug budget.',
        'If the compile surface stops being direct_derive_no_native_build, expect offline compile failures to include local build-script or native-helper rescue work instead of pure cache/bootstrap trouble.',
    ]

    return {
        'tool': 'build_cloudtainer_userspace_offline_proof_ladder',
        'summary': {
            'current_state_code': summary_recovery.get('current_state_code'),
            'fetch_surface_code': summary_fetch.get('fetch_surface_code'),
            'compile_surface_code': summary_compile.get('compile_surface_code'),
            'offline_ladder_code': 'fetch_then_offline_compile_then_exact',
            'quick_foothold_label': quick_foothold.get('label'),
            'quick_foothold_prefix': quick_foothold.get('prefix_index'),
            'quick_foothold_patch_path': quick_foothold.get('latest_patch_path'),
            'quick_foothold_target': (quick_foothold.get('test_targets') or [''])[0],
            'quick_foothold_exact_witness_count': quick_foothold.get('new_exact_witness_count'),
            'phase_ids': [phase['phase_id'] for phase in phases],
            'network_required_phase_count': sum(1 for phase in phases if phase.get('network_required')),
            'transient_roots': list((plan_report.get('summary') or {}).get('transient_roots') or []),
        },
        'commands': {
            'warm_cache': phases[0]['command'],
            'patch_apply': patch_command,
            'offline_compile_no_run': offline_compile_command,
            'offline_exact_witness': offline_exact_command,
            'offline_lane_smoke': offline_lane_smoke_command,
            'cleanup': phases[-1]['command'],
        },
        'phases': phases,
        'failure_interpretation': interpretations,
        'implications': implications,
        'tripwires': tripwires,
    }


def emit_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    commands = report['commands']
    lines = [
        '# Cloudtainer userspace offline proof ladder',
        '',
        'Generated by `scripts/report/build_cloudtainer_userspace_offline_proof_ladder.py`.',
        '',
        'This card is the execution companion to the userspace fetch/compile audits: once a later machine has warmed the locked cache, it records the smallest command ladder that proves the comeback lane can keep moving **offline** before widening to more Rust work.',
        '',
        '## Summary',
        '',
        f"- current recovery state: `{summary['current_state_code']}`",
        f"- upstream fetch surface: `{summary['fetch_surface_code']}`",
        f"- upstream compile surface: `{summary['compile_surface_code']}`",
        f"- offline ladder code: `{summary['offline_ladder_code']}`",
        f"- quick foothold plateau: `{summary['quick_foothold_label']}` at shard prefix `{summary['quick_foothold_prefix']}`",
        f"- touched test target: `{summary['quick_foothold_target']}`",
        f"- network-required phases: `{summary['network_required_phase_count']}` of `{len(report['phases'])}`",
        f"- transient prune roots: `{', '.join(summary['transient_roots'])}`",
        '',
        '## Sources carried into this ladder',
        '',
        '- `RS-GR-560`: `cargo fetch --locked` can stage later offline commands while `Cargo.lock` stays unchanged.',
        '- `RS-GR-564`: `cargo test --no-run` compiles the selected test target without executing it, which makes it the cleanest offline compile checkpoint before the exact witness.',
        '- `RS-GR-565`: Cargo\'s offline / frozen guidance says network access is forbidden and should error instead of silently falling back online, which is exactly the guard this ladder wants.',
        '',
        '## Command ladder',
        '',
        '| phase | network? | command | purpose |',
        '| --- | --- | --- | --- |',
    ]
    for phase in report['phases']:
        command_cell = ' / '.join(f'`{cmd}`' for cmd in phase.get('commands', [phase.get('command')]))
        lines.append(
            f"| `{phase['phase_id']}` | `{'yes' if phase['network_required'] else 'no'}` | {command_cell} | {phase['intent']} |"
        )
    lines.extend([
        '',
        '## Why this is the right narrow proof',
        '',
    ])
    for item in report['implications']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Failure interpretation',
        '',
        '| phase | what a failure means now |',
        '| --- | --- |',
    ])
    for row in report['failure_interpretation']:
        lines.append(f"| `{row['phase_id']}` | {row['if_it_fails']} |")
    lines.extend([
        '',
        '## Exact commands at a glance',
        '',
        f"- warm cache: `{commands['warm_cache']}`",
        f"- apply patch: `{commands['patch_apply']}`",
        f"- offline compile only: `{commands['offline_compile_no_run']}`",
        f"- offline exact witness: `{commands['offline_exact_witness']}`",
        f"- offline lane smoke: `{commands['offline_lane_smoke']}`",
        f"- cleanup: `{commands['cleanup']}`",
        '',
        '## Tripwires',
        '',
    ])
    for item in report['tripwires']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Reentry use',
        '',
        '- Open this card after `docs/CLOUDTAINER_USERSPACE_FETCH_SURFACE.md` and `docs/CLOUDTAINER_USERSPACE_COMPILE_SURFACE.md` when you want one execution sequence that proves the warmed cache is genuinely sufficient for the first comeback witness.',
        '- Open `docs/CLOUDTAINER_USERSPACE_RUSTUP_PLAN.md` when you still need the full bootstrap/export/install lane; this card intentionally starts at the lockfile warm-cache seam and then stays offline.',
        '- Keep the commands explicit with `--locked --offline` in transcripts even though Cargo also offers `--frozen`; the extra verbosity is useful when reading later-machine logs in the archive.',
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build an offline-proof command ladder for the later-machine userspace Rust comeback lane.')
    parser.add_argument('--write', action='store_true', help='write the JSON and markdown outputs instead of printing JSON only')
    args = parser.parse_args()

    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(emit_markdown(report), encoding='utf-8')
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
