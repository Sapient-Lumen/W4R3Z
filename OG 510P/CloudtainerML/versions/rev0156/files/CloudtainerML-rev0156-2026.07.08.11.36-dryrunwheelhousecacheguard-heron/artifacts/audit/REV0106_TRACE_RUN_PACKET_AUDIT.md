# Trace run packet audit — REV0106

Status: `fail`  
Promotion allowed: `false`

## Target

- model: `None`
- revision: `None`
- license: `None`
- command: `None`

## Errors

- `missing_tinyllama_run_packet`
- `target_model_id_not_tinyllama_chat_v1`
- `model_revision_not_full_immutable_hash`
- `license_not_reviewed_apache_2_0`
- `weights_source_not_commit_tree_url`
- `do_sample_not_forced_false`
- `num_beams_not_one`
- `num_return_sequences_not_one`
- `use_cache_not_required`
- `exact_new_token_contract_missing`
- `decode_steps_not_positive`
- `attention_implementation_not_eager`
- `cache_implementation_not_dynamic`
- `cache_implementation_contract_missing`
- `cache_implementation_not_explicit_generate_argument`
- `cache_config_present_must_be_false`
- `prompt_manifest_contract_missing`
- `token_provenance_contract_not_v2`
- `tokenizer_call_add_special_tokens_not_true`
- `tokenizer_call_padding_not_false`
- `tokenizer_call_truncation_not_false`
- `tokenizer_call_return_attention_mask_not_true`
- `tokenizer_call_return_tensors_not_pt`
- `chat_template_applied_must_be_false`
- `download_default_not_closed`
- `commands_do_not_use_current_tinyllama_wrapper`
- `reviewed_download_command_not_explicit`
- `missing_expected_output_REV0106_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz`
- `missing_expected_output_REV0106_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json`
- `missing_expected_output_REV0106_PUBLIC_TRACE_GATE_REAL_MODEL.json`
- `backend_identity_probe_missing_from_packet`
- `cache_implementation_audit_missing_from_packet`
- `prompt_manifest_audit_missing_from_packet`
- `current_entrypoint_consistency_missing_from_packet`
- `too_few_online_sources_recorded`

## Warnings

- `max_rows_low_for_public_trace_probe`

## Interpretation

This audit converts the next step from a generic instruction into a concrete immutable public-model trace packet with backend/cache identity and prompt-manifest replayability. It is still non-promotional until the trace is captured and accepted by the gate.
