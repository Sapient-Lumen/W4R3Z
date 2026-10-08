#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law import (
    build_shortest_generator_word_choice_prefix_validation_summary,
)

EXPECTED_BIT_LENGTH_SPECTRUM = {0: 33, 1: 210, 4: 210, 5: 60}
EXPECTED_STATE_CATEGORY_SPECTRUM = {
    'interior_nonsingleton': {1: 210},
    'interior_singleton': {4: 210, 5: 60},
    'unique_state': {0: 33},
}
EXPECTED_STATE_LOCAL_TOTAL_BITS_SPECTRUM = {0: 33, 2: 105, 76: 15}
EXPECTED_TOTAL_PREFIX_BITS = 1350
EXPECTED_TOTAL_FIXED_WIDTH_BITS = 1560
EXPECTED_WEIGHTED_STATE_PREFIX_BITS = 3809
EXPECTED_COMBINED_TOTAL_BITS = 5159


def main() -> None:
    summary = build_shortest_generator_word_choice_prefix_validation_summary()
    assert summary['reachable_exact_feasible_interval_kernel_count'] == 153
    assert summary['represented_exact_shortest_word_count'] == 513
    assert summary['exact_choice_index_roundtrip_count'] == 513
    assert summary['exact_word_roundtrip_count'] == 513
    assert summary['exact_state_roundtrip_count'] == 513
    assert summary['exact_choice_prefix_sequential_stream_roundtrip_count'] == 513
    assert summary['all_state_local_choice_prefix_families_are_prefix_free'] is True
    assert summary['canonical_choice_index_is_zero_for_every_state'] is True
    assert summary['interior_singleton_short_prefix_count'] == 14
    assert summary['interior_singleton_long_prefix_count'] == 4
    assert summary['interior_singleton_short_prefix_bit_length'] == 4
    assert summary['interior_singleton_long_prefix_bit_length'] == 5
    assert summary['choice_prefix_bit_length_spectrum_over_exact_words'] == EXPECTED_BIT_LENGTH_SPECTRUM
    assert summary['choice_prefix_bit_length_spectrum_by_state_category'] == EXPECTED_STATE_CATEGORY_SPECTRUM
    assert summary['state_local_choice_family_total_prefix_bits_spectrum'] == EXPECTED_STATE_LOCAL_TOTAL_BITS_SPECTRUM
    assert summary['total_choice_prefix_bits_over_exact_word_catalog'] == EXPECTED_TOTAL_PREFIX_BITS
    assert summary['total_fixed_width_choice_index_bits_over_exact_word_catalog'] == EXPECTED_TOTAL_FIXED_WIDTH_BITS
    assert summary['saved_bits_vs_fixed_width_choice_indices_over_exact_word_catalog'] == 210
    assert summary['weighted_state_prefix_bits_over_exact_word_catalog'] == EXPECTED_WEIGHTED_STATE_PREFIX_BITS
    assert summary['combined_state_prefix_plus_choice_prefix_total_bits_over_exact_word_catalog'] == EXPECTED_COMBINED_TOTAL_BITS
    assert summary['state_known_local_choice_prefix_is_strictly_smaller_than_global_exact_word_prefix'] is True
    assert summary['state_prefix_plus_choice_prefix_is_strictly_larger_than_global_exact_word_prefix'] is True
    assert summary['represented_exact_shortest_word_catalog_is_streamable_without_search_once_interval_state_is_known'] is True
    print('ok')


if __name__ == '__main__':
    main()
