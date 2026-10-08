#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_uniform_prefix_optimality_law import (
    build_uniform_prefix_optimality_summary,
)


def main() -> None:
    summary = build_uniform_prefix_optimality_summary()
    assert summary['state_prefix_is_uniform_prefix_optimal'] is True
    assert summary['global_exact_word_prefix_is_uniform_prefix_optimal'] is True
    assert summary['state_known_local_choice_prefix_is_familywise_uniform_prefix_optimal'] is True
    assert summary['canonical_shortest_word_prefix_inherits_uniform_prefix_optimality_from_state_prefix'] is True
    assert summary['no_current_uniform_binary_prefix_catalog_can_lose_one_bit_without_leaving_the_prefix_or_equiprobable_regime'] is True

    assert summary['state_prefix_optimal_length_spectrum'] == {7: 103, 8: 50}
    assert summary['state_prefix_total_optimal_bits'] == 1121
    assert summary['global_exact_word_prefix_optimal_length_spectrum'] == {9: 511, 10: 2}
    assert summary['global_exact_word_prefix_total_optimal_bits'] == 4619
    assert summary['state_known_local_choice_optimal_total_bits'] == 1350

    profiles = summary['local_choice_family_optimal_profiles']
    assert profiles['unique_state']['family_count'] == 33
    assert profiles['unique_state']['family_size'] == 1
    assert profiles['unique_state']['optimal_length_spectrum_per_family'] == {0: 1}
    assert profiles['unique_state']['optimal_total_bits_per_family'] == 0

    assert profiles['interior_nonsingleton']['family_count'] == 105
    assert profiles['interior_nonsingleton']['family_size'] == 2
    assert profiles['interior_nonsingleton']['optimal_length_spectrum_per_family'] == {1: 2}
    assert profiles['interior_nonsingleton']['optimal_total_bits_per_family'] == 2

    assert profiles['interior_singleton']['family_count'] == 15
    assert profiles['interior_singleton']['family_size'] == 18
    assert profiles['interior_singleton']['optimal_length_spectrum_per_family'] == {4: 14, 5: 4}
    assert profiles['interior_singleton']['optimal_total_bits_per_family'] == 76

    assert math.isclose(summary['state_prefix_entropy_gap_bits_over_uniform_bound'], 1121 - 153 * math.log2(153))
    assert math.isclose(summary['global_exact_word_prefix_entropy_gap_bits_over_uniform_bound'], 4619 - 513 * math.log2(513))
    assert math.isclose(summary['interior_singleton_choice_entropy_gap_bits_per_family'], 76 - 18 * math.log2(18))

    print('ok')


if __name__ == '__main__':
    main()
