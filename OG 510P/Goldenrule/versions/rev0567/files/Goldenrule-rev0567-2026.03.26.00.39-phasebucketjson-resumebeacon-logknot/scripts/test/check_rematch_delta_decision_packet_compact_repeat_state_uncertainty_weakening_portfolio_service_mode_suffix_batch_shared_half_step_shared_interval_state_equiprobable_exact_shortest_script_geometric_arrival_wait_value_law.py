#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value_law import (
    build_geometric_arrival_wait_value_validation_summary,
    compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair,
    compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_wait_value_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_probability_cost_timeout_cases'] == 153 * 8 * 4 * 4 * 6
    assert validation['validated_timeout_sign_invariance_panels'] == 153 * 8 * 4 * 4
    assert validation['validated_state_schedule_pairs'] == 4
    assert validation['validated_universal_schedule_pairs'] == 5

    universal_quarter_tenth = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 4, 1, 10)
    universal_half_tenth = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 2, 1, 10)
    universal_three_quarter_tenth = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(3, 4, 1, 10)
    universal_half_quarter = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 2, 1, 4)
    universal_quarter_half = compute_universal_max_current_batch_length_for_arrival_probability_hold_cost_pair(1, 4, 1, 2)

    assert universal_quarter_tenth['maximum_strictly_positive_current_batch_length'] == 3
    assert universal_half_tenth['maximum_strictly_positive_current_batch_length'] == 5
    assert universal_three_quarter_tenth['maximum_strictly_positive_current_batch_length'] == 6
    assert universal_half_quarter['maximum_strictly_positive_current_batch_length'] == 3
    assert universal_quarter_half['maximum_strictly_positive_current_batch_length'] == 1
    assert universal_quarter_half['strictly_positive_wait_exists'] is True

    one_sided = compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((0, 16), 1, 2, 1, 10)
    assert one_sided['maximum_strictly_positive_current_batch_length'] == 5
    assert _fraction(one_sided['achieved_sign_invariant_term_bits_per_script_per_tick']) == Fraction(1, 60)
    assert _fraction(one_sided['next_nonpositive_sign_invariant_term_bits_per_script_per_tick']) == Fraction(-1, 60)

    seven_twelve = compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((7, 12), 1, 4, 1, 10)
    assert seven_twelve['maximum_strictly_positive_current_batch_length'] == 3
    assert _fraction(seven_twelve['achieved_sign_invariant_term_bits_per_script_per_tick']) == Fraction(1, 15)
    assert _fraction(seven_twelve['next_nonpositive_sign_invariant_term_bits_per_script_per_tick']) == Fraction(0, 1)

    singleton = compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((8, 8), 3, 4, 1, 4)
    assert singleton['maximum_strictly_positive_current_batch_length'] == 4
    assert _fraction(singleton['achieved_sign_invariant_term_bits_per_script_per_tick']) == Fraction(1, 20)
    assert _fraction(singleton['next_nonpositive_sign_invariant_term_bits_per_script_per_tick']) == Fraction(-1, 20)

    dominated = compute_max_current_batch_length_for_state_arrival_probability_hold_cost_pair((15, 15), 1, 4, 1, 2)
    assert dominated['maximum_strictly_positive_current_batch_length'] == 1
    assert dominated['strictly_positive_wait_exists'] is True

    short_timeout = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value((7, 12), 3, 1, 2, 1, 10, 1)
    long_timeout = evaluate_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_wait_value((7, 12), 3, 1, 2, 1, 10, 6)
    assert short_timeout['sign_classification'] == 'positive'
    assert long_timeout['sign_classification'] == 'positive'
    assert _fraction(short_timeout['expected_net_wait_value_bits_per_script']) == Fraction(7, 30)
    assert _fraction(long_timeout['expected_net_wait_value_bits_per_script']) == Fraction(147, 320)
    assert _fraction(short_timeout['sign_invariant_term_bits_per_script_per_tick']) == Fraction(7, 30)
    assert _fraction(long_timeout['sign_invariant_term_bits_per_script_per_tick']) == Fraction(7, 30)

    print('shared-state equiprobable geometric-arrival wait-value law checks passed')


if __name__ == '__main__':
    main()
