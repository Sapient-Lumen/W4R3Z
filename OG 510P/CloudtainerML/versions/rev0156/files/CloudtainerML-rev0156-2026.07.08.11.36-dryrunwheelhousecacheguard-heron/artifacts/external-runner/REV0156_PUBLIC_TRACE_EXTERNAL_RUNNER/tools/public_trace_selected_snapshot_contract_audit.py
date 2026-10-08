#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def src(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def order(src_text: str, first: str, second: str) -> bool:
    a = src_text.find(first)
    b = src_text.find(second)
    return a >= 0 and b >= 0 and a < b


def main() -> int:
    preflight = src('tools/public_trace_capture_start_preflight_report.py')
    run_rel = f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
    one_rel = f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh'
    run = src(run_rel)
    one = src(one_rel)
    smoke = src('tools/smoke_validate.py')

    checks: dict[str, bool] = {
        'preflight_selects_digest_verified_snapshot_path': 'choose_digest_verified_snapshot' in preflight and 'digest_verified_local_snapshot_path_v1' in preflight,
        'preflight_writes_runtime_capture_env': "CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh" in preflight and "CAPTURE_MODEL_SOURCE" in preflight,
        'preflight_records_selected_snapshot_in_json': "'selected_snapshot_path'" in preflight and "'selected_snapshot_digest_verified'" in preflight,
        'run_wrapper_sources_fresh_capture_env_after_preflight': order(run, 'public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only', 'source "$CAPTURE_ENV"'),
        'one_shot_sources_capture_env_after_preflight': (
            order(one, 'public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only', 'source \"$CAPTURE_ENV\"')
            or (
                'PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE:-0' in one
                and 'Direct one-shot execution path' in one
                and order(one.split('Direct one-shot execution path', 1)[1], 'public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only', 'source \"$CAPTURE_ENV\"')
            )
        ),
        'one_shot_requires_selected_local_snapshot': 'selected digest-verified LOCAL_SNAPSHOT_DIR was not exported by preflight' in one,
        'one_shot_prefers_capture_model_export': 'CAPTURE_MODEL="${CAPTURE_MODEL:-$LOCAL_SNAPSHOT_DIR}"' in one,
        'one_shot_still_forbids_download': '--allow-download' not in one and 'export ALLOW_DOWNLOAD=0' in one,
        'one_shot_passes_loader_binding_flag': '--require-loader-snapshot-bind' in one,
        'loader_binding_audit_wired_into_live_path': 'public_trace_loader_snapshot_binding_audit.py' in run and 'public_trace_loader_snapshot_binding_audit.py' in one,
        'smoke_guards_selected_snapshot_contract': 'selected_snapshot_contract' in smoke and 'CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh' in smoke and 'loader_snapshot_binding' in smoke,
    }
    errors = [name for name, ok in checks.items() if not ok]
    status = 'pass' if not errors else 'fail'
    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(META.get('revision_number', 0)),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Ensures the capture-start preflight binds the live loader to the same local TinyLlama snapshot path whose model.safetensors digest was verified, rather than merely proving that some candidate snapshot exists somewhere in cache.',
        'checks': checks,
        'errors': errors,
        'risk_closed': 'digest_verified_snapshot_exists_but_loader_uses_ambiguous_model_id_or_different_cache_entry',
        'online_basis': [
            {
                'url': 'https://huggingface.co/docs/transformers/en/installation',
                'note': 'Offline Transformers runs require cached/downloaded model files before loading.'
            },
            {
                'url': 'https://huggingface.co/docs/hub/en/local-cache',
                'note': 'Hugging Face Hub cache exposes snapshots under commit-addressed local paths.'
            },
            {
                'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download',
                'note': 'Downloaded files are cached and returned as local paths; capture should not modify or ambiguously resolve them.'
            },
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_SELECTED_SNAPSHOT_CONTRACT_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace selected-snapshot contract audit — {REVUP}',
        '',
        f'Status: `{status}`  ',
        'Promotion allowed: `false`',
        '',
        '## Checks',
        '',
    ]
    md.extend([f'- {name}: `{ok}`' for name, ok in checks.items()])
    md.extend(['', '## Interpretation', '', 'The preflight must not only prove that a digest-verified snapshot exists. It must select a concrete local snapshot path, make the capture wrapper load that exact path, and make the Python capture helper independently require that its own --model source is that digest-verified path. This prevents cache-resolution ambiguity from turning a hash check into evidence about the wrong bytes.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_SELECTED_SNAPSHOT_CONTRACT_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
