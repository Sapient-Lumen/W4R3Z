#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_dense_index_law import (
    build_feasible_interval_state_dense_index_validation_summary,
)


def main() -> None:
    summary = build_feasible_interval_state_dense_index_validation_summary()
    assert summary['reachable_exact_feasible_interval_kernel_count'] == 153
    assert summary['maximum_feasible_interval_state_dense_index'] == 152
    assert summary['dense_index_bit_width'] == 8
    assert summary['raw_endpoint_pair_bit_width'] == 10
    assert summary['dense_index_bit_savings_vs_raw_endpoint_pair'] == 2
    assert math.isclose(summary['dense_index_bit_savings_share_vs_raw_endpoint_pair'], 0.2)
    assert summary['exact_dense_index_roundtrip_count'] == 153
    assert summary['exact_half_step_kernel_roundtrip_count'] == 153
    assert summary['exact_canonical_shortest_word_roundtrip_count'] == 153
    assert summary['dense_index_catalog_is_contiguous'] is True
    assert summary['dense_index_zero_state'] == [0, 0]
    assert summary['dense_index_max_state'] == [16, 16]
    assert math.isclose(summary['mean_local_choice_bit_width_once_dense_interval_index_is_known'], 180 / 153)
    assert summary['every_dense_interval_index_decodes_to_a_unique_exact_interval_kernel_state'] is True
    print('ok')


if __name__ == '__main__':
    main()
