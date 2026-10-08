#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law import (
    build_shortest_generator_word_prefix_validation_summary,
)


def main() -> None:
    summary = build_shortest_generator_word_prefix_validation_summary()
    assert summary['represented_exact_shortest_generator_word_count'] == 513
    assert summary['short_prefix_bit_length'] == 9
    assert summary['long_prefix_bit_length'] == 10
    assert summary['short_prefix_code_count'] == 511
    assert summary['long_prefix_code_count'] == 2
    assert summary['long_prefix_dense_index_range'] == [511, 512]
    assert summary['exact_prefix_dense_index_roundtrip_count'] == 513
    assert summary['exact_prefix_word_roundtrip_count'] == 513
    assert summary['exact_prefix_state_roundtrip_count'] == 513
    assert summary['exact_prefix_choice_roundtrip_count'] == 513
    assert summary['exact_prefix_sequential_stream_roundtrip_count'] == 513
    assert summary['prefix_catalog_is_prefix_free'] is True
    assert summary['total_prefix_bits_over_exact_catalog'] == 4619
    assert summary['fixed_width_dense_index_total_bits_over_exact_catalog'] == 5130
    assert summary['saved_bits_vs_fixed_width_dense_index'] == 511
    assert math.isclose(summary['saved_bits_share_vs_fixed_width_dense_index'], 511 / 5130)
    assert math.isclose(summary['mean_prefix_bit_length'], 4619 / 513)
    assert math.isclose(summary['mean_bit_savings_vs_fixed_width_dense_index'], 511 / 513)
    assert math.isclose(summary['exact_uniform_entropy_lower_bound_bits'], math.log2(513))
    assert summary['canonical_long_prefix_words'] == [[[0, 1], [15, 16]], [[0, 0], [15, 16]]]
    assert summary['every_exact_shortest_generator_word_is_streamable_as_a_prefix_code_over_the_existing_dense_index'] is True
    print('ok')


if __name__ == '__main__':
    main()
