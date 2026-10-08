#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_reduced_mean_law import (
    build_batch_mean_reduced_mean_examples,
    build_batch_mean_reduced_mean_validation_summary,
    build_service_mode_suffix_batch_mean_reduced_mean_snapshot,
    canonicalize_l2_summary_to_reduced_mean,
    select_batch_mean_projection_witness_set_from_reduced_mean,
    summarize_preferred_state_codes_by_canonical_l2_mean,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def _assert_close(actual: float, expected: float, message: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_reduced_mean_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_reduced_mean_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated interval count mismatch')
    _assert_equal(validation['validated_preference_bundle_widths'], [1, 2, 3, 4, 5], 'validated widths mismatch')
    _assert_equal(validation['validated_multiset_count'], 26333, 'validated multiset count mismatch')
    _assert_equal(validation['validated_two_integer_class_count'], 245, 'two-integer class count mismatch')
    _assert_equal(validation['validated_reduced_mean_class_count'], 161, 'reduced mean class count mismatch')
    _assert_equal(validation['reduced_mean_validation_case_count'], 24633, 'reduced mean case count mismatch')
    _assert_equal(validation['two_integer_comparison_case_count'], 37485, 'two-integer comparison count mismatch')
    _assert_close(validation['bundle_to_reduced_mean_reduction_factor'], 163.55900621118013, 'bundle reduction factor mismatch')
    _assert_close(validation['two_integer_to_reduced_mean_reduction_factor'], 1.5217391304347827, 'two-integer reduction factor mismatch')
    _assert_equal(validation['width_to_multiset_count'], {1: 17, 2: 153, 3: 969, 4: 4845, 5: 20349}, 'multiset count by width mismatch')
    _assert_equal(validation['width_to_two_integer_class_count'], {1: 17, 2: 33, 3: 49, 4: 65, 5: 81}, 'two-integer class count by width mismatch')
    _assert_equal(validation['width_to_reduced_mean_class_count'], {1: 17, 2: 33, 3: 49, 4: 65, 5: 81}, 'reduced-mean class count by width mismatch')
    _assert_equal(validation['width_to_new_canonical_mean_class_count'], {1: 17, 2: 16, 3: 32, 4: 32, 5: 64}, 'new canonical class count by width mismatch')
    _assert_equal(validation['cross_width_overlap_class_count'], 33, 'cross-width overlap count mismatch')
    _assert_equal(validation['cross_width_overlap_only_integer_or_half_integer'], True, 'overlap denominator mismatch')
    _assert_equal(validation['integer_overlap_class_count'], 17, 'integer overlap count mismatch')
    _assert_equal(validation['half_integer_overlap_class_count'], 16, 'half-integer overlap count mismatch')
    _assert_equal(validation['duplicate_width_specific_class_count_removed_by_canonicalization'], 84, 'duplicate removal mismatch')
    _assert_equal(validation['duplicate_width_specific_classes_exactly_explained_by_integer_and_half_integer_overlap'], True, 'duplicate explanation mismatch')
    _assert_equal(validation['reduced_mean_matches_rational_bruteforce_l2_argmin'], True, 'rational brute-force mismatch')
    _assert_equal(validation['reduced_mean_matches_two_integer_selection'], True, 'two-integer equivalence mismatch')
    _assert_equal(validation['infeasible_reduced_mean_selection_stays_blocked'], True, 'infeasible carry-forward mismatch')
    _assert_equal(validation['cross_width_overlap_examples']['integer_mean_3']['realizable_widths'], [1, 2, 3, 4, 5], 'integer overlap widths mismatch')
    _assert_equal(validation['cross_width_overlap_examples']['half_integer_mean_1_over_2']['realizable_widths'], [2, 4], 'half-integer overlap widths mismatch')
    _assert_equal(validation['cross_width_overlap_examples']['third_mean_1_over_3']['realizable_widths'], [3], 'third overlap widths mismatch')

    reduced = canonicalize_l2_summary_to_reduced_mean(preferred_count=4, preferred_rank_sum=12)
    _assert_equal(reduced['canonical_reduced_mean_summary'], [3, 1], 'canonical summary mismatch')

    bundle_summary = summarize_preferred_state_codes_by_canonical_l2_mean(['S10', 'S10', 'E5', 'E5'])
    _assert_equal(bundle_summary['compact_l2_summary'], [4, 12], 'two-int summary mismatch')
    _assert_equal(bundle_summary['canonical_reduced_mean_summary'], [3, 1], 'bundle canonical summary mismatch')

    source_relax6 = [{'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0}]
    half_step = select_batch_mean_projection_witness_set_from_reduced_mean(
        source_relax6,
        reduced_mean_numerator=1,
        reduced_mean_denominator=2,
    )
    _assert_equal(half_step['projected_optimal_state_codes'], ['S10', 'S9'], 'half-step tie mismatch')

    examples = build_batch_mean_reduced_mean_examples()
    _assert_equal(examples[0]['shared_reduced_mean_summary'], [1, 2], 'shared reduced mean mismatch')
    _assert_equal(examples[0]['width_two_selection']['projected_optimal_state_codes'], ['S10', 'S9'], 'width-two selection mismatch')
    _assert_equal(examples[0]['width_four_selection']['projected_optimal_state_codes'], ['S10', 'S9'], 'width-four selection mismatch')
    _assert_equal(examples[1]['selection_from_reduced_mean']['projected_optimal_state_codes'], ['S8'], 'feasible reduced-mean selection mismatch')
    _assert_equal(examples[2]['selection_from_reduced_mean']['selection_status'], 'infeasible', 'infeasible reduced-mean example mismatch')
    _assert_equal(snapshot['headline_findings']['validation_summary']['validated_reduced_mean_class_count'], 161, 'snapshot reduced mean count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
