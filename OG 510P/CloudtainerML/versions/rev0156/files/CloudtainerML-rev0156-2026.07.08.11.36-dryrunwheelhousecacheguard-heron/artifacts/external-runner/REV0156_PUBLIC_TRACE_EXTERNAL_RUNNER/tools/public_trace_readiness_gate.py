#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0099'))
REVUP = REV.upper()
OUT_AUDIT = ROOT / 'artifacts' / 'audit'
OUT_LOGS = ROOT / 'artifacts' / 'run-logs'
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT_LOGS.mkdir(parents=True, exist_ok=True)


EXPENSIVE_OR_POSTTRACE_STEPS: list[tuple[str, list[str]]] = [
    ('llama_surface', [sys.executable, 'tools/transformers_llama_surface_probe.py']),
    ('backend_identity', [sys.executable, 'tools/public_trace_backend_identity_probe.py']),
    ('cache_implementation', [sys.executable, 'tools/public_trace_cache_implementation_audit.py']),
    ('prompt_manifest', [sys.executable, 'tools/public_trace_prompt_manifest_audit.py']),
    ('device_dtype_timing', [sys.executable, 'tools/public_trace_device_dtype_timing_audit.py']),
    ('hardware_timing_boundary', [sys.executable, 'tools/public_trace_hardware_timing_boundary_audit.py']),
    ('acceptance_bundle', [sys.executable, 'tools/public_trace_acceptance_bundle_audit.py']),
    ('evaluation_verdict', [sys.executable, 'tools/public_trace_evaluation_verdict_audit.py']),
    ('evaluation_receipt', [sys.executable, 'tools/public_trace_evaluation_receipt_audit.py']),
    ('selector_entry_gate', [sys.executable, 'tools/public_trace_selector_entry_gate.py']),
    ('receipt_relocation', [sys.executable, 'tools/public_trace_receipt_relocation_audit.py']),
    ('selector_entry_receipt', [sys.executable, 'tools/public_trace_selector_entry_receipt_audit.py']),
    ('selector_receipt_replay', [sys.executable, 'tools/public_trace_selector_receipt_replay_gate.py']),
    ('selector_receipt_replay_audit', [sys.executable, 'tools/public_trace_selector_receipt_replay_audit.py']),
    ('model_identity', [sys.executable, 'tools/capture_model_identity_audit.py']),
]


