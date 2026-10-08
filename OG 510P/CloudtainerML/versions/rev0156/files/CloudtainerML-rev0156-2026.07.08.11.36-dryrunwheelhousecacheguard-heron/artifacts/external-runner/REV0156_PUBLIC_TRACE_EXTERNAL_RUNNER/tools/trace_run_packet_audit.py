#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0094'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

HEX40 = re.compile(r'^[0-9a-fA-F]{40}$')


def is_full_hash(s: str) -> bool:
    return bool(HEX40.match(str(s or '').strip()))


def main() -> int:
    packet_path = ROOT / 'artifacts' / 'run-manifests' / f'{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json'
    errors: list[str] = []
    warnings: list[str] = []
    if not packet_path.exists():
        errors.append('missing_tinyllama_run_packet')
        packet: dict[str, Any] = {}
    else:
        packet = json.loads(packet_path.read_text(encoding='utf-8'))

    # Rev0137: the packet is not current if its top-level identity is stale.
    # Previous packets could pass all semantic checks while still carrying an
    # older revision_number/package_name, which is enough to confuse handoff and
    # operator logs.
    if packet.get('revision') != REV:
        errors.append('run_packet_revision_not_current')
    if packet.get('revision_number') is not None and int(packet.get('revision_number')) != int(REV.replace('rev','')):
        errors.append('run_packet_revision_number_not_current')
    if packet.get('package_name') and packet.get('package_name') != META.get('package_name'):
        errors.append('run_packet_package_name_not_current')
    if packet.get('archive_name') and packet.get('archive_name') != META.get('archive_name'):
        errors.append('run_packet_archive_name_not_current')

    target = packet.get('target_model', {})
    det = packet.get('determinism_contract', {})
    dl = packet.get('download_policy', {})
    cmd_download = str(packet.get('command_reviewed_download', ''))
    cmd_offline = str(packet.get('command_local_cache_only', ''))
    expected_outputs = packet.get('expected_outputs', [])
    env_pre = packet.get('environment_preflight', {})
    sources = packet.get('sources', [])

    if target.get('model_id') != 'TinyLlama/TinyLlama-1.1B-Chat-v1.0':
        errors.append('target_model_id_not_tinyllama_chat_v1')
    if not is_full_hash(target.get('model_revision', '')):
        errors.append('model_revision_not_full_immutable_hash')
    if target.get('tokenizer_revision') != target.get('model_revision'):
        errors.append('tokenizer_revision_not_pinned_to_model_revision')
    if str(target.get('license', '')).lower() != 'apache-2.0':
        errors.append('license_not_reviewed_apache_2_0')
    if '/tree/' not in str(target.get('weights_source', '')):
        errors.append('weights_source_not_commit_tree_url')
    if 'main' in str(target.get('weights_source', '')).lower():
        errors.append('weights_source_uses_mutable_main')

    if det.get('do_sample') is not False:
        errors.append('do_sample_not_forced_false')
    if det.get('num_beams') != 1:
        errors.append('num_beams_not_one')
    if det.get('num_return_sequences') != 1:
        errors.append('num_return_sequences_not_one')
    if det.get('use_cache') is not True:
        errors.append('use_cache_not_required')
    if det.get('min_new_tokens_equals_max_new_tokens') is not True:
        errors.append('exact_new_token_contract_missing')
    if int(det.get('decode_steps', 0)) <= 0:
        errors.append('decode_steps_not_positive')
    if det.get('attention_implementation') != 'eager':
        errors.append('attention_implementation_not_eager')
    if det.get('cache_implementation') != 'dynamic':
        errors.append('cache_implementation_not_dynamic')
    if det.get('cache_implementation_contract') != 'hf_generate_dynamic_cache_v1':
        errors.append('cache_implementation_contract_missing')
    if det.get('cache_implementation_source') != 'explicit_generate_argument':
        errors.append('cache_implementation_not_explicit_generate_argument')
    if det.get('cache_config_present') is not False:
        errors.append('cache_config_present_must_be_false')
    if det.get('prompt_manifest_contract') != 'prompt_text_tokenizer_call_manifest_v1':
        errors.append('prompt_manifest_contract_missing')
    if det.get('token_provenance_contract') != 'prompt_input_ids_attention_mask_digest_v2':
        errors.append('token_provenance_contract_not_v2')
    if det.get('tokenizer_call_add_special_tokens') is not True:
        errors.append('tokenizer_call_add_special_tokens_not_true')
    if det.get('tokenizer_call_padding') is not False:
        errors.append('tokenizer_call_padding_not_false')
    if det.get('tokenizer_call_truncation') is not False:
        errors.append('tokenizer_call_truncation_not_false')
    if det.get('tokenizer_call_return_attention_mask') is not True:
        errors.append('tokenizer_call_return_attention_mask_not_true')
    if det.get('tokenizer_call_return_tensors') != 'pt':
        errors.append('tokenizer_call_return_tensors_not_pt')
    if det.get('chat_template_applied') is not False:
        errors.append('chat_template_applied_must_be_false')
    if det.get('snapshot_local_only_gate_import_light') is not True:
        errors.append('snapshot_local_only_gate_import_light_marker_missing')
    if det.get('snapshot_download_gate_requires_huggingface_hub') is not True:
        errors.append('snapshot_download_gate_requires_huggingface_hub_marker_missing')
    if det.get('snapshot_local_only_gate_audit_required') is not True:
        errors.append('snapshot_local_only_gate_audit_required_marker_missing')
    if det.get('weight_hash_preflight_required') is not True:
        errors.append('weight_hash_preflight_required_marker_missing')
    if det.get('snapshot_materializer_hashes_weights_by_default') is not True:
        errors.append('snapshot_materializer_hashes_weights_by_default_marker_missing')
    if det.get('snapshot_step_timeout_contract') != 'snapshot_materialization_not_limited_by_short_probe_timeout_v1':
        errors.append('snapshot_step_timeout_contract_missing')
    if det.get('selected_snapshot_path_contract') != 'digest_verified_local_snapshot_path_v1':
        errors.append('selected_snapshot_path_contract_missing')
    if det.get('capture_model_must_equal_selected_LOCAL_SNAPSHOT_DIR') is not True:
        errors.append('capture_model_must_equal_selected_LOCAL_SNAPSHOT_DIR_marker_missing')
    if det.get('loader_snapshot_binding_contract') != 'model_loader_uses_selected_digest_verified_local_snapshot_v1':
        errors.append('loader_snapshot_binding_contract_missing')
    if det.get('loader_snapshot_binding_required') is not True:
        errors.append('loader_snapshot_binding_required_marker_missing')
    if det.get('capture_helper_requires_loader_snapshot_bind') is not True:
        errors.append('capture_helper_requires_loader_snapshot_bind_marker_missing')
    if det.get('acceptance_requires_loader_snapshot_binding') is not True:
        errors.append('acceptance_requires_loader_snapshot_binding_marker_missing')
    if det.get('acceptance_loader_binding_contract') != 'public_trace_acceptance_requires_loader_digest_binding_v1':
        errors.append('acceptance_loader_binding_contract_missing')
    if det.get('acceptance_requires_model_load_source_resolved_path_equals_verified_snapshot_path') is not True:
        errors.append('acceptance_loader_path_equality_marker_missing')
    if det.get('downstream_identity_receipt_contract') != 'public_trace_downstream_identity_receipt_v1':
        errors.append('downstream_identity_receipt_contract_missing')
    if det.get('selector_entry_chain_contract') != 'public_trace_selector_entry_chain_v1':
        errors.append('selector_entry_chain_contract_missing')
    if det.get('selector_entry_chain_binding_required') is not True:
        errors.append('selector_entry_chain_binding_required_marker_missing')
    if det.get('selector_entry_chain_binds_evaluation_receipt_identity_and_actual_bundle') is not True:
        errors.append('selector_entry_chain_binds_subjects_marker_missing')
    if det.get('selector_receipt_replay_tamper_harness_contract') != 'selector_receipt_replay_tamper_enforcement_v1':
        errors.append('selector_receipt_replay_tamper_harness_contract_missing')
    if det.get('selector_receipt_replay_enforcement_harness_required') is not True:
        errors.append('selector_receipt_replay_enforcement_harness_required_marker_missing')
    if det.get('selector_receipt_replay_good_path_and_tamper_failures_required') is not True:
        errors.append('selector_receipt_replay_good_path_and_tamper_failures_required_marker_missing')
    if det.get('evaluation_receipt_requires_trace_identity') is not True:
        errors.append('evaluation_receipt_trace_identity_marker_missing')
    if det.get('selector_entry_requires_trace_identity') is not True:
        errors.append('selector_entry_trace_identity_marker_missing')
    if det.get('handoff_manifest_requires_trace_identity_chain') is not True:
        errors.append('handoff_manifest_trace_identity_marker_missing')
    required_acceptance_digest = {'snapshot_digest_authenticity_contract', 'snapshot_digest_authenticity_required', 'snapshot_digest_authenticity_verified', 'model_safetensors_sha256', 'expected_model_safetensors_sha256', 'model_safetensors_sha256_matches_expected'}
    if not required_acceptance_digest.issubset(set(det.get('acceptance_requires_snapshot_digest_fields', []))):
        errors.append('acceptance_snapshot_digest_fields_incomplete')
    required_acceptance_loader = {'loader_snapshot_binding_contract', 'loader_snapshot_binding_required', 'loader_snapshot_binding_verified', 'model_load_source_resolved_path', 'verified_snapshot_path'}
    if not required_acceptance_loader.issubset(set(det.get('acceptance_requires_loader_binding_fields', []))):
        errors.append('acceptance_loader_binding_fields_incomplete')
    if int(det.get('max_rows', 0)) < 64:
        warnings.append('max_rows_low_for_public_trace_probe')

    if dl.get('default_ALLOW_DOWNLOAD') != '0':
        errors.append('download_default_not_closed')
    if f'{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh' not in cmd_download + cmd_offline:
        errors.append('commands_do_not_use_current_tinyllama_wrapper')
    if 'ALLOW_DOWNLOAD=1' not in cmd_download:
        errors.append('reviewed_download_command_not_explicit')
    for suffix in [
        f'{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz',
        f'{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json',
        f'{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json',
    ]:
        if not any(str(x).endswith(suffix) for x in expected_outputs):
            errors.append('missing_expected_output_' + suffix)
    if env_pre.get('backend_identity_probe') != 'tools/public_trace_backend_identity_probe.py':
        errors.append('backend_identity_probe_missing_from_packet')
    if env_pre.get('cache_implementation_audit') != 'tools/public_trace_cache_implementation_audit.py':
        errors.append('cache_implementation_audit_missing_from_packet')
    if env_pre.get('prompt_manifest_audit') != 'tools/public_trace_prompt_manifest_audit.py':
        errors.append('prompt_manifest_audit_missing_from_packet')
    if env_pre.get('current_entrypoint_consistency_audit') != 'tools/current_entrypoint_consistency_audit.py':
        errors.append('current_entrypoint_consistency_missing_from_packet')
    if env_pre.get('hash_preflight_contract_audit') != 'tools/public_trace_hash_preflight_contract_audit.py':
        errors.append('hash_preflight_contract_audit_missing_from_packet')
    if env_pre.get('loader_snapshot_binding_audit') != 'tools/public_trace_loader_snapshot_binding_audit.py':
        errors.append('loader_snapshot_binding_audit_missing_from_packet')
    if env_pre.get('acceptance_loader_binding_audit') != 'tools/public_trace_acceptance_loader_binding_audit.py':
        errors.append('acceptance_loader_binding_audit_missing_from_packet')
    if env_pre.get('downstream_identity_receipt_audit') != 'tools/public_trace_downstream_identity_receipt_audit.py':
        errors.append('downstream_identity_receipt_audit_missing_from_packet')
    if env_pre.get('selector_receipt_replay_enforcement_harness') != 'tools/public_trace_selector_receipt_replay_enforcement_harness.py':
        errors.append('selector_receipt_replay_enforcement_harness_missing_from_packet')
    if len(sources) < 5:
        errors.append('too_few_online_sources_recorded')

    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': 'pass' if not errors else 'fail',
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Validates the concrete TinyLlama public trace run packet, including current metadata identity and the executable selector-receipt replay tamper harness, so the next turn has a specific immutable target instead of a generic model handoff.',
        'packet': packet_path.relative_to(ROOT).as_posix(),
        'errors': errors,
        'warnings': warnings,
        'decision': 'run_packet_is_current_next_action' if not errors else 'repair_packet_before_trace_attempt',
    }
    json_path = OUT / f'{REVUP}_TRACE_RUN_PACKET_AUDIT.json'
    md_path = OUT / f'{REVUP}_TRACE_RUN_PACKET_AUDIT.md'
    json_path.write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    md_path.write_text('# Trace run packet audit — ' + REVUP + '\n\n'
        + f"Status: `{audit['status']}`  \nPromotion allowed: `false`\n\n"
        + '## Target\n\n'
        + f"- model: `{target.get('model_id')}`\n"
        + f"- revision: `{target.get('model_revision')}`\n"
        + f"- license: `{target.get('license')}`\n"
        + f"- command: `{packet.get('command_reviewed_download')}`\n\n"
        + '## Errors\n\n' + ('\n'.join(f'- `{e}`' for e in errors) if errors else '- none') + '\n\n'
        + '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        + '## Interpretation\n\nThis audit converts the next step from a generic instruction into a concrete immutable public-model trace packet with backend/cache identity and prompt-manifest replayability. It is still non-promotional until the trace is captured and accepted by the gate.\n', encoding='utf-8')
    print(json.dumps({'status': audit['status'], 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
