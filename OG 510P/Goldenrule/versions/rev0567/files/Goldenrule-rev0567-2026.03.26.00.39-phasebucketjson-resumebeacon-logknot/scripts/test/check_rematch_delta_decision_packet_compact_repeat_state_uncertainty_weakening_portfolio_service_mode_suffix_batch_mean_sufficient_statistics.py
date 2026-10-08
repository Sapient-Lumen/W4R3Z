#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_sufficient_statistic_law import (
    build_batch_mean_sufficient_statistic_examples,
    build_batch_mean_sufficient_statistic_validation_summary,
    build_service_mode_suffix_batch_mean_sufficient_statistic_snapshot,
    select_batch_mean_projection_witness_set_from_statistics,
    summarize_preferred_state_codes_for_l2,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def _assert_close(actual: float, expected: float, message: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_sufficient_statistic_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_sufficient_statistic_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated realized interval count mismatch')
    _assert_equal(validation['validated_preference_bundle_widths'], [1, 2, 3, 4, 5], 'validated widths mismatch')
    _assert_equal(validation['validated_multiset_count'], 26333, 'validated multiset count mismatch')
    _assert_equal(validation['validated_statistic_class_count'], 245, 'validated statistic class count mismatch')
    _assert_equal(validation['validation_case_count'], 4028949, 'validation case count mismatch')
    _assert_equal(validation['statistic_class_case_count'], 37485, 'statistic class case count mismatch')
    _assert_close(validation['class_reduction_factor'], 107.48163265306123, 'class reduction factor mismatch')
    _assert_equal(validation['width_to_multiset_count'], {1: 17, 2: 153, 3: 969, 4: 4845, 5: 20349}, 'multiset count by width mismatch')
    _assert_equal(validation['width_to_statistic_class_count'], {1: 17, 2: 33, 3: 49, 4: 65, 5: 81}, 'statistic class count by width mismatch')
    _assert_equal(validation['sufficient_statistics_match_bruteforce_l2_argmin'], True, 'bruteforce equivalence mismatch')
    _assert_equal(validation['sufficient_statistics_match_expanded_mean_selection'], True, 'expanded mean equivalence mismatch')
    _assert_equal(validation['compact_pair_strictly_smaller_count'], 26326, 'compact-pair smaller count mismatch')
    _assert_equal(validation['compact_pair_equal_count'], 7, 'compact-pair tie count mismatch')
    _assert_equal(validation['compact_pair_never_larger_than_expanded_bundle'], True, 'compact-pair dominance mismatch')
    _assert_equal(validation['width_to_compact_pair_smaller_count'], {1: 10, 2: 153, 3: 969, 4: 4845, 5: 20349}, 'compact-pair smaller count by width mismatch')
    _assert_equal(validation['infeasible_sufficient_statistic_selection_stays_blocked'], True, 'infeasible carry-forward mismatch')
    _assert_equal(validation['l1_needs_more_than_count_and_rank_sum'], True, 'l1 information-loss flag mismatch')
    _assert_equal(validation['l1_collision_example']['shared_statistics'], [4, 12], 'l1 collision stats mismatch')
    _assert_equal(validation['l1_collision_example']['bundle_a_l1_state_codes'], ['S10', 'S9', 'E8', 'S8', 'S7', 'S6', 'E5'], 'l1 collision bundle-a mismatch')
    _assert_equal(validation['l1_collision_example']['bundle_b_l1_state_codes'], ['S8'], 'l1 collision bundle-b mismatch')

    summary = summarize_preferred_state_codes_for_l2(['S10', 'S10', 'E5', 'E5'])
    _assert_equal(summary['compact_l2_summary'], [4, 12], 'compact summary mismatch')
    _assert_equal(summary['preferred_source_ranks'], [0, 0, 6, 6], 'preferred ranks mismatch')

    source_relax6 = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    l2_selection = select_batch_mean_projection_witness_set_from_statistics(source_relax6, preferred_count=4, preferred_rank_sum=12)
    _assert_equal(l2_selection['projected_optimal_state_codes'], ['S8'], 'statistics-based l2 selection mismatch')

    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    clamped = select_batch_mean_projection_witness_set_from_statistics(feasible_family, preferred_count=3, preferred_rank_sum=6)
    _assert_equal(clamped['projected_optimal_state_codes'], ['S8'], 'lower-bound clamp mismatch')
    _assert_equal(clamped['selection_certificate']['projection_case'], 'clamp_to_lower_boundary', 'projection case mismatch')

    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': 'S8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': 'S3', 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    infeasible = select_batch_mean_projection_witness_set_from_statistics(infeasible_family, preferred_count=3, preferred_rank_sum=22)
    _assert_equal(infeasible['selection_status'], 'infeasible', 'infeasible statistics selection mismatch')
    _assert_equal(infeasible['selection_certificate']['blocker_certificate']['gap_size_in_rank_units'], 9, 'infeasible gap mismatch')

    examples = build_batch_mean_sufficient_statistic_examples()
    _assert_equal(examples[1]['bundle_a_l2_selection']['projected_optimal_state_codes'], ['S8'], 'collision bundle-a l2 mismatch')
    _assert_equal(examples[1]['bundle_b_l2_selection']['projected_optimal_state_codes'], ['S8'], 'collision bundle-b l2 mismatch')
    _assert_equal(examples[1]['bundle_a_l1_selection']['projected_optimal_state_codes'], ['S10', 'S9', 'E8', 'S8', 'S7', 'S6', 'E5'], 'collision bundle-a l1 mismatch')
    _assert_equal(examples[1]['bundle_b_l1_selection']['projected_optimal_state_codes'], ['S8'], 'collision bundle-b l1 mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['validated_statistic_class_count'], 245, 'snapshot statistic class count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
