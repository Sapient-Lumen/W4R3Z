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

RUN = ROOT / 'artifacts' / 'capture-kit' / f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh'
ONE = ROOT / 'artifacts' / 'capture-kit' / f'{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh'
PREP = ROOT / 'artifacts' / 'capture-kit' / f'{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh'
FAST = ROOT / 'tools' / 'public_trace_fast_prereq_gate.py'
ENV = ROOT / 'tools' / 'public_trace_env_preflight.py'
READY = ROOT / 'tools' / 'public_trace_readiness_gate.py'
SMOKE = ROOT / 'tools' / 'smoke_validate.py'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    files = {
        'run_wrapper': RUN,
        'one_shot_wrapper': ONE,
        'prepare_wrapper': PREP,
        'fast_gate': FAST,
        'env_preflight': ENV,
        'readiness_gate': READY,
        'smoke_validate': SMOKE,
    }
    for label, path in files.items():
        if not path.exists():
            errors.append(f'missing_{label}:{path.relative_to(ROOT).as_posix()}')

    run_src = read(RUN)
    one_src = read(ONE)
    prep_src = read(PREP)
    fast_src = read(FAST)
    env_src = read(ENV)
    ready_src = read(READY)
    smoke_src = read(SMOKE)

    checks = {
        'fast_gate_accepts_require_weight_hash': "--require-weight-hash" in fast_src,
        'fast_gate_hashes_snapshot_candidates_when_required': "include_hashes=require_weight_hash" in fast_src,
        'fast_gate_emits_hash_verified_snapshot_available': "hash_verified_snapshot_available" in fast_src,
        'env_preflight_accepts_require_weight_hash': "--require-weight-hash" in env_src,
        'env_preflight_emits_digest_verified_snapshot': "found_digest_verified_integrity_snapshot" in env_src,
        'env_preflight_blocks_missing_digest_in_local_only': "no_digest_verified_local_hf_snapshot_and_download_not_allowed" in env_src,
        'run_wrapper_hash_gates_local_capture': "--phase capture --local-only --strict --require-weight-hash" in run_src,
        'run_wrapper_forbids_download_capture_gate': "--phase capture --download --strict" not in run_src,
        'one_shot_env_preflight_hash_required': "public_trace_env_preflight.py --strict trace --require-weight-hash --capture-local-only" in one_src,
        'prepare_hashes_weights_by_default': 'export HASH_WEIGHTS="${HASH_WEIGHTS:-1}"' in prep_src,
        'prepare_materializer_passes_hash_arg': 'hf_snapshot_materializer.py --download --strict "${HASH_ARG[@]}"' in prep_src and 'hf_snapshot_materializer.py --local-only --strict "${HASH_ARG[@]}"' in prep_src,
        'readiness_materializer_uses_include_hashes_by_default': "['--include-hashes'] if env.get('HASH_WEIGHTS', '1') == '1'" in ready_src,
        'readiness_snapshot_timeout_not_global_8s': 'SNAPSHOT_GATE_STEP_TIMEOUT' in ready_src and 'def step_timeout_seconds' in ready_src,
        'smoke_guards_hash_preflight_contract': 'hash_preflight_contract' in smoke_src,
    }
    for name, ok in checks.items():
        if not ok:
            errors.append(name)

    if 'TRACE_GATE_STEP_TIMEOUT' in ready_src and 'SNAPSHOT_GATE_STEP_TIMEOUT' not in ready_src:
        errors.append('readiness_gate_still_uses_global_short_timeout_for_snapshot')
    if 'HASH_WEIGHTS:-0' in prep_src:
        errors.append('prepare_wrapper_defaults_to_structural_only_hash_weights_0')
    if 'model_safetensors_sha256_not_checked' in fast_src and '--require-weight-hash' not in run_src:
        errors.append('structural_snapshot_warning_not_escalated_before_capture')

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
        'summary': 'Ensures the live public-trace path cannot treat a merely structural TinyLlama snapshot as capture-ready: the fast gate, env preflight, prepare wrapper, one-shot wrapper, readiness materializer, and smoke all carry the pinned model.safetensors SHA-256 requirement. Also ensures the snapshot materializer is not governed by the short generic probe timeout and that download permission cannot mask a missing local snapshot during capture.',
        'checks': checks,
        'errors': errors,
        'warnings': warnings,
        'risk_closed': 'wrong_weight_or_unhashed_snapshot_advancing_to_model_capture_ALLOW_DOWNLOAD_masking_missing_local_snapshot_and_2gb_download_hash_step_killed_by_8s_probe_timeout',
        'source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Offline Transformers use requires files downloaded and cached ahead of time.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'fact': 'Hub downloads are cached by revision; snapshot_download is the repository materialization path.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'fact': 'Safetensors headers can be parsed cheaply, but header structure is not the same as full byte digest authenticity.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables', 'fact': 'HF_HUB_OFFLINE disables network calls, so local snapshot material must already be complete and authentic.'},
        ],
        'decision': 'hash_preflight_contract_ok' if not errors else 'repair_hash_preflight_contract_before_live_capture',
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_HASH_PREFLIGHT_CONTRACT_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace hash preflight contract audit — {REVUP}',
        '',
        f"Status: `{status}`  ",
        'Promotion allowed: `false`',
        '',
        '## Errors',
        '',
    ]
    md.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    md.extend(['', '## Interpretation', '', 'A valid safetensors header is useful structural evidence, but the live public trace must not advance to capture unless the pinned TinyLlama weight digest is checked on the same local snapshot that will be loaded. Rev0131 also ensures capture remains local-files-only even if ALLOW_DOWNLOAD=1 is set, and separates long snapshot/download/hash work from the short generic probe timeout.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_HASH_PREFLIGHT_CONTRACT_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
