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
    run = read(f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh')
    one = read(f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh')
    prep = read(f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh')
    env = read('tools/public_trace_env_preflight.py')
    fast = read('tools/public_trace_fast_prereq_gate.py')
    report = read('tools/public_trace_capture_start_preflight_report.py')
    smoke = read('tools/smoke_validate.py')

    required = {
        'run_wrapper': bool(run),
        'one_shot_wrapper': bool(one),
        'prepare_wrapper': bool(prep),
        'env_preflight': bool(env),
        'fast_gate': bool(fast),
        'capture_start_report': bool(report),
    }
    for label, ok in required.items():
        if not ok:
            errors.append('missing_' + label)

    if 'export ALLOW_DOWNLOAD=0' not in run:
        errors.append('run_wrapper_does_not_force_ALLOW_DOWNLOAD_0_for_capture')
    if 'export CAPTURE_LOCAL_ONLY="${CAPTURE_LOCAL_ONLY:-1}"' not in run:
        errors.append('run_wrapper_does_not_assert_CAPTURE_LOCAL_ONLY')
    if 'public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only' not in run:
        errors.append('run_wrapper_missing_strict_capture_start_report')
    if '--phase capture --download' in run:
        errors.append('run_wrapper_still_allows_download_mode_capture_gate')
    if 'public_trace_readiness_gate.py --download --strict' in run:
        errors.append('run_wrapper_still_allows_download_mode_readiness_gate')
    if 'public_trace_env_preflight.py --strict trace --require-weight-hash --capture-local-only' not in one:
        errors.append('one_shot_env_preflight_not_capture_local_only')
    if 'public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only' not in one:
        errors.append('one_shot_missing_capture_start_report')
    if '--allow-download' in one:
        errors.append('one_shot_capture_helper_still_allows_download')
    if '--capture-local-only' not in env or 'allow_download_for_snapshot_preflight' not in env:
        errors.append('env_preflight_missing_capture_local_only_semantics')
    if '--capture-local-only' not in fast or 'download_requested_ignored_because_capture_phase_is_local_files_only' not in fast:
        errors.append('fast_gate_missing_capture_local_only_semantics')
    if 'capture_local_only_contract' not in smoke:
        errors.append('smoke_does_not_guard_capture_local_only_contract')

    # Download belongs in the preparation lane, not in the evidence capture lane.
    if 'public_trace_fast_prereq_gate.py --phase snapshot --download --strict' not in prep or 'hf_snapshot_materializer.py --download --strict' not in prep:
        errors.append('prepare_wrapper_no_longer_has_download_materialization_lane')

    status = 'pass' if not errors else 'fail'
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Guards the rev0131 refactor: downloads are allowed only during snapshot preparation. Evidence capture is local-files-only and must see a digest-verified local TinyLlama snapshot before the model loader starts.',
        'errors': errors,
        'warnings': warnings,
        'decision': 'capture_local_only_contract_guarded' if not errors else 'repair_capture_local_only_contract_before_live_run',
        'risk_closed': 'ALLOW_DOWNLOAD_1_preflight_forgiving_missing_snapshot_even_though_capture_helper_would_load_local_files_only',
        'source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline mode requires cached/downloaded model files before use.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'snapshot_download is the repository materialization path and should be separated from local-only capture.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_CAPTURE_LOCAL_ONLY_CONTRACT_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [f'# Public trace capture local-only contract audit — {REVUP}', '', f"Status: `{status}`  ", 'Promotion allowed: `false`', '', '## Errors', '']
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Interpretation', '', 'This audit prevents a wasteful capture path: `ALLOW_DOWNLOAD=1` may be useful while preparing a snapshot, but the public evidence capture wrapper intentionally does not pass `--allow-download` to the Hugging Face loader. Therefore capture preflight must require the digest-verified local snapshot.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_CAPTURE_LOCAL_ONLY_CONTRACT_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
