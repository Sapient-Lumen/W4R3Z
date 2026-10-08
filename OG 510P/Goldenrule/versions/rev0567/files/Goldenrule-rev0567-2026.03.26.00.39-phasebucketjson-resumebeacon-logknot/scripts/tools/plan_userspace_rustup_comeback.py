#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CARGO_HOME = '.local/cargo'
DEFAULT_RUSTUP_HOME = '.local/rustup'
DEFAULT_TARGET_DIR = '.local/target'
DEFAULT_PROFILE = 'minimal'
RECOVERY_CARD = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
TOOLCHAIN_FILE = ROOT / 'rust-toolchain.toml'


def _load_toolchain(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding='utf-8'))
    toolchain = dict(data.get('toolchain') or {})
    components = [str(component) for component in toolchain.get('components', [])]
    targets = [str(target) for target in toolchain.get('targets', [])]
    return {
        'channel': str(toolchain.get('channel', 'stable')),
        'profile': str(toolchain.get('profile', DEFAULT_PROFILE)),
        'components': components,
        'targets': targets,
    }


def _load_recovery_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding='utf-8'))
    summary = dict(payload.get('summary') or {})
    bridge = dict(payload.get('current_bridge') or {})
    return {
        'current_state_code': summary.get('current_state_code'),
        'preferred_lane_id': summary.get('preferred_lane_id'),
        'rust_available_now': summary.get('rust_available_now'),
        'documented_in_place_recovery_possible': summary.get('documented_in_place_recovery_possible'),
        'bridge_mode': bridge.get('mode'),
        'bridge_reason': bridge.get('reason'),
    }


def _q(text: str) -> str:
    return shlex.quote(text)


def build_plan(
    *,
    root: Path = ROOT,
    cargo_home: str = DEFAULT_CARGO_HOME,
    rustup_home: str = DEFAULT_RUSTUP_HOME,
    target_dir: str = DEFAULT_TARGET_DIR,
    profile: str = DEFAULT_PROFILE,
    recovery_card: Path = RECOVERY_CARD,
    toolchain_file: Path = TOOLCHAIN_FILE,
) -> dict[str, Any]:
    toolchain = _load_toolchain(toolchain_file)
    requested_profile = profile or toolchain.get('profile') or DEFAULT_PROFILE
    channel = str(toolchain['channel'])
    components = list(toolchain['components'])
    targets = list(toolchain['targets'])
    recovery = _load_recovery_summary(recovery_card)
    cargo_lock_present = (root / 'Cargo.lock').exists()

    env_exports = [
        f'export CARGO_HOME="$PWD/{cargo_home}"',
        f'export RUSTUP_HOME="$PWD/{rustup_home}"',
        f'export CARGO_TARGET_DIR="$PWD/{target_dir}"',
        'export PATH="$CARGO_HOME/bin:$PATH"',
    ]

    install_cmd = (
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs "
        "| sh -s -- --default-toolchain none -y"
    )
    rustup_set_profile_cmd = f'rustup set profile {shlex.quote(requested_profile)}'
    install_parts = [
        'rustup', 'toolchain', 'install', shlex.quote(channel), '--profile', shlex.quote(requested_profile),
    ]
    for component in components:
        install_parts.extend(['--component', shlex.quote(component)])
    for target in targets:
        install_parts.extend(['--target', shlex.quote(target)])
    toolchain_install_cmd = ' '.join(install_parts)

    warm_cache_cmds: list[str] = []
    if cargo_lock_present:
        warm_cache_cmds.append('cargo fetch --locked')

    proof_cmds = [
        'rustup show',
        'make doctor',
        'make update-rust-comeback-execution-card',
        'git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch',
        'cargo test -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact',
        'cargo test -p gr_engine --test probe_run',
    ]

    cleanup_cmds = [
        f'rm -rf {_q(cargo_home)} {_q(rustup_home)} {_q(target_dir)}',
    ]

    notes = [
        'This plan is for a later machine with HTTPS egress and write access under the repo or $HOME; do not waste time trying it in the current JuNest-binary-missing cloudtainer state.',
        'Use a repo-local target/build cache root so compiled artifacts stay easy to delete before the next archive cut.',
        'Warm the dependency cache while the network is available, then run the smallest existing Rust foothold instead of widening immediately to the full test surface.',
        'Treat .local cargo/rustup/target roots as transient scratch, not durable archive content.',
    ]
    if targets:
        notes.append('The repo toolchain file also requests explicit compilation targets; the emitted install command includes them so the userspace toolchain matches the checked-in override.')
    if components:
        notes.append('The repo toolchain file requests additive components on top of the chosen profile; the emitted install command carries those component flags explicitly.')
    if cargo_lock_present:
        notes.append('Cargo.lock is present, so cargo fetch --locked is included to preserve deterministic dependency resolution while staging the offline cache.')

    return {
        'tool': 'plan_userspace_rustup_comeback',
        'root': root.as_posix(),
        'recovery_context': recovery,
        'toolchain': toolchain,
        'paths': {
            'cargo_home': cargo_home,
            'rustup_home': rustup_home,
            'target_dir': target_dir,
        },
        'cargo_lock_present': cargo_lock_present,
        'phases': [
            {'phase_id': 'env', 'label': 'export repo-local toolchain roots', 'commands': env_exports},
            {'phase_id': 'bootstrap', 'label': 'install rustup without selecting a default toolchain yet', 'commands': [install_cmd]},
            {'phase_id': 'toolchain', 'label': 'select minimal profile and install the repo-pinned toolchain plus additive components', 'commands': [rustup_set_profile_cmd, toolchain_install_cmd]},
            {'phase_id': 'warm_cache', 'label': 'stage dependency cache while network exists', 'commands': warm_cache_cmds},
            {'phase_id': 'first_proof', 'label': 'take the smallest existing Rust comeback witness', 'commands': proof_cmds},
            {'phase_id': 'cleanup', 'label': 'prune transient userspace toolchain roots before the next archive cut', 'commands': cleanup_cmds},
        ],
        'notes': notes,
    }


