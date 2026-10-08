#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    capture_rel = 'experiments/public_trace_capture/hf_attention_trace_capture.py'
    capture = read(capture_rel)
    one_shot_rel = f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh'
    one_shot = read(one_shot_rel)
    run_rel = f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
    run = read(run_rel)
    smoke = read('tools/smoke_validate.py')

    required_capture_markers = [
        'EXPECTED_MODEL_SAFETENSORS_SHA256',
        'def _snapshot_digest_authenticity_proof(',
        '--require-model-safetensors-sha256',
        'snapshot_digest_verified',
        'snapshot_digest_authenticity_contract',
        'model_safetensors_sha256_matches_expected',
        'model_safetensors_digest_authenticity_not_verified',
    ]
    for marker in required_capture_markers:
        if marker not in capture:
            errors.append('capture_missing_digest_acceptance_marker:' + marker)
    if '--require-model-safetensors-sha256' not in one_shot:
        errors.append('one_shot_capture_does_not_require_model_safetensors_sha256')

    if '--allow-download' in one_shot:
        errors.append('one_shot_capture_must_not_download_during_evidence_capture')
    if 'capture itself must not depend on network state' not in one_shot:
        errors.append('one_shot_capture_missing_local_only_evidence_capture_comment')
    if 'public_trace_fast_prereq_gate.py --phase capture' not in run:
        errors.append('run_wrapper_missing_fast_prereq_before_digest_capture')
    if 'public_trace_digest_acceptance_audit.py' not in run and 'public_trace_digest_acceptance_audit.py' not in one_shot:
        warnings.append('digest_acceptance_audit_not_run_on_live_capture_path')
    if 'public_trace_digest_acceptance_audit' not in smoke:
        errors.append('smoke_does_not_guard_public_trace_digest_acceptance_audit')

    status = 'pass' if not errors else 'fail'
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev', '')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Executable audit for the rev0124 evidence-lane hardening: public trace promotion requires a model.safetensors SHA-256 proof and the capture wrapper remains local-files-only; downloads belong to snapshot preparation, not evidence capture.',
        'checked_files': [capture_rel, one_shot_rel, run_rel, 'tools/smoke_validate.py'],
        'errors': errors,
        'warnings': warnings,
        'decision': 'digest_acceptance_contract_guarded' if not errors else 'repair_digest_acceptance_contract',
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'snapshot_download materializes a local snapshot of repository files at a requested revision.'},
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline Transformers use requires files to be downloaded/cached ahead of time.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'fact': 'Safetensors metadata is parseable without tensor loading, but byte authenticity still requires digest checking.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_DIGEST_ACCEPTANCE_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [
        f'# Public trace digest acceptance audit — {REVUP}',
        '',
        f"Status: `{status}`  ",
        'Promotion allowed: `false`',
        '',
        '## Errors',
        '',
    ]
    lines.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    lines.extend(['', '## Warnings', ''])
    lines.extend([f'- `{w}`' for w in warnings] if warnings else ['- none'])
    lines.extend([
        '',
        '## Interpretation',
        '',
        'This is a substance guard, not a new paperwork lane: public capture can only self-promote after the local or cached `model.safetensors` bytes match the pinned TinyLlama SHA-256, and the capture wrapper must not invoke network downloads. Structural safetensors parsing still catches fake/truncated files cheaply; digest acceptance closes the wrong-weight local snapshot gap while local-only capture avoids run-to-run network drift.',
    ])
    (OUT / f'{REVUP}_PUBLIC_TRACE_DIGEST_ACCEPTANCE_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
