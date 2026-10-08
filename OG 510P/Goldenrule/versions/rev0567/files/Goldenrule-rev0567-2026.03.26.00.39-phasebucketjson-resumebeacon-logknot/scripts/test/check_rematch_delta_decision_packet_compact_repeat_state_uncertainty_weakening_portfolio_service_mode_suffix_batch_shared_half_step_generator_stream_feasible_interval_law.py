#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law import (
    build_batch_shared_half_step_generator_stream_feasible_interval_examples,
    build_batch_shared_half_step_generator_stream_feasible_interval_validation_summary,
    build_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_snapshot,
    serialize_feasible_interval_kernel_state,
    update_feasible_interval_kernel_state,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_generator_stream_feasible_interval_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_snapshot()

    _assert_equal(validation['validated_distinct_one_sided_generator_interval_count'], 33, 'generator count mismatch')
    _assert_equal(validation['validated_one_sided_generator_stream_length_range'], [1, 4], 'length range mismatch')
    _assert_equal(validation['validated_ordered_one_sided_generator_stream_count'], 1222980, 'stream count mismatch')
    _assert_equal(validation['represented_half_step_input_output_case_count'], 40358340, 'case count mismatch')
    _assert_equal(validation['reachable_exact_feasible_interval_kernel_count'], 153, 'reachable interval count mismatch')
    _assert_equal(validation['reachable_singleton_interval_kernel_count'], 17, 'singleton count mismatch')
    _assert_equal(validation['reachable_nonsingleton_interval_kernel_count'], 136, 'nonsingleton count mismatch')
    _assert_equal(validation['reachable_exact_feasible_interval_kernels_match_realized_catalog'], True, 'catalog equivalence mismatch')
    _assert_equal(validation['every_reachable_exact_feasible_interval_kernel_matches_direct_composition'], True, 'direct composition mismatch')
    _assert_equal(validation['all_reachable_exact_feasible_interval_kernels_appear_by_depth_two'], True, 'depth-two coverage mismatch')
    _assert_equal(validation['normal_form_family_count_before_singleton_interval_quotient'], 170, 'normal-form family count mismatch')
    _assert_equal(validation['singleton_interval_quotient_removes_duplicate_constant_vs_singleton_pairs'], 17, 'quotient removal mismatch')
    _assert_equal(validation['every_previous_constant_normal_form_quotients_to_matching_singleton_interval'], True, 'quotient equivalence mismatch')
    _assert_equal(validation['singleton_interval_first_depth_spectrum'], {1: 2, 2: 15}, 'singleton depth spectrum mismatch')
    _assert_equal(validation['nonsingleton_interval_first_depth_spectrum'], {0: 1, 1: 30, 2: 105}, 'nonsingleton depth spectrum mismatch')
    _assert_equal(validation['nonsingleton_to_nonsingleton_generator_transition_count'], 2856, 'nonsingleton->nonsingleton transition mismatch')
    _assert_equal(validation['nonsingleton_to_singleton_generator_transition_count'], 1632, 'nonsingleton->singleton transition mismatch')
    _assert_equal(validation['singleton_to_singleton_generator_transition_count'], 561, 'singleton->singleton transition mismatch')
    _assert_equal(validation['singleton_to_nonsingleton_generator_transition_count'], 0, 'singleton->nonsingleton transition mismatch')
    _assert_equal(validation['singleton_intervals_are_absorbing_as_exact_kernels'], True, 'singleton absorption mismatch')

    floor_then_cap = ((1, 16), (0, 0))
    cap_then_floor = ((0, 0), (1, 16))
    state = (0, 16)
    for interval in floor_then_cap:
        state = update_feasible_interval_kernel_state(state, interval)
    _assert_equal(serialize_feasible_interval_kernel_state(state), {'interval': [0, 0], 'projected_half_step_witness_index_range': [0, 0], 'is_singleton_interval': True}, 'floor-then-cap singleton mismatch')

    state = (0, 16)
    for interval in cap_then_floor:
        state = update_feasible_interval_kernel_state(state, interval)
    _assert_equal(serialize_feasible_interval_kernel_state(state), {'interval': [1, 1], 'projected_half_step_witness_index_range': [2, 2], 'is_singleton_interval': True}, 'cap-then-floor singleton mismatch')

    examples = build_batch_shared_half_step_generator_stream_feasible_interval_examples()
    _assert_equal(examples[0]['feasible_stream_reduces_to_interval_kernel']['interval_kernel_state']['interval'], [3, 8], 'feasible example interval mismatch')
    _assert_equal(examples[1]['disjoint_floor_then_cap_stream_reduces_to_singleton_interval_kernel']['interval_kernel_state']['interval'], [0, 0], 'floor/cap example mismatch')
    _assert_equal(examples[2]['disjoint_cap_then_floor_stream_reduces_to_singleton_interval_kernel']['interval_kernel_state']['interval'], [1, 1], 'cap/floor example mismatch')
    _assert_equal(examples[3]['once_singleton_every_later_generator_keeps_the_stream_singleton']['interval_kernel_state']['interval'], [2, 2], 'singleton persistence example mismatch')

    _assert_equal(
        snapshot['headline_findings']['every_ordered_one_sided_generator_stream_reduces_exactly_to_one_feasible_interval_kernel'],
        True,
        'headline theorem mismatch',
    )


if __name__ == '__main__':
    main()
