import pathlib

from gpustorming_contract_lib import build_gpustorming_toolchain

CONTRACT_PATTERN_GROUPS = {
    "late_research": (
        "check_evidence_*_contract.py",
        "check_citation_*_contract.py",
    ),
    "gpu": (
        "check_gpu_*_contract.py",
    ),
}


def _stable_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def contract_patterns(*groups: str) -> list[str]:
    unknown = [group for group in groups if group not in CONTRACT_PATTERN_GROUPS]
    if unknown:
        raise KeyError(f"unknown contract pattern group(s): {unknown}")
    patterns: list[str] = []
    for group in groups:
        patterns.extend(CONTRACT_PATTERN_GROUPS[group])
    return _stable_unique(patterns)


RESEARCH_AND_GPU_CONTRACT_PATTERNS = contract_patterns("late_research", "gpu")


BASE_TOOLS = [
    "check_discovery.py",
    "check_registry_ids.py",
    "check_revision_sync.py",
    "check_archive_index_order.py",
    "check_archive_index_table_shape.py",
    "check_prompt_pair_contract.py",
    "check_release_hygiene.py",
    "check_release_hygiene_relative_root.py",
    "check_release_identity_canaries.py",
    "check_internal_surface_references.py",
    "check_path_portability_contract.py",
    "check_path_alias_ledger_contract.py",
    "check_path_alias_witness_contract.py",
    "check_alias_retention_policy_contract.py",
    "check_alias_retention_witness_contract.py",
    "check_generated_surface_drift.py",
    "check_generated_surface_nonmutation_canary.py",
    "check_package_release_preflight_contract.py",
    "check_package_artifact_smoke_negative_canaries.py",
    "check_package_deterministic_zip_canaries.py",
    "check_package_sidecar_canaries.py",
    "check_external_metadata_contract.py",
    "check_package_identity_witness_contract.py",
    "check_release_validation_truth_gate_contract.py",
    "check_priority_zero_custody_timeline_gate_contract.py",
    "check_oq0266_isolated_batch_barrier_contract.py",
    "check_priority_zero_frozen_response_score_sheet_contract.py",
    "check_priority_zero_selfhash_split_bundle_contract.py",
    "check_priority_zero_preanswer_material_clamp_contract.py",
    "check_lint_idempotence_witness_contract.py",
    "check_schema_conformance_witness_contract.py",
    "check_schema_coverage_witness_contract.py",
    "check_basis_provenance_witness_contract.py",
    "check_archive_economy_witness_contract.py",
    "check_basis_provenance_currentness_contract.py",
    "check_json_schema_surface_contract.py",
    "check_frontier_backlog_contract.py",
    "check_frontier_backlog_current_tail_alignment.py",
    "check_link_integrity_policy_contract.py",
    "check_canary_protocol_contract.py",
    "check_ledger_audit_contract.py",
    "check_ledger_debt_guard.py",
    "check_ledger_coldstore_roundtrip_contract.py",
    "check_ledger_coldstore_mutation_canaries.py",
    "check_receipt_coldstore_roundtrip_contract.py",
    "check_receipt_coldstore_mutation_canaries.py",
    "check_archive_economy_audit_contract.py",
    "check_batch_spec_locality_contract.py",
    "check_hot_surface_compaction_contract.py",
    "check_hot_surface_source_roundtrip_contract.py",
    "check_open_question_tail_ordinal_contract.py",
    "check_latest_revision_cue_contract.py",
    "check_startup_current_head_contract.py",
    "check_hot_current_supports_contract.py",
    "check_landing_current_additions_alignment.py",
    "check_docs_readme_current_docs_head_alignment.py",
    "check_llm_runbook_current_cue_alignment.py",
    "check_bibliography_contract.py",
    "check_frozen_head_alignment.py",
    "check_surface_status_current_key_coherence.py",
    "check_currentness_residue_guard.py",
    "check_current_receipt_contract.py",
    "check_currentness_witness_contract.py",
    "check_agents_contract.py",
    "check_canary_runs_contract.py",
    "check_context_pack_budget.py",
    "check_currentness_cue_audit_contract.py",
    "check_package_identity_audit_contract.py",
    "check_basis_provenance_audit_contract.py",
    "check_lint_idempotence_audit_contract.py",
    "check_schema_coverage_audit_contract.py",
    "check_schema_conformance_audit_contract.py",
    "check_release_integrity_negative_canaries.py",
    "check_release_integrity_contract.py",
    "check_context_pack_fidelity.py",
    "check_context_pack_contract.py",
    "check_operator_command_surface_contract.py",
    "check_current_innovation_packet_contract.py",
    "check_frontier_ticket_contract.py",
    "check_replay_capsule_contract.py",
    "check_compact_surface_bundle_contract.py",
    "check_validation_index_contract.py",
    "check_validation_toolchain_manifest_contract.py",
    "check_context_pack_warning_contract.py",
    "check_context_pack_open_question_contract.py",
    "check_open_question_title_integrity.py",
    "check_open_question_successor_alignment.py",
    "check_reentry_surface_contract.py",
    "check_reentry_generation_closure_contract.py",
    "check_reentry_command_visibility_contract.py",
    "check_core_lexicon_contract.py",
    "check_move_registry_contract.py",
    "check_promotion_contract.py",
    "check_decay_watch_contract.py",
    "check_decay_watch_horizon_freshness.py",
    "check_recovery_kernel_contract.py",
    "check_basis_witness_contract.py",
    "check_basis_witness_exactness.py",
    "check_basis_anchor_precision_contract.py",
    "check_scope_witness_contract.py",
    "check_authorship_witness_contract.py",
    "check_status_lane_witness_contract.py",
    "check_revision_receipt_contract.py",
    "check_receipt_freshness_contract.py",
    "check_receipt_delta_coherence.py",
    "check_receipt_current_key_coherence.py",
    "check_global_truth_surface_contract.py",
    "check_continuity_tail_alignment.py",
    "check_template_placeholder_closure.py",
    "check_self_sufficiency_tail_alignment.py",
    "check_self_sufficiency_assay_contract.py",
    "check_priority_zero_smoke_slice_contract.py",
    "check_priority_zero_burden_gate_contract.py",
    "check_priority_zero_rotated_smoke_slice_contract.py",
    "check_priority_zero_role_blind_replay_contract.py",
    "check_priority_zero_external_replay_handoff_contract.py",
    "check_priority_zero_current_tail_external_bundle_contract.py",
    "check_priority_zero_response_intake_hollowguard_contract.py",
    "check_priority_zero_external_response_dryrun_gate_contract.py",
    "check_priority_zero_clean_response_admission_gate_contract.py",
    "check_frontier_backlog_resolved_residue_contract.py",
    "check_current_witness_receipt_slot.py",
    "check_release_hardening_witness_contract.py",
    "check_canary_evidence_witness_contract.py",
    "check_revision_receipt_refs.py",
    "check_revision_receipt_pointer_integrity.py",
    "check_counterfactual_shadow_contract.py",
    "check_public_state_packet_contract.py",
    "check_innovation_packet_contract.py",
    "check_core_method_batch_contract.py",
    "check_core_method_batch_negative_canaries.py",
    "check_method_doc_ratchet_batch_contract.py",
    "check_reasoning_firebreak_witness_contract.py",
    "check_vocabulary_witness_contract.py",
    "check_self_sufficiency_priority_contract.py",
    "check_template_law_contract.py",
    "check_runtime_triplet_contract.py",
    "check_sham_runtime_contract.py",
    "check_challenge_escrow_contract.py",
    "check_external_optimizer_contract.py",
    "check_replay_reconsolidation_contract.py",
    "check_procedural_compilation_contract.py",
    "check_rehearsal_packet_contract.py",
    "check_retrospective_write_contract.py",
    "check_credit_packet_contract.py",
    "check_alias_packet_contract.py",
    "check_gpustorming_scopenarrow_contract.py",
    "check_gpustorming_claimceiling_contract.py",
    "check_sink_namespace_contract.py",
    "check_consultation_packet_contract.py",
    "check_contradiction_packet_contract.py",
    "check_rival_set_contract.py",
    "check_operator_core_contract.py",
    "check_linearity_budget_contract.py",
    "check_chart_transition_contract.py",
    "check_triangle_defect_contract.py",
    "check_gauge_fixing_witness_contract.py",
    "check_scale_fixing_witness_contract.py",
    "check_hysteresis_witness_contract.py",
    "check_excitation_witness_contract.py",
    "check_backaction_witness_contract.py",
    "check_probe_order_witness_contract.py",
    "check_reset_witness_contract.py",
    "check_relapse_witness_contract.py",
    "check_cue_neighborhood_witness_contract.py",
    "check_directional_neighborhood_witness_contract.py",
    "check_mixed_direction_witness_contract.py",
    "check_interpolation_path_witness_contract.py",
    "check_feedback_policy_witness_contract.py",
    "check_dual_effect_witness_contract.py",
    "check_amortization_witness_contract.py",
    "check_applicability_witness_contract.py",
    "check_arbitration_witness_contract.py",
    "check_operational_head_contract.py",
    "check_status_lane_contract.py",
    "check_reentry_cue_contract.py",
    "check_followthrough_witness_contract.py",
    "check_assumption_witness_contract.py",
    "check_obligation_witness_contract.py",
    "check_obligation_packet_contract.py",
    "check_exception_witness_contract.py",
    "check_renewal_witness_contract.py",
    "check_renewal_scope_witness_contract.py",
    "check_declarative_witness_contract_batch.py",
    "check_foreign_pressure_witness_contract.py",
    "check_transfer_ledger_contract.py",
    "check_transfer_packet_contract.py",
    "check_import_hygiene_contract.py",
    "check_action_lane_contract.py",
    "check_action_lane_packet_contract.py",
    "check_gate_class_contract.py",
    "check_gate_class_packet_contract.py",
    "check_resolution_witness_contract.py",
    "check_replicate_bundle_witness_contract.py",
    "check_servo_packet_contract.py",
    "check_settle_packet_contract.py",
    "check_quarantine_contract.py",
    "check_trajectory_map_open_questions.py",
    "check_open_question_posture_contract.py",
    "check_open_question_registry_posture_completeness.py",
    "check_queue_health_contract.py",
    "check_self_sufficiency_ledger_contract.py",
    "check_witness_family_handle_contract.py",
    "check_mechanism_pressure_latest_alignment.py",
    "check_mechanism_pressure_register_contract.py",
]


