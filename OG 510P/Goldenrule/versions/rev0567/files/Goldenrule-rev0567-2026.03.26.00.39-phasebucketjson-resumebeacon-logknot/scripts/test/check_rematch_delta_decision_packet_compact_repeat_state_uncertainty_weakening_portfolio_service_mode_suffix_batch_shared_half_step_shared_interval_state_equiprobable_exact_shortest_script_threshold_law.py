#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_threshold_law import (
    build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile,
    build_shared_interval_state_equiprobable_exact_shortest_script_threshold_validation_summary,
    summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean,
)


def main() -> None:
    summary = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_validation_summary()
    assert summary['total_audited_batch_cases'] == 94179
    assert summary['weak_expected_threshold_counter'] == {'1': 138, '2': 15}
    assert summary['strict_expected_threshold_counter'] == {'1': 106, '2': 47}
    assert summary['state_uniform_expected_comparison_counter_by_batch_length'] == {
        '1': {'expected_loss': 15, 'expected_tie': 32, 'strict_expected_win': 106},
        '2': {'strict_expected_win': 153},
        '3': {'strict_expected_win': 153},
    }
    assert summary['strict_threshold_improvement_vs_worst_case_counter'] == {'interior_singleton': 8}
    assert summary['all_states_match_the_closed_form_expected_margin_rule'] is True
    assert summary['all_states_are_expected_strict_winners_by_batch_length_2'] is True
    assert summary['only_eight_bit_interior_singletons_improve_against_the_worst_case_strict_threshold'] is True

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile((8, 15))
    assert profile['state_category'] == 'interior_nonsingleton'
    assert profile['equiprobable_mean_local_choice_prefix_bits'] == {
        'numerator': 2,
        'denominator': 2,
        'decimal': 1.0,
    }
    assert profile['equiprobable_per_word_margin_bits'] == {
        'numerator': 16,
        'denominator': 2,
        'decimal': 8.0,
    }
    assert profile['weak_expected_switch_threshold'] == 1
    assert profile['strict_expected_switch_threshold'] == 2

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_threshold_profile((8, 8))
    assert profile['state_category'] == 'interior_singleton'
    assert profile['equiprobable_mean_local_choice_prefix_bits'] == {
        'numerator': 76,
        'denominator': 18,
        'decimal': 76 / 18,
    }
    assert profile['equiprobable_per_word_margin_bits'] == {
        'numerator': 86,
        'denominator': 18,
        'decimal': 86 / 18,
    }
    assert profile['weak_expected_switch_threshold'] == 2
    assert profile['strict_expected_switch_threshold'] == 2

    one_word = summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean((8, 15), 1)
    assert one_word['guarantee'] == 'expected_tie'
    assert one_word['recommendation'] == 'either_frontier_or_shared_interval_state_prefix_plus_local_choice_prefixes'

    two_words = summarize_shared_interval_state_exact_shortest_script_batch_by_equiprobable_mean((8, 8), 2)
    assert two_words['guarantee'] == 'strict_expected_win'
    assert two_words['recommendation'] == 'shared_interval_state_prefix_plus_local_choice_prefixes'
    assert two_words['equiprobable_mean_winning_margin_bits'] == {
        'numerator': 14,
        'denominator': 9,
        'decimal': 14 / 9,
    }

    print('ok')


if __name__ == '__main__':
    main()
