#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'
BUDGET_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_budget_card.json'
COMEBACK_EXECUTION_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_comeback_execution_card.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_RUST_RECOVERY_CARD.md'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _execution_lanes_snapshot() -> dict[str, Any]:
    module = _load_module('build_cooperation_benchmark_card_execution_lanes', EXECUTION_LANES_BUILDER)
    collected = module.collect()
    return {
        'preferred_lane_id': collected['preferred_lane_id'],
        'counts': dict(collected['counts']),
        'observation': dict(collected['observation']),
        'rust_lane': next(lane for lane in collected['lanes'] if lane['lane_id'] == 'rust-harness'),
    }


def _state_code(rust_lane: dict[str, Any], observation: dict[str, Any]) -> str:
    basis = str(rust_lane['availability_basis'])
    blocking = set(rust_lane.get('blocking_reason_codes') or [])
    if basis == 'native-rust':
        return 'native_ready'
    if basis == 'junest-rust':
        return 'junest_ready'
    if 'junest-binary-missing' in blocking:
        return 'junest_binary_missing'
    if 'junest-home-missing' in blocking:
        return 'junest_home_missing'
    if 'junest-rust-toolchain-missing' in blocking:
        return 'junest_toolchain_missing'
    if not observation.get('rust_exec_present', False):
        return 'rust_exec_missing'
    return 'rust_unavailable_other'


def _state_cards(
    *,
    rust_lane: dict[str, Any],
    observation: dict[str, Any],
    current_state_code: str,
    medium_budget: dict[str, Any],
    quick_foothold: dict[str, Any],
) -> list[dict[str, Any]]:
    junest_home = observation.get('junest_home_path') or '.sandworm/toolroot/junest-home'
    setup_cmd = f'env SW_JUNEST_HOME="$PWD/{junest_home}" /run/sandworm/toolroot/bin/junest setup'
    install_cmd = (
        f'env SW_JUNEST_HOME="$PWD/{junest_home}" /run/sandworm/toolroot/bin/junest ns -f -- sh -lc '
        '"pacman -Syy --noconfirm && pacman -Sy --noconfirm archlinux-keyring && pacman -S --noconfirm rust"'
    )

    cards = [
        {
            'state_code': 'native_ready',
            'current': current_state_code == 'native_ready',
            'condition_summary': 'native `cargo` and `rustc` are both visible on PATH; no JuNest bootstrap is required.',
            'next_commands': ['make doctor', 'make test-quick'],
            'success_witness': 'the Rust lane stays available with `availability_basis=native-rust`, then `make test-quick` advances beyond the wrapper boundary.',
        },
        {
            'state_code': 'junest_ready',
            'current': current_state_code == 'junest_ready',
            'condition_summary': 'JuNest exists, the JuNest home exists, and both `cargo` and `rustc` resolve inside that home.',
            'next_commands': ['make doctor', 'make test-quick'],
            'success_witness': 'the Rust lane stays available with `availability_basis=junest-rust`, then `make test-quick` advances beyond the wrapper boundary.',
        },
        {
            'state_code': 'junest_home_missing',
            'current': current_state_code == 'junest_home_missing',
            'condition_summary': 'the JuNest binary exists but the configured JuNest home has not been initialized yet.',
            'next_commands': [setup_cmd, 'make doctor', 'make test-quick'],
            'success_witness': 'the next execution-lane snapshot flips `junest_home_present=true`; if Rust is already installed inside that home, the lane upgrades to `availability_basis=junest-rust`.',
        },
        {
            'state_code': 'junest_toolchain_missing',
            'current': current_state_code == 'junest_toolchain_missing',
            'condition_summary': 'the JuNest binary and home exist, but `cargo`/`rustc` do not both resolve inside JuNest yet.',
            'next_commands': [install_cmd, 'make doctor', 'make test-quick'],
            'success_witness': 'the next execution-lane snapshot shows non-null `junest_cargo_version` and `junest_rustc_version`, then `make test-quick` crosses the Rust wrapper boundary.',
        },
        {
            'state_code': 'junest_binary_missing',
            'current': current_state_code == 'junest_binary_missing',
            'condition_summary': 'native Rust is absent and the documented JuNest entrypoint `/run/sandworm/toolroot/bin/junest` is missing, so the in-place bootstrap ladder cannot even start here.',
            'next_commands': [
                medium_budget['command'],
                'make update-rust-comeback-execution-card',
                quick_foothold['apply_hint'],
            ],
            'success_witness': 'stay productive on the static lane in this cloudtainer; move the first real Rust witness to a later machine that can execute the quick foothold shard.',
        },
    ]
    if current_state_code == 'rust_exec_missing':
        cards.append(
            {
                'state_code': 'rust_exec_missing',
                'current': True,
                'condition_summary': 'the repo wrapper `tools/rust_exec.sh` is missing, so the normal Rust entrypoint is broken before capability detection finishes.',
                'next_commands': ['git status --short tools/rust_exec.sh', 'git checkout -- tools/rust_exec.sh', 'make doctor'],
                'success_witness': 'the wrapper path exists again and the execution-lane snapshot can classify native versus JuNest Rust normally.',
            }
        )
    if current_state_code == 'rust_unavailable_other':
        cards.append(
            {
                'state_code': 'rust_unavailable_other',
                'current': True,
                'condition_summary': 'the Rust lane is unavailable for a reason that does not collapse to the standard native/JuNest missing-home/missing-toolchain ladder.',
                'next_commands': ['make doctor', medium_budget['command']],
                'success_witness': 'either a later execution-lane snapshot resolves to one of the standard recovery states, or the blocked session keeps the static handoff surfaces current.',
            }
        )
    return cards


