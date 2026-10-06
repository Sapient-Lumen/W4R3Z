import pathlib

from gpustorming_contract_lib import build_gpustorming_toolchain

BASE_TOOLS = [
    "check_discovery.py",
    "check_registry_ids.py",
    "check_revision_sync.py",
    "check_archive_index_order.py",
    "check_prompt_pair_contract.py",
    "check_release_hygiene.py",
    "check_bibliography_contract.py",
    "check_frozen_head_alignment.py",
    "check_agents_contract.py",
    "gen_context_pack.py",
    "gen_innovation_packet.py",
    "gen_frontier_ticket.py",
    "gen_replay_capsule.py",
    "gen_compact_surface_bundle.py",
    "gen_validation_index.py",
    "gen_reentry_surface_conformance.py",
    "check_context_pack_budget.py",
    "check_context_pack_fidelity.py",
    "check_context_pack_contract.py",
    "check_current_innovation_packet_contract.py",
    "check_frontier_ticket_contract.py",
    "check_replay_capsule_contract.py",
    "check_compact_surface_bundle_contract.py",
    "check_validation_index_contract.py",
    "check_context_pack_warning_contract.py",
    "check_context_pack_open_question_contract.py",
    "check_reentry_surface_contract.py",
    "check_core_lexicon_contract.py",
    "check_move_registry_contract.py",
    "check_promotion_contract.py",
    "check_decay_watch_contract.py",
    "check_recovery_kernel_contract.py",
    "check_basis_witness_contract.py",
    "check_basis_witness_exactness.py",
    "check_basis_anchor_precision_contract.py",
    "check_scope_witness_contract.py",
    "check_authorship_witness_contract.py",
    "check_status_lane_witness_contract.py",
    "check_revision_receipt_contract.py",
    "check_receipt_freshness_contract.py",
    "check_revision_receipt_refs.py",
    "check_revision_receipt_pointer_integrity.py",
    "check_counterfactual_shadow_contract.py",
    "check_regime_probe_contract.py",
    "check_public_hidden_state_contract.py",
    "check_public_state_packet_contract.py",
    "check_belief_state_contract.py",
    "check_innovation_packet_contract.py",
    "check_rate_distortion_contract.py",
    "check_revision_gain_contract.py",
    "check_witness_set_contract.py",
    "check_hold_packet_contract.py",
    "check_sentinel_panel_contract.py",
    "check_identification_packet_contract.py",
    "check_timescale_lane_contract.py",
    "check_phase_boundary_contract.py",
    "check_gauge_discipline_contract.py",
    "check_loop_closure_contract.py",
    "check_continuation_margin_contract.py",
    "check_control_authority_contract.py",
    "check_balanced_archive_contract.py",
    "check_memory_vs_reentry_contract.py",
    "check_predictive_state_contract.py",
    "check_future_equivalence_contract.py",
    "check_intervention_equivalence_contract.py",
    "check_homing_packet_contract.py",
    "check_probe_economics_contract.py",
    "check_stopping_packet_contract.py",
    "check_continuation_monitor_contract.py",
    "check_observer_actuator_split_contract.py",
    "check_negative_control_handle_contract.py",
    "check_blind_packet_contract.py",
    "check_execution_witness_contract.py",
    "check_assistant_echo_filter_contract.py",
    "check_reasoning_firebreak_contract.py",
    "check_reasoning_firebreak_witness_contract.py",
    "check_vocabulary_witness_contract.py",
    "check_dependence_adjusted_witness_contract.py",
    "check_rewrite_witness_contract.py",
    "check_conformance_witness_contract.py",
    "check_necessity_witness_contract.py",
    "check_sufficiency_witness_contract.py",
    "check_triangulation_witness_contract.py",
    "check_basin_fingerprint_contract.py",
    "check_identifiability_budget_contract.py",
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
    "check_selector_witness_contract.py",
    "check_selector_provenance_witness_contract.py",
    "check_selector_freshness_witness_contract.py",
    "check_selector_enforcement_witness_contract.py",
    "check_enforcement_regime_witness_contract.py",
    "check_response_witness_contract.py",
    "check_repair_scope_witness_contract.py",
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
    return names


def _insert_patterns_before(root: pathlib.Path, tools: list[str], before: str, patterns: list[str]) -> list[str]:
    return _insert_before(tools, before, _expand_glob_patterns(root, patterns))


def _apply_pattern_insertions(root: pathlib.Path, tools: list[str], insertions: list[tuple[str, list[str]]]) -> list[str]:
    for before, patterns in insertions:
        tools = _insert_patterns_before(root, tools, before, patterns)
    return tools


def build_validation_toolchain(root: pathlib.Path) -> list[str]:
    tools = list(BASE_TOOLS)

    tools = _apply_pattern_insertions(root, tools, [
        ("check_replay_reconsolidation_contract.py", ["check_shadow_*_contract.py"]),
        ("check_foreign_pressure_witness_contract.py", [
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
    return tools
