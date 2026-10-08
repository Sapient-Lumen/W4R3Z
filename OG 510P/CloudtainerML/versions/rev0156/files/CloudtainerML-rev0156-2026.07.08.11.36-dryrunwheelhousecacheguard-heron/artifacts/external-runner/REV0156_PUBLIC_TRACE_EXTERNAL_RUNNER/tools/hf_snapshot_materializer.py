#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    ALLOW_PATTERNS,
    DEFAULT_MODEL_ID,
    DEFAULT_REVISION,
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    EXPECTED_MODEL_SAFETENSORS_XET_HASH,
    REQUIRED_SNAPSHOT_FILES,
    cache_roots,
    inspect_snapshot,
    snapshot_path,
    sha256_file_with_receipt,
)

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0096'))
REVUP = REV.upper()
OUT_AUDIT = ROOT / 'artifacts' / 'audit'
OUT_MANIFEST = ROOT / 'artifacts' / 'run-manifests'
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT_MANIFEST.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    return str(sha256_file_with_receipt(path, expected_sha256=EXPECTED_MODEL_SAFETENSORS_SHA256).get('sha256') or '')


def maybe_hash_weights(checks: list[dict[str, Any]]) -> None:
    for check in checks:
        if not check.get('complete_required_snapshot'):
            continue
        p = Path(str(check.get('path', ''))) / 'model.safetensors'
        if check.get('model_safetensors', {}).get('sha256'):
            continue
        if p.exists() and p.is_file():
            check['model_safetensors']['sha256'] = sha256_file(p)
            check['model_safetensors']['sha256_matches_expected'] = check['model_safetensors']['sha256'] == EXPECTED_MODEL_SAFETENSORS_SHA256
            if not check['model_safetensors']['sha256_matches_expected']:
                check.setdefault('blockers', []).append('model_safetensors_sha256_mismatch')
                check['complete_required_snapshot'] = False


