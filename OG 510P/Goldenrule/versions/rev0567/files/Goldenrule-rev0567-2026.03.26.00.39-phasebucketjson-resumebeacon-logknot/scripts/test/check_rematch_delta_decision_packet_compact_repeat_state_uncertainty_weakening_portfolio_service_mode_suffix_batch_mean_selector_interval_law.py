#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_selector_interval_law import (
    build_batch_mean_selector_interval_examples,
    build_batch_mean_selector_interval_validation_summary,
    build_service_mode_suffix_batch_mean_selector_interval_snapshot,
    select_batch_mean_projection_witness_set_from_selector_interval,
    summarize_l2_statistics_by_selector_interval,
    summarize_preferred_state_codes_by_l2_selector_interval,
    summarize_reduced_mean_by_selector_interval,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def _assert_close(actual: float, expected: float, message: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_selector_interval_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_selector_interval_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated interval count mismatch')
    _assert_equal(validation['validated_preference_bundle_widths'], [1, 2, 3, 4, 5], 'validated widths mismatch')
    _assert_equal(validation['validated_multiset_count'], 26333, 'validated multiset count mismatch')
    _assert_equal(validation['validated_reduced_mean_class_count'], 161, 'validated reduced mean count mismatch')
    _assert_equal(validation['validated_selector_interval_class_count'], 33, 'validated selector interval count mismatch')
    _assert_equal(validation['selector_interval_validation_case_count'], 24633, 'selector interval case count mismatch')
    _assert_close(validation['bundle_to_selector_interval_reduction_factor'], 797.969696969697, 'bundle reduction factor mismatch')
    _assert_close(validation['reduced_mean_to_selector_interval_reduction_factor'], 4.878787878787879, 'reduced-mean reduction factor mismatch')
    _assert_equal(validation['width_to_multiset_count'], {1: 17, 2: 153, 3: 969, 4: 4845, 5: 20349}, 'multiset count by width mismatch')
    _assert_equal(validation['width_to_reduced_mean_class_count'], {1: 17, 2: 33, 3: 49, 4: 65, 5: 81}, 'reduced-mean count by width mismatch')
    _assert_equal(validation['width_to_selector_interval_class_count'], {1: 17, 2: 33, 3: 17, 4: 33, 5: 17}, 'selector interval count by width mismatch')
    _assert_equal(validation['singleton_selector_class_count'], 17, 'singleton selector count mismatch')
    _assert_equal(validation['adjacent_tie_selector_class_count'], 16, 'adjacent tie selector count mismatch')
    _assert_equal(validation['every_selector_class_is_cross_width_shared'], True, 'cross-width sharing mismatch')
    _assert_equal(validation['singleton_selector_classes_realizable_widths'], [1, 2, 3, 4, 5], 'singleton widths mismatch')
    _assert_equal(validation['adjacent_tie_selector_classes_realizable_widths'], [2, 4], 'tie widths mismatch')
    _assert_equal(validation['boundary_singleton_selector_mean_class_count'], 5, 'boundary singleton collapse mismatch')
    _assert_equal(validation['interior_singleton_selector_mean_class_count'], 9, 'interior singleton collapse mismatch')
    _assert_equal(validation['tie_selector_mean_class_count'], 1, 'tie selector collapse mismatch')
    _assert_equal(validation['selector_projection_matches_reduced_mean_selection'], True, 'selector/reduced mean mismatch')
    _assert_equal(validation['selector_projection_matches_rational_bruteforce_l2_argmin'], True, 'selector/bruteforce mismatch')
    _assert_equal(validation['infeasible_selector_interval_selection_stays_blocked'], True, 'infeasible carry-forward mismatch')
    _assert_equal(validation['example_selector_classes']['boundary_singleton_rank_0']['collapsed_reduced_mean_class_count'], 5, 'boundary example collapse mismatch')
    _assert_equal(validation['example_selector_classes']['interior_singleton_rank_1']['collapsed_reduced_mean_class_count'], 9, 'interior example collapse mismatch')
    _assert_equal(validation['example_selector_classes']['adjacent_tie_rank_0_1']['collapsed_reduced_mean_class_count'], 1, 'tie example collapse mismatch')

    selector = summarize_reduced_mean_by_selector_interval(reduced_mean_numerator=3, reduced_mean_denominator=5)
    _assert_equal(selector['selector_interval_summary'], [1, 1], 'reduced mean selector mismatch')

    stats_selector = summarize_l2_statistics_by_selector_interval(preferred_count=5, preferred_rank_sum=3)
    _assert_equal(stats_selector['selector_interval_summary'], [1, 1], 'statistics selector mismatch')

    bundle_selector = summarize_preferred_state_codes_by_l2_selector_interval(['S10', 'S10', 'S10', 'S10', 'S9'])
    _assert_equal(bundle_selector['selector_interval_summary'], [0, 0], 'bundle selector mismatch')

    interval_1_3_family = [{'constraint_label': 'interval_1_3', 'state_code': 'S9', 'max_forward_steps': 2, 'max_backward_steps': 0}]
    clipped_tie = select_batch_mean_projection_witness_set_from_selector_interval(
        interval_1_3_family,
        selector_lower_rank=0,
        selector_upper_rank=1,
    )
    _assert_equal(clipped_tie['projected_optimal_state_codes'], ['S9'], 'clipped tie mismatch')

    examples = build_batch_mean_selector_interval_examples()
    _assert_equal(examples[0]['shared_selector_interval_summary'], [0, 0], 'shared singleton selector mismatch')
    _assert_equal(examples[0]['bundle_a_selection']['projected_optimal_state_codes'], ['S10'], 'bundle-a selector selection mismatch')
    _assert_equal(examples[0]['bundle_b_selection']['projected_optimal_state_codes'], ['S10'], 'bundle-b selector selection mismatch')
    _assert_equal(examples[1]['shared_selector_interval_summary'], [1, 1], 'shared interior selector mismatch')
    _assert_equal(examples[1]['three_fifths_selection']['projected_optimal_state_codes'], ['S8'], 'three-fifths selector selection mismatch')
    _assert_equal(examples[1]['one_selection']['projected_optimal_state_codes'], ['S8'], 'one selector selection mismatch')
    _assert_equal(examples[2]['clipped_tie_selection']['projected_optimal_state_codes'], ['S9'], 'clipped selector tie example mismatch')
    _assert_equal(examples[3]['selection_from_selector_interval']['selection_status'], 'infeasible', 'infeasible selector example mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['validated_selector_interval_class_count'], 33, 'snapshot selector interval count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
