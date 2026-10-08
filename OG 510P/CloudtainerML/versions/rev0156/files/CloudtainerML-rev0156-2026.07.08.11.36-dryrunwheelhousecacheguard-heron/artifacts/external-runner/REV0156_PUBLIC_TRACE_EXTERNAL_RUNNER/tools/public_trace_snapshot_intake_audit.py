#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (
    DEFAULT_MODEL_ID,
    DEFAULT_REVISION,
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    REQUIRED_SNAPSHOT_FILES,
    inspect_snapshot,
)

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0100'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
MAN = ROOT / 'artifacts' / 'run-manifests'
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)
PUBLIC_ID_ALLOWLIST = [DEFAULT_MODEL_ID]


def is_hex_revision(value: str) -> bool:
    text = str(value or '').strip()
    return len(text) == 40 and all(c in '0123456789abcdefABCDEF' for c in text)


def main() -> int:
    ap = argparse.ArgumentParser(description='Audit a local/mounted HF snapshot directory for public-trace capture intake.')
    ap.add_argument('--snapshot-dir', default=os.environ.get('LOCAL_SNAPSHOT_DIR'), help='flat snapshot directory containing config/tokenizer/model.safetensors files')
    ap.add_argument('--model-id', default=os.environ.get('MODEL_ID', DEFAULT_MODEL_ID))
    ap.add_argument('--model-revision', default=os.environ.get('MODEL_REVISION', DEFAULT_REVISION))
    ap.add_argument('--hash-weights', action='store_true', help='hash model.safetensors as part of intake; can be slow')
    ap.add_argument('--strict', action='store_true', help='return nonzero if a provided snapshot is invalid')
    args = ap.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []
    if not str(args.model_id).strip():
        blockers.append('model_id_empty')
    if str(args.model_id) not in PUBLIC_ID_ALLOWLIST:
        warnings.append('model_id_not_in_current_public_trace_allowlist')
    if not is_hex_revision(str(args.model_revision)):
        blockers.append('model_revision_not_immutable_40_hex_commit')

    if args.snapshot_dir:
        snapshot = inspect_snapshot(Path(args.snapshot_dir), model_id=args.model_id, revision=args.model_revision, include_hashes=args.hash_weights)
        if not snapshot.get('complete_required_snapshot'):
            blockers.extend(str(x) for x in snapshot.get('blockers', []))
        warnings.extend(str(x) for x in snapshot.get('warnings', []))
    else:
        snapshot = {'provided': False, 'exists': False, 'complete_required_snapshot': False, 'blockers': [], 'warnings': ['local_snapshot_dir_not_set']}
        warnings.append('local_snapshot_dir_not_set')

    status = 'local_snapshot_ready' if snapshot.get('complete_required_snapshot') and not blockers else ('not_provided' if not args.snapshot_dir and not blockers else 'blocked_here')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev', '')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Local snapshot intake audit. Rev0121 shares the strict snapshot-integrity contract used by the materializer so a local path cannot pass by filename presence alone.',
        'model_id': args.model_id,
        'model_revision': args.model_revision,
        'expected_model_safetensors_sha256': EXPECTED_MODEL_SAFETENSORS_SHA256,
        'local_snapshot_dir_env': os.environ.get('LOCAL_SNAPSHOT_DIR'),
        'hash_weights': bool(args.hash_weights),
        'required_files': REQUIRED_SNAPSHOT_FILES,
        'snapshot': snapshot,
        'blockers': sorted(set(blockers)),
        'warnings': sorted(set(warnings)),
        'operator_contract': {
            'loader_path_env': 'LOCAL_SNAPSHOT_DIR',
            'canonical_public_identity_env': 'MODEL_ID',
            'why': 'from_pretrained may load from a local path, but public evidence should retain the immutable public model identifier and commit in provenance.',
        },
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'snapshot_download can filter files with allow_patterns and can download to a local_dir.'},
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline Transformers use requires downloaded/cached files ahead of time and local_files_only or HF_HUB_OFFLINE controls.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'fact': 'Safetensors headers can be parsed separately from tensor buffers.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_SNAPSHOT_INTAKE_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_PUBLIC_TRACE_SNAPSHOT_INTAKE_AUDIT.md').write_text(
        f'# Public trace snapshot intake audit — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        f"Model id: `{args.model_id}`  \nModel revision: `{args.model_revision}`  \nLocal snapshot dir: `{args.snapshot_dir or 'not set'}`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in audit['blockers']) if audit['blockers'] else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in audit['warnings']) if audit['warnings'] else '- none') + '\n\n'
        '## Interpretation\n\nThis audit enables an offline/operator path: set `LOCAL_SNAPSHOT_DIR` to a reviewed flat snapshot directory, keep `MODEL_ID` as the canonical HF id, and let the launcher pass `--public-model-id` so provenance does not become a local filesystem path.\n',
        encoding='utf-8'
    )
    (MAN / f'{REVUP}_LOCAL_SNAPSHOT_INTAKE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'blockers': audit['blockers'], 'warnings': audit['warnings']}, indent=2))
    return 1 if args.strict and blockers else 0


if __name__ == '__main__':
    raise SystemExit(main())
