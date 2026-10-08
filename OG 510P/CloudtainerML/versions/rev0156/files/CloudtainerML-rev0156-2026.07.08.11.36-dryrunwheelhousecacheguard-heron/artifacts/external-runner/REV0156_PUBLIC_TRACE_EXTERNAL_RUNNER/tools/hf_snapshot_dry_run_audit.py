#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib
import importlib.util
import inspect
import json
import os
import socket
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0099'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
MAN = ROOT / 'artifacts' / 'run-manifests'
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL_ID = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
DEFAULT_REVISION = 'fe8a4ea1ffedaf415f4da2f062534de366a451e6'
ALLOW_PATTERNS = ['config.json', 'generation_config.json', 'model.safetensors', 'special_tokens_map.json', 'tokenizer.json', 'tokenizer.model', 'tokenizer_config.json', 'README.md']
REQUIRED_FILES = ['config.json', 'generation_config.json', 'model.safetensors', 'special_tokens_map.json', 'tokenizer.json', 'tokenizer.model', 'tokenizer_config.json']


def module_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    out: dict[str, Any] = {'present': bool(spec is not None), 'origin': getattr(spec, 'origin', None) if spec else None}
    if spec is None:
        return out
    try:
        mod = importlib.import_module(name)
        out['import_ok'] = True
        out['version'] = str(getattr(mod, '__version__', 'unknown'))
    except Exception as exc:
        out['import_ok'] = False
        out['error'] = repr(exc)
    return out


def network_probe(host: str = 'huggingface.co', port: int = 443, timeout: float = 3.0) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {'ok': True, 'host': host, 'port': port, 'timeout': timeout}
    except Exception as exc:
        return {'ok': False, 'host': host, 'port': port, 'timeout': timeout, 'error': type(exc).__name__ + ': ' + repr(exc)}


