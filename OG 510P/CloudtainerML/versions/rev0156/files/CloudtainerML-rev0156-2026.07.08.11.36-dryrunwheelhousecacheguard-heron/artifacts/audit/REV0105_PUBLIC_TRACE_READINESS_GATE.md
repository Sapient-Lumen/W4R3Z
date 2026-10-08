# Public trace readiness gate — REV0105

Status: `blocked_here`  
Promotion allowed: `false`

This is the current single stop/go command for the public TinyLlama trace lane. rev0105 also requires the captured NPZ plus provenance JSON to form a complete acceptance bundle before evaluation, while named-hardware timing remains a later promotion lane.

## Readiness bits

- `revision_metadata_coherent` = `true`
- `dependency_lock_ok` = `false`
- `source_lock_pass` = `true`
- `trace_packet_pass` = `true`
- `env_trace_ready` = `false`
- `llama_surface_compatible` = `false`
- `backend_identity_ok` = `true`
- `cache_implementation_contract_ok` = `true`
- `prompt_manifest_contract_ok` = `true`
- `device_dtype_timing_contract_ok` = `true`
- `hardware_timing_boundary_ok` = `true`
- `acceptance_bundle_contract_ok` = `true`
- `local_snapshot_intake_ok` = `true`
- `capture_model_identity_ok` = `true`
- `snapshot_dry_run_ok_or_not_needed` = `true`
- `snapshot_complete` = `false`
- `capture_source_checks_ok` = `true`
- `capture_readiness_audit_ready` = `false`
- `capture_surface_refactor_ok` = `true`
- `active_surface_ok` = `true`
- `current_entrypoints_ok` = `true`
- `open_questions_surface_ok` = `true`

## Blockers

- `transformers_not_importable`
- `no_complete_local_hf_snapshot_and_download_not_allowed`
- `transformers_not_importable_runtime_surface_unchecked`
- `actual_public_pretrained_prompt_manifest_trace_missing`
- `transformers_runtime_and_tinyllama_snapshot_still_required_for_real_capture`
- `runtime_dependencies_missing_here`
- `actual_public_pretrained_trace_missing`
- `named_hardware_sparse_vs_dense_timing_missing`
- `accepted_public_trace_required_before_performance_promotion`
- `real_public_trace_npz_and_provenance_pair_missing`
- `accepted_trace_bundle_required_before_named_hardware_timing`
- `complete_tinyllama_snapshot_not_available`
- `transformers_dependency_absent`
- `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`
- `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`
- `step_failed:dependency_lock`

## Next

`repair blockers above, then rerun python tools/public_trace_readiness_gate.py --strict`
