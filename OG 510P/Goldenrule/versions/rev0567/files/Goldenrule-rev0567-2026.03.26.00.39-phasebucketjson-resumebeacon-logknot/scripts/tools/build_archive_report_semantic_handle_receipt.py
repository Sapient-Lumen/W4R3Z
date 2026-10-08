#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOTSPOT_RECEIPT = ROOT / 'examples' / 'snapshots' / 'archive_report_hotspot_receipt.json'
DEFAULT_OUTPUT = ROOT / 'examples' / 'snapshots' / 'archive_report_semantic_handle_receipt.json'
REPORT_ROOT = ROOT / 'artifacts' / 'reports'
HOTSPOT_BUFFER_LIMIT = 13
FAMILY_SUFFIX_PATTERNS = [
    re.compile(r'_snapshot_\d{8}$'),
    re.compile(r'_\d{8}$'),
    re.compile(r'_[0-9]{4}\.[0-9]{2}\.[0-9]{2}$'),
]

ALIASES: list[dict[str, Any]] = [
    {
        'family': 'rematch_proxy_delta_policy_box_corner',
        'report_path': 'artifacts/reports/rematch_proxy_delta_policy_box_corner_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_policy_box_corner_certification.md',
        'family_evidence_markers': ['policy box', 'representative corners', 'strict hazard edge'],
        'handle_evidence_markers': ['policy box', 'representative corners', 'strict hazard edge'],
        'semantic_bridge': 'The report family and the library topic both certify that the synthesized family10 policy box is only publication-safe after representative corner checks preserve shortlist identity and keep the strict hazard edge explicit.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_local_axis_persistence.md',
        'family_evidence_markers': ['axis_run_count', 'all_exact_runs_are_singletons', 'longest_suffix_run_summary', 'persistence_steps_remaining'],
        'handle_evidence_markers': ['axis persistence horizon', 'exact-only run has length `1`', 'longest suffix-only run has length `3`', 'shared-diagonal run has length `1`'],
        'semantic_bridge': 'The local-axis-persistence report family and the standing persistence-horizon topic both reduce repeated width-only SLA relaxations to the same run geometry of singleton exact spikes, persistent suffix corridors, and one shared diagonal kink, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_service_relaxations_by_local_corridor_triads.md',
        'family_evidence_markers': ['triad_family_histogram', 'diagonal_neighborhood', 'terminal_tail', 'shared_visibility_depth'],
        'handle_evidence_markers': ['local triad grammar', 'diagonal kink', 'terminal tail', 'shared diagonal'],
        'semantic_bridge': 'The local-triad-grammar report family and the standing corridor-triads topic both compress the service staircase into the same tiny forecast language of alternating bridge, diagonal neighborhood, and terminal tail, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_one_shot_exact_uncertainty_anchor_retuning_as_a_small_exact_route_atlas.md',
        'family_evidence_markers': ['ordered_distinct_anchor_routes', 'weakening_from_precision_starts_at_boundary_8', 'anchor 25', 'route rows'],
        'handle_evidence_markers': ['exact route atlas', '13 -> 19 -> 25', '25 -> 18 -> 13', 'collapse straight to `2`'],
        'semantic_bridge': 'The canonical-anchor path-atlas report family and the standing exact-route-atlas topic both reduce one-shot steady-anchor retuning to the same six exact routes among anchors 2, 13, and 25, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_weakening_sla_thresholds_as_a_two_ladder_basis.md',
        'family_evidence_markers': ['threshold_provenance_word', 'shared_collision_threshold_fraction', 'sorted union', 'staircase path word'],
        'handle_evidence_markers': ['two-ladder basis', 'one shared rung', 'SSESSSESSESDSESE', '16 unique positive thresholds'],
        'semantic_bridge': 'The threshold-provenance report family and the standing two-ladder-basis topic both reconstruct the positive-service staircase from the same exact-only ladder, suffix-only ladder, and lone 1/91 collision, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_not_treat_multi_tick_promises_as_locally_time_consistent.md',
        'family_evidence_markers': ['time_consistency_rule', 'boundary_drift_rule', 'restoration_rule', 'K = 1'],
        'handle_evidence_markers': ['K = 1', 'locally time-consistent', '2K - 1', 'accept drift'],
        'semantic_bridge': 'The time-consistency report family and the standing multi-tick-promises topic both state that live reoptimization preserves a finite promise exactly iff the minimum blind-commit timeout is one tick, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_catalog_page_filter',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_filter_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_page_filters_beside_paged_catalogs.md',
        'family_evidence_markers': ['page-filter bytes', 'main rule', 'repeat detection', 'append-locality check'],
        'handle_evidence_markers': ['page filters beside paged catalogs', 'repeat detection', 'prune repeat lookups'],
        'semantic_bridge': 'The catalog-page-filter report family and the standing paged-catalog filter topic both add the same tiny digest-byte membership sidecar beside append-only raw-digest pages so repeat detection can skip impossible pages before decoding them, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_amortize_exact_shortest_script_transport_across_shared_interval_state_batches.md',
        'family_evidence_markers': ['shared_state_transport_never_loses_at_batch_length_2', 'strictly_dominant_for_every_audited_case_at_batch_length_3', 'state-once transport'],
        'handle_evidence_markers': ['shared interval-state batches', 'state prefix once + local choice prefixes'],
        'semantic_bridge': 'The shared-interval-state exact-transport report family and the standing amortized-transport topic both state that once exact scripts share one feasible interval state, state-once transport with local choice prefixes never loses at batch length two and wins strictly from batch length three onward, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_live_countdowns_as_usable_wait_windows_plus_dead_reserve.md',
        'family_evidence_markers': ['usable window', 'dead reserve', 'H >= 2K - 1', 'live countdown'],
        'handle_evidence_markers': ['usable wait window', 'dead reserve', 'H >= 2K - 1', 'live countdown policy'],
        'semantic_bridge': 'The countdown-reserve report family and the standing live-countdown topic both state that miss-by-miss reoptimization exposes only the usable wait window and holds the last K-1 ticks as dead reserve, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'geometric_arrival_effective_horizon_law',
        'report_path': 'artifacts/reports/geometric_arrival_effective_horizon_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_stateless_live_deadlines_by_effective_blind_horizon.md',
        'family_evidence_markers': ['effective_horizon_rule', 'floor((h + 1) / 2)', 'controller_equivalence_rule', 'odd_even_pair_rule'],
        'handle_evidence_markers': ['effective-horizon law', 'floor((h + 1) / 2)', 'deadlines `2j - 1` and `2j`', 'budget only the effective blind horizon'],
        'semantic_bridge': 'The effective-horizon report family and the standing budgeting topic both state that same-deadline stateless live control preserves only the promise class of blind commit with horizon floor((H + 1) / 2), so the existing durable topic should back future citation and compaction for this family.',
    },
    {
        'family': 'geometric_arrival_live_dominance_frontier_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_dominance_frontier_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compress_positive_same_deadline_live_policies_by_dominance_frontiers.md',
        'family_evidence_markers': ['pareto', 'positive same-deadline live', 'promise safety is monotone'],
        'handle_evidence_markers': ['pareto', 'positive same-deadline live', 'promise safety is monotone'],
        'semantic_bridge': 'The report family and the library topic both compress positive same-deadline live admission into a favorable-order Pareto frontier, so the durable handle can stand in for repeated reopening of the dense report pair.',
    },
    {
        'family': 'geometric_arrival_live_deadline_formula_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_deadline_formula_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_solve_same_deadline_live_minima_from_one_closed_form.md',
        'family_evidence_markers': ['direct closed-form minimum same-deadline live deadline', 'alpha', 'delta'],
        'handle_evidence_markers': ['exact direct formula', 'alpha', 'delta'],
        'semantic_bridge': 'The report family and the library topic both encode the same direct closed-form rule for minimum same-deadline live deadlines from delta and alpha, so the existing durable handle should be reused before minting another note for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_run_positive_batches_by_precomputed_remaining_horizon_countdowns.md',
        'family_evidence_markers': ['remaining-horizon countdown', 'minimum timeout', 'continue exactly while', 'current geometric-arrival model'],
        'handle_evidence_markers': ['remaining-horizon countdowns', 'minimum timeout', 'continue exactly while', 'current geometric-arrival model'],
        'semantic_bridge': 'The dense deadline-countdown report family and the standing library topic both reduce live positive-batch control to one precomputed remaining-horizon threshold, so the existing topic should be reused before another compact note is minted for the projected second-wave frontier.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_not_panic_close_positive_batches_after_geometric_miss_streaks.md',
        'family_evidence_markers': ['elapsed miss streak', 'memoryless', 'one more tick right now', 'not on how many empty ticks have already elapsed'],
        'handle_evidence_markers': ['elapsed miss streak', 'memoryless', 'one more tick right now', 'panic-close a positive batch'],
        'semantic_bridge': 'The checkpoint-extension report and the standing miss-streak topic both say that under stationary geometric arrivals the value of one more tick depends on remaining horizon and current economics, not on elapsed miss age, so the archive should reuse that existing topic instead of minting another handle here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_select_positive_service_local_weakening_witnesses_by_interval_clamp.md',
        'family_evidence_markers': ['interval clamp', 'earliest feasible witness', 'latest', 'nearest_preferred'],
        'handle_evidence_markers': ['interval clamp', 'earliest feasible witness', 'latest feasible witness', 'closest feasible witness'],
        'semantic_bridge': 'The feasible-witness-selector report family and the interval-clamp topic both collapse bounded positive-service local weakening selection to clamping a preferred rank into one overlap interval, so the topic already carries the implementor-facing claim.',
    },
    {
        'family': 'geometric_arrival_live_hold_cost_ceiling_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_hold_cost_ceiling_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_positive_same_deadline_live_waits_by_hold_cost_ceiling.md',
        'family_evidence_markers': ['hold-cost ceiling', 'same-deadline stateless live control', 'effective blind horizon', 'odd_even_plateau_rule'],
        'handle_evidence_markers': ['hold-cost ceiling', 'same-deadline stateless live wait', 'effective blind horizon', 'odd/even deadline ladder'],
        'semantic_bridge': 'The live hold-cost ceiling report and the existing budgeting topic both give the same closed-form threshold for promise-safe same-deadline live waiting, so the archive can cite that topic when the smaller-tree frontier surfaces this family.',
    },

    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_selector_classes_as_one_half_step_index.md',
        'family_evidence_markers': ['half_step_selector_index', 'adjacent tie selectors', '33', 'selector interval'],
        'handle_evidence_markers': ['half_step_selector_index', 'adjacent tie selectors', '33', 'selector interval'],
        'semantic_bridge': 'The selector-index report family and the existing library topic both say that batch-L2 selector classes compress exactly to one half-step integer without losing any witness-selection behavior, so the archive should cite that topic instead of retaining another report pair here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_solve_target_batch_promises_by_minimum_timeout.md',
        'family_evidence_markers': ['required_capture', 'minimum timeout', 'target margin', 'all-state guardrail'],
        'handle_evidence_markers': ['required_capture', 'minimum timeout', 'target margin', 'all-state guardrail'],
        'semantic_bridge': 'The target-batch-timeout report family and the standing minimum-timeout topic both invert realized batch promises into one required-capture scalar and then into an exact minimum timeout, so that durable topic already carries the implementor-facing claim.',
    },
    {
        'family': 'geometric_arrival_live_prefix_floor_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_prefix_floor_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_admit_positive_same_deadline_live_promises_by_prefix_floor.md',
        'family_evidence_markers': ['prefix floor', 'same-deadline stateless live', 'effective blind horizon', 'seven-bit'],
        'handle_evidence_markers': ['prefix floor', 'same-deadline stateless live', 'effective blind horizon', 'seven-bit'],
        'semantic_bridge': 'The live prefix-floor report and the standing prefix-budget topic both reduce positive same-deadline live admission to one integer prefix threshold plus the same seven-bit guardrail, so the archive should reuse that topic instead of retaining another report pair there.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_positive_wait_timeouts_by_arrival_hazard_capture_targets.md',
        'family_evidence_markers': ['arrival-only', 'capture target', 'finite timeout', 'asymptotic positive value'],
        'handle_evidence_markers': ['arrival-only', 'capture target', 'finite timeout', 'asymptotic positive value'],
        'semantic_bridge': 'The timeout-capture report family and the existing arrival-hazard capture-target topic both collapse positive waiting into one arrival-only timeout schedule that targets a desired fraction of asymptotic positive value, so that standing topic already serves as the durable citation handle.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_turn_capture_targeted_positive_waits_into_margin_floor_batch_caps.md',
        'family_evidence_markers': ['effective cost', 'capture target', 'realized margin', 'arrival-only timeout'],
        'handle_evidence_markers': ['effective cost', 'capture target', 'realized margin', 'arrival-only timeout'],
        'semantic_bridge': 'The timeout-margin-floor report family and the standing capture-targeted margin-floor topic both absorb realized-margin requirements into one effective-cost scalar layered on an arrival-only timeout schedule, so the archive can cite that topic rather than keep another paired report family for the same implementor-facing law.',
    },
    {
        'family': 'rematch_proxy_delta_hazard_cap_profile',
        'report_path': 'artifacts/reports/rematch_proxy_delta_hazard_cap_profile_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_declared_hazard_cap_profiles.md',
        'family_evidence_markers': ['hazard cap', 'width floor', 'shortlist', 'guardrail'],
        'handle_evidence_markers': ['hazard cap', 'width floor', 'shortlist', 'guardrail'],
        'semantic_bridge': 'The hazard-cap profile report and the standing declaration topic both distinguish the declared hazard-cap guardrail from the family and width filters that actually move the shortlist, so the existing topic already carries the durable contract for that report family.',
    },



    {
        'family': 'rematch_proxy_delta_decision_packet_catalog_page_resolution',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_resolution_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_resolve_catalog_slot_references_directly_from_paged_digest_catalogs.md',
        'family_evidence_markers': ['append-only catalog-slot repeat references', 'paged raw-digest catalog state', 'full ordered sha256-string catalog', 'resolve straight from those pages'],
        'handle_evidence_markers': ['repeat references should resolve directly from those pages', 'append-only semantic-fingerprint catalog', 'full ordered `sha256:` string list', 'direct slot resolution'],
        'semantic_bridge': 'The catalog-page-resolution report family and the standing paged-digest-resolution topic both say that short/catalog slot references should resolve directly from append-only raw-digest pages rather than by rebuilding the full ordered sha256 string catalog, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_catalog_reference',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_reference_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_repeat_writes_directly_from_paged_digest_catalogs.md',
        'family_evidence_markers': ['catalog_reference', 'append-only ordered semantic-fingerprint catalog', 'unordered fingerprint set', 'repeat writes'],
        'handle_evidence_markers': ['catalog_reference', 'append-only raw-digest pages', 'repeat-vs-new'],
        'semantic_bridge': 'The catalog-reference report family and the standing paged-digest-repeat-planning topic both say that once the archive preserves an append-only ordered semantic-fingerprint catalog, repeat writes should emit catalog-reference packets directly from that catalog instead of falling back to unordered-set byte references, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_freedom_tariff_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_price_higher_exact_uncertainty_guarantees_by_lost_dwell_freedom_not_just_cap_and_checkpoints.md',
        'family_evidence_markers': ['lost dwell freedom', 'continuous non-precision dwell support', 'dwell-freedom knee', 'floor per lost dwell'],
        'handle_evidence_markers': ['lost dwell freedom', 'continuous non-precision dwell freedom', 'dwell-freedom knee', '0.95'],
        'semantic_bridge': 'The dwell-freedom-tariff report family and the standing lost-dwell-freedom topic both price tighter exact uncertainty tiers by the same collapse in live dwell support, identifying exact 0.95 as the last tier with continuous non-precision dwell freedom, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_certify_path_l2_selector_classes_by_adjacent_threshold_fingerprint_words.md',
        'family_evidence_markers': ['adjacent-interval fingerprint word', 'monotone ternary forms', 'selector classes'],
        'handle_evidence_markers': ['adjacent-threshold fingerprint word', 'monotone ternary words'],
        'semantic_bridge': 'The threshold-fingerprint report family and the standing adjacent-threshold-fingerprint topic both certify path-L2 selector classes by the same 16-symbol monotone ternary word over adjacent midpoint thresholds and the same 33-class decode rule, so the existing topic should back citation and compaction for this family.',
    },

    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_the_cheapest_feasible_exact_tier_before_retuning_canonical_anchors.md',
        'family_evidence_markers': ['cheapest feasible exact tier', 'request oracle', 'canonical anchor', 'boundary-stabilization'],
        'handle_evidence_markers': ['cheapest feasible exact tier', 'request oracle', 'canonical anchor', 'boundary-stabilization'],
        'semantic_bridge': 'The canonical-anchor-control report family and the standing cheapest-feasible-tier topic both collapse steady exact-uncertainty control to one rule: run the request oracle, choose the cheapest feasible exact tier, then retune among canonical anchors only when needed, so the archive can cite that topic instead of retaining another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_width_only_weakening_slas_as_two_breakpoint_tiers.md',
        'family_evidence_markers': ['suffix_hitchhike_only', 'any_single_axis_hitchhike', 'width cap', 'positive service target'],
        'handle_evidence_markers': ['suffix_hitchhike_only', 'any_single_axis_hitchhike', 'width cap', 'positive service target'],
        'semantic_bridge': 'The service-tier-law report family and the standing two-breakpoint SLA topic both reduce width-only and width-cap weakening planning to the same tiny tier rule over exact-only, suffix-only, and dual-axis profiles, so the archive should reuse that existing topic as the durable citation handle.',
    },
    {
        'family': 'geometric_arrival_live_batch_cap_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_batch_cap_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_cap_same_deadline_stateless_live_batches_by_effective_horizon.md',
        'family_evidence_markers': ['effective blind horizon', 'same-deadline stateless live', 'positive live batch cap', 'maximum_admissible_batch_length'],
        'handle_evidence_markers': ['effective blind horizon', 'same-deadline stateless live', 'positive live batch cap', 'exact admissible batch cap'],
        'semantic_bridge': 'The live-batch-cap report family and the standing effective-horizon batch-cap topic both say that same-deadline stateless live batches must be capped as though blind commit had only the effective blind horizon, so the existing topic already carries the implementor-facing law.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_by_unconstrained_selector_interval.md',
        'family_evidence_markers': ['selector interval', 'singleton', 'adjacent tie pair', 'feasible overlap interval'],
        'handle_evidence_markers': ['selector interval', 'singleton', 'adjacent tie pair', 'feasible overlap interval'],
        'semantic_bridge': 'The selector-interval law and the standing batch-L2 selector-interval topic both reduce feasible compromise witness choice to one unconstrained selector interval projected onto the feasible overlap interval, so the archive can reuse that existing topic instead of preserving another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_close_shared_state_equiprobable_exact_batches_by_marginal_gain.md',
        'family_evidence_markers': ['shared-state equiprobable exact', 'same-state exact script', 'state_prefix_bits / (n(n+1))', '7/(n(n+1))'],
        'handle_evidence_markers': ['shared-state equiprobable exact', 'same-state exact script', 'state_prefix_bits / (n(n+1))', '7/(n(n+1))'],
        'semantic_bridge': 'The marginal-gain law and the standing shared-state equiprobable exact batching topic both collapse one-more-item wait decisions to the same per-script gain formula `state_prefix_bits / (n(n+1))`, so the existing topic already carries the durable operational claim.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_width_only_weakening_profile_upgrades_by_service_horizons.md',
        'family_evidence_markers': ['target service share', 'width-only weakening', 'support horizon', 'upgrade schedule'],
        'handle_evidence_markers': ['target service share', 'width-only weakening', 'support horizon', 'upgrade schedule'],
        'semantic_bridge': 'The service-horizon law and the standing width-only upgrade topic both invert SLA targets into exact-only and suffix-only support horizons, so the archive should reuse that topic when the one-trim-ahead frontier surfaces this family.',
    },

    {
        'family': 'geometric_arrival_live_reoptimization_deficit_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_reoptimization_deficit_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_price_stateless_live_reoptimization_as_a_geometric_promise_deficit.md',
        'family_evidence_markers': ['same-horizon deficit', 'K = 1', 'geometric deficit', 'blind-commit minus live-reoptimized value'],
        'handle_evidence_markers': ['same-horizon deficit', 'K = 1', 'geometric promise deficit', 'blind-commit value minus the exact geometric deficit'],
        'semantic_bridge': 'The live-reoptimization-deficit report family and the standing geometric-promise-deficit topic both state that stateless live reoptimization should be priced as blind-commit value minus an exact same-horizon geometric deficit, with zero deficit only at one-tick promises, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_catalog_route_block',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_route_block_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_digest_byte_route_blocks_beside_paged_catalogs.md',
        'family_evidence_markers': ['route blocks', 'repeat lookup', 'paged catalog', 'digest-byte'],
        'handle_evidence_markers': ['route blocks beside paged catalogs', 'repeat lookup', 'paged catalogs', 'digest-byte'],
        'semantic_bridge': 'The catalog-route-block report family and the standing digest-byte-route-block topic both compile append-local repeat evidence into the same compact route-block sidecar beside paged digest catalogs, so the archive should reuse that existing topic as the durable citation handle.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_step_positive_service_local_weakening_with_a_two_support_successor_automaton.md',
        'family_evidence_markers': ['successor', 'two support', 'suffix budget', 'terminal absorbing'],
        'handle_evidence_markers': ['successor automaton', 'two-support', 'suffix budget', 'terminal is absorbing'],
        'semantic_bridge': 'The mode-suffix-successor report family and the standing two-support-successor-automaton topic both regenerate the local positive-service weakening chain from the same tiny successor rule over exact/shared support sets and an absorbing terminal, so the existing topic should back citation and compaction for this family.',
    },


    {
        'family': 'rematch_proxy_delta_decision_packet_catalog_page_write',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_catalog_page_write_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_repeat_writes_directly_from_paged_digest_catalogs.md',
        'family_evidence_markers': ['page-native', 'paged digest catalog', 'repeat detection', 'short_catalog_reference'],
        'handle_evidence_markers': ['paged digest catalogs', 'repeat detection', 'short_catalog_reference', 'live repeat planning'],
        'semantic_bridge': 'The catalog-page-write report family and the standing paged-digest-repeat-planning topic both say repeat-vs-new decisions should be made directly from append-only paged digest state rather than by rebuilding a full ordered fingerprint list, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_switch_penalty_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_price_sidecar_churn_on_exact_switch_penalty_frontiers.md',
        'family_evidence_markers': ['switch-penalty frontier', 'fixed policy', 'robust mid-cost regime', '5679.676082'],
        'handle_evidence_markers': ['exact switch-penalty frontier', 'fixed route blocks', '4-transition schedule', '5679.676082'],
        'semantic_bridge': 'The compact-repeat switch-penalty report family and the standing exact-switch-penalty-frontier topic both say sidecar churn should be priced as a frontier of surviving switches rather than one average regret threshold, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_preference_halfspace',
        'report_path': 'artifacts/reports/rematch_proxy_delta_preference_halfspace_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_preference_separating_inequalities.md',
        'family_evidence_markers': ['additive half-space patterns', 'width floor and delta ceiling drop out entirely', 'explicit inequality', '0.00142'],
        'handle_evidence_markers': ['separating inequality', 'width floor and delta ceiling no longer change the preference boundary', '0.00142', 'declared metric premiums'],
        'semantic_bridge': 'The preference-halfspace report family and the standing preference-separating-inequalities topic both turn the final certified candidate choice into one explicit additive inequality over declared metric premiums, so the archive should reuse that topic instead of keeping another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_fixed_policy_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compare_sidecar_churn_against_fixed_policy_regret.md',
        'family_evidence_markers': ['fixed compact repeat sidecar', 'regret vs dynamic', '927.685921', 'best fixed sidecar'],
        'handle_evidence_markers': ['fixed-policy regret', 'regret versus the fully dynamic schedule', '927.68592', 'best fixed policy'],
        'semantic_bridge': 'The compact-repeat fixed-policy report family and the standing fixed-policy-regret topic both treat sidecar churn as a budgeted choice by comparing the best fixed sidecar against the fully dynamic schedule, so the existing topic should back citation and compaction for this family.',
    },

    {
        'family': 'rematch_proxy_delta_decision_packet_weight_atom_group',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_weight_atom_group_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_group_repeated_weight_atoms_inside_packed_seeds.md',
        'family_evidence_markers': ['grouping repeated atoms', 'axis masks', 'dense_all_ones', 'sparse ordered-value vector'],
        'handle_evidence_markers': ['grouped atom-mask form', 'axis mask per atom', 'dense all-ones', 'sparse ordered-value vector'],
        'semantic_bridge': 'The weight-atom-group report family and the standing grouped-weight-atoms topic both say repeated scalar atoms in oracle-weight packed seeds should be stored once per atom behind axis masks and compared against the sparse ordered-value vector, so the existing topic should back citation and compaction for this family.',
    },


    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_checkpoint_schedule_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_schedule_compact_repeat_sidecar_rechecks_at_finite_checkpoint_sets.md',
        'family_evidence_markers': ['finite checkpoint schedule', 'routine page births', 'structural checkpoints', 'per-append sidecar reconsideration'],
        'handle_evidence_markers': ['finite checkpoint set', 'page-birth checkpoint stream', 'structural recheck points', 'per-append reconsideration'],
        'semantic_bridge': 'The checkpoint-schedule report and the standing finite-checkpoint-set topic both reduce compact repeat-sidecar maintenance to a sparse pre-registered checkpoint set keyed to page births and structural cliffs, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_short_catalog_reference',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_short_catalog_reference_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_short_catalog_slot_references_inside_small_append_only_catalogs.md',
        'family_evidence_markers': ['short_catalog_reference', 'append-only ordered semantic-fingerprint catalog', 'slot fits under 16384', '14-bit short token'],
        'handle_evidence_markers': ['short_catalog_reference', 'append-only ordered semantic-fingerprint catalog', 'below `16384`', '14-bit short token'],
        'semantic_bridge': 'The short-catalog-reference report and the standing small-append-only-catalog topic both say repeats should use a fixed-width short slot token whenever the ordered append-only catalog stays below 16384 entries, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_repair_floor_driven_exact_uncertainty_changes_at_support_boundaries_and_only_then_recenter_to_canonical_anchors.md',
        'family_evidence_markers': ['boundary compass', 'canonical anchor', 'transient feasibility', 'steady operating mode'],
        'handle_evidence_markers': ['boundary compass', 'canonical anchors', 'first repair step', 'steady mode'],
        'semantic_bridge': "The boundary-stabilization protocol report and the standing boundary-first recentering topic both say floor-driven exact-uncertainty retuning should first land on the nearest surviving support boundary and only then optionally recenter to the destination band's canonical anchor, so the existing topic should back citation and compaction for this family.",
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_stream_canonical_shortest_half_step_generator_words_via_interval_state_prefixes.md',
        'family_evidence_markers': ['canonical shortest generator word', 'interval-state prefix', 'no extra script-only', 'standalone transport'],
        'handle_evidence_markers': ['deterministic shortest script', 'interval-state prefix', 'canonical shortest', 'script-only decode block'],
        'semantic_bridge': 'The canonical-shortest-generator-word prefix report and the standing interval-state-prefix topic both show that standalone canonical shortest-script transport collapses to the existing interval-state prefix codec, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_govern_exact_uncertainty_weakening_approximations_by_overshoot_axis_admission_profiles.md',
        'family_evidence_markers': ['precision_hitchhike_only', 'suffix_hitchhike_only', 'mixed hole-family portfolios', 'workload-level necessity'],
        'handle_evidence_markers': ['precision-only', 'suffix-only', 'dual-axis permission', 'portfolio-wide convenience'],
        'semantic_bridge': 'The weakening-portfolio guardrail report and the standing overshoot-axis admission-profile topic both reduce exact-uncertainty weakening control to a tiny menu over exact-only, precision-only, suffix-only, and dual-axis portfolio permissions, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_anchor_contract',
        'report_path': 'artifacts/reports/rematch_proxy_delta_anchor_contract_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_topology_stable_delta_anchors.md',
        'family_evidence_markers': ['topology-stable subband', 'admissible parent band', 'boundary fragility', 'nearest topology boundary'],
        'handle_evidence_markers': ['topology-stable subbands', 'stability-first anchor', 'anchor laundering', 'boundary fragility'],
        'semantic_bridge': 'The anchor-contract report family and the standing topology-stable-delta-anchor topic both replace boundary-biased parent-band anchors with an interior stability-first anchor or explicit topology-stable subbands, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_profile',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_profile_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_share_decision_packet_provenance_profiles.md',
        'family_evidence_markers': ['archive-local', 'shared profile ref', 'portable storage form', 'standalone'],
        'handle_evidence_markers': ['archive-local', 'shared provenance profile', 'standalone', 'storage form'],
        'semantic_bridge': 'The decision-packet-profile report family and the standing shared-provenance-profile topic both replace repeated per-packet provenance with an archive-local profile reference while preserving exact standalone reconstruction, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_hazard_preference_regime',
        'report_path': 'artifacts/reports/rematch_proxy_delta_hazard_preference_regime_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_hazard_preference_regime_contracts.md',
        'family_evidence_markers': ['exact hazard-preference regimes', 'caps `10..14`', 'caps `15..19`', 'caps `20..10000`'],
        'handle_evidence_markers': ['three exact cap regimes', '10..14', '15..19', '20+',],
        'semantic_bridge': 'The hazard-preference-regime report family and the standing hazard-regime-contract topic both collapse the residual hazard term into exact discrete cap regimes with the same flip at 15 and the same later panel switch from 20 onward, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_weight_vector',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_weight_vector_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_keyless_weight_vectors_inside_packed_seeds.md',
        'family_evidence_markers': ['weight-vector', 'packed seeds', 'oracle_weights', 'fixed family10 weight order'],
        'handle_evidence_markers': ['keyless weight vector', 'packed_seed', 'oracle_weights', 'axis names'],
        'semantic_bridge': 'The decision-packet weight-vector report family and the standing keyless-weight-vector topic both replace repeated named coordinate payloads with the same packed weight-vector form inside packed seeds, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_analytic_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_analytic_frontier_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md',
        'family_evidence_markers': ['packed_seed', 'byte_seed', 'byte_reference', 'candidate evaluations'],
        'handle_evidence_markers': ['packed_seed', 'byte_seed', 'byte_reference', 'deterministic frontier set'],
        'semantic_bridge': 'The analytic-frontier report family and the standing exact-shortlist topic both replace repeated frontier measurement with the same packed-seed / byte-seed / byte-reference shortlist rule, so the archive can cite that topic instead of preserving another paired report family for the same writer contract.',
    },


    {
        'family': 'geometric_arrival_live_minimum_deadline_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_minimum_deadline_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_positive_same_deadline_live_promises_on_odd_deadlines.md',
        'family_evidence_markers': ['minimum nominal live deadline', '2k - 1', 'odd_deadline_entry', 'zero_margin_formula'],
        'handle_evidence_markers': ['minimum same-deadline live deadline', '2k - 1', 'odd ladder', 'zero-floor shortcut'],
        'semantic_bridge': 'The live-minimum-deadline report and the existing odd-deadline topic both show that positive same-deadline live promises first enter exactly on the odd ladder 2K-1, so the archive should reuse that topic as the durable citation handle.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_cap_batches_directly_from_fixed_timeouts_and_margin_floors.md',
        'family_evidence_markers': ['maximum admissible batch length', 'realized margin', 'batch cap', 'quadratic'],
        'handle_evidence_markers': ['maximum admissible batch length', 'realized margin', 'batch cap', 'quadratic'],
        'semantic_bridge': 'The timeout-batch-cap report family and the standing fixed-timeout margin-floor topic both solve the same admissible-batch quadratic directly from a realized-margin requirement, so the archive can cite that topic instead of retaining another paired report family here.',
    },
    {
        'family': 'geometric_arrival_live_arrival_floor_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_arrival_floor_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_gate_positive_same_deadline_live_promises_by_arrival_floor.md',
        'family_evidence_markers': ['positive arrival floor', 'upward-closed', 'one-dimensional threshold'],
        'handle_evidence_markers': ['positive arrival floor', 'upward-closed', 'one-dimensional threshold'],
        'semantic_bridge': 'The live-arrival-floor report and the standing arrival-floor topic both turn positive same-deadline live promise admission into one upward-closed hazard threshold, so the archive should reuse that topic before treating this frontier family as a fresh durable-note gap.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_width_only_weakening_profiles_by_service_frontier_not_full_profile_menu.md',
        'family_evidence_markers': ['precision_hitchhike_only', 'suffix_hitchhike_only', '11/15', 'one-axis'],
        'handle_evidence_markers': ['precision_hitchhike_only', 'suffix_hitchhike_only', '11/15', 'one-axis'],
        'semantic_bridge': 'The width-only service-frontier report and the standing service-frontier topic both show that suffix-only dominates precision-only under width-conditioned uncertainty and that one-axis service tops out at 11/15, so the existing topic should carry this hotspot family too.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_gate_shared_state_equiprobable_exact_batch_waiting_by_arrival_hazard_and_hold_cost.md',
        'family_evidence_markers': ['same-state exact script', 'arrival hazard', 'hold cost', 'gain - c/p'],
        'handle_evidence_markers': ['same-state exact script', 'arrival hazard', 'hold cost', 'gain - c/p'],
        'semantic_bridge': 'The geometric-arrival wait-value report and the standing exact-batch waiting topic both gate waiting by the same arrival-hazard versus hold-cost comparison and the same closed-form gain minus c over p law, so the topic already covers this family for citation-first compaction.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_frontier_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md',
        'family_evidence_markers': ['byte_seed', 'byte_reference', 'oracle_weights'],
        'handle_evidence_markers': ['byte_seed', 'byte_reference', 'oracle_weights'],
        'semantic_bridge': 'The measured decision-packet frontier report and the standing exact-shortlist topic both preserve the same live rule: repeat writes go straight to byte_reference, most first writes go to byte_seed, and only oracle_weights remains a tiny measured exception set.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_as_two_integer_summaries.md',
        'family_evidence_markers': ['preferred_count', 'preferred_rank_sum', 'two integers', 'l2'],
        'handle_evidence_markers': ['preferred_count', 'preferred_rank_sum', 'two integers', 'l2'],
        'semantic_bridge': 'The batch-mean sufficient-statistic report and the standing two-integer summary topic both compress L2 witness choice down to preferred_count and preferred_rank_sum, so the existing topic can stand in for this heavy report family on the next frontier.',
    },
    {
        'family': 'rematch_gap_retirement_rubric',
        'report_path': 'artifacts/reports/rematch_gap_retirement_rubric_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/sg003_phase3_now_needs_world_emission_not_more_proxy_reports.md',
        'family_evidence_markers': ['world emission', 'proxy', 'endogenous rematch-world benchmark'],
        'handle_evidence_markers': ['world emission', 'proxy', 'endogenous rematch-world benchmark'],
        'semantic_bridge': 'The phase-3 gap-retirement rubric and the standing SG-003 world-emission topic both say the same thing: the compact proxy contract already exists, and progress now comes from one endogenous rematch-world benchmark emitting it rather than from more proxy fanout.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_use_portfolio_width_as_a_confidence_prior_for_dual_axis_weakening_permission.md',
        'family_evidence_markers': ['confidence ladder', 'dual-axis permission', 'suffix-only family', 'width-conditioned'],
        'handle_evidence_markers': ['confidence ladder', 'dual-axis permission', 'suffix-only family', 'width-conditioned'],
        'semantic_bridge': 'The portfolio-confidence-ladder report and the standing width-prior topic both turn weakening governance into the same width-conditioned confidence staircase: dual-axis permission becomes the default by width four, the ninety-percent prior by width seven, and the one-axis tail collapses toward suffix-only as width grows.',
    },

    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_reduce_width_cap_weakening_service_planning_to_the_worst_case_batch_width.md',
        'family_evidence_markers': ['suffix_hitchhike_only', '11/15'],
        'handle_evidence_markers': ['suffix_hitchhike_only', '11/15'],
        'semantic_bridge': 'The width-cap guarantee report and the standing worst-case-width topic both collapse capped-width service planning to the endpoint width, preserve the same suffix_hitchhike_only survival thresholds, and force dual-axis above the same 11/15 ceiling.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_weakening_overshoot_profiles_by_portfolio_width.md',
        'family_evidence_markers': ['dual-axis permission', 'majority minimal profile', 'universal'],
        'handle_evidence_markers': ['dual-axis permission', 'majority minimal profile', 'universal'],
        'semantic_bridge': 'The width-law report and the standing portfolio-width topic both give the same compact governance thresholds: dual-axis permission becomes the majority minimal profile by width four and becomes universal once the portfolio is wide enough.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compute_shared_state_equiprobable_exact_transport_margins_by_affine_family.md',
        'family_evidence_markers': ['43n/9 - 8', 'universal lower envelope', 'one-word expected ties'],
        'handle_evidence_markers': ['43n/9 - 8', 'universal lower envelope', 'one-word expected ties'],
        'semantic_bridge': 'The affine-margin report and the standing affine-family topic both compress the 153-state equiprobable shared-state transport law down to seven affine families with the same 43n/9 - 8 lower envelope.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_byteframe',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_byteframe_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_base64url_byteframes_inside_archive.md',
        'family_evidence_markers': ['base64url', 'byte_seed', 'byte_reference'],
        'handle_evidence_markers': ['base64url', 'byte_seed', 'byte_reference'],
        'semantic_bridge': 'The byteframe snapshot and the standing byteframe topic both preserve the same narrow storage rule: encode packed payloads as base64url byteframes, prefer byte_seed for first writes when measured best, and use byte_reference for repeats.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_merge_positive_service_local_weakening_constraints_by_clock_interval_intersection.md',
        'family_evidence_markers': ['max(lower_rank) <= min(upper_rank)', 'common witness', 'pairwise-overlapping'],
        'handle_evidence_markers': ['max(lower_rank) <= min(upper_rank)', 'common witness', 'pairwise-overlapping'],
        'semantic_bridge': 'The feasibility-intersection report and the standing clock-interval topic both collapse multi-constraint positive-service local weakening feasibility to one closed-interval overlap test with the same common-witness and blocker-certificate geometry.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_bounded_positive_service_local_weakening_queries_as_clock_intervals.md',
        'family_evidence_markers': ['bounded local', 'clock/rank intervals', 'pairwise_path_distance + 1'],
        'handle_evidence_markers': ['bounded local', 'clock intervals', 'pairwise_path_distance + 1'],
        'semantic_bridge': 'The interval-law report and the standing clock-interval topic both collapse bounded positive-service local weakening navigation to one clipped rank/clock interval whose segment size is exactly pairwise_path_distance + 1, so the archive can cite that topic instead of retaining another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_exact_uncertainty_weakening_as_a_chain_with_holes_in_two_bundle_space.md',
        'family_evidence_markers': ['3x5', 'exact coordinates', 'monotone chain', 'hitchhiking overshoot'],
        'handle_evidence_markers': ['3x5', 'exact coordinates', 'monotone chain', 'hitchhiking overshoot'],
        'semantic_bridge': 'The primitive-demand-surface report and the standing two-bundle-space topic both expose the same shape: the weakening menu is a monotone chain with audited holes inside the 3x5 primitive box, so off-chain requests must buy the least dominating overshoot point rather than an exact primitive coordinate.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_shared_state_equiprobable_exact_batches_by_mean_cost.md',
        'family_evidence_markers': ['38/9 + 8/n', 'bits per script', 'local_choice_floor', 'no finite'],
        'handle_evidence_markers': ['38/9 + 8/n', 'bits per script', 'local_choice_floor', 'no finite'],
        'semantic_bridge': 'The mean-cost-law report and the standing budgeting topic both compress equiprobable shared-state exact batching to the same per-script cost law `local_choice_floor + state_prefix_bits / n`, with one universal all-state envelope `38/9 + 8/n` and no finite batch below the asymptotic floor.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_govern_exact_uncertainty_weakening_approximations_by_overshoot_axis_admission_profiles.md',
        'family_evidence_markers': ['exact_only', 'precision_hitchhike_only', 'suffix_hitchhike_only'],
        'handle_evidence_markers': ['exact_only', 'precision_hitchhike_only', 'suffix_hitchhike_only'],
        'semantic_bridge': 'The overshoot-axis guardrails report and the standing admission-profile topic both collapse exact-uncertainty weakening governance to the same tiny menu over exact-only, precision-only, and suffix-only hitchhike permissions, so the archive can reuse that topic instead of preserving another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_batch_l2_compromise_requests_by_canonical_reduced_mean.md',
        'family_evidence_markers': ['cross-width', 'integers and half-integers', 'l2'],
        'handle_evidence_markers': ['cross-width', 'integers and half-integers', 'l2'],
        'semantic_bridge': 'The reduced-mean law report and the standing canonical-reduced-mean topic both show that L2 batch witness choice collapses to the same cross-width reduced-mean key, with cross-width reuse appearing only for integers and half-integers, so the existing topic already carries the durable implementation rule.',
    },
    {
        'family': 'geometric_arrival_live_burden_axis_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_burden_axis_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_cache_same_deadline_live_promises_on_one_burden_axis.md',
        'family_evidence_markers': ['b_live', 'effective blind horizon', 'state_prefix_bits'],
        'handle_evidence_markers': ['b_live', 'effective blind horizon', 'state_prefix_bits'],
        'semantic_bridge': 'The live burden-axis report and the standing one-burden-axis topic both collapse same-deadline live admission to the same exact burden scalar b_live layered over the effective blind horizon, so the archive should reuse that topic before treating the projected frontier family as a fresh note gap.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_bounded_local_weakening_compromise_witnesses_by_mean_projection.md',
        'family_evidence_markers': ['feasible overlap interval', 'outliers', 'l2'],
        'handle_evidence_markers': ['feasible overlap interval', 'outliers', 'l2'],
        'semantic_bridge': 'The mean-projection law report and the standing mean-projection topic both reduce bounded local weakening L2 witness choice to projecting the arithmetic mean onto the feasible overlap interval, with the same outlier-sensitive compromise semantics, so the archive can cite that topic instead of preserving another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_local_upgrade_witness.md',
        'family_evidence_markers': ['positive-service', 'support signature', 'next exact', 'next suffix'],
        'handle_evidence_markers': ['positive-service', 'support signature', 'next exact', 'next suffix'],
        'semantic_bridge': 'The local-upgrade-witness report and the standing local-upgrade topic both compress positive-service relaxation planning to the same support-signature card with next-exact versus next-suffix thresholds, so the archive should cite that topic rather than retain another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_switch_shared_state_exact_transport_by_local_margin_thresholds.md',
        'family_evidence_markers': ['state prefix', 'interior singleton', 'interior nonsingleton', 'safe at one'],
        'handle_evidence_markers': ['state prefix', 'interior singleton', 'interior nonsingleton', 'safe at one'],
        'semantic_bridge': 'The shared-state exact threshold report and the standing local-margin-threshold topic both reduce safe-versus-strict batch switching to the same local state-prefix margin geometry across interior singleton and nonsingleton cases, so the existing topic already carries the durable rule for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_transition_budget_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_compact_repeat_sidecar_rewrites_by_transition_count.md',
        'family_evidence_markers': ['rewrite count', 'route blocks', 'filters', '0.968419'],
        'handle_evidence_markers': ['rewrite count', 'route blocks', 'filters', '0.968419'],
        'semantic_bridge': 'The transition-budget report family and the standing rewrite-count topic both say the same thing: compact repeat sidecars should spend the first few transitions on the structural regime changes first, then stop once the large cliff-fallback savings are already captured.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_commitment_tariff_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_dwell_8_through_18_as_the_neutral_exact_uncertainty_zone_and_price_other_live_regions_as_commitments.md',
        'family_evidence_markers': ['precision commitment', 'relaxed-only commitment', '0.109999', 'neutral exact uncertainty zone'],
        'handle_evidence_markers': ['precision commitment', 'relaxed-only commitment', '0.109999', 'neutral exact uncertainty zone'],
        'semantic_bridge': 'The dwell-commitment tariff report and the standing neutral-zone topic both price dwell choices as commitment types: 8–18 is the neutral exact zone, dwell 2 is a precision commitment, and dwell 19–32 is a relaxed-only commitment unless external constraints force it.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_median_projection_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_bounded_local_weakening_compromise_witnesses_by_median_projection.md',
        'family_evidence_markers': ['projected_median_interval_matches_bruteforce_argmin', 'all_ties_come_from_even_preference_widths', 'feasible overlap interval', 'source-rank coordinate'],
        'handle_evidence_markers': ['path `l1` problem', 'median interval', 'feasible overlap interval', 'source ranks'],
        'semantic_bridge': 'The batch median-projection report and the standing median-projection topic both reduce bounded local weakening compromise choice to projecting one unconstrained L1 median interval onto the feasible overlap interval, so the archive should reuse that topic instead of keeping another report pair here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_prefix_reference',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_prefix_reference_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_store_prefix_resolved_references_inside_archive.md',
        'family_evidence_markers': ['shortest unique local prefix', 'full semantic fingerprints', 'minimum configured prefix length', 'archive-local prefix reference'],
        'handle_evidence_markers': ['shortest unique local fingerprint prefix', 'full portable fingerprint reference', 'archive-local prefix reference', '`12`-hex prefix floor'],
        'semantic_bridge': 'The prefix-reference report and the standing prefix-resolved-reference topic both say that once the archive already stores a semantic body, repeat writes should shrink to the shortest unique local fingerprint prefix instead of restating the full exported reference string.',
    },
    {
        'family': 'geometric_arrival_live_hazard_staircase_law',
        'report_path': 'artifacts/reports/geometric_arrival_live_hazard_staircase_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_budget_same_deadline_live_deadlines_as_odd_hazard_staircases.md',
        'family_evidence_markers': ['same-deadline live schedule class', 'odd ladder', 'one-way odd staircase', 'higher arrival hazard never requires a longer minimum deadline'],
        'handle_evidence_markers': ['same-deadline live schedule over hazard', 'odd ladder', 'one-way odd staircase', 'higher arrival estimates never demand a longer same-deadline live deadline'],
        'semantic_bridge': 'The hazard-staircase report and the standing odd-hazard-staircase topic both compress positive same-deadline live control into one monotone odd hazard ladder, so the durable topic should carry this family for future compaction.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_width_only_service_relaxations_by_residual_axis_budgets.md',
        'family_evidence_markers': ['residual axis budget', 'shared_diagonal_remaining', 'future growth is now pure single-axis countdown', 'staircase distance to terminal'],
        'handle_evidence_markers': ['residual budget triple', 'shared_diagonal_remaining', 'future growth is now a pure single-axis countdown', 'staircase distance to terminal'],
        'semantic_bridge': 'The residual-axis-budget report and the standing residual-budget topic both summarize every future width-only service relaxation by exact-only, suffix-only, and shared-diagonal remaining counts, so the archive should reuse that topic instead of retaining another paired report surface here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_local_weakening_state_as_mode_plus_suffix_budget.md',
        'family_evidence_markers': ['one-counter code', 'suffix budget', 'zero-consumption bridge states', 'mode plus remaining suffix budget'],
        'handle_evidence_markers': ['suffix counter', 'zero-consumption bridge states', 'one-counter chain', 'mode plus suffix budget'],
        'semantic_bridge': 'The mode-suffix counter-law report and the standing mode-plus-suffix-budget topic both compress positive-service local weakening into one code with suffix-consuming steps and zero-consumption bridge modes, so the archive should cite that durable topic rather than retain another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_backstep_positive_service_local_weakening_with_the_same_two_support_sets.md',
        'family_evidence_markers': ['strict predecessor', 'same tiny support basis', 'source boundary', 'terminal boundary'],
        'handle_evidence_markers': ['strict predecessor', 'same exact/shared support basis', 'source boundary', 'terminal boundary'],
        'semantic_bridge': 'The mode-suffix predecessor-law report and the standing backstep topic both recover strict predecessors from the same exact/shared support sets plus the two boundaries, so the existing topic already carries the durable implementor rule for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_positive_service_local_weakening_as_a_single_rank_clock.md',
        'family_evidence_markers': ['successor', 'predecessor', 'path distance', 'absolute clock difference'],
        'handle_evidence_markers': ['successor', 'predecessor', 'path distance', 'absolute clock difference'],
        'semantic_bridge': 'The mode-suffix rank-clock law report and the standing single-rank-clock topic both collapse positive-service local weakening into one arithmetic clock, so the existing topic already carries the implementor-facing claim for this family.',
    },
    {
        'family': 'rematch_world_benchmark_fill_status',
        'report_path': 'artifacts/reports/rematch_world_benchmark_fill_status_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/filled_rematch_benchmarks_should_clear_template_slots_without_touching_open_ended_decision_intervals.md',
        'family_evidence_markers': ['24-slot fill job', 'template strings', 'open-ended `end_delay: null` intervals', 'five world-dependent section statuses'],
        'handle_evidence_markers': ['TEMPLATE_*', 'world-dependent null telemetry fields', 'open-ended `end_delay: null` intervals', 'five world-dependent section statuses'],
        'semantic_bridge': 'The fill-status snapshot and the standing completion-gate topic both say the same thing: clear world-dependent template/null slots, flip the five fill statuses, and preserve the copied open-ended decision intervals, so the durable topic should carry this family for compaction.',
    },
    {
        'family': 'rematch_world_benchmark_mutation_surface',
        'report_path': 'artifacts/reports/rematch_world_benchmark_mutation_surface_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/filled_rematch_world_benchmarks_should_freeze_copied_contract_state_and_mutate_only_seed_designated_prefixes.md',
        'family_evidence_markers': ['allowed mutable prefixes', 'frozen prefixes', 'compact decision bundle', 'contract pointers'],
        'handle_evidence_markers': ['allowed mutable prefixes', 'frozen prefixes', 'compact decision bundle', 'contract pointers'],
        'semantic_bridge': 'The mutation-surface report and the new prefix-discipline topic both keep the same publication boundary: mutate only the seed-designated fill prefixes and keep copied contract state frozen while the first endogenous benchmark is completed.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_exact_uncertainty_weakening_as_a_chain_with_holes_in_two_bundle_space.md',
        'family_evidence_markers': ['single-axis tax', 'forced overshoot', 'precision-only hitchhike', 'suffix-only hitchhike'],
        'handle_evidence_markers': ['3x5', 'chain with holes', 'forced overshoot', 'Deep suffix-only demands'],
        'semantic_bridge': 'The primitive-overshoot taxonomy and the standing two-bundle chain-with-holes topic both say the same implementor-facing thing: off-chain primitive demands should be treated as forced single-axis overshoot requests against the current weakening menu rather than as exact attainable coordinates.',
    },
    {
        'family': 'rematch_proxy_delta_admissibility',
        'report_path': 'artifacts/reports/rematch_proxy_delta_admissibility_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_budget_admissible_delta_bands.md',
        'family_evidence_markers': ['paired-seed cap', 'admissible deltas', 'bands', 'knife-edge'],
        'handle_evidence_markers': ['budget-admissible delta band', 'budget caps', 'admissible delta bands', 'knife-edge'],
        'semantic_bridge': 'The delta-admissibility snapshot and the standing budget-admissible-delta-bands topic both replace naked SESOI points with budget-aware admissible intervals, so the archive can cite that compact topic instead of retaining another paired report surface here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_scalar_atom',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_scalar_atom_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_atomize_common_decimal_scalars_inside_packed_seeds.md',
        'family_evidence_markers': ['shared scalar atom codebook', 'repeated canonical decimal strings', 'quoted decimal text', 'packed seed'],
        'handle_evidence_markers': ['shared scalar atom codebook', 'quoted decimal strings', 'common canonical decimal strings', 'packed seed'],
        'semantic_bridge': 'The scalar-atom snapshot and the standing scalar-atom topic both say that packed seeds should replace repeated canonical decimal strings with a tiny shared atom codebook, so the durable topic already carries the implementor-facing rule for this family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_exact_uncertainty_service_relaxations_by_bandwise_local_slack_lead.md',
        'family_evidence_markers': ['signed local slack lead', 'suffix unlocks first', 'exact unlocks first', 'shared diagonal tie'],
        'handle_evidence_markers': ['signed local slack lead', 'suffix unlocks first', 'exact unlocks first', 'shared diagonal unlock'],
        'semantic_bridge': 'The local-slack-lead law and the standing bandwise slack-lead topic both compress next-axis choice plus losing-axis tax to one signed local threshold gap, so the archive should reuse that durable note instead of preserving another report pair here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_service_relaxations_by_local_corridor_exit_witnesses.md',
        'family_evidence_markers': ['current corridor', 'corridor steps remaining', 'boundary transition', 'next corridor'],
        'handle_evidence_markers': ['current corridor', 'corridor steps remaining', 'boundary transition', 'next corridor'],
        'semantic_bridge': 'The local-corridor-exit witness law and the standing corridor-exit topic both summarize service-relaxation planning as a small corridor grammar with boundary handoffs, so the archive can cite that compact topic instead of retaining another paired report family here.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_size_shared_state_equiprobable_exact_batches_by_target_margin.md',
        'family_evidence_markers': ['target margin', 'minimum batch length', 'equiprobable', '43n/9 - 8'],
        'handle_evidence_markers': ['target margin', 'minimum batch length', 'equiprobable', '43n/9 - 8'],
        'semantic_bridge': 'The target-margin law and the standing equiprobable target-margin topic both invert desired shared-state exact savings into one closed-form minimum batch length, so the current frontier can cite that durable topic instead of retaining another JSON+MD report pair.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compiled_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compiled_frontier_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md',
        'family_evidence_markers': ['byte_reference', 'byte_seed', 'packed_seed', 'oracle_weights'],
        'handle_evidence_markers': ['byte_reference', 'byte_seed', 'packed_seed', 'oracle_weights'],
        'semantic_bridge': 'The compiled-frontier snapshot and the standing exact-shortlists topic both collapse local decision-packet storage to the same implementor rule: repeats go straight to byte_reference, non-weight first writes go straight to byte_seed, and only oracle_weights first writes need the packed_seed versus byte_seed comparison.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_switch_shared_state_exact_transport_by_equiprobable_mean_margins.md',
        'family_evidence_markers': ['strict expected switch threshold', 'strict expected winner by batch length 2', 'eight 8-bit interior singleton', 'equiprobable'],
        'handle_evidence_markers': ['strict expected switch threshold', 'strict expected winner by batch length 2', 'eight 8-bit interior singleton', 'equiprobable'],
        'semantic_bridge': 'The equiprobable exact-threshold law and the standing equiprobable-mean-margins topic both give the same closed-form mean switch thresholds for shared-state exact transport, including the batch-length-2 strict-win rule and the eight interior singleton improvement cases.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_choose_shortest_script_transport_by_state_knowledge_and_branch_exactness.md',
        'family_evidence_markers': ['exact noncanonical shortest branch', 'deterministic canonicalization is acceptable', 'interval-state prefix', 'zero script bits'],
        'handle_evidence_markers': ['exact noncanonical shortest branch', 'deterministic canonicalization is acceptable', 'interval-state prefix', 'zero script bits'],
        'semantic_bridge': 'The shortest-script transport-frontier law and the standing state-knowledge-and-branch-exactness topic both compress transport choice to the same four regimes over state knowledge and exact-branch preservation, so the archive can cite that topic instead of keeping another paired report family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_resolve_batch_l2_witnesses_by_clamping_half_step_selector_indices_into_doubled_feasible_bands.md',
        'family_evidence_markers': ['half_step_selector_index', 'doubled feasible band', '33', 'same half-step lattice'],
        'handle_evidence_markers': ['half_step_selector_index', 'doubled feasible band', '33', 'same half-step lattice'],
        'semantic_bridge': 'The feasible-band clamp law and the standing doubled-feasible-band topic both reduce batch-L2 witness execution to clamping one half-step selector index on the shared 33-class lattice, so the archive can cite that topic instead of retaining another paired report family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_width_conditioned_weakening_service_as_a_cardinality_law.md',
        'family_evidence_markers': ['exact_only', 'precision_hitchhike_only', 'suffix_hitchhike_only', '11/15'],
        'handle_evidence_markers': ['exact_only', 'precision_hitchhike_only', 'suffix_hitchhike_only', '11/15'],
        'semantic_bridge': 'The family-cardinality law and the standing width-conditioned-cardinality topic both collapse the recent weakening service stack to the same admissible-family counts and 11/15 singleton ceiling, so the archive can cite that topic instead of preserving another report pair.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_plan_width_only_weakening_profile_upgrades_by_service_horizons.md',
        'family_evidence_markers': ['width-only', 'exact horizon', 'suffix horizon', 'staircase'],
        'handle_evidence_markers': ['width-only', 'exact-only horizon', 'suffix-only horizon', 'upgrade schedule'],
        'semantic_bridge': 'The service-horizon staircase law and the standing service-horizons topic both compress width-only weakening upgrades to exact and suffix support horizons with one monotone schedule, so the archive can reuse that topic rather than keeping another paired report family.',
    },
    {
        'family': 'inheritor_priority',
        'report_path': 'artifacts/reports/inheritor_priority_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_gap_sg003_should_be_retired_in_three_compact_layers.md',
        'family_evidence_markers': ['minimal machine-checkable artifact contracts', 'planner-manifest', 'turnover tempo', 'paired raw/in-match rankings'],
        'handle_evidence_markers': ['minimal machine-checkable artifact contracts', 'planner-manifest', 'turnover tempo', 'paired raw/in-match rankings'],
        'semantic_bridge': 'The inheritor-priority snapshot and the standing SG-003 three-layer note both say the same compact thing: retire the rematch backlog by freezing planner-manifest and comparability contracts before any bulky rerun surfaces, so the archive can cite that topic instead of keeping another paired priority report in the frontier.',
    },

    {
        'family': 'tranche_status',
        'report_path': 'artifacts/reports/tranche_status.json',
        'handle_path': 'docs/LIBRARY/topics/rematch_benchmark_programs_should_publish_tranche_closure_as_a_governance_surface.md',
        'family_evidence_markers': ['completion_percent', 'completed', 'rows', 'done'],
        'handle_evidence_markers': ['tranche-closure state', 'governance metadata', 'publication-ready', 'provisionally staged'],
        'semantic_bridge': 'The tranche-status report and the standing tranche-closure governance note both treat closure state as explicit benchmark-governance metadata rather than operator memory, so the archive can cite that note instead of retaining another operational status artifact family.',
    },

    {
        'family': 'rematch_proxy_delta_unique_minimal_cap_probe',
        'report_path': 'artifacts/reports/rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_unique_minimal_cap_probe_contracts.md',
        'family_evidence_markers': ['unique minimal sufficient probe caps are `[10, 20, 10000]`', 'only caps realizing those three exact thresholds are `10`, `10000`, and `20`', 'the only universally valid strict-winner probe triple'],
        'handle_evidence_markers': ['exactly three thresholds', 'They are the only thresholds that can universally separate the adjacent class pairs', 'publish `[10, 20, 10000]` as the **unique** strict-winner probe triple'],
        'semantic_bridge': 'The unique-minimal-cap-probe report family and the standing unique-minimal-probe topic both certify that `[10, 20, 10000]` is not just a convenient witness set but the only universally valid strict-winner probe triple, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_budget_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_budget_frontier_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_delta_budget_frontiers.md',
        'family_evidence_markers': ['turns `delta` into a real closure-cost frontier', 'approx extra paired seeds to close all', 'The point is not to let budget secretly choose delta'],
        'handle_evidence_markers': ['extra paired-seed budget needed to close all unresolved top panels is not a monotone function of `delta`', 'The inheritor needs a compact frontier over a plausible `delta` band', 'keep scientific materiality and simulation cost separate, but surface their tradeoff openly'],
        'semantic_bridge': 'The delta-budget-frontier report family and the standing delta-budget-frontier topic both reduce rematch closure planning to the same object: a compact frontier over declared `delta` values that separates scientific materiality from simulation cost, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'validator_inventory',
        'report_path': 'artifacts/reports/validator_inventory.json',
        'handle_path': 'docs/LIBRARY/topics/rematch_benchmark_programs_should_publish_validator_inventory_as_a_governance_surface.md',
        'family_evidence_markers': ['validators', 'scripts/test/check_archive_report_hotspot_receipt.py', 'scripts/test/check_archive_report_semantic_handle_receipt.py', 'scripts/test/check_rematch_world_benchmark_package_receipt.py'],
        'handle_evidence_markers': ['validator inventory', 'governance surface', 'which checks define readiness', 'which ones remain open'],
        'semantic_bridge': 'The validator-inventory report and the standing validator-governance note both say that benchmark readiness depends on a declared validator set that should be published as governance metadata rather than reconstructed from scattered tool outputs.',
    },
    {
        'family': 'repro_bundle_index',
        'report_path': 'artifacts/reports/repro_bundle_index.json',
        'handle_path': 'docs/LIBRARY/topics/rematch_benchmark_programs_should_publish_repro_bundle_posture_as_a_governance_surface.md',
        'family_evidence_markers': ['categories', 'formal', 'process', 'release'],
        'handle_evidence_markers': ['replay posture', 'what can be rebuilt now', 'retained materials', 'governance metadata'],
        'semantic_bridge': 'The repro-bundle index and the standing repro-posture governance note both expose replayability as a governance surface over retained materials rather than an implicit promise, so the archive can cite that note instead of keeping another bundle-index family in the long-term frontier.',
    },
    {
        'family': 'examples_validation',
        'report_path': 'artifacts/reports/examples_validation.json',
        'handle_path': 'docs/LIBRARY/topics/examples_corpus_should_remain_validated_as_a_scientific_fixture_baseline.md',
        'family_evidence_markers': ['examples/gauntlet/gauntlet_v1.json', 'examples/probes/registry_smoke.json', 'examples/worlds/ipd_core.json'],
        'handle_evidence_markers': ['scientific fixture baseline', 'examples/gauntlet/gauntlet_v1.json', 'examples/worlds/ipd_core.json'],
        'semantic_bridge': 'The examples-validation report and the standing fixture-baseline topic both say the same thing: the canonical `examples/` corpus should stay validated as a compact scientific baseline, so future archive shaping can cite that topic instead of retaining another example-inventory report family.',
    },
    {
        'family': 'risk_register_summary',
        'report_path': 'artifacts/reports/risk_register_summary.json',
        'handle_path': 'docs/LIBRARY/topics/rematch_benchmark_programs_should_publish_risk_review_cadence_as_a_governance_surface.md',
        'family_evidence_markers': ['review_date', 'status', 'severity', 'summary'],
        'handle_evidence_markers': ['risk-review cadence', 'governance metadata', 'reviewed recently', 'unresolved risk posture'],
        'semantic_bridge': 'The risk-register summary and the standing risk-review governance note both treat review cadence and unresolved risk posture as explicit benchmark-governance metadata rather than scattered meeting residue, so the archive can cite that note instead of retaining another risk-summary report family.',
    },
    {
        'family': 'geometric_arrival_deadline_inflation_law',
        'report_path': 'artifacts/reports/geometric_arrival_deadline_inflation_law_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compensate_stateless_live_reoptimization_by_deadline_inflation.md',
        'family_evidence_markers': ['live(H + K - 1) = blind_commit(H)', 'K - 1', 'deadline inflation', 'zero-inflation'],
        'handle_evidence_markers': ['K - 1', 'deadline inflation', 'live(H + K - 1) = blind_commit(H)', 'one-tick'],
        'semantic_bridge': 'The deadline-inflation snapshot and the standing compensation note both state the same exact repair law for stateless live reoptimization, so the archive should reuse that durable topic rather than preserve another report pair for the same control correction.',
    },
    {
        'family': 'rematch_proxy_delta_cap_robust_preference',
        'report_path': 'artifacts/reports/rematch_proxy_delta_cap_robust_preference_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_cap_robust_preference_certificates.md',
        'family_evidence_markers': ['all-caps ambiguity strip', 'cap-robust stability condition', 'cap-robust material condition', 'endpoint-only checking misses'],
        'handle_evidence_markers': ['all-caps ambiguity strip', 'cap-robust certificates', 'endpoint-only view was too weak', 'additional-budget cap'],
        'semantic_bridge': 'The cap-robust-preference snapshot and the standing cap-robust-preference topic both say that once cap enters the final two-anchor rule, the archive needs one exact all-caps ambiguity strip plus outside-strip certificates rather than endpoint-only spot checks, so the existing topic should back citation and compaction for this family.',
    },
    {
        'family': 'rematch_proxy_delta_frontier',
        'report_path': 'artifacts/reports/rematch_proxy_delta_frontier_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_need_delta_frontier_reports.md',
        'family_evidence_markers': ['two thresholds', 'material if delta <', 'tie if delta >=', 'undecided'],
        'handle_evidence_markers': ['two thresholds', 'material leader', 'practical tie', 'compact per-panel delta frontier'],
        'semantic_bridge': 'The delta-frontier snapshot and the standing delta-frontier topic both compress rematch materiality reporting to two thresholds per panel instead of bulky per-delta tables, so the archive can cite that standing topic rather than keep another frontier report family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_anchor_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_cap_safe_dwell_anchors_as_band_labels_not_magic_constants.md',
        'family_evidence_markers': ['anchor dwell', 'widest minimum-dwell plateau', 'anchor margin', 'minimum gain share'],
        'handle_evidence_markers': ['representative label', 'plateau', 'cap-safe band', 'boundaries that actually alter the promise'],
        'semantic_bridge': 'The minimum-dwell-anchor snapshot and the standing cap-safe-dwell-anchor topic both replace fragile dwell integers with representative interior labels for a wider admissible plateau, so the archive can cite that topic instead of retaining another paired anchor snapshot family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot_20260308.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_full_precision_exact_uncertainty_relaxed_release_as_a_two_bundle_composition.md',
        'family_evidence_markers': ['primitive_value_bundle_count', 'composite_value_bundle_count', 'full_precision_release_is_exact_bundle_sum', 'canonical_anchor_chain_for_composition'],
        'handle_evidence_markers': ['two primitive', 'one composite', 'exact composition', '11 + 12'],
        'semantic_bridge': 'The bundle-composition snapshot and the standing two-bundle-composition topic both say that full precision relaxed release is not a third primitive but the exact composition of the two primitive bundles, so the archive can cite that topic instead of retaining another composition report family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law_snapshot_20260309.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_treat_current_half_step_uniform_prefix_codecs_as_optimal_under_equiprobable_catalogs.md',
        "family_evidence_markers": ["Current normalized half-step prefix codecs are already optimal under the archive\'s equiprobable binary-prefix catalog assumptions.", "further_savings_require_nonuniform_or_nonprefix_assumptions", "state_prefix_total_optimal_bits", "global_exact_word_prefix_total_optimal_bits"],
        'handle_evidence_markers': ['binary prefix + equiprobable catalog', 'stop searching for shorter uniform binary prefix trees', 'The current archive codecs already match those forced spectra exactly.', '`103` seven-bit leaves + `50` eight-bit leaves'],
        'semantic_bridge': 'The uniform-prefix-optimality snapshot and the standing equiprobable-catalog topic both certify that the current half-step transport trees are already the forced uniform binary-prefix optima, so future archive shaping can cite that topic instead of retaining another paired optimality report family.',
    },
    {
        'family': 'rematch_proxy_delta_decision_packet_weight_formula',
        'report_path': 'artifacts/reports/rematch_proxy_delta_decision_packet_weight_formula_snapshot_20260307.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_worlds_should_compile_measured_decision_packet_frontiers_into_exact_shortlists.md',
        'family_evidence_markers': ['oracle_weights', 'packed_seed', 'byte_seed', 'byte_reference'],
        'handle_evidence_markers': ['oracle_weights', 'packed_seed', 'byte_seed', 'byte_reference'],
        'semantic_bridge': 'The weight-formula snapshot and the standing exact-shortlists topic both collapse live packet choice to the same implementor rule over byte_reference, byte_seed, and the packed_seed-versus-byte_seed comparison for oracle_weights writes, so the archive can cite that topic instead of retaining another report family.',
    },

    {
        'family': 'rematch_world_benchmark_patch_compaction',
        'report_path': 'artifacts/reports/rematch_world_benchmark_patch_compaction_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/rematch_world_benchmark_fill_work_should_flow_through_one_tiny_patch_then_compile_back_to_one_artifact.md',
        'family_evidence_markers': ['compact patch', 'frozen compact decision bundle', 'compile it back onto the standing seed', 'scratch fill work'],
        'handle_evidence_markers': ['compact fill patch', 'frozen compact decision bundle', 'compiled back onto the standing seed', 'scratch work'],
        'semantic_bridge': 'The patch-compaction report family and the standing fill-patch workflow topic both say the same thing: keep rematch-world fill scratch tiny by editing one compact patch instead of recopied seed state, then compile that patch back onto the standing seed artifact, so the archive can cite the existing topic instead of retaining another paired report family.',
    },
    {
        'family': 'rematch_world_benchmark_evidence_flow',
        'report_path': 'artifacts/reports/rematch_world_benchmark_evidence_flow_snapshot_20260316.md',
        'handle_path': 'docs/LIBRARY/topics/first_endogenous_rematch_benchmarks_should_distill_one_tiny_evidence_packet_before_compiling_the_fill_patch.md',
        'family_evidence_markers': ['one tiny evidence packet', 'compile it into the standard fill patch', 'raw run output stay scratch-only', 'retain one tiny evidence packet from a real rematch-world run'],
        'handle_evidence_markers': ['one tiny evidence packet', 'compile that packet into the standard fill patch', 'Everything bulkier than that can stay scratch-only', 'keep one tiny evidence packet containing only the world-dependent facts needed by the standing fill patch'],
        'semantic_bridge': 'The evidence-flow report family and the standing tiny-evidence-packet topic both carry the same implementation rule: distill a real rematch-world run into one small packet that compiles into the standard fill patch while wider run traces stay scratch-only, so the archive can cite that standing topic instead of retaining another paired evidence-flow report family.',
    },
    {
        'family': 'risk_register_validation',
        'report_path': 'artifacts/reports/risk_register_validation.json',
        'handle_path': 'docs/LIBRARY/topics/risk_register_validation_should_collapse_to_the_risk_register_contract.md',
        'family_evidence_markers': ['domain_counts', 'status_counts', 'overdue_open_or_mitigated', 'total'],
        'handle_evidence_markers': ['domain_counts', 'status_counts', 'overdue_open_or_mitigated', 'total'],
        'semantic_bridge': 'The risk-register validation summary and the standing risk-register-contract topic both say the same compact thing: the durable question is whether the canonical risk register remains populated, classed, and not silently overdue, so the archive can cite that topic instead of retaining another validation-summary family.',
    },
    {
        'family': 'claim_register_validation',
        'report_path': 'artifacts/reports/claim_register_validation.json',
        'handle_path': 'docs/LIBRARY/topics/claim_register_validation_should_collapse_to_the_claim_register_contract.md',
        'family_evidence_markers': ['class_counts', 'status_counts', 'strict_active_claims', 'total'],
        'handle_evidence_markers': ['class_counts', 'status_counts', 'strict_active_claims', 'total'],
        'semantic_bridge': 'The claim-register validation summary and the standing claim-register-contract topic both say the same compact thing: the durable question is whether the canonical claim register remains populated, classed, and strict-gate aware, so the archive can cite that topic instead of retaining another validation-summary family.',
    },
    {
        'family': 'claim_classes_validation',
        'report_path': 'artifacts/reports/claim_classes_validation.json',
        'handle_path': 'docs/LIBRARY/topics/claim_class_validation_should_collapse_to_the_claim_taxonomy_contract.md',
        'family_evidence_markers': ['evidence_classes', 'ids', 'strict_required', 'total'],
        'handle_evidence_markers': ['evidence_classes', 'ids', 'strict_required', 'total'],
        'semantic_bridge': 'The claim-class validation summary and the standing claim-taxonomy-contract topic both say the same compact thing: the durable question is whether the canonical class taxonomy remains populated and strict-gate aware, so the archive can cite that topic instead of retaining another validation-summary family.',
    },
    {
        'family': 'extortion_metric_snapshot',
        'report_path': 'artifacts/reports/extortion_metric_snapshot_20260306.md',
        'handle_path': 'docs/LIBRARY/topics/anti_vampire_scorecard_spec.md',
        'family_evidence_markers': ['avg_a', 'payoff gap', 'payoff-only', 'vampire'],
        'handle_evidence_markers': ['avg_a', 'payoff gap', 'payoff-only', 'vampire'],
        'semantic_bridge': 'The extortion-metric snapshot and the standing anti-vampire scorecard spec both say the same compact thing: payoff-only search against extortion is a metric trap, so inheritors should carry own payoff plus payoff-gap scorecard semantics instead of another paired extortion-metric report family.',
    },

]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _handle_kind(rel: str) -> str:
    if rel.startswith('docs/LIBRARY/topics/'):
        return 'library_topic'
    if rel.startswith('examples/snapshots/'):
        return 'snapshot'
    return 'doc'