def load(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        return {'_load_error': repr(exc), '_path': rel}


def step_timeout_seconds(name: str, env: dict[str, str]) -> float:
    # Fast static probes should stay bounded, but snapshot materialization and
    # digest verification of a 2.2GB public weight file cannot share the same
    # 8-second timeout without creating a false external-runner blocker.
    if name == 'snapshot':
        return float(env.get('SNAPSHOT_GATE_STEP_TIMEOUT', '1800' if env.get('ALLOW_DOWNLOAD') == '1' else '300'))
    if name == 'snapshot_dry_run':
        return float(env.get('SNAPSHOT_DRY_RUN_TIMEOUT', '120'))
    if name == 'env_preflight':
        return float(env.get('PREFLIGHT_TIMEOUT_SECONDS', '90')) + 5.0
    return float(env.get('TRACE_GATE_STEP_TIMEOUT', '8'))


def run_step(name: str, cmd: list[str], env: dict[str, str]) -> dict[str, Any]:
    step_timeout = step_timeout_seconds(name, env)
    try:
        proc = subprocess.Popen(
            cmd, cwd=ROOT, env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=step_timeout)
            timed_out = False
            returncode = int(proc.returncode or 0)
        except subprocess.TimeoutExpired:
            import os as _os, signal as _signal
            timed_out = True
            try:
                _os.killpg(proc.pid, _signal.SIGKILL)
            except Exception:
                proc.kill()
            stdout, stderr = proc.communicate()
            stderr = (stderr or '') + f'\nSTEP TIMEOUT after {step_timeout} seconds'
            returncode = 124
    except Exception as exc:
        timed_out = False
        stdout = ''
        stderr = f'failed to launch step: {exc!r}'
        returncode = 125
    log_path = OUT_LOGS / f'{REVUP}_READINESS_GATE_{name}.log'
    log_path.write_text(
        '$ ' + ' '.join(cmd) + '\n\n' +
        '## stdout\n' + (stdout or '') + '\n\n' +
        '## stderr\n' + (stderr or '') + '\n',
        encoding='utf-8'
    )
    return {
        'name': name,
        'cmd': cmd,
        'returncode': returncode,
        'timed_out': timed_out,
        'log': log_path.relative_to(ROOT).as_posix(),
        'stdout_tail': (stdout or '')[-2000:],
        'stderr_tail': (stderr or '')[-2000:],
    }


def collect_list(key: str, *audits: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for audit in audits:
        value = audit.get(key)
        if isinstance(value, list):
            for item in value:
                text = str(item)
                if text and text not in out:
                    out.append(text)
    return out


def collect_blockers(*audits: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ['blockers', 'errors']:
        for item in collect_list(key, *audits):
            if item not in out:
                out.append(item)
    return out


def mode_args(args: argparse.Namespace, env: dict[str, str]) -> tuple[list[str], list[str], bool]:
    if args.download:
        env['ALLOW_DOWNLOAD'] = '1'
        env.setdefault('ALLOW_NETWORK_DRY_RUN', '1')
        hash_args = ['--include-hashes'] if env.get('HASH_WEIGHTS', '1') == '1' else []
        return ['--download'] + hash_args, ['--require-network', '--strict'], True
    if args.local_only:
        env.setdefault('ALLOW_DOWNLOAD', '0')
        hash_args = ['--include-hashes'] if env.get('HASH_WEIGHTS', '1') == '1' else []
        return ['--local-only'] + hash_args, ['--skip-network'], False
    if env.get('ALLOW_DOWNLOAD') == '1':
        env.setdefault('ALLOW_NETWORK_DRY_RUN', '1')
        hash_args = ['--include-hashes'] if env.get('HASH_WEIGHTS', '1') == '1' else []
        return ['--download'] + hash_args, ['--require-network', '--strict'], True
    env.setdefault('ALLOW_DOWNLOAD', '0')
    hash_args = ['--include-hashes'] if env.get('HASH_WEIGHTS', '1') == '1' else []
    return ['--local-only'] + hash_args, ['--skip-network'], False



def write_env_preflight_placeholder(reason: str) -> None:
    """Write a safe blocked env-preflight receipt only when no current one exists.

    If dependency import/probe is already blocked, rerunning the heavier env
    preflight can waste the cloudtainer. A real runner with dependencies fixed
    will reach the normal env_preflight step and replace this receipt.
    """
    rel = OUT_AUDIT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json'
    current = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json')
    if current.get('revision') == REV and current.get('status') in {'blocked_here', 'trace_env_ready', 'pass'}:
        return
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'blocked_here',
        'trace_ready': False,
        'timing_ready': False,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'blockers': [reason],
        'warnings': ['env_preflight_skipped_until_dependency_lock_passes'],
        'summary': 'Safe placeholder written by the fail-fast readiness gate when dependency prerequisites are already blocked; rerun public_trace_env_preflight.py --strict trace after dependency repair.',
    }
    rel.write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT_AUDIT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.md').write_text(
        f'# Public trace environment preflight — {REVUP}\n\nStatus: `blocked_here`  \nPromotion allowed: `false`\n\nEnv preflight was skipped by the fail-fast readiness gate because `{reason}`. Rerun `python3 tools/public_trace_env_preflight.py --strict trace` after dependency repair.\n',
        encoding='utf-8'
    )

def load_core_audits() -> dict[str, dict[str, Any]]:
    return {
        'revision_meta': load(f'artifacts/audit/{REVUP}_REVISION_METADATA_COHERENCE_AUDIT.json'),
        'dependency': load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.json'),
        'source': load(f'artifacts/audit/{REVUP}_SOURCE_LOCK_AUDIT.json'),
        'packet': load(f'artifacts/audit/{REVUP}_TRACE_RUN_PACKET_AUDIT.json'),
        'env_pre': load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json'),
        'intake': load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SNAPSHOT_INTAKE_AUDIT.json'),
        'dry': load(f'artifacts/audit/{REVUP}_HF_SNAPSHOT_DRY_RUN_AUDIT.json'),
        'snapshot': load(f'artifacts/audit/{REVUP}_HF_SNAPSHOT_MATERIALIZER.json'),
    }


def prerequisite_blockers(audits: dict[str, dict[str, Any]], download_mode: bool) -> list[str]:
    blockers: list[str] = []
    dependency = audits['dependency']
    source = audits['source']
    packet = audits['packet']
    env_pre = audits['env_pre']
    intake = audits['intake']
    dry = audits['dry']
    snapshot = audits['snapshot']

    if audits['revision_meta'].get('status') != 'pass':
        blockers.append('revision_metadata_not_coherent')
    if dependency.get('status') not in {'pass', 'pass_with_warnings'}:
        blockers.append('dependency_lock_not_ready')
    if source.get('status') != 'pass':
        blockers.append('source_lock_not_pass')
    if packet.get('status') != 'pass':
        blockers.append('trace_run_packet_not_pass')
    if env_pre.get('trace_ready') is not True:
        blockers.append('trace_environment_not_ready')
    if intake.get('status') not in {'local_snapshot_ready', 'not_provided'}:
        blockers.append('snapshot_intake_not_ready')
    if download_mode:
        if dry.get('status') != 'dry_run_pass':
            blockers.append('download_dry_run_not_pass')
    else:
        if dry.get('status') not in {'skipped', 'dry_run_pass'}:
            blockers.append('local_only_dry_run_state_unexpected')
    if snapshot.get('complete_snapshot_available') is not True:
        blockers.append('complete_snapshot_not_available')
    return blockers


def readiness_bits(download_mode: bool) -> dict[str, bool]:
    revision_meta = load(f'artifacts/audit/{REVUP}_REVISION_METADATA_COHERENCE_AUDIT.json')
    dependency = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.json')
    source = load(f'artifacts/audit/{REVUP}_SOURCE_LOCK_AUDIT.json')
    packet = load(f'artifacts/audit/{REVUP}_TRACE_RUN_PACKET_AUDIT.json')
    env_pre = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json')
    surface = load(f'artifacts/audit/{REVUP}_TRANSFORMERS_LLAMA_SURFACE_PROBE.json')
    backend = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_BACKEND_IDENTITY_PROBE.json')
    cache_impl = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_CACHE_IMPLEMENTATION_AUDIT.json')
    prompt_manifest = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_PROMPT_MANIFEST_AUDIT.json')
    device_dtype_timing = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_DEVICE_DTYPE_TIMING_AUDIT.json')
    hardware_timing_boundary = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_HARDWARE_TIMING_BOUNDARY_AUDIT.json')
    acceptance_bundle = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ACCEPTANCE_BUNDLE_AUDIT.json')
    evaluation_verdict = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_EVALUATION_VERDICT_AUDIT.json')
    evaluation_receipt = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT_AUDIT.json')
    selector_entry_gate = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_GATE_AUDIT.json')
    receipt_relocation = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_RECEIPT_RELOCATION_AUDIT.json')
    selector_entry_receipt = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.json')
    selector_receipt_replay_gate = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_GATE_AUDIT.json')
    selector_receipt_replay_audit = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_AUDIT.json')
    intake = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SNAPSHOT_INTAKE_AUDIT.json')
    model_identity = load(f'artifacts/audit/{REVUP}_CAPTURE_MODEL_IDENTITY_AUDIT.json')
    dry = load(f'artifacts/audit/{REVUP}_HF_SNAPSHOT_DRY_RUN_AUDIT.json')
    snapshot = load(f'artifacts/audit/{REVUP}_HF_SNAPSHOT_MATERIALIZER.json')
    capture_ready = load(f'artifacts/audit/{REVUP}_PUBLIC_TRACE_CAPTURE_READINESS_AUDIT.json')
    cap_surface = load(f'artifacts/audit/{REVUP}_CAPTURE_SURFACE_REFACTOR_AUDIT.json')
    active_surface = load(f'artifacts/audit/{REVUP}_ACTIVE_SURFACE_TRIM_AUDIT.json')
    entrypoints = load(f'artifacts/audit/{REVUP}_CURRENT_ENTRYPOINT_CONSISTENCY_AUDIT.json')
    oq_surface = load(f'artifacts/audit/{REVUP}_OPEN_QUESTIONS_SURFACE_AUDIT.json')
    return {
        'revision_metadata_coherent': revision_meta.get('status') == 'pass',
        'dependency_lock_ok': dependency.get('status') in {'pass', 'pass_with_warnings'},
        'source_lock_pass': source.get('status') == 'pass',
        'trace_packet_pass': packet.get('status') == 'pass',
        'env_trace_ready': env_pre.get('trace_ready') is True,
        'llama_surface_compatible': surface.get('status') in {'pass', 'pass_with_warnings'},
        'backend_identity_ok': backend.get('status') in {'pass', 'pass_with_warnings'},
        'cache_implementation_contract_ok': cache_impl.get('status') in {'pass_with_blockers', 'pass'},
        'prompt_manifest_contract_ok': prompt_manifest.get('status') in {'pass_with_blockers', 'pass'},
        'device_dtype_timing_contract_ok': device_dtype_timing.get('status') in {'pass_with_blockers', 'pass'},
        'hardware_timing_boundary_ok': hardware_timing_boundary.get('status') in {'pass_with_blockers', 'pass'},
        'acceptance_bundle_contract_ok': acceptance_bundle.get('status') in {'pass_with_blockers', 'pass'},
        'evaluation_verdict_not_rejected': evaluation_verdict.get('status') in {'pass_with_blockers', 'pass'} and evaluation_verdict.get('verdict') != 'trace_bundle_rejected_before_evaluation',
        'evaluation_receipt_contract_ok': evaluation_receipt.get('status') in {'pass_with_blockers', 'pass'},
        'selector_entry_gate_safe': selector_entry_gate.get('status') in {'pass_with_blockers', 'pass'} and selector_entry_gate.get('verdict') != 'selector_entry_allowed_without_receipt',
        'receipt_relocation_contract_ok': receipt_relocation.get('status') in {'pass_with_blockers', 'pass'},
        'selector_entry_receipt_contract_ok': selector_entry_receipt.get('status') in {'pass_with_blockers', 'pass'},
        'selector_receipt_replay_gate_safe': selector_receipt_replay_gate.get('status') in {'pass_with_blockers', 'pass'} and selector_receipt_replay_gate.get('verdict') != 'selector_receipt_replay_verified_without_selector_entry',
        'selector_receipt_replay_audit_ok': selector_receipt_replay_audit.get('status') in {'pass_with_blockers', 'pass'},
        'local_snapshot_intake_ok': intake.get('status') in {'local_snapshot_ready', 'not_provided'},
        'capture_model_identity_ok': model_identity.get('status') in {'pass', 'pass_with_warnings'},
        'snapshot_dry_run_ok_or_not_needed': (not download_mode and dry.get('status') in {'skipped', 'dry_run_pass'}) or (download_mode and dry.get('status') == 'dry_run_pass'),
        'snapshot_complete': snapshot.get('complete_snapshot_available') is True,
        'capture_source_checks_ok': capture_ready.get('status') != 'fail' and not capture_ready.get('errors'),
        'capture_readiness_audit_ready': capture_ready.get('status') == 'ready_to_run_cached_capture',
        'capture_surface_refactor_ok': cap_surface.get('status') in {'pass', 'pass_with_debt'},
        'active_surface_ok': active_surface.get('status') in {'pass', 'pass_with_debt'},
        'current_entrypoints_ok': entrypoints.get('status') in {'pass', 'pass_with_debt'},
        'open_questions_surface_ok': oq_surface.get('status') in {'pass', 'pass_with_debt'},
    }


def load_all_readiness_audits(download_mode: bool) -> list[dict[str, Any]]:
    names = [
        f'artifacts/audit/{REVUP}_REVISION_METADATA_COHERENCE_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.json',
        f'artifacts/audit/{REVUP}_SOURCE_LOCK_AUDIT.json',
        f'artifacts/audit/{REVUP}_TRACE_RUN_PACKET_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json',
        f'artifacts/audit/{REVUP}_TRANSFORMERS_LLAMA_SURFACE_PROBE.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_BACKEND_IDENTITY_PROBE.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_CACHE_IMPLEMENTATION_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_PROMPT_MANIFEST_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_DEVICE_DTYPE_TIMING_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_HARDWARE_TIMING_BOUNDARY_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_ACCEPTANCE_BUNDLE_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_EVALUATION_VERDICT_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_GATE_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_RECEIPT_RELOCATION_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_GATE_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_AUDIT.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_SNAPSHOT_INTAKE_AUDIT.json',
        f'artifacts/audit/{REVUP}_CAPTURE_MODEL_IDENTITY_AUDIT.json',
        f'artifacts/audit/{REVUP}_HF_SNAPSHOT_DRY_RUN_AUDIT.json',
        f'artifacts/audit/{REVUP}_HF_SNAPSHOT_MATERIALIZER.json',
        f'artifacts/audit/{REVUP}_PUBLIC_TRACE_CAPTURE_READINESS_AUDIT.json',
        f'artifacts/audit/{REVUP}_CAPTURE_SURFACE_REFACTOR_AUDIT.json',
        f'artifacts/audit/{REVUP}_ACTIVE_SURFACE_TRIM_AUDIT.json',
        f'artifacts/audit/{REVUP}_CURRENT_ENTRYPOINT_CONSISTENCY_AUDIT.json',
        f'artifacts/audit/{REVUP}_OPEN_QUESTIONS_SURFACE_AUDIT.json',
    ]
    return [load(n) for n in names]


def write_gate_audit(*, status: str, download_mode: bool, snapshot_skipped: bool, step_results: list[dict[str, Any]], blockers: list[str], warnings: list[str], skipped_steps: list[str], fail_fast_prerequisite_blockers: list[str]) -> int:
    bits = readiness_bits(download_mode)
    ready_to_attempt_capture = bool(
        bits['dependency_lock_ok']
        and bits['source_lock_pass']
        and bits['trace_packet_pass']
        and bits['env_trace_ready']
        and bits['llama_surface_compatible']
        and bits['backend_identity_ok']
        and bits['cache_implementation_contract_ok']
        and bits['prompt_manifest_contract_ok']
        and bits['device_dtype_timing_contract_ok']
        and bits['hardware_timing_boundary_ok']
        and bits['acceptance_bundle_contract_ok']
        and bits['evaluation_verdict_not_rejected']
        and bits['evaluation_receipt_contract_ok']
        and bits['selector_entry_gate_safe']
        and bits['receipt_relocation_contract_ok']
        and bits['selector_entry_receipt_contract_ok']
        and bits['selector_receipt_replay_gate_safe']
        and bits['selector_receipt_replay_audit_ok']
        and bits['local_snapshot_intake_ok']
        and bits['capture_model_identity_ok']
        and bits['snapshot_dry_run_ok_or_not_needed']
        and bits['snapshot_complete']
        and bits['capture_source_checks_ok']
        and bits['capture_surface_refactor_ok']
        and bits['active_surface_ok']
        and bits['current_entrypoints_ok']
        and bits['open_questions_surface_ok']
    )
    if ready_to_attempt_capture:
        status = 'ready_to_attempt_capture'
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Single stop/go readiness gate for the public TinyLlama trace lane. Rev0118 makes it fail-fast on runtime/source/snapshot prerequisites so a blocked cloudtainer does not drift into expensive backend/model probes.',
        'snapshot_mode': 'download' if download_mode else 'local_only',
        'download_dry_run_required': download_mode,
        'snapshot_materializer_skipped_after_dry_run_failure': snapshot_skipped,
        'fail_fast_enabled': True,
        'fail_fast_prerequisite_blockers': fail_fast_prerequisite_blockers,
        'skipped_steps': skipped_steps,
        'readiness': bits,
        'ready_to_attempt_capture': ready_to_attempt_capture,
        'commands_executed': step_results,
        'blockers': blockers,
        'warnings': warnings,
        'next_if_ready': f'ALLOW_DOWNLOAD={1 if download_mode else 0} bash artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh',
        'next_if_blocked': [
            'repair the fail_fast_prerequisite_blockers before running expensive backend/model probes',
            'install/import torch + transformers + safetensors + huggingface_hub in an isolated environment',
            'prepopulate or materialize the exact HF snapshot; use HF_HUB_OFFLINE=1/local_files_only=True for offline verification after materialization',
            'keep ATTENTION_IMPLEMENTATION=eager and CACHE_IMPLEMENTATION=dynamic for trace extraction',
            'do not edit registries or add doctrine until this gate either passes or yields a new precise runtime incompatibility',
        ],
    }
    (OUT_AUDIT / f'{REVUP}_PUBLIC_TRACE_READINESS_GATE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [
        f'# Public trace readiness gate — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        'Rev0118 fails fast on runtime/source/snapshot prerequisites before expensive model/backend probes.',
        '',
        '## Fail-fast prerequisite blockers',
        '',
    ]
    lines.extend([f'- `{b}`' for b in fail_fast_prerequisite_blockers] if fail_fast_prerequisite_blockers else ['- none'])
    lines.extend(['', '## Skipped steps', ''])
    lines.extend([f'- `{s}`' for s in skipped_steps] if skipped_steps else ['- none'])
    lines.extend(['', '## Readiness bits', ''])
    lines.extend(f'- `{k}` = `{str(v).lower()}`' for k, v in bits.items())
    lines.extend(['', '## Blockers', ''])
    lines.extend([f'- `{b}`' for b in blockers] if blockers else ['- none'])
    lines.extend(['', '## Next', '', f"`{audit['next_if_ready'] if ready_to_attempt_capture else 'repair blockers above, then rerun python tools/public_trace_readiness_gate.py --strict'}`"])
    (OUT_AUDIT / f'{REVUP}_PUBLIC_TRACE_READINESS_GATE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'ready_to_attempt_capture': ready_to_attempt_capture, 'fail_fast_prerequisite_blockers': fail_fast_prerequisite_blockers, 'blockers': blockers, 'warnings': warnings, 'skipped_steps': skipped_steps}, indent=2))
    return 0 if ready_to_attempt_capture else 1


def main() -> int:
    ap = argparse.ArgumentParser(description='Fail-fast stop/go gate for the current public TinyLlama trace lane.')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--download', action='store_true', help='allow hf_snapshot_materializer.py to download the reviewed snapshot after dry-run preflight')
    mode.add_argument('--local-only', action='store_true', help='verify local HF cache only')
    ap.add_argument('--strict', action='store_true', help='exit nonzero unless all capture-readiness checks pass')
    ap.add_argument('--continue-after-prereq-blockers', action='store_true', help='debug mode: run expensive/post-trace checks even if runtime/source prerequisites are already blocked')
    args = ap.parse_args()

    env = os.environ.copy()
    env.setdefault('MODEL_ID', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0')
    env.setdefault('MODEL_REVISION', 'fe8a4ea1ffedaf415f4da2f062534de366a451e6')
    env.setdefault('TOKENIZER_REVISION', env['MODEL_REVISION'])
    env.setdefault('WEIGHTS_SOURCE', 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6')
    env.setdefault('LICENSE', 'apache-2.0')
    env.setdefault('DECODE_STEPS', '2')
    env.setdefault('MAX_ROWS', '128')
    env.setdefault('ATTENTION_IMPLEMENTATION', 'eager')
    env.setdefault('CACHE_IMPLEMENTATION', 'dynamic')
    env.setdefault('TRACE_TORCH_DTYPE', 'float32')
    env.setdefault('TRACE_DEVICE', 'auto')
    snapshot_args, dry_args, download_mode = mode_args(args, env)

    early_steps: list[tuple[str, list[str]]] = [
        ('revision_metadata_coherence', [sys.executable, 'tools/revision_metadata_coherence_audit.py']),
        ('dependency_lock', [sys.executable, 'tools/public_trace_dependency_lock_audit.py']),
        ('source_lock', [sys.executable, 'tools/source_lock_audit.py']),
        ('trace_packet', [sys.executable, 'tools/trace_run_packet_audit.py']),
    ]
    step_results: list[dict[str, Any]] = []
    for name, cmd in early_steps:
        step_results.append(run_step(name, cmd, env))

    early_audits = load_core_audits()
    dependency_not_ready = early_audits['dependency'].get('status') not in {'pass', 'pass_with_warnings'}
    if dependency_not_ready and not args.continue_after_prereq_blockers:
        write_env_preflight_placeholder('dependency_lock_not_ready_skipped_env_preflight')
        step_results.append({
            'name': 'env_preflight_skipped',
            'cmd': [sys.executable, 'tools/public_trace_env_preflight.py', '--strict', 'trace', '--require-weight-hash'],
            'returncode': 0,
            'timed_out': False,
            'log': None,
            'stdout_tail': 'skipped because dependency_lock_not_ready',
            'stderr_tail': '',
        })
    else:
        step_results.append(run_step('env_preflight', [sys.executable, 'tools/public_trace_env_preflight.py', '--strict', 'trace', '--require-weight-hash'], env))

    snapshot_steps: list[tuple[str, list[str]]] = [
        ('snapshot_intake', [sys.executable, 'tools/public_trace_snapshot_intake_audit.py']),
        ('snapshot_dry_run', [sys.executable, 'tools/hf_snapshot_dry_run_audit.py'] + dry_args),
    ]
    for name, cmd in snapshot_steps:
        step_results.append(run_step(name, cmd, env))

    dry_run_failed = any(s['name'] == 'snapshot_dry_run' and s['returncode'] != 0 for s in step_results)
    snapshot_skipped = bool('--download' in snapshot_args and dry_run_failed)
    if snapshot_skipped:
        skip_audit = {
            'revision': REV,
            'revision_number': int(REV.replace('rev','')),
            'package_name': META.get('package_name'),
            'archive_name': META.get('archive_name'),
            'status': 'skipped_after_dry_run_failure',
            'promotion_allowed': False,
            'public_pretrained_trace_loaded': False,
            'gpu_fused_kernel_measured': False,
            'complete_snapshot_available': False,
            'blockers': ['snapshot_materializer_skipped_because_dry_run_failed'],
            'warnings': [],
        }
        (OUT_AUDIT / f'{REVUP}_HF_SNAPSHOT_MATERIALIZER.json').write_text(json.dumps(skip_audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
        (OUT_AUDIT / f'{REVUP}_HF_SNAPSHOT_MATERIALIZER.md').write_text(
            f'# HF snapshot materializer — {REVUP}\n\nStatus: `skipped_after_dry_run_failure`  \nPromotion allowed: `false`\n\nThe full snapshot materializer was intentionally skipped because the dry-run preflight failed.\n',
            encoding='utf-8')
        step_results.append({'name': 'snapshot', 'cmd': [sys.executable, 'tools/hf_snapshot_materializer.py'] + snapshot_args, 'returncode': 99, 'log': None, 'stdout_tail': '', 'stderr_tail': 'skipped after dry-run failure', 'timed_out': False})
    else:
        step_results.append(run_step('snapshot', [sys.executable, 'tools/hf_snapshot_materializer.py'] + snapshot_args, env))

    core_audits = load_core_audits()
    fail_fast = prerequisite_blockers(core_audits, download_mode)
    failed_steps = [s for s in step_results if s.get('returncode') != 0]
    base_audits = list(core_audits.values())
    blockers = collect_blockers(*base_audits)
    warnings = collect_list('warnings', *base_audits)
    for step in failed_steps:
        tag = 'step_failed:' + str(step['name'])
        if tag not in blockers:
            blockers.append(tag)
    for b in fail_fast:
        if b not in blockers:
            blockers.append(b)

    skipped_steps: list[str] = []
    if fail_fast and not args.continue_after_prereq_blockers:
        skipped_steps = [name for name, _ in EXPENSIVE_OR_POSTTRACE_STEPS]
        return_code = write_gate_audit(
            status='blocked_here_fail_fast',
            download_mode=download_mode,
            snapshot_skipped=snapshot_skipped,
            step_results=step_results,
            blockers=blockers,
            warnings=warnings,
            skipped_steps=skipped_steps,
            fail_fast_prerequisite_blockers=fail_fast,
        )
        return return_code if args.strict else 0

    for name, cmd in EXPENSIVE_OR_POSTTRACE_STEPS:
        step_results.append(run_step(name, cmd, env))
    all_audits = load_all_readiness_audits(download_mode)
    blockers = collect_blockers(*all_audits)
    warnings = collect_list('warnings', *all_audits)
    for step in [s for s in step_results if s.get('returncode') != 0]:
        tag = 'step_failed:' + str(step['name'])
        if tag not in blockers:
            blockers.append(tag)
    return_code = write_gate_audit(
        status='blocked_here',
        download_mode=download_mode,
        snapshot_skipped=snapshot_skipped,
        step_results=step_results,
        blockers=blockers,
        warnings=warnings,
        skipped_steps=skipped_steps,
        fail_fast_prerequisite_blockers=fail_fast,
    )
    return return_code if args.strict else 0


if __name__ == '__main__':
    raise SystemExit(main())