def main() -> int:
    ap = argparse.ArgumentParser(description='Materialize or verify the exact TinyLlama snapshot for public trace capture.')
    ap.add_argument('--model-id', default=os.environ.get('MODEL_ID', DEFAULT_MODEL_ID))
    ap.add_argument('--revision', default=os.environ.get('MODEL_REVISION', DEFAULT_REVISION))
    ap.add_argument('--cache-dir', default=os.environ.get('HF_HUB_CACHE'))
    ap.add_argument('--snapshot-dir', default=os.environ.get('LOCAL_SNAPSHOT_DIR'), help='optional reviewed flat/local snapshot directory to verify before HF cache/download paths')
    ap.add_argument('--download', action='store_true', help='call huggingface_hub.snapshot_download for the reviewed revision')
    ap.add_argument('--local-only', action='store_true', help='do not download; only verify cache')
    ap.add_argument('--include-hashes', action='store_true', help='hash files found in the local snapshot; hashes the 2.2GB weight file')
    ap.add_argument('--strict', action='store_true', help='return nonzero if a complete integrity-valid snapshot is unavailable after requested action')
    args = ap.parse_args()
    blockers: list[str] = []
    warnings: list[str] = []
    download_attempted = False
    download_error = None
    resolved_snapshot = None
    if args.download and args.local_only:
        raise SystemExit('choose either --download or --local-only, not both')
    if args.download:
        if importlib.util.find_spec('huggingface_hub') is None:  # type: ignore[attr-defined]
            blockers.append('huggingface_hub_not_importable_for_snapshot_download')
        else:
            try:
                from huggingface_hub import snapshot_download  # type: ignore
                download_attempted = True
                resolved_snapshot = snapshot_download(
                    repo_id=args.model_id,
                    revision=args.revision,
                    cache_dir=args.cache_dir,
                    local_files_only=False,
                    allow_patterns=ALLOW_PATTERNS,
                )
            except Exception as exc:
                download_error = type(exc).__name__ + ': ' + repr(exc)
                blockers.append('snapshot_download_failed')
    elif not args.local_only:
        warnings.append('neither_download_nor_local_only_set_defaulted_to_local_cache_check')

    checks: list[dict[str, Any]] = []
    if args.snapshot_dir:
        checks.append(inspect_snapshot(Path(args.snapshot_dir).expanduser().resolve(), model_id=args.model_id, revision=args.revision, include_hashes=args.include_hashes))
    if resolved_snapshot:
        checks.append(inspect_snapshot(Path(resolved_snapshot), model_id=args.model_id, revision=args.revision, include_hashes=args.include_hashes))
    for root in cache_roots(args.cache_dir):
        p = snapshot_path(root, args.model_id, args.revision)
        item = inspect_snapshot(p, model_id=args.model_id, revision=args.revision, include_hashes=args.include_hashes)
        if not any(c.get('path') == item.get('path') for c in checks):
            checks.append(item)
    if args.include_hashes:
        maybe_hash_weights(checks)
    complete = any(c.get('complete_required_snapshot') for c in checks)
    if not complete:
        blockers.append('complete_integrity_valid_tinyllama_snapshot_not_available')
    integrity_blockers = sorted(set(str(b) for c in checks for b in c.get('blockers', [])))

    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'snapshot_ready' if complete else 'blocked_here',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Materializes or verifies the exact TinyLlama HF snapshot. Rev0142 keeps this from filename presence to integrity and a stat-bound digest receipt cache: required file sizes, parseable JSON config, Llama/TinyLlama config fields, and safetensors header/tensor-offset sanity are checked without importing transformers.',
        'model_id': args.model_id,
        'model_revision': args.revision,
        'expected_model_safetensors_sha256': EXPECTED_MODEL_SAFETENSORS_SHA256,
        'expected_model_safetensors_xet_hash': EXPECTED_MODEL_SAFETENSORS_XET_HASH,
        'local_snapshot_dir': args.snapshot_dir,
        'required_files': REQUIRED_SNAPSHOT_FILES,
        'allow_patterns': ALLOW_PATTERNS,
        'download_attempted': download_attempted,
        'download_error': download_error,
        'cache_checks': checks,
        'complete_snapshot_available': complete,
        'integrity_blockers': integrity_blockers,
        'blockers': sorted(set(blockers)),
        'warnings': sorted(set(warnings)),
        'next_if_blocked': 'Install/use huggingface_hub with network or prepopulate the listed HF cache snapshot with full non-sparse files, then rerun this tool before capture.',
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download', 'fact': 'snapshot_download supports revisions, local_files_only, allow_patterns, dry_run, and reports incomplete snapshots.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/main/model.safetensors', 'fact': 'TinyLlama model.safetensors is published as a 2.2 GB safetensors file with SHA256 6e6001da2106d4757498752a021df6c2bdc332c650aae4bae6b0c004dcf14933.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'fact': 'Safetensors metadata can be parsed from the header without loading the full tensor buffer.'},
        ],
    }
    (OUT_AUDIT / f'{REVUP}_HF_SNAPSHOT_MATERIALIZER.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT_AUDIT / f'{REVUP}_HF_SNAPSHOT_MATERIALIZER.md').write_text(
        f'# HF snapshot materializer — {REVUP}\n\n'
        f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        f"Project revision: `{REV}`  \nModel: `{args.model_id}`  \nModel revision: `{args.revision}`\n\n"
        '## Required files\n\n' + '\n'.join(f'- `{x}`' for x in REQUIRED_SNAPSHOT_FILES) + '\n\n'
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in audit['blockers']) if audit['blockers'] else '- none') + '\n\n'
        '## Integrity blockers observed across candidates\n\n' + ('\n'.join(f'- `{b}`' for b in integrity_blockers) if integrity_blockers else '- none') + '\n\n'
        '## Interpretation\n\nThis is an executable repair for the highest-risk blocker: missing immutable public model material. It does not claim that the trace has run.\n',
        encoding='utf-8')
    (OUT_MANIFEST / f'{REVUP}_TINYLLAMA_SNAPSHOT_MATERIALIZATION.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'complete_snapshot_available': complete, 'blockers': audit['blockers'], 'integrity_blockers': integrity_blockers, 'warnings': audit['warnings']}, indent=2))
    if args.strict and not complete:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