def _glob_sorted_names(root: pathlib.Path, pattern: str) -> list[str]:
    return sorted(path.name for path in (root / "tools").glob(pattern))


def _insert_before(tools: list[str], before: str, additions: list[str]) -> list[str]:
    insert_at = tools.index(before)
    return [*tools[:insert_at], *additions, *tools[insert_at:]]


def _expand_glob_patterns(root: pathlib.Path, patterns: list[str]) -> list[str]:
    names: list[str] = []
    for pattern in patterns:
        names.extend(_glob_sorted_names(root, pattern))
    return _stable_unique(names)


def _insert_patterns_before(root: pathlib.Path, tools: list[str], before: str, patterns: list[str]) -> list[str]:
    return _insert_before(tools, before, _expand_glob_patterns(root, patterns))


def _assert_unique_toolchain(tools: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for tool in tools:
        if tool in seen and tool not in duplicates:
            duplicates.append(tool)
        seen.add(tool)
    if duplicates:
        raise ValueError(f"duplicate validation tools: {duplicates}")
    return tools


def _apply_pattern_insertions(root: pathlib.Path, tools: list[str], insertions: list[tuple[str, list[str]]]) -> list[str]:
    for before, patterns in insertions:
        tools = _insert_patterns_before(root, tools, before, patterns)
    return tools


def build_validation_toolchain(root: pathlib.Path) -> list[str]:
    tools = list(BASE_TOOLS)

    tools = _apply_pattern_insertions(root, tools, [
        ("check_replay_reconsolidation_contract.py", ["check_shadow_*_contract.py"]),
        ("check_foreign_pressure_witness_contract.py", [
            *RESEARCH_AND_GPU_CONTRACT_PATTERNS,
            "check_recovery_*_witness_contract.py",
            "check_stake*_witness_contract.py",
            "check_refresh*_witness_contract.py",
        ]),
    ])

    gpustorming_tools = build_gpustorming_toolchain(root)
    tools = [tool for tool in tools if not tool.startswith("check_gpustorming")]
    tools = _insert_before(
        tools,
        "check_sink_namespace_contract.py",
        [*gpustorming_tools, "check_gpustorming_late_search_sync.py", "check_gpustorming_path_sync.py", "check_gpustorming_problem_chain_sync.py"],
    )
    return _assert_unique_toolchain(tools)
