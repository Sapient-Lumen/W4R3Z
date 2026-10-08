#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

ENV_PREFLIGHT = ROOT / 'tools/public_trace_env_preflight.py'
FAST_GATE = ROOT / 'tools/public_trace_fast_prereq_gate.py'
RUN = ROOT / f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
PREP = ROOT / f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh'
SMOKE = ROOT / 'tools/smoke_validate.py'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def has_all(src: str, markers: list[str]) -> list[str]:
    return [m for m in markers if m not in src]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    env_src = read(ENV_PREFLIGHT)
    fast_src = read(FAST_GATE)
    run_src = read(RUN)
    prep_src = read(PREP)
    smoke_src = read(SMOKE)

    if not ENV_PREFLIGHT.is_file():
        errors.append('missing_public_trace_env_preflight')
    missing = has_all(env_src, [
        'from tools.hf_snapshot_integrity import',
        'inspect_snapshot',
        'snapshot_candidate_paths',
        'def integrity_snapshot_status',
        'shared_integrity_inspector_used',
        'found_complete_integrity_snapshot',
        'no_integrity_valid_local_hf_snapshot_and_download_not_allowed',
    ])
    errors.extend('env_preflight_missing_marker:' + m for m in missing)
    if 'def cache_snapshot_status' in env_src:
        errors.append('env_preflight_still_defines_weak_cache_snapshot_status')
    if "required = ['config.json', 'model.safetensors'" in env_src:
        errors.append('env_preflight_still_uses_filename_minimum_snapshot_list')
    if "tokenizer.json_or_tokenizer.model" in env_src:
        errors.append('env_preflight_still_accepts_tokenizer_either_or_minimum_snapshot')

    fast_missing = has_all(fast_src, ['inspect_snapshot', 'snapshot_candidate_paths'])
    errors.extend('fast_gate_missing_shared_integrity_marker:' + m for m in fast_missing)

    for label, src in [('current_run_wrapper', run_src), ('snapshot_prepare_wrapper', prep_src)]:
        if 'tools/public_trace_env_snapshot_integrity_audit.py' not in src:
            errors.append(label + '_does_not_run_env_snapshot_integrity_audit')

    if 'public_trace_env_snapshot_integrity_audit.py' not in smoke_src:
        errors.append('smoke_validate_does_not_guard_env_snapshot_integrity_audit')
    if 'def cache_snapshot_status' not in smoke_src or 'env_preflight_still_defines_weak_cache_snapshot_status' not in smoke_src:
        warnings.append('smoke_validate_has_no_explicit_weak_cache_snapshot_marker_check')

    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(META.get('revision_number') or REV.replace('rev', '') or 0),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Checks that the env preflight uses the same shared TinyLlama snapshot integrity contract as the materializer/capture path instead of a weak filename/minimum-file cache probe.',
        'risk_closed': 'filename_only_env_preflight_could_waste_capture_lane_or_greenlight_invalid_snapshot',
        'env_preflight': ENV_PREFLIGHT.relative_to(ROOT).as_posix(),
        'current_run_wrapper': RUN.relative_to(ROOT).as_posix(),
        'snapshot_prepare_wrapper': PREP.relative_to(ROOT).as_posix(),
        'shared_integrity_required_markers': [
            'inspect_snapshot',
            'snapshot_candidate_paths',
            'found_complete_integrity_snapshot',
            'no_integrity_valid_local_hf_snapshot_and_download_not_allowed',
        ],
        'source_basis': [
            {
                'url': 'https://huggingface.co/docs/transformers/en/installation',
                'fact': 'Offline Transformers use requires downloaded/cached files ahead of time and local_files_only/HF_HUB_OFFLINE controls.',
            },
            {
                'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download',
                'fact': 'snapshot_download is revision-addressed, cached, and can filter files with allow_patterns.',
            },
            {
                'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/main',
                'fact': 'The selected TinyLlama tree publishes concrete file sizes for the required snapshot files.',
            },
        ],
        'errors': errors,
        'warnings': warnings,
        'decision': 'env_preflight_uses_shared_snapshot_integrity' if not errors else 'repair_env_snapshot_preflight_before_capture',
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_ENV_SNAPSHOT_INTEGRITY_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace env snapshot integrity audit — {REVUP}',
        '',
        f"Status: `{audit['status']}`  ",
        'Promotion allowed: `false`',
        '',
        '## Risk closed',
        '',
        audit['risk_closed'],
        '',
        '## Errors',
        '',
    ]
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Warnings', ''])
    md.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    md.extend(['', '## Interpretation', '', audit['summary']])
    (OUT / f'{REVUP}_PUBLIC_TRACE_ENV_SNAPSHOT_INTEGRITY_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
