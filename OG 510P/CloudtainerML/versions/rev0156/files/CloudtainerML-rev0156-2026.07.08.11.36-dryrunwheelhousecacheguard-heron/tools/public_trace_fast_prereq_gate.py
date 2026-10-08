#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata as md
import importlib.util
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    REQUIRED_SNAPSHOT_FILES,
    inspect_snapshot,
    snapshot_candidate_paths,
)

META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
REVNO = int(REV.replace('rev', ''))
OUT = ROOT / 'artifacts' / 'audit'
RUN_MAN = ROOT / 'artifacts' / 'run-manifests'
OUT.mkdir(parents=True, exist_ok=True)
RUN_MAN.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL_ID = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
DEFAULT_REVISION = 'fe8a4ea1ffedaf415f4da2f062534de366a451e6'
CAPTURE_REQUIRED_MODULES = ['torch', 'transformers', 'huggingface_hub', 'safetensors']
SNAPSHOT_REQUIRED_MODULES = ['huggingface_hub']
OPTIONAL_DOWNLOAD_MODULES = ['accelerate', 'hf_xet']
ACTIVE_SCRIPTS = [
    'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh',
    'artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh',
    f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh',
    f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh',
    f'artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh',
    f'artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh',
]


def module_presence(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    out: dict[str, Any] = {
        'name': name,
        'present': bool(spec is not None),
        'origin': getattr(spec, 'origin', None) if spec else None,
        'checked_without_importing_module': True,
    }
    if spec is not None:
        try:
            out['version'] = md.version(name)
        except Exception as exc:
            out['version_error'] = repr(exc)
    return out


def scan_shell_dependencies() -> dict[str, Any]:
    errors: list[str] = []
    refs: list[dict[str, str]] = []
    py_re = re.compile(r"(?:python3|python|sys\.executable)\s+([A-Za-z0-9_./-]+\.py)")
    dyn_sh_re = re.compile(r"\$\{REVUP\}_([A-Z0-9_]+\.sh)")
    stale_re = re.compile(r"REV(\d{4})_[A-Z0-9_]+\.(?:sh|py)")
    for rel in ACTIVE_SCRIPTS:
        p = ROOT / rel
        if not p.exists():
            errors.append('missing_active_shell_script:' + rel)
            continue
        src = p.read_text(encoding='utf-8', errors='replace')
        for m in py_re.finditer(src):
            target = m.group(1).strip().strip('"').strip("'")
            if target.startswith(('tools/', 'experiments/')) or target == 'VERIFY_HANDOFF.py':
                refs.append({'script': rel, 'target': target, 'kind': 'python'})
                if not (ROOT / target).is_file():
                    errors.append(f'{rel} references missing python file: {target}')
        for m in dyn_sh_re.finditer(src):
            target = f'artifacts/capture-kit/{REVUP}_{m.group(1)}'
            refs.append({'script': rel, 'target': target, 'kind': 'dynamic_shell'})
            if not (ROOT / target).is_file():
                errors.append(f'{rel} references missing dynamic shell file: {target}')
        for m in stale_re.finditer(src):
            found = 'REV' + m.group(1)
            if found != REVUP:
                errors.append(f'{rel} contains stale executable reference: {m.group(0)}')
    return {'active_scripts': ACTIVE_SCRIPTS, 'referenced_targets': refs, 'errors': errors}


def stable_aliases_ok() -> list[str]:
    errors: list[str] = []
    run = ROOT / 'artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh'
    prep = ROOT / 'artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh'
    if run.exists() and f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in run.read_text(encoding='utf-8', errors='replace'):
        errors.append('RUN_CURRENT_PUBLIC_TRACE_not_targeting_current_revision')
    if prep.exists() and f'{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh' not in prep.read_text(encoding='utf-8', errors='replace'):
        errors.append('PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT_not_targeting_current_revision')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Single-process cheap prerequisite gate for the public trace lane.')
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--download', action='store_true')
    mode.add_argument('--local-only', action='store_true')
    ap.add_argument('--phase', choices=['capture', 'snapshot'], default='capture', help='capture requires runtime packages; snapshot only requires materialization prerequisites and snapshot integrity')
    ap.add_argument('--strict', action='store_true')
    ap.add_argument('--require-weight-hash', action='store_true', default=os.environ.get('REQUIRE_WEIGHT_HASH') == '1', help='require the pinned model.safetensors SHA-256 for any local snapshot considered ready')
    ap.add_argument('--capture-local-only', action='store_true', default=False, help='force capture-phase preflight to require a local digest-verified snapshot even if ALLOW_DOWNLOAD=1 is set')
    args = ap.parse_args()
    download_requested = args.download or (not args.local_only and os.environ.get('ALLOW_DOWNLOAD') == '1')
    phase = args.phase
    capture_local_only = bool(args.capture_local_only or phase == 'capture')
    download_mode = bool(download_requested and not capture_local_only)
    require_weight_hash = bool(args.require_weight_hash)
    model_id = os.environ.get('MODEL_ID', DEFAULT_MODEL_ID)
    model_revision = os.environ.get('MODEL_REVISION', DEFAULT_REVISION)

    all_modules = sorted(set(CAPTURE_REQUIRED_MODULES + SNAPSHOT_REQUIRED_MODULES + OPTIONAL_DOWNLOAD_MODULES))
    modules = {name: module_presence(name) for name in all_modules}
    hard_blockers: list[str] = []
    capture_blockers: list[str] = []
    warnings: list[str] = []
    shell = scan_shell_dependencies()
    hard_blockers.extend(shell['errors'])
    hard_blockers.extend(stable_aliases_ok())
    if sys.version_info < (3, 10):
        hard_blockers.append('python_version_below_3_10')

    for name in CAPTURE_REQUIRED_MODULES:
        if not modules[name]['present']:
            capture_blockers.append(f'{name}_not_importable')
    # Local-only snapshot verification is import-light: it can inspect a mounted
    # Hugging Face snapshot using tools/hf_snapshot_integrity.py without requiring
    # huggingface_hub. Only download/materialization mode needs the Hub client.
    if download_requested and capture_local_only:
        warnings.append('download_requested_ignored_because_capture_phase_is_local_files_only')
    if download_mode:
        for name in SNAPSHOT_REQUIRED_MODULES:
            if not modules[name]['present']:
                hard_blockers.append(f'{name}_not_importable_for_snapshot_materialization')
        usage = shutil.disk_usage(ROOT)
        free_gb = usage.free / (1024 ** 3)
        if free_gb < 6:
            hard_blockers.append('download_allowed_but_less_than_6gb_free_space')
        for name in OPTIONAL_DOWNLOAD_MODULES:
            if not modules[name]['present']:
                warnings.append(f'{name}_not_present_download_may_be_slower_or_less_robust')
    if phase == 'capture':
        hard_blockers.extend(capture_blockers)
    elif capture_blockers:
        warnings.append('capture_runtime_blockers_deferred_until_after_snapshot_materialization')

    snapshot_checks = [inspect_snapshot(p, model_id=model_id, revision=model_revision, include_hashes=require_weight_hash) for p in snapshot_candidate_paths(model_id, model_revision)]
    complete_snapshot = any(c.get('complete_required_snapshot') for c in snapshot_checks)
    hash_verified_snapshot = any(bool(c.get('complete_required_snapshot')) and bool(c.get('model_safetensors', {}).get('sha256_matches_expected')) for c in snapshot_checks)
    if not complete_snapshot and not download_mode:
        hard_blockers.append('complete_tinyllama_snapshot_not_available')
    if require_weight_hash and complete_snapshot and not hash_verified_snapshot:
        hard_blockers.append('complete_snapshot_without_pinned_model_safetensors_sha256')
    if require_weight_hash and not complete_snapshot and not download_mode:
        hard_blockers.append('digest_verified_tinyllama_snapshot_not_available')
    if not complete_snapshot and download_mode:
        warnings.append('complete_tinyllama_snapshot_not_currently_local_download_mode_can_materialize_later')
    warnings.append('cuda_not_checked_by_fast_gate_full_readiness_gate_handles_named_hardware_timing')

    status = 'pass' if not hard_blockers else 'blocked_here_fast_prereq'
    audit = {
        'revision': REV,
        'revision_number': REVNO,
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Import-light front gate with explicit capture-vs-snapshot phases. Snapshot/local-only verification can inspect mounted model material without huggingface_hub or transformers; snapshot/download mode requires huggingface_hub; capture phase is always local-files-only and fails fast on runtime dependencies plus missing digest-verified model material.',
        'phase': phase,
        'download_requested': download_requested,
        'download_mode': download_mode,
        'capture_local_only': capture_local_only,
        'require_weight_hash': require_weight_hash,
        'expected_model_safetensors_sha256': EXPECTED_MODEL_SAFETENSORS_SHA256,
        'model_id': model_id,
        'model_revision': model_revision,
        'python': {'version': platform.python_version(), 'executable': sys.executable, 'platform': platform.platform()},
        'modules_checked_without_importing_torch_or_transformers': True,
        'modules': modules,
        'shell_dependency_closure': shell,
        'required_snapshot_files': REQUIRED_SNAPSHOT_FILES,
        'snapshot_candidates': snapshot_checks,
        'complete_snapshot_available': complete_snapshot,
        'hash_verified_snapshot_available': hash_verified_snapshot,
        'hard_blockers': sorted(set(hard_blockers)),
        'capture_runtime_blockers_deferred_until_after_snapshot_materialization': sorted(set(capture_blockers)) if phase == 'snapshot' else [],
        'blockers': sorted(set(hard_blockers)),
        'warnings': sorted(set(warnings)),
        'next_if_blocked': [
            'repair hard_blockers before running public_trace_readiness_gate.py',
            'use ALLOW_DOWNLOAD=1 PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh to materialize a missing snapshot if package/network policy allows; then run capture with ALLOW_DOWNLOAD=0',
            'install the capture runtime requirements before expecting RUN_CURRENT_PUBLIC_TRACE.sh to produce a real trace',
            'populate LOCAL_SNAPSHOT_DIR or the Hugging Face cache with the exact model revision and integrity-valid files',
        ],
        'source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'note': 'Transformers offline mode requires downloaded/cached files ahead of time and supports HF_HUB_OFFLINE/local_files_only for offline loads.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download', 'note': 'snapshot_download supports revision, local_files_only, allow_patterns, dry_run, and incomplete snapshot errors.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/main/model.safetensors', 'note': 'The selected TinyLlama model.safetensors is a 2.2 GB safetensors file with a published SHA256.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_FAST_PREREQ_GATE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace fast prerequisite gate — {REVUP}',
        '',
        f"Status: `{status}`  ",
        f"Phase: `{phase}`  ",
        'Promotion allowed: `false`',
        '',
        '## Hard blockers',
        '',
    ]
    md.extend([f'- `{b}`' for b in audit['hard_blockers']] if audit['hard_blockers'] else ['- none'])
    md.extend(['', '## Deferred capture-runtime blockers', ''])
    md.extend([f'- `{b}`' for b in audit['capture_runtime_blockers_deferred_until_after_snapshot_materialization']] if audit['capture_runtime_blockers_deferred_until_after_snapshot_materialization'] else ['- none'])
    md.extend(['', '## Warnings', ''])
    md.extend([f'- `{w}`' for w in audit['warnings']] if audit['warnings'] else ['- none'])
    md.extend(['', '## Interpretation', '', 'This is the front-door anti-waste gate. In `--phase snapshot --local-only`, mounted snapshot verification is allowed without `huggingface_hub`; in `--phase snapshot --download`, the Hub client is a hard blocker. Missing capture-only packages such as `transformers` are recorded but deferred so the model-source blocker can be repaired first. In `--phase capture`, capture is local-files-only: download permission is ignored and a digest-verified local snapshot must already be available.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_FAST_PREREQ_GATE.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    (RUN_MAN / f'{REVUP}_PUBLIC_TRACE_FAST_PREREQ_GATE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'phase': phase, 'blockers': audit['blockers'], 'deferred_capture_runtime_blockers': audit['capture_runtime_blockers_deferred_until_after_snapshot_materialization'], 'warnings': audit['warnings']}, indent=2))
    return 0 if (not hard_blockers or not args.strict) else 1


if __name__ == '__main__':
    raise SystemExit(main())
