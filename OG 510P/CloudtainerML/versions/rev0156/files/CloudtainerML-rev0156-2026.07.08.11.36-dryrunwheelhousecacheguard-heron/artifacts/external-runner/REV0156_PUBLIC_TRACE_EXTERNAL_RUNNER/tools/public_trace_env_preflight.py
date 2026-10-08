#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib
import importlib.util
import json
import os
import platform
import shutil
import signal
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0095'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL_ID = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
DEFAULT_REVISION = 'fe8a4ea1ffedaf415f4da2f062534de366a451e6'

# Rev0128: environment preflight must use the same structural snapshot
# integrity contract as the materializer/capture digest path. A filename-only
# cache check can green-light a stale/truncated model just long enough to waste
# the live capture lane.
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    REQUIRED_SNAPSHOT_FILES,
    inspect_snapshot,
    snapshot_candidate_paths,
)


PREFLIGHT_TIMEOUT_SECONDS_DEFAULT = 90


def _timeout_handler(signum, frame):  # type: ignore[no-untyped-def]
    raise TimeoutError('public_trace_env_preflight_timed_out')


def write_timeout_audit(timeout_seconds: int) -> int:
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'blocked_here',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'trace_ready': False,
        'timing_ready': False,
        'timeout_seconds': timeout_seconds,
        'blockers': ['public_trace_env_preflight_timed_out_before_completion'],
        'warnings': [],
        'next_repair_if_blocked': [
            'rerun with a larger --timeout-seconds only if imports or cache scans are expected to be slow',
            'otherwise inspect dependency imports and local HF cache paths for hangs before attempting capture',
        ],
    }
    json_path = OUT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json'
    md_path = OUT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.md'
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md_path.write_text(
        f'# Public trace environment preflight — {REVUP}\n\n'
        f"Status: `blocked_here`  \nPromotion allowed: `false`\n\n"
        f"Trace ready: `false`  \nTiming ready: `false`\n\n"
        f"## Blockers\n\n- `public_trace_env_preflight_timed_out_before_completion`\n\n"
        f"## Interpretation\n\nThe preflight itself timed out after `{timeout_seconds}` seconds. This is a local execution blocker, not promotion evidence.\n",
        encoding='utf-8'
    )
    print(json.dumps({'status': 'blocked_here', 'trace_ready': False, 'timing_ready': False, 'blockers': audit['blockers'], 'warnings': []}, indent=2))
    return 1


def module_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    result: dict[str, Any] = {'name': name, 'present': bool(spec is not None)}
    if spec is None:
        return result
    try:
        mod = importlib.import_module(name)
        result['import_ok'] = True
        result['version'] = str(getattr(mod, '__version__', 'unknown'))
    except Exception as exc:
        result['import_ok'] = False
        result['error'] = repr(exc)
    return result


def env_path(name: str) -> str | None:
    v = os.environ.get(name)
    return v if v else None


def candidate_cache_roots() -> list[Path]:
    roots: list[Path] = []
    if env_path('HF_HUB_CACHE'):
        roots.append(Path(env_path('HF_HUB_CACHE')).expanduser())
    if env_path('HF_HOME'):
        roots.append(Path(env_path('HF_HOME')).expanduser() / 'hub')
    roots.append(Path.home() / '.cache' / 'huggingface' / 'hub')
    # de-duplicate while preserving order
    out: list[Path] = []
    seen: set[str] = set()
    for r in roots:
        key = str(r)
        if key not in seen:
            out.append(r)
            seen.add(key)
    return out


def integrity_snapshot_status(model_id: str, revision: str, *, include_hashes: bool = False) -> dict[str, Any]:
    """Return shared-integrity snapshot readiness for the env gate.

    Earlier env preflights used a filename/minimum-file check. That was cheaper,
    but it could mark the trace environment ready while the materializer/capture
    path would later reject the same snapshot for parse, size, architecture, or
    safetensors-header reasons. This uses the common import-light inspector so
    all live gates share one snapshot meaning before a long capture starts.
    """
    checks: list[dict[str, Any]] = []
    for path in snapshot_candidate_paths(model_id, revision):
        try:
            checks.append(inspect_snapshot(path, model_id=model_id, revision=revision, include_hashes=include_hashes))
        except Exception as exc:
            checks.append({
                'path': str(path),
                'exists': bool(path.exists()),
                'is_dir': bool(path.is_dir()) if path.exists() else False,
                'complete_required_snapshot': False,
                'blockers': ['snapshot_integrity_inspection_exception'],
                'error': type(exc).__name__ + ': ' + repr(exc),
            })
    found_complete = any(bool(c.get('complete_required_snapshot')) for c in checks)
    hash_verified = any(bool(c.get('complete_required_snapshot')) and bool(c.get('model_safetensors', {}).get('sha256_matches_expected')) for c in checks)
    return {
        'snapshot_integrity_contract': 'hf_snapshot_integrity_v1',
        'shared_integrity_inspector_used': True,
        'model_safetensors_hash_required': bool(include_hashes),
        'expected_model_safetensors_sha256': EXPECTED_MODEL_SAFETENSORS_SHA256,
        'required_snapshot_files': REQUIRED_SNAPSHOT_FILES,
        'found_complete_integrity_snapshot': found_complete,
        'found_digest_verified_integrity_snapshot': hash_verified,
        # Compatibility mirror for old readers, deliberately stricter than the
        # old minimum-file check.
        'found_complete_minimum_snapshot': found_complete,
        'local_snapshot_dir': env_path('LOCAL_SNAPSHOT_DIR'),
        'candidate_snapshots': checks,
        'candidate_snapshot_count': len(checks),
        'snapshot_blockers_observed': sorted(set(str(b) for c in checks for b in c.get('blockers', []))),
    }

