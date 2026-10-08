#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_law import (
    build_batch_shared_half_step_shortest_generator_word_examples,
    build_batch_shared_half_step_shortest_generator_word_validation_summary,
    build_canonical_shortest_generator_word_for_feasible_interval_state,
    build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_snapshot,
    decode_shortest_generator_word_to_feasible_interval_state,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_shared_half_step_shortest_generator_word_validation_summary()
    snapshot = build_service_mode_suffix_batch_shared_half_step_shortest_generator_word_snapshot()

    _assert_equal(validation['reachable_exact_feasible_interval_kernel_count'], 153, 'reachable interval count mismatch')
    _assert_equal(validation['canonical_shortest_generator_word_length_spectrum'], {0: 1, 1: 32, 2: 120}, 'length spectrum mismatch')
    _assert_equal(validation['shortest_generator_word_multiplicity_spectrum'], {1: 33, 2: 105, 18: 15}, 'multiplicity spectrum mismatch')
    _assert_equal(validation['unique_shortest_generator_word_count'], 33, 'unique shortest count mismatch')
    _assert_equal(validation['two_shortest_generator_word_count'], 105, 'two-shortest count mismatch')
    _assert_equal(validation['eighteen_shortest_generator_word_count'], 15, 'eighteen-shortest count mismatch')
    _assert_equal(validation['represented_half_step_input_output_case_count'], 5049, 'selector-case count mismatch')
    _assert_equal(validation['canonical_shortest_generator_word_matches_shortest_depth_for_every_state'], True, 'shortest-depth mismatch')
    _assert_equal(validation['canonical_shortest_generator_word_is_always_one_of_the_shortest_words'], True, 'canonical-word membership mismatch')
    _assert_equal(validation['all_exact_interval_states_admit_a_shortest_generator_word_of_length_at_most_two'], True, 'depth-two bound mismatch')
    _assert_equal(validation['identity_interval_uses_only_the_empty_word'], True, 'identity empty-word mismatch')
    _assert_equal(validation['interior_singleton_intervals_have_uniform_shortest_word_multiplicity'], True, 'interior singleton multiplicity mismatch')
    _assert_equal(validation['interior_singleton_shortest_word_multiplicity'], 18, 'interior singleton multiplicity value mismatch')
    _assert_equal(
        validation['shortest_word_multiplicity_by_category'],
        {
            'identity': {1: 1},
            'interior_nonsingleton': {2: 105},
            'interior_singleton': {18: 15},
            'one_sided_nonidentity': {1: 32},
        },
        'multiplicity by category mismatch',
    )

    _assert_equal(build_canonical_shortest_generator_word_for_feasible_interval_state((0, 16)), (), 'identity canonical word mismatch')
    _assert_equal(build_canonical_shortest_generator_word_for_feasible_interval_state((4, 16)), ((4, 16),), 'floor canonical word mismatch')
    _assert_equal(build_canonical_shortest_generator_word_for_feasible_interval_state((0, 11)), ((0, 11),), 'cap canonical word mismatch')
    _assert_equal(build_canonical_shortest_generator_word_for_feasible_interval_state((3, 8)), ((3, 16), (0, 8)), 'interior canonical word mismatch')
    _assert_equal(build_canonical_shortest_generator_word_for_feasible_interval_state((5, 5)), ((5, 16), (0, 5)), 'singleton canonical word mismatch')
    _assert_equal(decode_shortest_generator_word_to_feasible_interval_state(((5, 16), (0, 5))), (5, 5), 'singleton decode mismatch')

    examples = build_batch_shared_half_step_shortest_generator_word_examples()
    _assert_equal(examples[0]['identity_interval_uses_the_empty_generator_word']['canonical_shortest_generator_word'], [], 'identity example mismatch')
    _assert_equal(examples[1]['one_sided_floor_interval_has_one_shortest_generator_word']['shortest_generator_word_count'], 1, 'floor example count mismatch')
    _assert_equal(examples[2]['one_sided_cap_interval_has_one_shortest_generator_word']['shortest_generator_word_count'], 1, 'cap example count mismatch')
    _assert_equal(
        examples[3]['interior_nonsingleton_interval_has_two_shortest_generator_words']['all_shortest_generator_words'],
        [[[0, 8], [3, 16]], [[3, 16], [0, 8]]],
        'interior example word set mismatch',
    )
    _assert_equal(examples[4]['interior_singleton_interval_has_eighteen_shortest_generator_words_but_one_canonical_choice']['shortest_generator_word_count'], 18, 'singleton example count mismatch')

    _assert_equal(
        snapshot['headline_findings']['every_exact_normalized_half_step_interval_state_has_a_canonical_shortest_generator_word'],
        True,
        'headline theorem mismatch',
    )


if __name__ == '__main__':
    main()
