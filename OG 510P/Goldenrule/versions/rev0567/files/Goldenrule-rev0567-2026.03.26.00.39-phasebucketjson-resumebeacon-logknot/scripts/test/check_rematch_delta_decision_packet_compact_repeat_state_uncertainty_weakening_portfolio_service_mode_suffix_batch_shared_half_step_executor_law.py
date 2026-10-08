#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law import (
    build_batch_shared_half_step_executor_examples,
    build_batch_shared_half_step_executor_validation_summary,
    build_service_mode_suffix_batch_shared_half_step_executor_snapshot,
    select_batch_shared_half_step_witness_set,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law import (
    select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law import (
    select_batch_minimax_projection_witness_set_from_half_step_selector_index,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_projection_law import (
    build_interval_realizer,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_executor_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_executor_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'realized interval count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'selector class count mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'selector range mismatch')
    _assert_equal(validation['validated_selection_case_count'], 5049, 'selection case count mismatch')
    _assert_equal(validation['shared_executor_validation_pair_count'], 10098, 'pair count mismatch')
    _assert_equal(validation['shared_executor_matches_path_l2_half_step_clamp_law'], True, 'L2 equivalence mismatch')
    _assert_equal(validation['shared_executor_matches_path_linf_half_step_selection_law'], True, 'Linf equivalence mismatch')
    _assert_equal(validation['distinct_projected_half_step_witness_index_count'], 33, 'output class count mismatch')
    _assert_equal(validation['projected_half_step_witness_index_range'], [0, 32], 'output range mismatch')
    _assert_equal(validation['preserve_within_band_case_count'], 1785, 'preserve count mismatch')
    _assert_equal(validation['clamp_up_to_lower_boundary_case_count'], 1904, 'lower clamp count mismatch')
    _assert_equal(validation['clamp_down_to_upper_boundary_case_count'], 1360, 'upper clamp count mismatch')
    _assert_equal(
        validation['path_l2_and_path_linf_share_the_same_feasible_executor_once_half_step_selector_index_is_fixed'],
        True,
        'shared executor theorem mismatch',
    )

    interval = [build_interval_realizer(0, 2)]
    shared = select_batch_shared_half_step_witness_set(interval, half_step_selector_index=3)
    path_l2 = select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(interval, half_step_selector_index=3)
    path_linf = select_batch_minimax_projection_witness_set_from_half_step_selector_index(interval, half_step_selector_index=3)
    _assert_equal(shared['projected_optimal_state_codes'], ['S9', 'E8'], 'direct shared executor output mismatch')
    _assert_equal(shared['projected_optimal_state_codes'], path_l2['projected_optimal_state_codes'], 'shared vs L2 mismatch')
    _assert_equal(shared['projected_optimal_state_codes'], path_linf['projected_optimal_state_codes'], 'shared vs Linf mismatch')

    examples = build_batch_shared_half_step_executor_examples()
    _assert_equal(examples[0]['same_half_step_index_from_distinct_semantics']['shared_half_step_selector_index'], 2, 'shared index example mismatch')
    _assert_equal(examples[0]['same_half_step_index_from_distinct_semantics']['shared_executor_selection']['projected_optimal_state_codes'], ['S9'], 'shared-semantic example mismatch')
    _assert_equal(examples[1]['same_low_boundary_collapse_for_both_semantics']['shared_executor_selection']['projected_half_step_witness_index'], 12, 'boundary clamp example mismatch')
    _assert_equal(examples[1]['same_low_boundary_collapse_for_both_semantics']['shared_executor_selection']['projected_optimal_state_codes'], ['E5'], 'boundary state code mismatch')
    _assert_equal(examples[2]['full_bundle_vs_endpoint_summary_inputs']['path_l2_bundle_selection']['projected_optimal_state_codes'], ['S9'], 'bundle-origin L2 example mismatch')
    _assert_equal(examples[2]['full_bundle_vs_endpoint_summary_inputs']['path_linf_bundle_selection']['projected_optimal_state_codes'], ['S9', 'E8'], 'bundle-origin Linf example mismatch')
    _assert_equal(examples[3]['infeasible_selection']['selection_status'], 'infeasible', 'infeasible example mismatch')

    _assert_equal(
        snapshot['headline_findings']['once_batch_compromise_is_encoded_as_one_half_step_selector_index_path_l2_and_path_linf_share_one_exact_feasible_executor'],
        True,
        'snapshot theorem mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
