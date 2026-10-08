# Validation log — REV0108

Package: `CloudtainerML-rev0108-2026.07.06.15.49-relocationreceiptmetafix-owl`

## Audit commands

### `python tools/revision_metadata_coherence_audit.py`

Return code: `0`

```text
{
  "status": "pass",
  "errors": [],
  "warnings": []
}


```

### `python tools/public_trace_evaluation_verdict_audit.py`

Return code: `0`

```text
{
  "status": "pass_with_blockers",
  "verdict": "blocked_no_trace_bundle",
  "receipt": "artifacts/probe-results/REV0108_PUBLIC_TRACE_EVALUATION_RECEIPT.json",
  "errors": [],
  "blockers": [
    "real_public_trace_npz_missing",
    "real_public_trace_provenance_missing",
    "capture_must_complete_before_selector_evaluation",
    "evaluation_receipt_emitted_but_not_accepted"
  ]
}


```

### `python tools/public_trace_evaluation_receipt_audit.py`

Return code: `0`

```text
{
  "status": "pass_with_blockers",
  "case_results": {
    "accepted_receipt_has_subject_set": true,
    "accepted_receipt_opens_selector_but_not_promotion": true,
    "hash_mismatch_closes_selector_entry": true,
    "missing_trace_receipt_blocks_selector_entry": true
  },
  "errors": []
}


```

### `python tools/public_trace_receipt_relocation_audit.py`

Return code: `0`

```text
{
  "status": "pass_with_blockers",
  "case_results": {
    "subject_set_stable_after_rename": true,
    "paths_differ_but_hashes_match": true,
    "selector_allows_original_matching_files": true,
    "selector_allows_relocated_matching_files": true,
    "selector_blocks_tampered_relocated_trace": true,
    "selector_blocks_v1_or_missing_subject_set": true
  },
  "errors": []
}


```

### `python tools/public_trace_selector_entry_gate.py`

Return code: `0`

```text
{
  "status": "pass_with_blockers",
  "verdict": "selector_entry_blocked_until_accepted_receipt",
  "errors": [],
  "blockers": [
    "evaluation_receipt_not_accepted_for_selector_entry"
  ]
}


```

### `python tools/current_entrypoint_consistency_audit.py`

Return code: `1`

```text
{
  "status": "fail",
  "errors": [
    "stable_prepare_alias_not_current_revision",
    "top_doc_missing_current_run_alias:START_HERE_SLIM.md",
    "top_doc_missing_current_run_alias:PRIORITY-LIST.md",
    "top_doc_missing_current_run_alias:NEXT-TURN-PROMPT.md"
  ],
  "debt": [
    "74 historical capture scripts retained as provenance only"
  ]
}


```

### `python tools/active_surface_trim_audit.py`

Return code: `1`

```text
{
  "status": "fail",
  "errors": [
    "stable_prepare_alias_not_current",
    "top_doc_missing_current_trace_entrypoint:START_HERE_SLIM.md",
    "top_doc_missing_current_trace_entrypoint:PRIORITY-LIST.md",
    "top_doc_missing_current_trace_entrypoint:NEXT-TURN-PROMPT.md"
  ],
  "debt": [
    "74 historical revision-specific capture scripts retained as provenance; top docs now use stable aliases"
  ]
}


```

### `python tools/open_questions_surface_audit.py`

Return code: `1`

```text
{
  "status": "fail",
  "errors": [
    "open_questions_shim_not_pointing_to_canonical",
    "canonical_questions_missing_dry_run_gate_question"
  ],
  "debt": []
}


```

## Final validation

### `python tools/smoke_validate.py`

Return code: `0`

```text
{
  "status": "pass",
  "revision": "rev0108",
  "revision_kind": "public_trace_relocation_safe_receipt_and_metadata_counter_fix",
  "errors": [],
  "warnings": []
}


```

### `sha256sum -c CHECKSUMS.sha256`

Return code: `0`

