#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law import (
    apply_generator_stream_directly,
    build_batch_shared_half_step_generator_stream_counterexample,
    build_batch_shared_half_step_generator_stream_examples,
    build_batch_shared_half_step_generator_stream_normal_form_validation_summary,
    build_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_snapshot,
    build_stream_normal_form,
    serialize_stream_normal_form,
    update_stream_normal_form,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_generator_stream_normal_form_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_snapshot()
    counterexample = build_batch_shared_half_step_generator_stream_counterexample()

    _assert_equal(validation['validated_distinct_one_sided_generator_interval_count'], 33, 'generator interval count mismatch')
    _assert_equal(validation['validated_one_sided_generator_stream_length_range'], [1, 4], 'stream length range mismatch')
    _assert_equal(validation['validated_ordered_one_sided_generator_stream_count'], 1222980, 'stream count mismatch')
    _assert_equal(validation['represented_half_step_input_output_case_count'], 40358340, 'case count mismatch')
    _assert_equal(validation['reachable_normal_form_count'], 170, 'normal-form count mismatch')
    _assert_equal(validation['reachable_interval_normal_form_count'], 153, 'interval normal-form count mismatch')
    _assert_equal(validation['reachable_constant_normal_form_count'], 17, 'constant normal-form count mismatch')
    _assert_equal(validation['reachable_interval_normal_forms_match_realized_feasible_kernel_catalog'], True, 'interval catalog theorem mismatch')
    _assert_equal(validation['reachable_constant_normal_forms_cover_all_path_ranks'], True, 'constant rank coverage mismatch')
    _assert_equal(validation['every_reachable_normal_form_matches_direct_composition'], True, 'direct composition mismatch')
    _assert_equal(validation['normal_form_state_count_by_depth'], {1: 33, 2: 170, 3: 170, 4: 170}, 'depth state count mismatch')
    _assert_equal(validation['depth_interval_stream_count'], {1: 33, 2: 817, 3: 17985, 4: 371281}, 'depth interval stream count mismatch')
    _assert_equal(validation['depth_constant_stream_count'], {1: 0, 2: 272, 3: 17952, 4: 814640}, 'depth constant stream count mismatch')
    _assert_equal(validation['all_reachable_normal_forms_appear_by_depth_two'], True, 'depth-two reachability mismatch')
    _assert_equal(validation['interval_normal_form_first_depth_spectrum'], {1: 33, 2: 120}, 'interval first-depth spectrum mismatch')
    _assert_equal(validation['constant_normal_form_first_depth_spectrum'], {2: 17}, 'constant first-depth spectrum mismatch')
    _assert_equal(validation['constant_normal_forms_are_absorbing'], True, 'constant absorption mismatch')
    _assert_equal(validation['interval_to_interval_generator_transition_count'], 3417, 'interval-to-interval transition mismatch')
    _assert_equal(validation['interval_to_constant_generator_transition_count'], 1632, 'interval-to-constant transition mismatch')
    _assert_equal(validation['constant_to_constant_generator_transition_count'], 561, 'constant-to-constant transition mismatch')
    _assert_equal(validation['weaker_extrema_and_infeasible_latch_summary_is_not_exact'], True, 'weaker-summary counterexample mismatch')

    _assert_equal(
        counterexample['shared_weaker_summary'],
        {'max_floor_rank': 1, 'min_cap_rank': 0, 'infeasible_latch': True},
        'counterexample weaker summary mismatch',
    )
    _assert_equal(counterexample['floor_then_cap_normal_form']['constant_rank'], 0, 'floor-then-cap constant mismatch')
    _assert_equal(counterexample['cap_then_floor_normal_form']['constant_rank'], 1, 'cap-then-floor constant mismatch')
    _assert_equal(counterexample['floor_then_cap_direct_output_half_step_index'], 0, 'floor-then-cap output mismatch')
    _assert_equal(counterexample['cap_then_floor_direct_output_half_step_index'], 2, 'cap-then-floor output mismatch')

    feasible_stream = ((3, 16), (0, 8), (2, 16), (0, 10))
    feasible_state = build_stream_normal_form(feasible_stream)
    _assert_equal(feasible_state, ('interval', 3, 8), 'feasible stream normal form mismatch')
    _assert_equal(serialize_stream_normal_form(feasible_state)['projected_half_step_witness_index_range'], [6, 16], 'feasible range mismatch')

    collapsed_upper_stream = ((1, 16), (0, 0))
    collapsed_lower_stream = ((0, 0), (1, 16))
    _assert_equal(build_stream_normal_form(collapsed_upper_stream), ('constant', 0), 'collapsed upper mismatch')
    _assert_equal(build_stream_normal_form(collapsed_lower_stream), ('constant', 1), 'collapsed lower mismatch')
    _assert_equal(apply_generator_stream_directly(collapsed_upper_stream), (0,) * 33, 'collapsed upper direct kernel mismatch')
    _assert_equal(apply_generator_stream_directly(collapsed_lower_stream), (2,) * 33, 'collapsed lower direct kernel mismatch')

    absorbed = update_stream_normal_form(('constant', 1), (5, 16))
    absorbed = update_stream_normal_form(absorbed, (0, 2))
    _assert_equal(absorbed, ('constant', 2), 'absorbing constant update mismatch')

    examples = build_batch_shared_half_step_generator_stream_examples()
    _assert_equal(examples[0]['feasible_stream_reduces_to_one_interval_normal_form']['normal_form']['interval'], [3, 8], 'example feasible mismatch')
    _assert_equal(examples[1]['disjoint_floor_then_cap_stream_collapses_to_upper_constant']['normal_form']['constant_rank'], 0, 'example upper mismatch')
    _assert_equal(examples[2]['disjoint_cap_then_floor_stream_collapses_to_lower_constant']['normal_form']['constant_rank'], 1, 'example lower mismatch')
    _assert_equal(examples[3]['once_constant_every_further_generator_keeps_the_stream_constant']['normal_form']['constant_rank'], 2, 'example absorbing mismatch')

    _assert_equal(
        snapshot['headline_findings']['every_ordered_one_sided_generator_stream_reduces_exactly_to_one_interval_or_constant_normal_form'],
        True,
        'snapshot theorem mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
