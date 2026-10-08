#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_index_law import (
    build_shortest_generator_word_choice_validation_summary,
)


EXPECTED_LOCAL_CHOICE_COUNT_SPECTRUM = {1: 33, 2: 105, 18: 15}
EXPECTED_MAXIMUM_LOCAL_CHOICE_INDEX_SPECTRUM = {0: 33, 1: 105, 17: 15}
EXPECTED_LOCAL_CHOICE_BIT_WIDTH_SPECTRUM = {0: 33, 1: 105, 5: 15}
EXPECTED_TOTAL_STATE_BITS = 180
EXPECTED_TOTAL_WORD_BITS = 1560


def main() -> None:
    summary = build_shortest_generator_word_choice_validation_summary()
    assert summary['reachable_exact_feasible_interval_kernel_count'] == 153
    assert summary['represented_exact_shortest_word_count'] == 513
    assert summary['exact_word_roundtrip_count'] == 513
    assert summary['exact_choice_index_roundtrip_count'] == 513
    assert summary['maximum_local_choice_index'] == 17
    assert summary['local_choice_count_spectrum'] == EXPECTED_LOCAL_CHOICE_COUNT_SPECTRUM
    assert summary['maximum_local_choice_index_spectrum'] == EXPECTED_MAXIMUM_LOCAL_CHOICE_INDEX_SPECTRUM
    assert summary['local_choice_bit_width_spectrum'] == EXPECTED_LOCAL_CHOICE_BIT_WIDTH_SPECTRUM
    assert summary['canonical_choice_index_is_zero_for_every_state'] is True
    assert summary['all_choice_indices_decode_to_closed_form_shortest_words'] is True
    assert summary['all_closed_form_shortest_words_encode_to_unique_choice_indices'] is True
    assert summary['total_minimal_fixed_width_local_choice_bits_over_states'] == EXPECTED_TOTAL_STATE_BITS
    assert summary['total_minimal_fixed_width_local_choice_bits_over_exact_word_catalog'] == EXPECTED_TOTAL_WORD_BITS
    assert summary['represented_exact_shortest_word_catalog_is_addressable_without_search'] is True
    print('ok')


if __name__ == '__main__':
    main()
