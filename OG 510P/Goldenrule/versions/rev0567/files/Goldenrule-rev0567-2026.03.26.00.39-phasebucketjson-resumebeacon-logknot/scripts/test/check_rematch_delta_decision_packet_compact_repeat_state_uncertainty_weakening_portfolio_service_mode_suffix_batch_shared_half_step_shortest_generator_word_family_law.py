#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_law import (
    build_batch_shared_half_step_shortest_generator_word_family_examples,
    build_batch_shared_half_step_shortest_generator_word_family_validation_summary,
    build_closed_form_shortest_generator_words_for_feasible_interval_state,
    build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_snapshot,
    build_shortest_generator_word_family_cardinality_for_feasible_interval_state,
    classify_feasible_interval_state,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_shortest_generator_word_family_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_family_snapshot()

    _assert_equal(validation['reachable_exact_feasible_interval_kernel_count'], 153, 'reachable interval count mismatch')
    _assert_equal(validation['all_closed_form_shortest_word_families_match_bruteforce'], True, 'closed-form mismatch')
    _assert_equal(validation['all_shortest_word_family_cardinality_formulas_match'], True, 'cardinality formula mismatch')
    _assert_equal(validation['total_exact_shortest_generator_word_count'], 513, 'total shortest word count mismatch')
    _assert_equal(
        validation['state_count_by_interval_category'],
        {
            'identity': 1,
            'interior_nonsingleton': 105,
            'interior_singleton': 15,
            'one_sided_nonidentity': 32,
        },
        'state count by category mismatch',
    )
    _assert_equal(
        validation['total_shortest_generator_word_count_by_interval_category'],
        {
            'identity': 1,
            'interior_nonsingleton': 210,
            'interior_singleton': 270,
            'one_sided_nonidentity': 32,
        },
        'word count by category mismatch',
    )
    _assert_equal(
        validation['shortest_word_family_multiplicity_by_interval_category'],
        {
            'identity': {1: 1},
            'interior_nonsingleton': {2: 105},
            'interior_singleton': {18: 15},
            'one_sided_nonidentity': {1: 32},
        },
        'multiplicity by category mismatch',
    )
    _assert_equal(validation['interior_singleton_fan_split_is_exact'], True, 'singleton fan mismatch')
    _assert_equal(validation['interior_nonsingleton_words_are_exactly_the_two_orderings'], True, 'nonsingleton ordering mismatch')
    _assert_equal(
        validation['all_nontrivial_nonuniqueness_beyond_swapped_order_is_concentrated_in_interior_singletons'],
        True,
        'nontrivial multiplicity concentration mismatch',
    )
    if not math.isclose(validation['interior_singleton_share_of_total_shortest_words'], 270 / 513, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError('singleton share mismatch')

    _assert_equal(classify_feasible_interval_state((0, 16)), 'identity', 'identity category mismatch')
    _assert_equal(classify_feasible_interval_state((0, 0)), 'one_sided_nonidentity', 'endpoint singleton category mismatch')
    _assert_equal(classify_feasible_interval_state((3, 8)), 'interior_nonsingleton', 'interior category mismatch')
    _assert_equal(classify_feasible_interval_state((5, 5)), 'interior_singleton', 'singleton category mismatch')
    _assert_equal(build_shortest_generator_word_family_cardinality_for_feasible_interval_state((0, 16)), 1, 'identity cardinality mismatch')
    _assert_equal(build_shortest_generator_word_family_cardinality_for_feasible_interval_state((3, 8)), 2, 'interior cardinality mismatch')
    _assert_equal(build_shortest_generator_word_family_cardinality_for_feasible_interval_state((5, 5)), 18, 'singleton cardinality mismatch')
    _assert_equal(
        build_closed_form_shortest_generator_words_for_feasible_interval_state((3, 8)),
        (((0, 8), (3, 16)), ((3, 16), (0, 8))),
        'interior shortest-word family mismatch',
    )
    _assert_equal(
        build_closed_form_shortest_generator_words_for_feasible_interval_state((5, 5)),
        (
            ((0, 0), (5, 16)),
            ((0, 1), (5, 16)),
            ((0, 2), (5, 16)),
            ((0, 3), (5, 16)),
            ((0, 4), (5, 16)),
            ((0, 5), (5, 16)),
            ((5, 16), (0, 5)),
            ((6, 16), (0, 5)),
            ((7, 16), (0, 5)),
            ((8, 16), (0, 5)),
            ((9, 16), (0, 5)),
            ((10, 16), (0, 5)),
            ((11, 16), (0, 5)),
            ((12, 16), (0, 5)),
            ((13, 16), (0, 5)),
            ((14, 16), (0, 5)),
            ((15, 16), (0, 5)),
            ((16, 16), (0, 5)),
        ),
        'singleton shortest-word family mismatch',
    )

    examples = build_batch_shared_half_step_shortest_generator_word_family_examples()
    _assert_equal(examples[0]['identity_interval_has_the_unique_empty_shortest_word']['closed_form_shortest_generator_words'], [[]], 'identity example mismatch')
    _assert_equal(examples[1]['endpoint_singleton_is_still_one_sided_and_has_one_shortest_word']['category'], 'one_sided_nonidentity', 'endpoint example category mismatch')
    _assert_equal(
        examples[2]['interior_nonsingleton_interval_has_exactly_the_two_orderings_of_floor_and_cap']['closed_form_shortest_generator_words'],
        [[[0, 8], [3, 16]], [[3, 16], [0, 8]]],
        'interior example mismatch',
    )
    _assert_equal(examples[3]['interior_singleton_interval_splits_into_left_cap_and_right_floor_fans']['left_cap_fan_cardinality'], 6, 'singleton left fan mismatch')
    _assert_equal(examples[3]['interior_singleton_interval_splits_into_left_cap_and_right_floor_fans']['right_floor_fan_cardinality'], 12, 'singleton right fan mismatch')
    _assert_equal(examples[3]['interior_singleton_interval_splits_into_left_cap_and_right_floor_fans']['total_shortest_word_count'], 18, 'singleton total mismatch')

    _assert_equal(
        snapshot['headline_findings']['every_exact_shortest_half_step_generator_word_family_is_closed_form'],
        True,
        'headline theorem mismatch',
    )


if __name__ == '__main__':
    main()