```text
eriments/trace_packet_twostage_cert_reuse/README.md: OK
experiments/trace_packet_twostage_cert_reuse/trace_packet_twostage_cert_reuse.cpp: OK
experiments/trace_packet_twostage_cert_reuse/trace_packet_twostage_cert_reuse.py: OK
experiments/trace_packet_value_layout_envelope/README.md: OK
experiments/trace_packet_value_layout_envelope/trace_packet_value_layout_envelope.cpp: OK
experiments/trace_packet_value_layout_envelope/trace_packet_value_layout_envelope.py: OK
experiments/tree_rollout_allocation/README.md: OK
experiments/tree_rollout_allocation/trace_prefix_probe.py: OK
experiments/tree_sparse_ffn_autoprune/tree_sparse_ffn_autoprune.cpp: OK
experiments/value_norm_guarded_attention/value_norm_guarded_attention.py: OK
experiments/value_norm_sidecar_cpu_path/run_value_norm_sidecar_cpu_path.py: OK
experiments/value_norm_sidecar_cpu_path/value_norm_sidecar_cpu_path.cpp: OK
experiments/value_outlier_eviction/README.md: OK
experiments/value_outlier_eviction/value_outlier_probe.py: OK
experiments/vericache_guard/README.md: OK
experiments/vericache_guard/vericache_guard_probe.cpp: OK
experiments/via_sd_tiered_verifier/via_sd_tiered_verifier.cpp: OK
experiments/xlstm_state_correction/xlstm_state_correction.cpp: OK
tools/active_surface_trim_audit.py: OK
tools/attention_end_to_end_cpu_audit.py: OK
tools/attention_frontier_trace_audit.py: OK
tools/attention_workload_audit.py: OK
tools/boundary_refined_selector_audit.py: OK
tools/cache_probe_report.py: OK
tools/capture_model_identity_audit.py: OK
tools/capture_surface_refactor_audit.py: OK
tools/certified_support_reuse_audit.py: OK
tools/charter_focus_audit.py: OK
tools/cube_audit.py: OK
tools/cube_bureaucracy_refactor_audit.py: OK
tools/current_entrypoint_consistency_audit.py: OK
tools/current_scientific_run_audit.py: OK
tools/deployable_selector_layout_audit.py: OK
tools/evidence_integrity_audit.py: OK
tools/exactness_guard_report.py: OK
tools/fused_dispatch_gate_audit.py: OK
tools/fused_streaming_schedule_audit.py: OK
tools/hard_gate_compilation_report.py: OK
tools/hf_snapshot_dry_run_audit.py: OK
tools/hf_snapshot_materializer.py: OK
tools/lane_decision_matrix_audit.py: OK
tools/learned_trace_block_bounds_audit.py: OK
tools/mass_certified_attention_audit.py: OK
tools/mechanism_promotion_report.py: OK
tools/memory_safety_report.py: OK
tools/mission_trace_fidelity_audit.py: OK
tools/native_family_report.py: OK
tools/native_hardening_report.py: OK
tools/native_phase_readiness_report.py: OK
tools/native_probe_audit.py: OK
tools/native_probe_index.py: OK
tools/novelty_salience_audit.py: OK
tools/observable_block_index_audit.py: OK
tools/open_questions_surface_audit.py: OK
tools/operator_route_report.py: OK
tools/p0_integrity_report.py: OK
tools/performance_core_report.py: OK
tools/performance_hardening_report.py: OK
tools/performance_promotion_report.py: OK
tools/platform_cost_calibration_audit.py: OK
tools/post_transform_trace_contract_audit.py: OK
tools/primary_metric_patcher.py: OK
tools/probe_dashboard.py: OK
tools/probe_graph_specs.py: OK
tools/probe_metric_index.py: OK
tools/probe_suite_dashboard.py: OK
tools/probe_taxonomy_audit.py: OK
tools/public_trace_absolute_position_audit.py: OK
tools/public_trace_acceptance_bundle_audit.py: OK
tools/public_trace_acceptance_preflight_audit.py: OK
tools/public_trace_active_keymask_audit.py: OK
tools/public_trace_backend_identity_probe.py: OK
tools/public_trace_cache_implementation_audit.py: OK
tools/public_trace_capture_kit_audit.py: OK
tools/public_trace_capture_readiness_audit.py: OK
tools/public_trace_claim_contract_audit.py: OK
tools/public_trace_decode_phase_audit.py: OK
tools/public_trace_dependency_lock_audit.py: OK
tools/public_trace_device_dtype_timing_audit.py: OK
tools/public_trace_e2e_ingest_contract_audit.py: OK
tools/public_trace_env_preflight.py: OK
tools/public_trace_evaluation_receipt_audit.py: OK
tools/public_trace_evaluation_verdict_audit.py: OK
tools/public_trace_gate_audit.py: OK
tools/public_trace_generation_determinism_audit.py: OK
tools/public_trace_generation_token_audit.py: OK
tools/public_trace_hardware_timing_boundary_audit.py: OK
tools/public_trace_kv_group_audit.py: OK
tools/public_trace_mask_fidelity_audit.py: OK
tools/public_trace_probability_semantics_audit.py: OK
tools/public_trace_prompt_manifest_audit.py: OK
tools/public_trace_readiness_gate.py: OK
tools/public_trace_receipt_relocation_audit.py: OK
tools/public_trace_rotary_position_audit.py: OK
tools/public_trace_selector_entry_gate.py: OK
tools/public_trace_snapshot_intake_audit.py: OK
tools/public_trace_token_provenance_audit.py: OK
tools/real_model_trace_adapter_audit.py: OK
tools/revision_lineage_static_audit.py: OK
tools/revision_metadata_coherence_audit.py: OK
tools/router_cost_frontier_audit.py: OK
tools/router_shift_stress_audit.py: OK
tools/routing_family_report.py: OK
tools/row_adaptive_router_audit.py: OK
tools/score_path_block_pruning_audit.py: OK
tools/screen_regret_report.py: OK
tools/slim_retention_audit.py: OK
tools/smoke_validate.py: OK
tools/source_lock_audit.py: OK
tools/sparse_index_compiler_report.py: OK
tools/sparse_program_report.py: OK
tools/spectral_operator_report.py: OK
tools/stage_prune_cert_policy_audit.py: OK
tools/support_reuse_amortization_audit.py: OK
tools/surprise_audit.py: OK
tools/tail_contract_patcher.py: OK
tools/tail_risk_report.py: OK
tools/trace_capture_roundtrip_audit.py: OK
tools/trace_lane_execution_audit.py: OK
tools/trace_packet_dispatch_replay_audit.py: OK
tools/trace_packet_native_replay_audit.py: OK
tools/trace_packet_qk_native_replay_audit.py: OK
tools/trace_packet_speed_envelope_audit.py: OK
tools/trace_packet_value_layout_envelope_audit.py: OK
tools/trace_run_packet_audit.py: OK
tools/traceability_report.py: OK
tools/trained_escalation_report.py: OK
tools/trained_mechanism_guard_report.py: OK
tools/transformers_llama_surface_probe.py: OK
tools/twostage_cert_reuse_audit.py: OK
tools/value_norm_sidecar_claim_audit.py: OK
tools/value_norm_stress_and_timing_audit.py: OK


```
