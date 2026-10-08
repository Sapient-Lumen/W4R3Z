#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import DIGEST_RECEIPT_CONTRACT, sha256_file_with_receipt  # noqa: E402

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
REVNO = int(str(META.get('revision_number', REV.replace('rev','0'))))
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    fixture_records: dict[str, Any] = {}
    old_disable = os.environ.pop('PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE', None)
    try:
        with tempfile.TemporaryDirectory(prefix='rev0142_digest_receipt_fixture_') as td:
            p = Path(td) / 'fixture-model.safetensors'
            payload1 = (b'not a real safetensors file; digest cache fixture\n' * 1024)
            p.write_bytes(payload1)
            expected1 = sha(payload1)
            first = sha256_file_with_receipt(p, expected_sha256=expected1, purpose='rev0142_fixture_first_hash')
            second = sha256_file_with_receipt(p, expected_sha256=expected1, purpose='rev0142_fixture_second_hash')
            payload2 = payload1 + b'changed\n'
            p.write_bytes(payload2)
            expected2 = sha(payload2)
            third = sha256_file_with_receipt(p, expected_sha256=expected2, purpose='rev0142_fixture_after_mutation')
            fixture_records = {'first': first, 'second': second, 'third_after_mutation': third}
            if first.get('sha256_source') != 'computed_full_file':
                errors.append('first_fixture_hash_did_not_compute_full_file')
            if second.get('sha256_source') != 'stat_bound_digest_receipt_cache':
                errors.append('second_fixture_hash_did_not_reuse_stat_bound_receipt')
            if third.get('sha256_source') != 'computed_full_file':
                errors.append('mutated_fixture_hash_did_not_invalidate_receipt')
            if first.get('sha256') != expected1 or second.get('sha256') != expected1 or third.get('sha256') != expected2:
                errors.append('fixture_sha256_mismatch')
    finally:
        if old_disable is not None:
            os.environ['PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE'] = old_disable
    src = (ROOT / 'tools' / 'hf_snapshot_integrity.py').read_text(encoding='utf-8', errors='replace')
    for marker in [DIGEST_RECEIPT_CONTRACT, 'PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE', 'sha256_file_with_receipt']:
        if marker not in src:
            errors.append('hf_snapshot_integrity_missing_marker:' + marker)
    audit = {
        'revision': REV,
        'revision_number': REVNO,
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Guards the high-risk 2.2GB model hash path: the first full SHA-256 remains mandatory, but subsequent gates may reuse only a stat-bound receipt when path, resolved path, size, mtime, ctime, device, and inode are unchanged.',
        'contract': DIGEST_RECEIPT_CONTRACT,
        'disable_env': 'PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1',
        'fixture_records': fixture_records,
        'errors': errors,
        'warnings': warnings,
        'online_basis': [
            {'url': 'https://huggingface.co/docs/transformers/installation', 'fact': 'Transformers offline mode requires downloaded/cached model files ahead of time and supports local_files_only for local directories.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'snapshot_download materializes repository files into the local cache/snapshot path before offline use.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/2fef61190c752e2412f7b5dd2c2bde6f08fdb634/model.safetensors', 'fact': 'The TinyLlama model.safetensors file is Xet-backed, about 2.2GB, and publishes the pinned SHA-256 used by this cube.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables', 'fact': 'HF_HUB_DOWNLOAD_TIMEOUT and HF_HUB_ETAG_TIMEOUT are configurable for slow connections.'},
        ],
        'decision': 'digest_receipt_cache_ok' if not errors else 'repair_digest_receipt_cache_before_hash_heavy_runner',
    }
    (OUT / f'{REVUP}_SNAPSHOT_DIGEST_RECEIPT_CACHE_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Snapshot digest receipt cache audit — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        audit['summary'],
        '',
        '## Contract',
        '',
        f"- `{DIGEST_RECEIPT_CONTRACT}`",
        '- First observed file identity computes a full SHA-256.',
        '- Later unchanged identities may reuse the receipt.',
        '- File mutation invalidates the receipt because stat identity changes.',
        '- Set `PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1` to force full rehash.',
        '',
        '## Errors',
        '',
    ]
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Warnings', ''])
    md.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    (OUT / f'{REVUP}_SNAPSHOT_DIGEST_RECEIPT_CACHE_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
