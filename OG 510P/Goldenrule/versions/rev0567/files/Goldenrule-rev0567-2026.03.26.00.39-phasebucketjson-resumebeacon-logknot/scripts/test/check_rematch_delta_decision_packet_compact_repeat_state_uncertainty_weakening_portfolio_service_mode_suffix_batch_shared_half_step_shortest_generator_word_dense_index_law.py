#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_dense_index_law import (
    build_shortest_generator_word_dense_index_validation_summary,
)


def main() -> None:
    summary = build_shortest_generator_word_dense_index_validation_summary()
    assert summary['reachable_exact_feasible_interval_kernel_count'] == 153
    assert summary['represented_exact_shortest_generator_word_count'] == 513
    assert summary['maximum_exact_shortest_generator_word_dense_index'] == 512
    assert summary['dense_index_bit_width'] == 10
    assert summary['fixed_width_dense_state_and_local_choice_pair_bit_width'] == 13
    assert summary['fixed_width_bit_savings_vs_dense_state_and_local_choice_pair'] == 3
    assert math.isclose(summary['fixed_width_bit_savings_share_vs_dense_state_and_local_choice_pair'], 3 / 13)
    assert summary['dense_index_catalog_is_contiguous'] is True
    assert summary['exact_dense_index_word_roundtrip_count'] == 513
    assert summary['exact_dense_index_state_roundtrip_count'] == 513
    assert summary['exact_dense_index_choice_roundtrip_count'] == 513
    assert summary['canonical_choice_zero_dense_index_count'] == 153
    assert summary['identity_dense_index_range'] == [0, 0]
    assert summary['one_sided_dense_index_range'] == [1, 32]
    assert summary['interior_nonsingleton_dense_index_range'] == [33, 242]
    assert summary['interior_singleton_dense_index_range'] == [243, 512]
    assert summary['dense_index_zero_word'] == []
    assert summary['dense_index_max_word'] == [[0, 0], [15, 16]]
    assert summary['every_exact_shortest_generator_word_is_addressable_as_one_dense_scalar'] is True
    print('ok')


if __name__ == '__main__':
    main()
