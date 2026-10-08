#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_law import (
    build_batch_mean_half_step_threshold_fingerprint_examples,
    build_batch_mean_half_step_threshold_fingerprint_validation_summary,
    build_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_snapshot,
    classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold,
    decode_half_step_selector_index_from_monotone_fingerprint_word,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    validation = build_batch_mean_half_step_threshold_fingerprint_validation_summary()
    snapshot = build_service_mode_suffix_batch_mean_half_step_threshold_fingerprint_snapshot()

    _assert_equal(validation['validated_half_step_selector_index_class_count'], 33, 'class count mismatch')
    _assert_equal(validation['adjacent_width_one_interval_count'], 16, 'adjacent interval count mismatch')
    _assert_equal(validation['adjacent_midpoint_thresholds'], list(range(1, 32, 2)), 'threshold list mismatch')
    _assert_equal(validation['distinct_monotone_fingerprint_word_count'], 33, 'distinct word count mismatch')
    _assert_equal(validation['fingerprint_words_match_width_one_execution_fingerprints'], True, 'width-1 match mismatch')
    _assert_equal(validation['fingerprint_words_decode_back_to_half_step_selector_indices'], True, 'decode mismatch')
    _assert_equal(validation['fingerprint_word_alphabet'], ['L', 'B', 'R'], 'alphabet mismatch')
    _assert_equal(validation['singleton_word_count'], 17, 'singleton word count mismatch')
    _assert_equal(validation['tie_word_count'], 16, 'tie word count mismatch')
    _assert_equal(validation['max_leading_r_count'], 16, 'max leading R count mismatch')
    _assert_equal(validation['minimal_complete_separating_family_by_single_omission'], True, 'minimal omission mismatch')
    _assert_equal(validation['fingerprint_word_examples']['boundary_singleton_index_0'], 'LLLLLLLLLLLLLLLL', 'boundary fingerprint mismatch')
    _assert_equal(validation['fingerprint_word_examples']['interior_singleton_index_14'], 'RRRRRRRLLLLLLLLL', 'interior singleton fingerprint mismatch')
    _assert_equal(validation['fingerprint_word_examples']['interior_tie_index_15'], 'RRRRRRRBLLLLLLLL', 'interior tie fingerprint mismatch')
    _assert_equal(validation['fingerprint_word_examples']['boundary_singleton_index_32'], 'RRRRRRRRRRRRRRRR', 'upper boundary fingerprint mismatch')
    _assert_equal(validation['single_omission_signature_count_is_uniform'], True, 'uniform omission count mismatch')
    _assert_equal(validation['single_omission_signature_count'], 31, 'single omission signature count mismatch')
    _assert_equal(validation['distinct_signature_count_by_adjacent_interval_omission']['[0, 1]'], 31, 'first omission count mismatch')
    _assert_equal(validation['distinct_signature_count_by_adjacent_interval_omission']['[7, 8]'], 31, 'middle omission count mismatch')
    _assert_equal(validation['distinct_signature_count_by_adjacent_interval_omission']['[15, 16]'], 31, 'last omission count mismatch')

    _assert_equal(
        classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
            half_step_selector_index=14,
            midpoint_half_step_threshold=15,
        )['fingerprint_symbol'],
        'L',
        'below-midpoint classification mismatch',
    )
    _assert_equal(
        classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
            half_step_selector_index=15,
            midpoint_half_step_threshold=15,
        )['fingerprint_symbol'],
        'B',
        'at-midpoint classification mismatch',
    )
    _assert_equal(
        classify_half_step_selector_index_against_adjacent_interval_midpoint_threshold(
            half_step_selector_index=16,
            midpoint_half_step_threshold=15,
        )['fingerprint_symbol'],
        'R',
        'above-midpoint classification mismatch',
    )

    _assert_equal(
        decode_half_step_selector_index_from_monotone_fingerprint_word(
            fingerprint_word='LLLLLLLLLLLLLLLL'
        )['half_step_selector_index'],
        0,
        'decode all-L mismatch',
    )
    _assert_equal(
        decode_half_step_selector_index_from_monotone_fingerprint_word(
            fingerprint_word='RRRRRRRBLLLLLLLL'
        )['half_step_selector_index'],
        15,
        'decode interior tie mismatch',
    )
    _assert_equal(
        decode_half_step_selector_index_from_monotone_fingerprint_word(
            fingerprint_word='RRRRRRRRRRRRRRRR'
        )['half_step_selector_index'],
        32,
        'decode all-R mismatch',
    )

    examples = build_batch_mean_half_step_threshold_fingerprint_examples()
    _assert_equal(examples[0]['decoded_boundary_singleton']['selector_interval_summary'], [0, 0], 'boundary example mismatch')
    _assert_equal(examples[1]['decoded_interior_singleton']['selector_interval_summary'], [7, 7], 'interior singleton example mismatch')
    _assert_equal(examples[2]['decoded_interior_tie']['selector_interval_summary'], [7, 8], 'interior tie example mismatch')
    _assert_equal(examples[3]['decoded_top_singleton']['selector_interval_summary'], [16, 16], 'top singleton example mismatch')
    _assert_equal(examples[4]['threshold_example']['relation'], 'at_midpoint', 'threshold example mismatch')

    _assert_equal(
        snapshot['headline_findings']['path_l2_selector_classes_have_a_closed_form_adjacent_interval_fingerprint_word'],
        33,
        'snapshot word count mismatch',
    )

    print('ok')


if __name__ == '__main__':
    main()
