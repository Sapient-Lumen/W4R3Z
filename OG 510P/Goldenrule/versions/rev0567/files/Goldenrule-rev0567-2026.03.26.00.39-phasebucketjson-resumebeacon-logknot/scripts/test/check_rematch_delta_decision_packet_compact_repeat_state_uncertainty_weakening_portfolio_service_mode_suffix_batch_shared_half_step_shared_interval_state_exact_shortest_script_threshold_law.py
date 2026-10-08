#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_threshold_law import (
    build_shared_interval_state_exact_shortest_script_threshold_profile,
    build_shared_interval_state_exact_shortest_script_threshold_validation_summary,
    recommend_shared_interval_state_exact_shortest_script_transport_by_threshold,
)


def main() -> None:
    summary = build_shared_interval_state_exact_shortest_script_threshold_validation_summary()
    assert summary['total_audited_batch_cases'] == 94179
    assert summary['weak_threshold_counter'] == {'1': 138, '2': 15}
    assert summary['strict_threshold_counter'] == {'1': 106, '2': 39, '3': 8}
    assert summary['safe_but_not_strict_counter'] == {'1': 32, '2': 8}
    assert summary['all_states_have_nine_bit_global_floor'] is True
    assert summary['all_state_thresholds_match_the_closed_form_margin_rule'] is True

    profile = build_shared_interval_state_exact_shortest_script_threshold_profile((8, 15))
    assert profile['state_category'] == 'interior_nonsingleton'
    assert profile['state_prefix_bit_length'] == 8
    assert profile['max_local_choice_prefix_bit_length'] == 1
    assert profile['min_global_exact_word_prefix_bit_length'] == 9
    assert profile['per_word_margin_bits'] == 8
    assert profile['weak_switch_threshold'] == 1
    assert profile['strict_switch_threshold'] == 2

    profile = build_shared_interval_state_exact_shortest_script_threshold_profile((8, 8))
    assert profile['state_category'] == 'interior_singleton'
    assert profile['state_prefix_bit_length'] == 8
    assert profile['max_local_choice_prefix_bit_length'] == 5
    assert profile['min_global_exact_word_prefix_bit_length'] == 9
    assert profile['per_word_margin_bits'] == 4
    assert profile['weak_switch_threshold'] == 2
    assert profile['strict_switch_threshold'] == 3

    one_word = recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 15), 1)
    assert one_word['recommendation'] == 'shared_interval_state_prefix_plus_local_choice_prefixes'
    assert one_word['guarantee'] == 'weak_win'

    two_words = recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((1, 1), 2)
    assert two_words['recommendation'] == 'shared_interval_state_prefix_plus_local_choice_prefixes'
    assert two_words['guarantee'] == 'strict_win'

    one_word_singleton = recommend_shared_interval_state_exact_shortest_script_transport_by_threshold((8, 8), 1)
    assert one_word_singleton['recommendation'] == 'keep_global_exact_word_prefix_frontier'
    assert one_word_singleton['guarantee'] == 'loss_possible'

    print('ok')


if __name__ == '__main__':
    main()
