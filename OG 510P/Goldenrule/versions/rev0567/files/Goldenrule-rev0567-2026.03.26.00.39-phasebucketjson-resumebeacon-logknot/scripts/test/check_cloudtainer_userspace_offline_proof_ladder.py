#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_offline_proof_ladder.json'
MD_PATH = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_OFFLINE_PROOF_LADDER.md'


def main() -> int:
    if not JSON_PATH.exists():
        print('cloudtainer-userspace-offline-proof-ladder: missing json report', file=sys.stderr)
        return 1
    if not MD_PATH.exists():
        print('cloudtainer-userspace-offline-proof-ladder: missing markdown report', file=sys.stderr)
        return 1

    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    summary = payload.get('summary') or {}
    expected = {
        'current_state_code': 'junest_binary_missing',
        'fetch_surface_code': 'registry_only_single_workspace',
        'compile_surface_code': 'direct_derive_no_native_build',
        'offline_ladder_code': 'fetch_then_offline_compile_then_exact',
        'quick_foothold_label': 'quick_foothold',
        'quick_foothold_prefix': 1,
        'quick_foothold_patch_path': 'artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch',
        'quick_foothold_target': 'probe_run',
        'quick_foothold_exact_witness_count': 1,
        'network_required_phase_count': 1,
        'transient_roots': ['.local/cargo', '.local/rustup', '.local/target'],
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            print(f'cloudtainer-userspace-offline-proof-ladder: unexpected {key}={summary.get(key)!r}', file=sys.stderr)
            return 1
    if summary.get('phase_ids') != [
        'warm_cache',
        'health_check',
        'apply_quick_foothold',
        'offline_compile',
        'offline_exact_witness',
        'offline_lane_smoke',
        'cleanup',
    ]:
        print(f"cloudtainer-userspace-offline-proof-ladder: unexpected phase_ids={summary.get('phase_ids')!r}", file=sys.stderr)
        return 1

    commands = payload.get('commands') or {}
    expected_commands = {
        'warm_cache': 'cargo fetch --locked',
        'patch_apply': 'git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch',
        'offline_compile_no_run': 'cargo test --locked --offline --no-run -p gr_engine --test probe_run',
        'offline_exact_witness': 'cargo test --locked --offline -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact',
        'offline_lane_smoke': 'cargo test --locked --offline -p gr_engine --test probe_run',
        'cleanup': 'rm -rf .local/cargo .local/rustup .local/target',
    }
    for key, value in expected_commands.items():
        if commands.get(key) != value:
            print(f'cloudtainer-userspace-offline-proof-ladder: unexpected {key}={commands.get(key)!r}', file=sys.stderr)
            return 1

    md = MD_PATH.read_text(encoding='utf-8')
    for needle in [
        'fetch_then_offline_compile_then_exact',
        'cargo test --locked --offline --no-run -p gr_engine --test probe_run',
        'RS-GR-564',
        'RS-GR-565',
        'Failure interpretation',
    ]:
        if needle not in md:
            print(f'cloudtainer-userspace-offline-proof-ladder: markdown missing {needle!r}', file=sys.stderr)
            return 1

    print('cloudtainer-userspace-offline-proof-ladder: ok (fetch_then_offline_compile_then_exact)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
