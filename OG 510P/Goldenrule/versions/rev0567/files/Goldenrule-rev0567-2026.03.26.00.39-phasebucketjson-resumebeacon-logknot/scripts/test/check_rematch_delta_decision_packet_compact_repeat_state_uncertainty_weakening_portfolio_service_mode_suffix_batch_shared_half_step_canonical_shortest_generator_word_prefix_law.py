#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_canonical_shortest_generator_word_prefix_law import (
    build_canonical_shortest_generator_word_prefix_validation_summary,
)


def main() -> None:
    summary = build_canonical_shortest_generator_word_prefix_validation_summary()
    assert summary['represented_canonical_shortest_generator_word_count'] == 153
    assert summary['exact_prefix_word_roundtrip_count'] == 153
    assert summary['exact_prefix_state_roundtrip_count'] == 153
    assert summary['exact_prefix_sequential_stream_roundtrip_count'] == 153
    assert summary['prefix_catalog_is_prefix_free'] is True
    assert summary['total_prefix_bits_over_canonical_catalog'] == 1121
    assert summary['global_exact_shortest_word_prefix_total_bits_over_canonical_catalog'] == 1377
    assert summary['fixed_width_exact_word_total_bits_over_canonical_catalog'] == 1530
    assert summary['fixed_width_state_dense_total_bits_over_canonical_catalog'] == 1224
    assert summary['saved_bits_vs_global_exact_word_prefix'] == 256
    assert summary['saved_bits_vs_fixed_width_exact_word'] == 409
    assert summary['saved_bits_vs_fixed_width_state_dense'] == 103
    assert math.isclose(summary['saved_bits_share_vs_global_exact_word_prefix'], 256 / 1377)
    assert math.isclose(summary['saved_bits_share_vs_fixed_width_exact_word'], 409 / 1530)
    assert math.isclose(summary['saved_bits_share_vs_fixed_width_state_dense'], 103 / 1224)
    assert math.isclose(summary['mean_prefix_bit_length'], 1121 / 153)
    assert math.isclose(summary['mean_bit_savings_vs_global_exact_word_prefix'], 256 / 153)
    assert math.isclose(summary['mean_bit_savings_vs_fixed_width_exact_word'], 409 / 153)
    assert math.isclose(summary['mean_bit_savings_vs_fixed_width_state_dense'], 103 / 153)
    assert math.isclose(summary['exact_uniform_entropy_lower_bound_bits'], math.log2(153))
    assert summary['global_exact_word_prefix_short_bit_length_on_canonical_subset'] == 9
    assert summary['every_canonical_shortest_generator_word_uses_nine_bits_under_the_global_exact_word_prefix'] is True
    assert summary['canonical_shortest_generator_word_prefix_is_exactly_the_existing_interval_state_prefix_codec'] is True
    assert summary['canonical_shortest_generator_word_prefix_requires_no_extra_script_only_block_beyond_interval_state_decode'] is True
    print('ok')


if __name__ == '__main__':
    main()
