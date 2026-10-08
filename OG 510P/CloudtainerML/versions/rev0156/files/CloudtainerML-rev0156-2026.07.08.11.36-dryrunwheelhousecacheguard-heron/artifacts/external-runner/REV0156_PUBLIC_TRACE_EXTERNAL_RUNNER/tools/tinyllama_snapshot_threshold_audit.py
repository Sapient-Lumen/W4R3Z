#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    ALLOW_PATTERNS,
    DEFAULT_MODEL_ID,
    DEFAULT_REVISION,
    MIN_BYTES,
    PUBLISHED_SIZE_BYTES,
    REQUIRED_SNAPSHOT_FILES,
)

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

# Source-observed locked file sizes from the pinned Hugging Face tree.  The
# purpose is not to replace content checks, but to prevent local thresholds from
# becoming impossible to satisfy for a legitimate locked snapshot.
SOURCE_FACTS = [
    {
        'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6',
        'observed_lines': 'tree lines 213-250 list config.json 608 Bytes, generation_config.json 124 Bytes, model.safetensors 2.2 GB, special_tokens_map.json 551 Bytes, tokenizer.json 1.84 MB, tokenizer.model 500 kB, tokenizer_config.json 1.29 kB',
    },
    {
        'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/fe8a4ea1ffedaf415f4da2f062534de366a451e6/config.json',
        'observed_lines': 'config page line 63 reports 608 Bytes and lines 65-112 show the expected LlamaForCausalLM/TinyLlama config fields',
    },
    {
        'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download',
        'observed_lines': 'snapshot_download downloads an entire repository at a revision and supports allow_patterns/dry-run planning',
    },
]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if set(REQUIRED_SNAPSHOT_FILES) != set(PUBLISHED_SIZE_BYTES):
        errors.append('published_size_hints_do_not_cover_required_snapshot_files')
    for name in REQUIRED_SNAPSHOT_FILES:
        min_bytes = int(MIN_BYTES.get(name, 1))
        published = PUBLISHED_SIZE_BYTES.get(name)
        if published is None:
            errors.append(f'missing_published_size_hint:{name}')
            continue
        if min_bytes > int(published):
            errors.append(f'min_bytes_exceeds_published_size:{name}:{min_bytes}>{published}')
        if min_bytes <= 0:
            errors.append(f'min_bytes_not_positive:{name}')
    if 'config.json' in MIN_BYTES and MIN_BYTES['config.json'] > 608:
        errors.append('config_json_min_bytes_would_reject_pinned_tinyllama_config')
    if set(ALLOW_PATTERNS) != set(REQUIRED_SNAPSHOT_FILES + ['README.md']):
        warnings.append('allow_patterns_changed_from_required_files_plus_readme')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Guards the snapshot integrity refactor against impossible hardcoded minimum-size thresholds. Rev0127 fixes the config.json threshold that would have rejected the locked 608-byte TinyLlama config.',
        'model_id': DEFAULT_MODEL_ID,
        'model_revision': DEFAULT_REVISION,
        'required_snapshot_files': REQUIRED_SNAPSHOT_FILES,
        'published_size_hints_bytes': PUBLISHED_SIZE_BYTES,
        'minimum_thresholds_bytes': MIN_BYTES,
        'errors': errors,
        'warnings': warnings,
        'source_basis': SOURCE_FACTS,
        'decision': 'snapshot_thresholds_do_not_reject_locked_tree' if not errors else 'repair_snapshot_thresholds_before_materialization',
    }
    (OUT / f'{REVUP}_TINYLLAMA_SNAPSHOT_THRESHOLD_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [
        f'# TinyLlama snapshot threshold audit — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        '## What this prevents',
        '',
        'A legitimate pinned TinyLlama snapshot must not be rejected by impossible local minimum-size thresholds. Rev0126 had `config.json >= 1000` even though the locked tree reports `config.json` as 608 bytes.',
        '',
        '## Errors',
        '',
    ]
    lines.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    lines.extend(['', '## Warnings', ''])
    lines.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    (OUT / f'{REVUP}_TINYLLAMA_SNAPSHOT_THRESHOLD_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
