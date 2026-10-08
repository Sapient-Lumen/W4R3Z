#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0121'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def index_or_none(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    return idx if idx >= 0 else None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    prep_rel = f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh'
    run_rel = f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
    fast_rel = 'tools/public_trace_fast_prereq_gate.py'
    prep = read(prep_rel)
    run = read(run_rel)
    fast = read(fast_rel)
    required_prep_markers = [
        'public_trace_fast_prereq_gate.py --phase snapshot --download --strict',
        'public_trace_fast_prereq_gate.py --phase snapshot --local-only --strict',
        'snapshot_integrity_contract_audit.py',
        'hf_snapshot_dry_run_audit.py --require-network --strict',
        'hf_snapshot_materializer.py --download --strict',
        'hf_snapshot_materializer.py --local-only --strict',
        'public_trace_dependency_lock_audit.py || true',
        'public_trace_env_preflight.py --strict trace',
        '--require-weight-hash || true',
        'snapshot_prepare_phase_order_audit.py',
    ]
    for marker in required_prep_markers:
        if marker not in prep:
            errors.append('snapshot_prepare_missing_marker:' + marker)
    if 'public_trace_fast_prereq_gate.py --phase capture --local-only --strict' not in run:
        errors.append('capture_run_missing_phase_marker:public_trace_fast_prereq_gate.py --phase capture --local-only --strict')
    if 'public_trace_fast_prereq_gate.py --phase capture --download --strict' in run:
        errors.append('capture_run_should_not_have_download_phase_marker')
    materializer_idx = index_or_none(prep, 'hf_snapshot_materializer.py')
    dep_idx = index_or_none(prep, 'public_trace_dependency_lock_audit.py')
    env_idx = index_or_none(prep, 'public_trace_env_preflight.py --strict trace')
    if materializer_idx is None:
        errors.append('snapshot_prepare_missing_materializer')
    if dep_idx is None:
        errors.append('snapshot_prepare_missing_dependency_lock_receipt')
    if env_idx is None:
        errors.append('snapshot_prepare_missing_env_preflight_receipt')
    if materializer_idx is not None and dep_idx is not None and dep_idx < materializer_idx:
        errors.append('dependency_lock_runs_before_snapshot_materializer')
    if materializer_idx is not None and env_idx is not None and env_idx < materializer_idx:
        errors.append('env_preflight_runs_before_snapshot_materializer')
    for marker in ['capture_runtime_blockers_deferred_until_after_snapshot_materialization', 'SNAPSHOT_REQUIRED_MODULES', 'CAPTURE_REQUIRED_MODULES', "choices=['capture', 'snapshot']"]:
        if marker not in fast:
            errors.append('fast_prereq_missing_phase_separation_marker:' + marker)
    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Audits the snapshot-preparation split: snapshot phase may proceed without transformers, capture phase may not, snapshot integrity is checked before capture-runtime receipts are collected, and rev0131 keeps digest-aware local-only capture preflight in the after-materializer phase.',
        'prepare_script': prep_rel,
        'run_script': run_rel,
        'fast_prereq_gate': fast_rel,
        'phase_order': {
            'first_materializer_marker_index': materializer_idx,
            'dependency_lock_marker_index': dep_idx,
            'env_preflight_marker_index': env_idx,
            'dependency_and_env_are_after_materializer': bool(materializer_idx is not None and dep_idx is not None and env_idx is not None and dep_idx > materializer_idx and env_idx > materializer_idx),
        },
        'errors': errors,
        'warnings': warnings,
        'decision': 'snapshot_materialization_can_progress_before_capture_runtime_repair' if not errors else 'repair_snapshot_prepare_phase_order',
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline Transformers use requires a downloaded/cached model repository ahead of time.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download', 'fact': 'snapshot_download can materialize selected files by revision and allow_patterns.'},
        ],
    }
    (OUT / f'{REVUP}_SNAPSHOT_PREPARE_PHASE_ORDER_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [f'# Snapshot prepare phase-order audit — {REVUP}', '', f"Status: `{audit['status']}`  ", 'Promotion allowed: `false`', '', '## Errors', '']
    lines.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    lines.extend(['', '## Warnings', ''])
    lines.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    lines.extend(['', '## Interpretation', '', 'This is a substance guard: preparing immutable model material is allowed to proceed before `transformers` is installed, while strict capture remains blocked until the runtime is repaired.'])
    (OUT / f'{REVUP}_SNAPSHOT_PREPARE_PHASE_ORDER_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
