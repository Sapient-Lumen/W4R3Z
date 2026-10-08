#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_script_transport_frontier_law import (
    build_canonical_choice_prefix_summary,
    build_shortest_script_transport_regime_frontier_summary,
    recommend_shortest_script_transport,
)


def main() -> None:
    canonical_choice = build_canonical_choice_prefix_summary()
    assert canonical_choice['represented_canonical_shortest_generator_word_count'] == 153
    assert canonical_choice['exact_roundtrip_count'] == 153
    assert canonical_choice['total_choice_prefix_bits_over_canonical_catalog'] == 165
    assert math.isclose(canonical_choice['mean_choice_prefix_bit_length_over_canonical_catalog'], 165 / 153)
    assert canonical_choice['choice_prefix_bit_length_spectrum_over_canonical_catalog'] == {0: 33, 1: 105, 4: 15}
    assert canonical_choice['canonical_shortest_generator_word_is_zero_choice_branch_but_not_zero_prefix_branch'] is True

    summary = build_shortest_script_transport_regime_frontier_summary()
    assert summary['frontier_regime_count'] == 4
    assert summary['nonzero_frontier_codec_count'] == 3
    assert summary['global_exact_shortest_word_prefix_is_optimal_only_when_state_is_unknown_and_exact_branch_must_survive'] is True
    assert summary['state_conditional_choice_prefix_is_optimal_only_when_state_is_known_and_exact_branch_must_survive'] is True
    assert summary['interval_state_prefix_is_optimal_for_standalone_canonical_shortest_script_transport'] is True
    assert summary['zero_bit_reconstruction_is_optimal_for_state_known_canonical_shortest_script_transport'] is True

    regimes = summary['regimes']
    assert regimes['standalone_canonical_shortest_script']['recommended_transport'] == 'interval_state_prefix'
    assert regimes['state_known_canonical_shortest_script']['recommended_transport'] == 'zero_bit_canonical_reconstruction_from_state'
    assert regimes['standalone_exact_shortest_script']['recommended_transport'] == 'global_exact_shortest_word_prefix'
    assert regimes['state_known_exact_shortest_script']['recommended_transport'] == 'state_conditional_choice_prefix'

    standalone_canonical = summary['dominance_checks']['standalone_canonical_shortest_script']
    assert standalone_canonical['recommended_total_bits'] == 1121
    assert standalone_canonical['best_alternative_transport'] == 'interval_state_dense_fixed_width'
    assert standalone_canonical['best_alternative_total_bits'] == 1224
    assert standalone_canonical['winning_margin_bits'] == 103
    assert math.isclose(standalone_canonical['recommended_mean_bits'], 1121 / 153)
    assert math.isclose(standalone_canonical['winning_margin_mean_bits'], 103 / 153)

    state_known_canonical = summary['dominance_checks']['state_known_canonical_shortest_script']
    assert state_known_canonical['recommended_total_bits'] == 0
    assert state_known_canonical['best_alternative_transport'] == 'state_conditional_choice_prefix_on_canonical_subset'
    assert state_known_canonical['best_alternative_total_bits'] == 165
    assert state_known_canonical['winning_margin_bits'] == 165
    assert math.isclose(state_known_canonical['best_alternative_mean_bits'], 165 / 153)

    standalone_exact = summary['dominance_checks']['standalone_exact_shortest_script']
    assert standalone_exact['recommended_total_bits'] == 4619
    assert standalone_exact['best_alternative_transport'] == 'global_exact_shortest_word_dense_fixed_width'
    assert standalone_exact['best_alternative_total_bits'] == 5130
    assert standalone_exact['winning_margin_bits'] == 511
    assert math.isclose(standalone_exact['recommended_mean_bits'], 4619 / 513)
    assert math.isclose(standalone_exact['winning_margin_mean_bits'], 511 / 513)

    state_known_exact = summary['dominance_checks']['state_known_exact_shortest_script']
    assert state_known_exact['recommended_total_bits'] == 1350
    assert state_known_exact['best_alternative_transport'] == 'fixed_choice_index'
    assert state_known_exact['best_alternative_total_bits'] == 1560
    assert state_known_exact['winning_margin_bits'] == 210
    assert math.isclose(state_known_exact['recommended_mean_bits'], 1350 / 513)
    assert math.isclose(state_known_exact['winning_margin_mean_bits'], 210 / 513)

    recommendation = recommend_shortest_script_transport(
        state_is_known_to_decoder=True,
        exact_noncanonical_branch_must_survive=False,
    )
    assert recommendation['regime'] == 'state_known_canonical_shortest_script'
    assert recommendation['recommended_transport'] == 'zero_bit_canonical_reconstruction_from_state'
    assert recommendation['recommended_total_bits'] == 0
    assert recommendation['best_alternative_transport'] == 'state_conditional_choice_prefix_on_canonical_subset'

    print('ok')


if __name__ == '__main__':
    main()