def build_report() -> dict[str, Any]:
    execution = _execution_lanes_snapshot()
    budget = _load_json(BUDGET_REPORT)
    comeback = _load_json(COMEBACK_EXECUTION_REPORT)

    rust_lane = dict(execution['rust_lane'])
    observation = dict(execution['observation'])
    current_state_code = _state_code(rust_lane, observation)
    rust_available = bool(rust_lane['available'])
    blocking = list(rust_lane.get('blocking_reason_codes') or [])
    medium_budget = next(card for card in budget['budget_cards'] if card['label'] == 'medium_budget')
    quick_foothold = next(card for card in comeback['plateau_cards'] if card['label'] == 'quick_foothold')
    full_closure = next(card for card in comeback['plateau_cards'] if card['label'] == 'full_closure')

    documented_in_place_recovery = current_state_code in {
        'native_ready',
        'junest_ready',
        'junest_home_missing',
        'junest_toolchain_missing',
    }

    if current_state_code == 'native_ready':
        current_bridge = {
            'mode': 'run_rust_now',
            'reason': 'Native Rust is already available; stop spending time on bootstrap scaffolding and cross the real harness gate.',
            'next_commands': ['make doctor', 'make test-quick'],
        }
    elif current_state_code == 'junest_ready':
        current_bridge = {
            'mode': 'run_rust_now',
            'reason': 'JuNest-backed Rust is already available; the wrapper boundary is no longer the blocker.',
            'next_commands': ['make doctor', 'make test-quick'],
        }
    elif current_state_code == 'junest_home_missing':
        current_bridge = {
            'mode': 'bootstrap_in_place',
            'reason': 'The documented recovery ladder can still succeed in this cloudtainer because the JuNest binary exists; initialize the home before doing anything else.',
            'next_commands': [
                next(card for card in _state_cards(rust_lane=rust_lane, observation=observation, current_state_code=current_state_code, medium_budget=medium_budget, quick_foothold=quick_foothold) if card['state_code'] == 'junest_home_missing')['next_commands'][0],
                'make doctor',
                'make test-quick',
            ],
        }
    elif current_state_code == 'junest_toolchain_missing':
        current_bridge = {
            'mode': 'bootstrap_in_place',
            'reason': 'The JuNest shell exists but the Rust toolchain is still absent there; install it before retrying the harness.',
            'next_commands': [
                next(card for card in _state_cards(rust_lane=rust_lane, observation=observation, current_state_code=current_state_code, medium_budget=medium_budget, quick_foothold=quick_foothold) if card['state_code'] == 'junest_toolchain_missing')['next_commands'][0],
                'make doctor',
                'make test-quick',
            ],
        }
    else:
        current_bridge = {
            'mode': 'stay_static_here',
            'reason': 'The documented in-place recovery ladder is blocked before setup/install because the JuNest binary itself is absent or the wrapper state is nonstandard.',
            'next_commands': [
                medium_budget['command'],
                medium_budget['resume_command'],
                'make update-rust-comeback-execution-card',
            ],
            'blocked_session_budget_seconds': medium_budget['buffered_budget_seconds'],
            'first_machine_quick_foothold': {
                'refresh_command': 'make update-rust-comeback-execution-card',
                'apply_hint': quick_foothold['apply_hint'],
                'exact_witness_commands': quick_foothold['new_exact_witness_commands'],
                'lane_smoke_commands': quick_foothold['lane_smoke_commands'],
            },
        }

    state_cards = _state_cards(
        rust_lane=rust_lane,
        observation=observation,
        current_state_code=current_state_code,
        medium_budget=medium_budget,
        quick_foothold=quick_foothold,
    )

    headline_findings = [
        (
            f"Current Rust availability basis is `{rust_lane['availability_basis']}` with blocking codes "
            f"{', '.join('`' + code + '`' for code in blocking) if blocking else 'none'}; "
            f"the environment therefore classifies as `{current_state_code}`."
        ),
        (
            'There is a real distinction between “recoverable here” and “blocked before recovery starts”: '
            'JuNest-home-missing and JuNest-toolchain-missing are salvageable inside this cloudtainer, but JuNest-binary-missing is not.'
        ),
        (
            f"When recovery is impossible here, the best blocked-session fallback remains `{medium_budget['command']}`; "
            f"it refreshes the comeback queue and seed-loader inputs in about `{medium_budget['buffered_budget_seconds']}` buffered seconds."
        ),
        (
            f"The first real Rust foothold on a capable machine is still `{quick_foothold['label']}`: apply `{quick_foothold['latest_patch_path']}` and run "
            f"`{quick_foothold['new_exact_witness_commands'][0]}` before broadening to `{quick_foothold['lane_smoke_commands'][0]}`."
        ),
        (
            f"Full comeback closure still ends at shard prefix `{full_closure['prefix_index']}` over targets "
            f"{', '.join('`' + target + '`' for target in full_closure['test_targets'])}; there is no earlier pure probe-only closure plateau."
        ),
    ]

    return {
        'metadata': {
            'inventory_version': 1,
            'source_reports': [
                BUDGET_REPORT.relative_to(ROOT).as_posix(),
                COMEBACK_EXECUTION_REPORT.relative_to(ROOT).as_posix(),
            ],
            'source_builder': EXECUTION_LANES_BUILDER.relative_to(ROOT).as_posix(),
        },
        'summary': {
            'preferred_lane_id': execution['preferred_lane_id'],
            'available_lane_count': int(execution['counts']['available_lane_count']),
            'blocked_lane_count': int(execution['counts']['blocked_lane_count']),
            'current_state_code': current_state_code,
            'rust_available': rust_available,
            'availability_basis': str(rust_lane['availability_basis']),
            'blocking_reason_codes': blocking,
            'documented_in_place_recovery': documented_in_place_recovery,
            'native_cargo_present': observation.get('native_cargo_version') is not None,
            'native_rustc_present': observation.get('native_rustc_version') is not None,
            'junest_bin_present': observation.get('junest_bin_path') is not None,
            'junest_home_present': bool(observation.get('junest_home_present')),
            'junest_rust_available': bool(observation.get('junest_rust_available')),
            'blocked_session_fallback_command': medium_budget['command'],
            'blocked_session_fallback_buffered_seconds': medium_budget['buffered_budget_seconds'],
            'first_machine_quick_foothold_apply_hint': quick_foothold['apply_hint'],
            'first_machine_quick_foothold_exact_witness_count': quick_foothold['new_exact_witness_count'],
            'full_closure_prefix': int(full_closure['prefix_index']),
        },
        'observation': observation,
        'current_bridge': current_bridge,
        'state_cards': state_cards,
        'headline_findings': headline_findings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    observation = report['observation']
    lines = [
        '# Cloudtainer Rust Recovery Card',
        '',
        'Generated by `scripts/report/build_cloudtainer_rust_recovery_card.py`. This fuses the live execution-lane observation with the shadow-pass budget card and the Rust comeback execution card so an inheritor can tell whether Rust is recoverable inside the current cloudtainer, when to stop trying, and what the first real Rust foothold should be on the next capable machine.',
        '',
        '## Summary',
        '',
        f"- preferred lane: `{summary['preferred_lane_id']}`",
        f"- current state: `{summary['current_state_code']}`",
        f"- Rust available now: `{str(summary['rust_available']).lower()}` via `{summary['availability_basis']}`",
        f"- blocking reason codes: {', '.join('`' + code + '`' for code in summary['blocking_reason_codes']) if summary['blocking_reason_codes'] else 'none'}",
        f"- documented in-place recovery possible: `{str(summary['documented_in_place_recovery']).lower()}`",
        f"- blocked-session fallback command: `{summary['blocked_session_fallback_command']}` (~`{summary['blocked_session_fallback_buffered_seconds']}` buffered seconds)",
        f"- first-machine quick foothold apply hint: `{summary['first_machine_quick_foothold_apply_hint']}`",
        f"- full closure prefix: `{summary['full_closure_prefix']}`",
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')

    lines.extend([
        '',
        '## Current observation',
        '',
        '| field | value |',
        '|---|---|',
    ])
    for key in [
        'python3_version',
        'native_cargo_version',
        'native_rustc_version',
        'junest_bin_path',
        'junest_home_path',
        'junest_home_present',
        'junest_cargo_version',
        'junest_rustc_version',
        'junest_rust_available',
        'rust_exec_path',
        'rust_exec_present',
    ]:
        value = observation.get(key)
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif value is None:
            rendered = 'none'
        else:
            rendered = f'`{value}`'
        lines.append(f'| `{key}` | {rendered} |')

    lines.extend([
        '',
        '## Current bridge',
        '',
        f"- mode: `{report['current_bridge']['mode']}`",
        f"- why: {report['current_bridge']['reason']}",
        '- next commands:',
    ])
    for command in report['current_bridge']['next_commands']:
        lines.append(f'  - `{command}`')
    if 'blocked_session_budget_seconds' in report['current_bridge']:
        lines.append(f"- blocked-session buffered budget: `{report['current_bridge']['blocked_session_budget_seconds']}` seconds")
    if 'first_machine_quick_foothold' in report['current_bridge']:
        bridge = report['current_bridge']['first_machine_quick_foothold']
        lines.extend([
            '- first-machine quick foothold:',
            f"  - refresh: `{bridge['refresh_command']}`",
            f"  - apply: `{bridge['apply_hint']}`",
        ])
        for command in bridge['exact_witness_commands']:
            lines.append(f'  - exact witness: `{command}`')
        for command in bridge['lane_smoke_commands']:
            lines.append(f'  - lane smoke: `{command}`')

    lines.extend([
        '',
        '## Recovery state ladder',
        '',
    ])
    for card in report['state_cards']:
        lines.extend([
            f"### `{card['state_code']}`{' ← current' if card['current'] else ''}",
            '',
            f"- condition: {card['condition_summary']}",
            '- next commands:',
        ])
        for command in card['next_commands']:
            lines.append(f'  - `{command}`')
        lines.extend([
            f"- success witness: {card['success_witness']}",
            '',
        ])

    lines.extend([
        '## Source surfaces',
        '',
        f"- live builder: `{report['metadata']['source_builder']}`",
    ])
    for path in report['metadata']['source_reports']:
        lines.append(f'- `{path}`')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact Rust recovery card for blocked cloudtainer sessions.')
    parser.add_argument('--write', action='store_true', help='write the JSON and markdown outputs in place')
    args = parser.parse_args()

    report = build_report()
    rendered = render_markdown(report)

    if not args.write:
        existing = _load_json(OUT_JSON)
        if existing != report:
            raise SystemExit('cloudtainer_rust_recovery_card.json is stale; run with --write')
        if OUT_MD.read_text(encoding='utf-8') != rendered:
            raise SystemExit('CLOUDTAINER_RUST_RECOVERY_CARD.md is stale; run with --write')
        print(
            'cloudtainer-rust-recovery-card: ok '
            f"(state={report['summary']['current_state_code']} rust_available={report['summary']['rust_available']})"
        )
        return 0

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(rendered, encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
