#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JSON_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_failure_resume_card.json'
MD_PATH = ROOT / 'docs' / 'CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'classify_cloudtainer_userspace_failure.py'


def fail(msg: str) -> int:
    print(f'cloudtainer-userspace-failure-resume-card: {msg}', file=sys.stderr)
    return 1


def _run_tool(text: str, *, command_key: str | None = None) -> dict[str, object]:
    cmd = ['python3', str(TOOL_PATH)]
    if command_key:
        cmd.extend(['--command-key', command_key])
    payload = subprocess.run(cmd, input=text, text=True, capture_output=True, check=True)
    return json.loads(payload.stdout)


def main() -> int:
    if not JSON_PATH.exists():
        return fail('missing json report')
    if not MD_PATH.exists():
        return fail('missing markdown report')

    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    summary = payload.get('summary') or {}
    expected = {
        'current_state_code': 'junest_binary_missing',
        'fetch_surface_code': 'registry_only_single_workspace',
        'compile_surface_code': 'direct_derive_no_native_build',
        'offline_ladder_code': 'fetch_then_offline_compile_then_exact',
        'failure_resume_code': 'phase_scoped_resume_tripwire',
        'class_count': 8,
        'json_capture_variant_count': 3,
        'exact_witness_test_name': 'lift_fsm_strategy_family_lift_first_seed',
        'quick_foothold_target': 'probe_run',
        'env_export_count': 4,
        'transient_roots': ['.local/cargo', '.local/rustup', '.local/target'],
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            return fail(f'unexpected {key}={summary.get(key)!r}')

    if payload.get('command_precedence') != [
        'bootstrap_command_missing',
        'toolchain_unresolved',
        'warm_cache_transport_or_registry',
        'offline_cache_incomplete_or_lock_drift',
        'patch_apply_mismatch',
        'compile_surface_failure',
        'exact_witness_semantic_failure',
        'lane_smoke_semantic_failure',
    ]:
        return fail(f"unexpected command_precedence={payload.get('command_precedence')!r}")

    commands = payload.get('commands') or {}
    expected_commands = {
        'bootstrap': "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --default-toolchain none -y",
        'toolchain_install': 'rustup toolchain install stable --profile minimal --component rustfmt',
        'warm_cache': 'cargo fetch --locked',
        'patch_apply': 'git apply artifacts/patches/rust_external_test_shards/01_fsm_grim_trigger_probe.patch',
        'offline_compile': 'cargo test --locked --offline --no-run -p gr_engine --test probe_run',
        'offline_exact_witness': 'cargo test --locked --offline -p gr_engine --test probe_run lift_fsm_strategy_family_lift_first_seed -- --exact',
        'offline_lane_smoke': 'cargo test --locked --offline -p gr_engine --test probe_run',
        'cleanup': 'rm -rf .local/cargo .local/rustup .local/target',
    }
    for key, value in expected_commands.items():
        if commands.get(key) != value:
            return fail(f'unexpected commands[{key}]={commands.get(key)!r}')

    json_capture = payload.get('json_capture_commands') or {}
    if json_capture.get('offline_compile') != 'cargo test --locked --offline --no-run -p gr_engine --test probe_run --message-format=json-render-diagnostics':
        return fail('unexpected offline_compile json capture command')

    md = MD_PATH.read_text(encoding='utf-8')
    for needle in [
        'phase_scoped_resume_tripwire',
        'RS-GR-566',
        'RS-GR-567',
        'classify_cloudtainer_userspace_failure.py',
        '--message-format=json-render-diagnostics',
    ]:
        if needle not in md:
            return fail(f'markdown missing {needle!r}')

    cases = [
        (
            'attempting to make an HTTP request, but --offline was specified\n',
            'offline_compile',
            'offline_cache_incomplete_or_lock_drift',
        ),
        (
            'error: test failed\nfailures:\n    lift_fsm_strategy_family_lift_first_seed\nassertion failed\n',
            'offline_exact_witness',
            'exact_witness_semantic_failure',
        ),
        (
            'cargo: command not found\n',
            None,
            'bootstrap_command_missing',
        ),
        (
            '{"reason":"compiler-message","message":{"rendered":"error[E0433]: failed to resolve\\n"}}\n',
            'offline_compile',
            'compile_surface_failure',
        ),
    ]
    for text, command_key, expected_class in cases:
        result = _run_tool(text, command_key=command_key)
        got = ((result.get('classification') or {}) if isinstance(result, dict) else {}).get('class_id')
        if got != expected_class:
            return fail(f'classifier returned {got!r} for expected {expected_class!r}')

    print('cloudtainer-userspace-failure-resume-card: ok (phase_scoped_resume_tripwire)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
