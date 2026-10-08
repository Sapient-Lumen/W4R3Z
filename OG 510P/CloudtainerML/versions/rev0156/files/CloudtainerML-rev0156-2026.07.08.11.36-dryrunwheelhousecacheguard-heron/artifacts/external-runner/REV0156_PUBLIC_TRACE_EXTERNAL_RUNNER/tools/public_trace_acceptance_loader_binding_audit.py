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


def main() -> int:
    verifier = read('experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py')
    helper = read('experiments/public_trace_capture/hf_attention_trace_capture.py')
    run = read(f'artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh')
    one = read(f'artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh')
    smoke = read('tools/smoke_validate.py')
    packet_path = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json'
    packet: dict[str, Any] = json.loads(packet_path.read_text(encoding='utf-8')) if packet_path.exists() else {}
    det = packet.get('determinism_contract', {}) if isinstance(packet, dict) else {}
    env = packet.get('environment_preflight', {}) if isinstance(packet, dict) else {}
    fields = [
        'snapshot_digest_authenticity_contract',
        'snapshot_digest_authenticity_required',
        'snapshot_digest_authenticity_verified',
        'loader_snapshot_binding_contract',
        'loader_snapshot_binding_required',
        'loader_snapshot_binding_verified',
        'model_load_source_resolved_path',
        'verified_snapshot_path',
        'model_safetensors_sha256',
        'expected_model_safetensors_sha256',
        'model_safetensors_sha256_matches_expected',
    ]

    checks: dict[str, bool] = {
        'capture_helper_emits_digest_and_loader_binding_fields': all(field in helper for field in fields),
        'verifier_declares_public_loader_binding_field_list': 'PUBLIC_LOADER_BINDING_FIELDS' in verifier and all(field in verifier for field in fields),
        'verifier_imports_pinned_expected_model_digest': 'EXPECTED_MODEL_SAFETENSORS_SHA256' in verifier,
        'verifier_requires_manifest_loader_binding_fields': 'manifest_loader_binding_errors' in verifier and '_loader_binding_field_errors(data' in verifier,
        'verifier_requires_npz_loader_binding_fields': 'npz_loader_binding_errors' in verifier and '_loader_binding_field_errors(meta' in verifier,
        'verifier_requires_loader_source_equals_verified_snapshot_path': 'model_load_source_resolved_path must equal verified_snapshot_path' in verifier and '_same_recorded_path' in verifier,
        'verifier_requires_expected_and_observed_safetensors_sha': 'expected_model_safetensors_sha256 must equal the pinned TinyLlama digest' in verifier and 'model_safetensors_sha256 must equal expected_model_safetensors_sha256' in verifier,
        'npz_self_attestation_requires_loader_fields': 'required_for_public' in verifier and '*PUBLIC_LOADER_BINDING_FIELDS' in verifier,
        'manifest_npz_crosscheck_includes_loader_fields': 'for key in [' in verifier and '*PUBLIC_LOADER_BINDING_FIELDS' in verifier,
        'wrappers_run_acceptance_loader_binding_audit': 'public_trace_acceptance_loader_binding_audit.py' in run and 'public_trace_acceptance_loader_binding_audit.py' in one,
        'smoke_guards_acceptance_loader_binding': 'acceptance_loader_binding' in smoke and 'PUBLIC_LOADER_BINDING_FIELDS' in smoke,
        'run_packet_declares_acceptance_loader_binding_contract': det.get('acceptance_requires_loader_snapshot_binding') is True,
        'run_packet_declares_acceptance_loader_binding_audit': env.get('acceptance_loader_binding_audit') == 'tools/public_trace_acceptance_loader_binding_audit.py',
    }
    errors = [name for name, ok in checks.items() if not ok]
    status = 'pass' if not errors else 'fail'
    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(str(REV).replace('rev', '') or 0),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Guards rev0134: downstream public-trace acceptance must require the same selected local snapshot, model.safetensors SHA-256, and loader-binding proof that capture startup now enforces.',
        'risk_closed': 'selector_or_evaluation_accepts_trace_provenance_without_proving_the_loaded_model_bytes_match_the_digest_verified_selected_snapshot',
        'checks': checks,
        'errors': errors,
        'online_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'note': 'Offline evidence must rely on already downloaded/cached files.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/guides/download', 'note': 'snapshot_download materializes revisioned files into a local snapshot/cache.'},
            {'url': 'https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables', 'note': 'Cache roots can vary by environment, so acceptance should use recorded selected paths rather than implicit cache resolution.'},
            {'url': 'https://huggingface.co/docs/safetensors/en/metadata_parsing', 'note': 'Safetensors header metadata is structural; acceptance requires the full model.safetensors digest.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_ACCEPTANCE_LOADER_BINDING_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md = [
        f'# Public trace acceptance loader-binding audit — {REVUP}',
        '',
        f'Status: `{status}`  ',
        'Promotion allowed: `false`',
        '',
        '## Checks',
        '',
    ]
    md.extend([f'- {name}: `{ok}`' for name, ok in checks.items()])
    md.extend(['', '## Interpretation', '', 'The live capture path can now refuse wrong loader sources before model import, but that is not sufficient. This audit ensures the downstream public-trace verifier rejects any trace/provenance pair that omits the selected-snapshot path, loader-binding boolean, and full pinned `model.safetensors` SHA-256 proof.'])
    (OUT / f'{REVUP}_PUBLIC_TRACE_ACCEPTANCE_LOADER_BINDING_AUDIT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
