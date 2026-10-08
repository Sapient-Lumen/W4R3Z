#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_law import (
    build_batch_mean_half_step_feasible_band_clamp_examples,
    build_batch_mean_half_step_feasible_band_clamp_validation_summary,
    build_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_snapshot,
    clamp_half_step_selector_index_to_doubled_feasible_band,
    select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')



def main() -> None:
    validation = build_batch_mean_half_step_feasible_band_clamp_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_half_step_feasible_band_clamp_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated interval count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'selector class count mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'selector index range mismatch')
    _assert_equal(validation['validated_selection_case_count'], 5049, 'validation case count mismatch')
    _assert_equal(validation['clamp_formula_matches_selector_interval_projection'], True, 'clamp formula mismatch')
    _assert_equal(validation['projected_half_step_witness_indices_share_the_same_33_class_lattice'], True, 'shared lattice mismatch')
    _assert_equal(validation['distinct_projected_half_step_witness_index_count'], 33, 'projected index count mismatch')
    _assert_equal(validation['projected_half_step_witness_index_range'], [0, 32], 'projected index range mismatch')
    _assert_equal(validation['preserve_within_band_case_count'], 1785, 'preserve count mismatch')
    _assert_equal(validation['clamp_up_to_lower_boundary_case_count'], 1904, 'lower-bound clamp count mismatch')
    _assert_equal(validation['clamp_down_to_upper_boundary_case_count'], 1360, 'upper-bound clamp count mismatch')

    boundary = clamp_half_step_selector_index_to_doubled_feasible_band(
        half_step_selector_index=1,
        feasible_lower_rank=1,
        feasible_upper_rank=3,
    )
    _assert_equal(boundary['projected_half_step_witness_index'], 2, 'boundary clamp index mismatch')
    _assert_equal(boundary['clamp_case'], 'clamp_up_to_lower_boundary', 'boundary clamp case mismatch')
    _assert_equal(boundary['projected_optimal_state_codes'], ['S9'], 'boundary clamp state mismatch')

    preserved = clamp_half_step_selector_index_to_doubled_feasible_band(
        half_step_selector_index=15,
        feasible_lower_rank=6,
        feasible_upper_rank=9,
    )
    _assert_equal(preserved['projected_half_step_witness_index'], 15, 'preserve index mismatch')
    _assert_equal(preserved['clamp_case'], 'preserve_within_band', 'preserve clamp case mismatch')
    _assert_equal(preserved['projected_optimal_state_codes'], ['S5', 'S4'], 'preserve state mismatch')

    upper = clamp_half_step_selector_index_to_doubled_feasible_band(
        half_step_selector_index=27,
        feasible_lower_rank=4,
        feasible_upper_rank=11,
    )
    _assert_equal(upper['projected_half_step_witness_index'], 22, 'upper clamp index mismatch')
    _assert_equal(upper['clamp_case'], 'clamp_down_to_upper_boundary', 'upper clamp case mismatch')
    _assert_equal(upper['projected_optimal_state_codes'], ['D2'], 'upper clamp state mismatch')

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_batch_mean_projection_witness_set_from_half_step_feasible_band_clamp(
        infeasible_family,
        half_step_selector_index=15,
    )
    _assert_equal(infeasible['selection_status'], 'infeasible', 'infeasible status mismatch')
    _assert_equal(infeasible['projected_half_step_witness_index'], None, 'infeasible index mismatch')

    examples = build_batch_mean_half_step_feasible_band_clamp_examples()
    _assert_equal(examples[0]['interval_1_3_selection']['projected_half_step_witness_index'], 2, 'example 0 index mismatch')
    _assert_equal(examples[1]['interval_6_9_selection']['projected_half_step_witness_index'], 15, 'example 1 index mismatch')
    _assert_equal(examples[2]['interval_4_11_selection']['projected_half_step_witness_index'], 22, 'example 2 index mismatch')
    _assert_equal(examples[3]['interval_6_9_output_indices'], [12, 12, 12], 'example 3 collapse mismatch')
    _assert_equal(examples[4]['infeasible_selection']['selection_status'], 'infeasible', 'example 4 infeasible mismatch')

    _assert_equal(
        snapshot['headline_findings']['path_l2_witness_choice_is_a_one_integer_clamp_over_the_half_step_lattice'],
        True,
        'snapshot clamp headline mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