def disk_status(path: Path) -> dict[str, Any]:
    try:
        usage = shutil.disk_usage(path)
    except Exception:
        usage = shutil.disk_usage(ROOT)
    return {
        'path': str(path),
        'total_bytes': int(usage.total),
        'used_bytes': int(usage.used),
        'free_bytes': int(usage.free),
        'free_gb': round(usage.free / (1024 ** 3), 3),
        'free_gb_ge_6': bool(usage.free >= 6 * 1024 ** 3),
    }


def torch_device_status(torch_status: dict[str, Any]) -> dict[str, Any]:
    if not torch_status.get('import_ok'):
        return {'torch_import_ok': False, 'cuda_available': False, 'devices': []}
    try:
        import torch  # type: ignore
        devices = []
        count = int(torch.cuda.device_count()) if torch.cuda.is_available() else 0
        for idx in range(count):
            props = torch.cuda.get_device_properties(idx)
            devices.append({
                'index': idx,
                'name': str(props.name),
                'total_memory_bytes': int(props.total_memory),
                'major': int(props.major),
                'minor': int(props.minor),
            })
        return {
            'torch_import_ok': True,
            'torch_version': str(getattr(torch, '__version__', 'unknown')),
            'cuda_available': bool(torch.cuda.is_available()),
            'cuda_version': str(getattr(torch.version, 'cuda', None)),
            'device_count': count,
            'devices': devices,
        }
    except Exception as exc:
        return {'torch_import_ok': False, 'cuda_available': False, 'error': repr(exc), 'devices': []}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', choices=['trace', 'timing', 'all'], default=None, help='return nonzero if the requested readiness lane is blocked')
    ap.add_argument('--timeout-seconds', type=int, default=int(os.environ.get('PREFLIGHT_TIMEOUT_SECONDS', str(PREFLIGHT_TIMEOUT_SECONDS_DEFAULT))), help='fail fast if dependency imports/cache checks hang')
    ap.add_argument('--require-weight-hash', action='store_true', default=os.environ.get('REQUIRE_WEIGHT_HASH') == '1', help='require pinned model.safetensors SHA-256 while evaluating local snapshot readiness')
    ap.add_argument('--capture-local-only', action='store_true', default=os.environ.get('CAPTURE_LOCAL_ONLY') == '1', help='treat public trace capture as local-files-only even when ALLOW_DOWNLOAD=1 was left in the environment')
    args = ap.parse_args()

    if args.timeout_seconds > 0 and hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(args.timeout_seconds)

    packet_path = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json'
    packet = json.loads(packet_path.read_text(encoding='utf-8')) if packet_path.exists() else {}
    target = packet.get('target_model', {})
    model_id = str(os.environ.get('MODEL_ID') or target.get('model_id') or DEFAULT_MODEL_ID)
    revision = str(os.environ.get('MODEL_REVISION') or target.get('model_revision') or DEFAULT_REVISION)
    allow_download = str(os.environ.get('ALLOW_DOWNLOAD', '0')) == '1'
    capture_local_only = bool(args.capture_local_only)
    allow_download_for_snapshot_preflight = bool(allow_download and not capture_local_only)
    require_weight_hash = bool(args.require_weight_hash)

    modules = {name: module_status(name) for name in ['numpy', 'torch', 'transformers', 'huggingface_hub', 'safetensors', 'accelerate', 'hf_xet']}
    cache = integrity_snapshot_status(model_id, revision, include_hashes=require_weight_hash)
    disk = disk_status(ROOT)
    device = torch_device_status(modules['torch'])

    blockers: list[str] = []
    warnings: list[str] = []
    if not modules['torch'].get('import_ok'):
        blockers.append('torch_not_importable')
    if not modules['transformers'].get('import_ok'):
        blockers.append('transformers_not_importable')
    if not modules['huggingface_hub'].get('import_ok'):
        blockers.append('huggingface_hub_not_importable')
    if not cache['found_complete_integrity_snapshot'] and not allow_download_for_snapshot_preflight:
        blockers.append('no_integrity_valid_local_hf_snapshot_and_download_not_allowed')
    if require_weight_hash and not cache['found_digest_verified_integrity_snapshot'] and not allow_download_for_snapshot_preflight:
        blockers.append('no_digest_verified_local_hf_snapshot_and_download_not_allowed')
    if require_weight_hash and cache['found_complete_integrity_snapshot'] and not cache['found_digest_verified_integrity_snapshot']:
        blockers.append('complete_snapshot_without_pinned_model_safetensors_sha256')
    if allow_download and capture_local_only:
        warnings.append('allow_download_ignored_for_local_only_capture_preflight')
    if allow_download_for_snapshot_preflight and not disk['free_gb_ge_6']:
        blockers.append('download_allowed_but_less_than_6gb_free_space')
    if allow_download_for_snapshot_preflight and not modules['hf_xet'].get('import_ok'):
        warnings.append('hf_xet_not_importable_download_may_be_slower_or_fail_for_xet_backed_files')
    if not device.get('cuda_available'):
        warnings.append('cuda_not_available_named_hardware_timing_blocked_here')
    if modules['transformers'].get('import_ok'):
        # Do not parse versions with packaging dependency; this is an informational warning.
        v = str(modules['transformers'].get('version', 'unknown'))
        if v != 'unknown' and v.startswith(('4.3', '4.4', '4.5')):
            warnings.append('transformers_version_may_be_too_old_for_current_attention_interface_capture')

    trace_ready = not blockers
    timing_ready = trace_ready and bool(device.get('cuda_available'))
    status = 'trace_env_ready' if trace_ready else 'blocked_here'
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'model_id': model_id,
        'model_revision': revision,
        'allow_download': allow_download,
        'capture_local_only': capture_local_only,
        'allow_download_for_snapshot_preflight': allow_download_for_snapshot_preflight,
        'require_weight_hash': require_weight_hash,
        'local_snapshot_dir': os.environ.get('LOCAL_SNAPSHOT_DIR'),
        'python': {
            'executable': sys.executable,
            'version': platform.python_version(),
            'platform': platform.platform(),
        },
        'modules': modules,
        'hf_cache': cache,
        'snapshot_integrity_contract': cache.get('snapshot_integrity_contract'),
        'shared_integrity_snapshot_preflight': bool(cache.get('shared_integrity_inspector_used')),
        'digest_verified_snapshot_preflight': bool(cache.get('found_digest_verified_integrity_snapshot')),
        'disk': disk,
        'device': device,
        'trace_ready': trace_ready,
        'timing_ready': timing_ready,
        'blockers': blockers,
        'warnings': warnings,
        'next_command_if_trace_ready': f'ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh',
        'next_repair_if_blocked': [
            'install/import transformers in the run environment',
            'populate an integrity-valid reviewed HF snapshot, set LOCAL_SNAPSHOT_DIR to a flat reviewed snapshot, or rerun with ALLOW_DOWNLOAD=1 after source review',
            'use CUDA hardware only for timing promotion; trace capture can be CPU but may be slow',
        ],
    }
    json_path = OUT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.json'
    md_path = OUT / f'{REVUP}_PUBLIC_TRACE_ENV_PREFLIGHT.md'
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md_path.write_text(
        f'# Public trace environment preflight — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        f"Trace ready: `{str(trace_ready).lower()}`  \nTiming ready: `{str(timing_ready).lower()}`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Environment\n\n'
        + f"- Python: `{platform.python_version()}`\n"
        + f"- torch: `{modules['torch'].get('version', 'missing')}`\n"
        + f"- transformers: `{modules['transformers'].get('version', 'missing')}`\n"
        + f"- huggingface_hub: `{modules['huggingface_hub'].get('version', 'missing')}`\n"
        + f"- CUDA available: `{device.get('cuda_available')}`\n"
        + f"- local integrity-valid snapshot: `{cache['found_complete_integrity_snapshot']}`\n"
        + f"- digest-verified snapshot: `{cache.get('found_digest_verified_integrity_snapshot')}`\n"
        + f"- require weight hash: `{require_weight_hash}`\n"
        + f"- allow download: `{allow_download}`\n"
        + f"- capture local-only: `{capture_local_only}`\n"
        + f"- allow download for snapshot preflight: `{allow_download_for_snapshot_preflight}`\n"
        + f"- free disk GB: `{disk['free_gb']}`\n\n"
        '## Interpretation\n\nThis is the execution gate that was missing from earlier packets. It turns an unrun public trace into a concrete repair list: dependencies, shared-integrity snapshot/cache state, download policy, disk, and timing hardware. For capture-local-only runs, download permission is ignored; a digest-verified local snapshot must exist before capture starts. It intentionally does not promote anything.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': status, 'trace_ready': trace_ready, 'timing_ready': timing_ready, 'blockers': blockers, 'warnings': warnings}, indent=2))
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)
    if args.strict in ('trace', 'all') and not trace_ready:
        return 1
    if args.strict in ('timing', 'all') and not timing_ready:
        return 1
    return 0


if __name__ == '__main__':
    try:
        exit_code = main()
    except TimeoutError:
        timeout_seconds = int(os.environ.get('PREFLIGHT_TIMEOUT_SECONDS', str(PREFLIGHT_TIMEOUT_SECONDS_DEFAULT)))
        exit_code = write_timeout_audit(timeout_seconds)
    # Some local torch/CUDA builds can stall during interpreter shutdown after
    # import-based capability checks. The preflight has already flushed its
    # audit files and printed its JSON summary, so bypass atexit handlers to
    # make this a bounded gate rather than another hidden runtime hang.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(int(exit_code))
