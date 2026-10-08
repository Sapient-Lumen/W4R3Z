#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARD_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_recovery_card.json'
BUDGET_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_budget_card.json'
COMEBACK_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_comeback_execution_card.json'
EXECUTION_LANES_BUILDER = ROOT / 'scripts' / 'report' / 'build_cooperation_benchmark_card_execution_lanes.py'


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    report = json.loads(CARD_REPORT.read_text(encoding='utf-8'))
    budget = json.loads(BUDGET_REPORT.read_text(encoding='utf-8'))
    comeback = json.loads(COMEBACK_REPORT.read_text(encoding='utf-8'))
    execution = _load_module('build_cooperation_benchmark_card_execution_lanes', EXECUTION_LANES_BUILDER).collect()

    rust_lane = next(lane for lane in execution['lanes'] if lane['lane_id'] == 'rust-harness')
    observation = execution['observation']
    summary = report.get('summary') or {}
    cards = report.get('state_cards') or []

    blocking = list(rust_lane.get('blocking_reason_codes') or [])
    if list(summary.get('blocking_reason_codes') or []) != blocking:
        print('cloudtainer-rust-recovery-card: blocking reason codes mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('rust_available')) != bool(rust_lane.get('available')):
        print('cloudtainer-rust-recovery-card: rust availability mismatch', file=sys.stderr)
        return 1
    if str(summary.get('availability_basis')) != str(rust_lane.get('availability_basis')):
        print('cloudtainer-rust-recovery-card: availability basis mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('junest_bin_present')) != (observation.get('junest_bin_path') is not None):
        print('cloudtainer-rust-recovery-card: junest presence mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('junest_home_present')) != bool(observation.get('junest_home_present')):
        print('cloudtainer-rust-recovery-card: junest home mismatch', file=sys.stderr)
        return 1
    if bool(summary.get('junest_rust_available')) != bool(observation.get('junest_rust_available')):
        print('cloudtainer-rust-recovery-card: junest rust mismatch', file=sys.stderr)
        return 1

    medium_budget = next(card for card in budget['budget_cards'] if card['label'] == 'medium_budget')
    if str(summary.get('blocked_session_fallback_command')) != str(medium_budget['command']):
        print('cloudtainer-rust-recovery-card: medium budget command mismatch', file=sys.stderr)
        return 1

    quick = next(card for card in comeback['plateau_cards'] if card['label'] == 'quick_foothold')
    if str(summary.get('first_machine_quick_foothold_apply_hint')) != str(quick['apply_hint']):
        print('cloudtainer-rust-recovery-card: quick foothold apply hint mismatch', file=sys.stderr)
        return 1
    if int(summary.get('first_machine_quick_foothold_exact_witness_count', -1)) != int(quick['new_exact_witness_count']):
        print('cloudtainer-rust-recovery-card: quick foothold witness count mismatch', file=sys.stderr)
        return 1

    current = [card for card in cards if card.get('current')]
    if len(current) != 1:
        print('cloudtainer-rust-recovery-card: expected exactly one current state card', file=sys.stderr)
        return 1
    if str(current[0].get('state_code')) != str(summary.get('current_state_code')):
        print('cloudtainer-rust-recovery-card: current state card mismatch', file=sys.stderr)
        return 1

    state = str(summary.get('current_state_code'))
    documented = bool(summary.get('documented_in_place_recovery'))
    if state in {'native_ready', 'junest_ready', 'junest_home_missing', 'junest_toolchain_missing'} and not documented:
        print('cloudtainer-rust-recovery-card: expected in-place recovery to be true', file=sys.stderr)
        return 1
    if state in {'junest_binary_missing', 'rust_exec_missing', 'rust_unavailable_other'} and documented:
        print('cloudtainer-rust-recovery-card: expected in-place recovery to be false', file=sys.stderr)
        return 1

    bridge = report.get('current_bridge') or {}
    if state in {'junest_binary_missing', 'rust_exec_missing', 'rust_unavailable_other'}:
        if str(bridge.get('mode')) != 'stay_static_here':
            print('cloudtainer-rust-recovery-card: expected stay_static_here bridge', file=sys.stderr)
            return 1
        quick_bridge = bridge.get('first_machine_quick_foothold') or {}
        if str(quick_bridge.get('apply_hint')) != str(quick['apply_hint']):
            print('cloudtainer-rust-recovery-card: bridge quick foothold mismatch', file=sys.stderr)
            return 1
    if state in {'junest_home_missing', 'junest_toolchain_missing'} and str(bridge.get('mode')) != 'bootstrap_in_place':
        print('cloudtainer-rust-recovery-card: expected bootstrap_in_place bridge', file=sys.stderr)
        return 1
    if state in {'native_ready', 'junest_ready'} and str(bridge.get('mode')) != 'run_rust_now':
        print('cloudtainer-rust-recovery-card: expected run_rust_now bridge', file=sys.stderr)
        return 1

    print(
        'cloudtainer-rust-recovery-card: ok '
        f"(state={summary.get('current_state_code')} bridge={bridge.get('mode')})"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