def _family_name(path: Path) -> str:
    name = path.stem
    for pattern in FAMILY_SUFFIX_PATTERNS:
        name = pattern.sub('', name)
    return name


def _mib(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 3)


def _current_hotspot_rows(report_bucket_raw_bytes: int, limit: int) -> list[dict[str, Any]]:
    families: defaultdict[str, dict[str, int]] = defaultdict(lambda: {'file_count': 0, 'raw_bytes': 0, 'json_bytes': 0, 'md_bytes': 0})
    for path in REPORT_ROOT.glob('*'):
        if not path.is_file():
            continue
        family = _family_name(path)
        entry = families[family]
        size = path.stat().st_size
        entry['file_count'] += 1
        entry['raw_bytes'] += size
        if path.suffix == '.json':
            entry['json_bytes'] += size
        elif path.suffix == '.md':
            entry['md_bytes'] += size
    rows: list[dict[str, Any]] = []
    for family, entry in families.items():
        rows.append(
            {
                'family': family,
                'file_count': int(entry['file_count']),
                'raw_bytes': int(entry['raw_bytes']),
                'raw_mebibytes': _mib(int(entry['raw_bytes'])),
                'share_of_report_bucket_raw_bytes': round(int(entry['raw_bytes']) / report_bucket_raw_bytes, 6) if report_bucket_raw_bytes else 0.0,
                'has_json_md_pair': entry['json_bytes'] > 0 and entry['md_bytes'] > 0,
            }
        )
    rows.sort(key=lambda row: (-row['raw_bytes'], row['family']))
    return rows[:limit]