def emit_shell(plan: dict[str, Any]) -> str:
    lines = [
        '# userspace rustup comeback plan',
        '# generated by scripts/tools/plan_userspace_rustup_comeback.py',
    ]
    for phase in plan['phases']:
        lines.append(f"\n# [{phase['phase_id']}] {phase['label']}")
        commands = phase.get('commands') or []
        if not commands:
            lines.append('# no commands for this phase in the current repo state')
            continue
        lines.extend(commands)
    return '\n'.join(lines) + '\n'


def emit_markdown(plan: dict[str, Any]) -> str:
    recovery = plan.get('recovery_context') or {}
    toolchain = plan['toolchain']
    paths = plan['paths']
    components = toolchain.get('components') or []
    targets = toolchain.get('targets') or []

    lines = [
        '# Userspace rustup comeback plan',
        '',
        'Generated by `scripts/tools/plan_userspace_rustup_comeback.py`.',
        '',
        '## Summary',
        '',
        f"- current recovery state: `{recovery.get('current_state_code') or 'unknown'}`",
        f"- current bridge mode: `{recovery.get('bridge_mode') or 'unknown'}`",
        f"- repo toolchain channel: `{toolchain['channel']}`",
        f"- requested profile: `{toolchain['profile']}`",
        f"- additive components: `{', '.join(components) if components else 'none'}`",
        f"- additive targets: `{', '.join(targets) if targets else 'none'}`",
        f"- repo-local `CARGO_HOME`: `{paths['cargo_home']}`",
        f"- repo-local `RUSTUP_HOME`: `{paths['rustup_home']}`",
        f"- repo-local `CARGO_TARGET_DIR`: `{paths['target_dir']}`",
        f"- `Cargo.lock` present: `{str(plan['cargo_lock_present']).lower()}`",
        '',
        '## Notes',
        '',
    ]
    for note in plan['notes']:
        lines.append(f'- {note}')
    lines.extend(['', '## Phases', ''])
    for phase in plan['phases']:
        lines.append(f"### `{phase['phase_id']}` — {phase['label']}")
        lines.append('')
        commands = phase.get('commands') or []
        if commands:
            lines.append('```bash')
            lines.extend(commands)
            lines.append('```')
        else:
            lines.append('_No commands emitted for this phase in the current repo state._')
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Emit a deterministic userspace rustup comeback plan for a later HTTPS-capable machine.')
    parser.add_argument('--emit', choices=['json', 'shell', 'markdown'], default='json')
    parser.add_argument('--cargo-home', default=DEFAULT_CARGO_HOME)
    parser.add_argument('--rustup-home', default=DEFAULT_RUSTUP_HOME)
    parser.add_argument('--target-dir', default=DEFAULT_TARGET_DIR)
    parser.add_argument('--profile', default=DEFAULT_PROFILE)
    args = parser.parse_args()

    plan = build_plan(
        cargo_home=args.cargo_home,
        rustup_home=args.rustup_home,
        target_dir=args.target_dir,
        profile=args.profile,
    )
    if args.emit == 'json':
        print(json.dumps(plan, indent=2, sort_keys=True))
    elif args.emit == 'shell':
        print(emit_shell(plan), end='')
    else:
        print(emit_markdown(plan), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
