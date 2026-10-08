#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_selector_index_law import (
    build_batch_mean_half_step_selector_index_examples,
    build_batch_mean_half_step_selector_index_validation_summary,
    build_service_mode_suffix_batch_mean_half_step_selector_index_snapshot,
    build_width_one_fingerprint,
    decode_half_step_selector_index,
    encode_selector_interval_as_half_step_selector_index,
    select_batch_mean_projection_witness_set_from_half_step_selector_index,
    summarize_preferred_state_codes_by_half_step_selector_index,
    summarize_reduced_mean_by_half_step_selector_index,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def _assert_close(actual: float, expected: float, message: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_half_step_selector_index_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_half_step_selector_index_snapshot()

    _assert_equal(validation['validated_realized_interval_count'], 153, 'validated interval count mismatch')
    _assert_equal(validation['validated_reduced_mean_class_count'], 161, 'validated reduced mean count mismatch')
    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'validated half-step class count mismatch')
    _assert_equal(validation['half_step_selector_index_range'], [0, 32], 'half-step index range mismatch')
    _assert_equal(validation['singleton_even_index_count'], 17, 'singleton even-index count mismatch')
    _assert_equal(validation['adjacent_tie_odd_index_count'], 16, 'adjacent tie odd-index count mismatch')
    _assert_equal(validation['reduced_mean_to_half_step_selector_index_validation_case_count'], 24633, 'validation case count mismatch')
    _assert_equal(validation['half_step_selector_index_matches_reduced_mean_selection'], True, 'reduced-mean selection mismatch')
    _assert_equal(validation['half_step_selector_index_matches_rational_bruteforce_l2_argmin'], True, 'bruteforce mismatch')
    _assert_equal(validation['one_integer_code_is_bijective_with_selector_interval_classes'], True, 'bijection mismatch')
    _assert_equal(validation['distinct_behavioral_signature_count_over_all_realized_intervals'], 33, 'full signature count mismatch')
    _assert_equal(validation['selector_classes_are_behaviorally_irreducible_over_all_realized_intervals'], True, 'irreducibility mismatch')
    _assert_equal(validation['adjacent_width_one_interval_count'], 16, 'adjacent interval count mismatch')
    _assert_equal(validation['distinct_behavioral_signature_count_over_adjacent_width_one_intervals'], 33, 'adjacent signature count mismatch')
    _assert_equal(validation['adjacent_width_one_intervals_form_a_complete_separating_family'], True, 'adjacent separation mismatch')
    _assert_equal(validation['adjacent_width_one_intervals_are_minimal_by_single_omission'], True, 'adjacent minimality mismatch')
    _assert_equal(validation['monotone_width_one_fingerprint_examples']['boundary_singleton_index_0'], 'LLLLLLLLLLLLLLLL', 'boundary singleton fingerprint mismatch')
    _assert_equal(validation['monotone_width_one_fingerprint_examples']['interior_singleton_index_14'], 'RRRRRRRLLLLLLLLL', 'interior singleton fingerprint mismatch')
    _assert_equal(validation['monotone_width_one_fingerprint_examples']['interior_tie_index_15'], 'RRRRRRRBLLLLLLLL', 'interior tie fingerprint mismatch')
    _assert_equal(validation['monotone_width_one_fingerprint_examples']['boundary_singleton_index_32'], 'RRRRRRRRRRRRRRRR', 'upper boundary fingerprint mismatch')

    _assert_equal(encode_selector_interval_as_half_step_selector_index(selector_lower_rank=0, selector_upper_rank=0), 0, 'encode boundary singleton mismatch')
    _assert_equal(encode_selector_interval_as_half_step_selector_index(selector_lower_rank=7, selector_upper_rank=8), 15, 'encode tie mismatch')
    _assert_equal(decode_half_step_selector_index(half_step_selector_index=0)['selector_interval_summary'], [0, 0], 'decode zero mismatch')
    _assert_equal(decode_half_step_selector_index(half_step_selector_index=15)['selector_interval_summary'], [7, 8], 'decode tie mismatch')
    _assert_equal(decode_half_step_selector_index(half_step_selector_index=32)['selector_interval_summary'], [16, 16], 'decode max mismatch')

    three_fifths = summarize_reduced_mean_by_half_step_selector_index(reduced_mean_numerator=3, reduced_mean_denominator=5)
    one = summarize_reduced_mean_by_half_step_selector_index(reduced_mean_numerator=1, reduced_mean_denominator=1)
    _assert_equal(three_fifths['half_step_selector_index'], 2, 'three-fifths index mismatch')
    _assert_equal(one['half_step_selector_index'], 2, 'one index mismatch')

    bundle = summarize_preferred_state_codes_by_half_step_selector_index(['S10', 'S10', 'S10', 'S10', 'S9'])
    _assert_equal(bundle['half_step_selector_index'], 0, 'bundle index mismatch')

    interval_1_3_family = [{'constraint_label': 'interval_1_3', 'state_code': 'S9', 'max_forward_steps': 2, 'max_backward_steps': 0}]
    clipped_tie = select_batch_mean_projection_witness_set_from_half_step_selector_index(
        interval_1_3_family,
        half_step_selector_index=1,
    )
    _assert_equal(clipped_tie['projected_optimal_state_codes'], ['S9'], 'clipped boundary tie mismatch')

    fingerprint = build_width_one_fingerprint(half_step_selector_index=15)
    _assert_equal(fingerprint['fingerprint_word'], 'RRRRRRRBLLLLLLLL', 'fingerprint word mismatch')
    _assert_equal(fingerprint['expected_monotone_word'], 'RRRRRRRBLLLLLLLL', 'expected fingerprint mismatch')

    examples = build_batch_mean_half_step_selector_index_examples()
    _assert_equal(examples[0]['shared_half_step_selector_index'], 0, 'shared boundary singleton index mismatch')
    _assert_equal(examples[0]['bundle_a_selection']['projected_optimal_state_codes'], ['S10'], 'bundle-a selection mismatch')
    _assert_equal(examples[0]['bundle_b_selection']['projected_optimal_state_codes'], ['S10'], 'bundle-b selection mismatch')
    _assert_equal(examples[1]['shared_half_step_selector_index'], 2, 'shared interior singleton index mismatch')
    _assert_equal(examples[1]['three_fifths_selection']['projected_optimal_state_codes'], ['S8'], 'three-fifths selection mismatch')
    _assert_equal(examples[1]['one_selection']['projected_optimal_state_codes'], ['S8'], 'one selection mismatch')
    _assert_equal(examples[2]['decoded_boundary_tie']['selector_interval_summary'], [0, 1], 'boundary tie decode example mismatch')
    _assert_equal(examples[2]['clipped_tie_selection']['projected_optimal_state_codes'], ['S9'], 'boundary tie selection example mismatch')
    _assert_equal(examples[3]['decoded_midpath_tie']['selector_interval_summary'], [7, 8], 'midpath tie decode mismatch')
    _assert_equal(examples[4]['selection_from_half_step_selector_index']['selection_status'], 'infeasible', 'infeasible example mismatch')

    _assert_equal(snapshot['headline_findings']['path_l2_selector_classes_can_be_keyed_by_one_half_step_integer'], 33, 'snapshot class count mismatch')

    print('ok')


if __name__ == '__main__':
    main()
