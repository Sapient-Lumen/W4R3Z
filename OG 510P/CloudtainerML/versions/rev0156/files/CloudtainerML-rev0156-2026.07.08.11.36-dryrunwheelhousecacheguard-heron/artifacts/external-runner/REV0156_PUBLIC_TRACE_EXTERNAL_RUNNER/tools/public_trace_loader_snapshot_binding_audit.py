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


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def ordered(text: str, *needles: str) -> bool:
    last = -1
    for needle in needles:
        idx = text.find(needle)
        if idx < 0 or idx <= last:
            return False
        last = idx
    return True


def main() -> int:
    helper = read('experiments/public_trace_capture/hf_attention_trace_capture.py')
    run = read(f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh')
    one = read(f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh')
    smoke = read('tools/smoke_validate.py')
    selected_audit = read('tools/public_trace_selected_snapshot_contract_audit.py')
    packet_path = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json'
    packet: dict[str, Any] = json.loads(packet_path.read_text(encoding='utf-8')) if packet_path.exists() else {}
    det = packet.get('determinism_contract', {}) if isinstance(packet, dict) else {}

    checks: dict[str, bool] = {
        'capture_helper_has_explicit_loader_binding_flag': '--require-loader-snapshot-bind' in helper,
        'capture_helper_computes_loader_binding_verified': 'loader_snapshot_binding_verified' in helper and 'model_loader_uses_selected_digest_verified_local_snapshot_v1' in helper,
        'capture_helper_rejects_nonlocal_or_unbound_model_source': 'model_load_source_not_local_snapshot_directory' in helper and 'model_load_source_not_digest_verified_snapshot_path' in helper,
        'capture_helper_public_provenance_requires_loader_binding': 'and loader_snapshot_binding_verified' in helper and 'loader_snapshot_binding_not_verified' in helper,
        'capture_helper_serializes_loader_binding_receipt': 'loader_snapshot_binding_contract=np.asarray' in helper and 'model_load_source_resolved_path' in helper and 'verified_snapshot_path' in helper,
        'one_shot_passes_loader_binding_flag_to_capture': '--require-loader-snapshot-bind' in one,
        'one_shot_loads_capture_model_from_selected_snapshot_env': '--model "$CAPTURE_MODEL"' in one and 'CAPTURE_MODEL="${CAPTURE_MODEL:-$LOCAL_SNAPSHOT_DIR}"' in one,
        'one_shot_forbids_cap_model_drift_before_helper': ordered(one, 'CAPTURE_MODEL="${CAPTURE_MODEL:-$LOCAL_SNAPSHOT_DIR}"', 'CAPTURE_MODEL must equal selected LOCAL_SNAPSHOT_DIR', 'hf_attention_trace_capture.py'),
        'live_wrappers_run_loader_binding_audit': 'public_trace_loader_snapshot_binding_audit.py' in run and 'public_trace_loader_snapshot_binding_audit.py' in one,
        'selected_snapshot_audit_checks_loader_binding_or_smoke_does': 'require-loader-snapshot-bind' in selected_audit or 'loader_snapshot_binding' in smoke,
        'smoke_guards_loader_binding_contract': 'loader_snapshot_binding' in smoke and '--require-loader-snapshot-bind' in smoke,
        'run_packet_declares_loader_binding_contract': det.get('loader_snapshot_binding_contract') == 'model_loader_uses_selected_digest_verified_local_snapshot_v1',
        'run_packet_declares_loader_binding_required': det.get('loader_snapshot_binding_required') is True,
    }
    errors = [name for name, ok in checks.items() if not ok]
    status = 'pass' if not errors else 'fail'
    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(META.get('revision_number', str(REV).replace('rev', '') or 0)),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Guards the rev0133 refactor: the digest proof must apply to the exact --model path consumed by AutoTokenizer/AutoModelForCausalLM, not merely to some cache candidate found during preflight.',
        'risk_closed': 'hash_verified_cache_candidate_but_model_loader_consumes_different_path_or_model_id_resolution',
        'checks': checks,
        'errors': errors,
        'online_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'note': 'Transformers can load a local directory with local_files_only=True after files are downloaded/cached.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'note': 'snapshot_download returns/materializes local snapshot files at a revision.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables', 'note': 'HF_HUB_CACHE/HF_HOME affect cache resolution; explicit local paths avoid ambiguity.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'note': 'Safetensors metadata is structural; rev0133 requires the full byte digest to bind to the loader path.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_LOADER_SNAPSHOT_BINDING_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace loader-snapshot binding audit — {REVUP}',
        '',
        f'Status: `{status}`  ',
        'Promotion allowed: `false`',
        '',
        '## Checks',
        '',
    ]
    md.extend([f'- {name}: `{ok}`' for name, ok in checks.items()])
    md.extend(['', '## Interpretation', '', 'This closes a narrower gap than rev0132: the wrapper selects `LOCAL_SNAPSHOT_DIR`, and now the Python capture helper must independently refuse public promotion unless its own `--model` load source is that digest-verified local snapshot path.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_LOADER_SNAPSHOT_BINDING_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