def dry_info_to_dict(item: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for name in ['filename', 'file_path', 'repo_file_path', 'size', 'file_size', 'is_cached', 'will_download', 'local_path', 'commit_hash']:
        if hasattr(item, name):
            try:
                v = getattr(item, name)
                if isinstance(v, Path):
                    v = str(v)
                data[name] = v
            except Exception:
                pass
    if not data:
        try:
            data.update(dict(vars(item)))
        except Exception:
            data['repr'] = repr(item)
    fname = data.get('filename') or data.get('file_path') or data.get('repo_file_path') or data.get('path') or ''
    data['normalized_filename'] = str(fname).split('/')[-1]
    size = data.get('size', data.get('file_size'))
    try:
        data['normalized_size_bytes'] = int(size) if size is not None else None
    except Exception:
        data['normalized_size_bytes'] = None
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Hugging Face snapshot dry-run preflight for the current TinyLlama trace packet.')
    ap.add_argument('--model-id', default=os.environ.get('MODEL_ID', DEFAULT_MODEL_ID))
    ap.add_argument('--revision', default=os.environ.get('MODEL_REVISION', DEFAULT_REVISION))
    ap.add_argument('--cache-dir', default=os.environ.get('HF_HUB_CACHE'))
    ap.add_argument('--etag-timeout', type=float, default=float(os.environ.get('HF_ETAG_TIMEOUT', '5')))
    ap.add_argument('--network-probe-timeout', type=float, default=float(os.environ.get('HF_NETWORK_PROBE_TIMEOUT', '3')))
    ap.add_argument('--require-network', action='store_true', help='treat skipped/failed dry-run as a blocker')
    ap.add_argument('--skip-network', action='store_true', help='do not call the Hub; only record that dry-run was skipped')
    ap.add_argument('--strict', action='store_true', help='return nonzero on blockers')
    args = ap.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []
    status = 'not_run'
    dry_run_attempted = False
    dry_run_error = None
    dry_run_items: list[dict[str, Any]] = []
    network_allowed = (os.environ.get('ALLOW_NETWORK_DRY_RUN') == '1') or args.require_network
    network_check: dict[str, Any] = {'ok': None, 'skipped': True}
    hf = module_status('huggingface_hub')
    caps: dict[str, Any] = {}

    if not hf.get('import_ok'):
        blockers.append('huggingface_hub_not_importable_for_snapshot_dry_run')
    else:
        try:
            from huggingface_hub import snapshot_download  # type: ignore
            sig = inspect.signature(snapshot_download)
            caps['signature'] = str(sig)
            caps['supports_dry_run'] = 'dry_run' in sig.parameters
            caps['supports_revision'] = 'revision' in sig.parameters
            caps['supports_allow_patterns'] = 'allow_patterns' in sig.parameters
            if not caps['supports_dry_run']:
                blockers.append('snapshot_download_dry_run_not_supported_by_installed_huggingface_hub')
            if not caps['supports_revision'] or not caps['supports_allow_patterns']:
                blockers.append('snapshot_download_missing_revision_or_allow_patterns_capability')
            if args.skip_network:
                status = 'network_dry_run_skipped'
                if args.require_network:
                    blockers.append('network_dry_run_required_but_explicitly_skipped')
            elif not network_allowed:
                status = 'network_dry_run_skipped'
                warnings.append('network_dry_run_not_attempted_set_ALLOW_NETWORK_DRY_RUN_1_or_use_require_network')
                if args.require_network:
                    blockers.append('network_dry_run_required_but_not_allowed')
            elif not blockers:
                network_check = network_probe(timeout=args.network_probe_timeout)
                if not network_check.get('ok'):
                    dry_run_error = 'network_probe_failed: ' + str(network_check.get('error'))
                    blockers.append('huggingface_host_not_reachable_before_snapshot_dry_run')
                    status = 'blocked_here'
                else:
                    dry_run_attempted = True
                    try:
                        result = snapshot_download(
                            repo_id=args.model_id,
                            revision=args.revision,
                            cache_dir=args.cache_dir,
                            local_files_only=False,
                            allow_patterns=ALLOW_PATTERNS,
                            etag_timeout=args.etag_timeout,
                            dry_run=True,
                        )
                        dry_run_items = [dry_info_to_dict(x) for x in result]
                        status = 'dry_run_pass'
                    except Exception as exc:
                        dry_run_error = type(exc).__name__ + ': ' + repr(exc)
                        blockers.append('snapshot_dry_run_failed')
                        status = 'blocked_here'
        except Exception as exc:
            blockers.append('snapshot_download_signature_probe_failed')
            dry_run_error = repr(exc)
            status = 'blocked_here'

    planned_names = {str(x.get('normalized_filename')) for x in dry_run_items}
    missing_required_from_plan = [name for name in REQUIRED_FILES if name not in planned_names]
    if dry_run_items and missing_required_from_plan:
        blockers.append('snapshot_dry_run_plan_missing_required_files')
    total_size = sum(int(x.get('normalized_size_bytes') or 0) for x in dry_run_items)
    large_files = [x for x in dry_run_items if int(x.get('normalized_size_bytes') or 0) > 100_000_000]
    if not blockers and status == 'not_run':
        status = 'network_dry_run_skipped'
    final_status = 'dry_run_pass' if status == 'dry_run_pass' and not blockers else ('skipped' if status == 'network_dry_run_skipped' and not blockers else 'blocked_here')

    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': final_status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Dry-run preflight for the exact TinyLlama snapshot. This fails fast on repository/revision/network/token problems and estimates planned files before any 2.2GB weight download.',
        'model_id': args.model_id,
        'model_revision': args.revision,
        'allow_patterns': ALLOW_PATTERNS,
        'required_files': REQUIRED_FILES,
        'etag_timeout': args.etag_timeout,
        'network_allowed': network_allowed,
        'network_probe': network_check,
        'dry_run_attempted': dry_run_attempted,
        'dry_run_error': dry_run_error,
        'huggingface_hub': hf,
        'snapshot_download_capabilities': caps,
        'planned_file_count': len(dry_run_items),
        'planned_total_size_bytes_known': total_size,
        'planned_total_size_gb_known': round(total_size / (1024 ** 3), 3),
        'large_planned_files': large_files[:10],
        'planned_files': dry_run_items[:50],
        'missing_required_from_plan': missing_required_from_plan,
        'blockers': blockers,
        'warnings': warnings,
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'snapshot_download supports revisions and allow_patterns and caches downloads.'},
            {'url': 'https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/_snapshot_download.py', 'fact': 'current snapshot_download supports dry_run and returns DryRunFileInfo objects.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6', 'fact': 'selected TinyLlama tree is a concrete commit containing the required config/tokenizer/safetensors files.'},
        ],
    }
    (OUT / f'{REVUP}_HF_SNAPSHOT_DRY_RUN_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_HF_SNAPSHOT_DRY_RUN_AUDIT.md').write_text(
        f'# HF snapshot dry-run audit — {REVUP}\n\n'
        f"Status: `{final_status}`  \nPromotion allowed: `false`\n\n"
        f"Dry run attempted: `{str(dry_run_attempted).lower()}`  \nKnown planned size GB: `{audit['planned_total_size_gb_known']}`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThis is a bandwidth/time safety valve. If `ALLOW_DOWNLOAD=1` is set, the gate should prove repo/revision reachability with `dry_run=True` before attempting to materialize the full snapshot.\n',
        encoding='utf-8'
    )
    (MAN / f'{REVUP}_HF_SNAPSHOT_DRY_RUN_PLAN.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': final_status, 'dry_run_attempted': dry_run_attempted, 'blockers': blockers, 'warnings': warnings}, indent=2))
    return 1 if args.strict and blockers else 0

if __name__ == '__main__':
    raise SystemExit(main())