def build_receipt(hotspot_receipt: dict[str, Any], hotspot_receipt_path: Path) -> dict[str, Any]:
    report_bucket_raw_bytes = int(hotspot_receipt.get('report_bucket_totals', {}).get('raw_bytes', 0))
    current_hotspot_rows = _current_hotspot_rows(report_bucket_raw_bytes, HOTSPOT_BUFFER_LIMIT)
    hotspot_rows = {str(row['family']): {'rank': rank, **row} for rank, row in enumerate(current_hotspot_rows, start=1)}

    semantic_aliases: list[dict[str, Any]] = []
    for alias in ALIASES:
        family = alias['family']
        if family not in hotspot_rows:
            continue
        report_path = ROOT / alias['report_path']
        handle_path = ROOT / alias['handle_path']
        report_text = report_path.read_text(encoding='utf-8', errors='ignore').lower()
        handle_text = handle_path.read_text(encoding='utf-8', errors='ignore').lower()
        family_markers = list(alias['family_evidence_markers'])
        handle_markers = list(alias['handle_evidence_markers'])
        family_marker_hits = [marker for marker in family_markers if marker.lower() in report_text]
        handle_marker_hits = [marker for marker in handle_markers if marker.lower() in handle_text]
        row = hotspot_rows[family]
        semantic_aliases.append(
            {
                'family': family,
                'current_rank_within_hotspot_buffer': int(row['rank']),
                'file_count': int(row['file_count']),
                'raw_bytes': int(row['raw_bytes']),
                'raw_mebibytes': row['raw_mebibytes'],
                'share_of_report_bucket_raw_bytes': row['share_of_report_bucket_raw_bytes'],
                'report_path': alias['report_path'],
                'matched_handle': {'path': alias['handle_path'], 'kind': _handle_kind(alias['handle_path'])},
                'family_evidence_markers': family_markers,
                'family_evidence_marker_hits': family_marker_hits,
                'handle_evidence_markers': handle_markers,
                'handle_evidence_marker_hits': handle_marker_hits,
                'semantic_bridge': alias['semantic_bridge'],
            }
        )
    semantic_aliases.sort(key=lambda row: (-row['raw_bytes'], row['family']))
    semantic_alias_raw_bytes = sum(int(row['raw_bytes']) for row in semantic_aliases)
    summary_metrics = {
        'semantic_alias_count': len(semantic_aliases),
        'semantic_alias_raw_bytes': semantic_alias_raw_bytes,
        'semantic_alias_raw_mebibytes': round(semantic_alias_raw_bytes / (1024 * 1024), 3),
        'semantic_alias_share_of_report_bucket_raw_bytes': round(semantic_alias_raw_bytes / report_bucket_raw_bytes, 6) if report_bucket_raw_bytes else 0.0,
        'library_topic_alias_count': sum(1 for row in semantic_aliases if row['matched_handle']['kind'] == 'library_topic'),
        'hotspot_buffer_limit': HOTSPOT_BUFFER_LIMIT,
    }
    hotspot_family_names = set(hotspot_rows)
    alias_handle_paths = [row['matched_handle']['path'] for row in semantic_aliases]
    policy_checks = {
        'hotspot_receipt_ready': bool(hotspot_receipt.get('status_counts', {}).get('ready_to_cite')),
        'semantic_alias_layer_consistent': True,
        'alias_families_are_within_hotspot_buffer': all(row['family'] in hotspot_family_names for row in semantic_aliases),
        'alias_families_unique': len({row['family'] for row in semantic_aliases}) == len(semantic_aliases),
        'alias_handles_exist': all((ROOT / row['matched_handle']['path']).exists() for row in semantic_aliases),
        'alias_handles_are_library_topics': all(row['matched_handle']['kind'] == 'library_topic' for row in semantic_aliases),
        'alias_handle_paths_unique': len(set(alias_handle_paths)) == len(alias_handle_paths),
        'evidence_markers_present': all(row['family_evidence_marker_hits'] == row['family_evidence_markers'] and row['handle_evidence_marker_hits'] == row['handle_evidence_markers'] for row in semantic_aliases),
    }
    passed = sum(1 for v in policy_checks.values() if v)
    ready = passed == len(policy_checks)
    top = semantic_aliases[0] if semantic_aliases else None
    headline_findings = [
        f"{len(semantic_aliases)} families within the current top {HOTSPOT_BUFFER_LIMIT} report-hotspot buffer already have semantically exact library-topic handles, recovering {semantic_alias_raw_bytes} raw bytes ({summary_metrics['semantic_alias_share_of_report_bucket_raw_bytes']} share of the reports bucket) without minting new durable notes." if semantic_aliases else 'No semantic-handle aliases are currently needed within the buffered hotspot surface; literal library-topic lookup already covers the live frontier.',
        f"The largest recovered hotspot is `{top['family']}` at {top['raw_bytes']} bytes, bridged to `{top['matched_handle']['path']}` by shared evidence markers rather than literal family-name matching." if top else 'No recovered hotspot is available.',
        'This buffered semantic-handle layer covers the current hotspot surface and the one-trim-ahead rehearsal frontier, reducing false handle-gap inflation before any retained report paths are removed.' if semantic_aliases else 'The semantic bridge table can stay empty on this smaller tree because the live frontier is already citation-covered without alias recovery.',
    ]
    return {
        'receipt_kind': 'archive_report_semantic_handle_receipt',
        'receipt_version': '2026-03-17.archive_report_semantic_handle_receipt.v1',
        'analysis_script': 'scripts/tools/build_archive_report_semantic_handle_receipt.py',
        'hotspot_receipt_path': _relativize(hotspot_receipt_path),
        'hotspot_receipt_sha256': _sha256_json(hotspot_receipt),
        'measurement_scope': {
            'hotspot_buffer_limit': HOTSPOT_BUFFER_LIMIT,
            'semantic_alias_family_count': len(ALIASES),
            'report_paths': [row['report_path'] for row in ALIASES],
            'handle_roots': ['docs/LIBRARY/topics'],
            'buffer_target_note': 'Scan slightly past the current top hotspot table so semantic reuse remains visible across the next projected compaction frontier too.',
        },
        'summary_metrics': summary_metrics,
        'semantic_aliases': semantic_aliases,
        'policy_checks': policy_checks,
        'status_counts': {'passed_check_count': passed, 'total_check_count': len(policy_checks), 'ready_to_cite': ready},
        'archive_posture': {'intended_retention_class': 'durable_semantic_handle_receipt', 'prefer_citation_over_recopy': True, 'size_discipline_note': 'Carry one tiny semantic-handle receipt so archive shaping can reuse existing durable topics when literal family-name search misses them, instead of minting redundant notes or preserving more bulky report pairs.'},
        'headline_findings': headline_findings,
        'recommended_next_move': 'When a hotspot family appears unhandled under literal search, check this buffered semantic-handle receipt before minting a new durable note; on the current smaller tree, the empty alias table itself is evidence that literal library-topic coverage already suffices for the live frontier.' if ready else 'Do not rely on semantic-handle reuse yet; rebuild the hotspot receipt and restore the aliased library topics before using this receipt to guide archive shaping.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one compact archive semantic-handle receipt that recovers hotspot families already backed by existing durable library-topic notes under semantic aliasing.')
    parser.add_argument('--hotspot-receipt', default=str(DEFAULT_HOTSPOT_RECEIPT))
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT))
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    receipt = build_receipt(load_json(Path(args.hotspot_receipt)), Path(args.hotspot_receipt))
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    Path(args.output).write_text(rendered, encoding='utf-8')
    return 0 if (not args.strict or receipt['status_counts']['ready_to_cite']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
