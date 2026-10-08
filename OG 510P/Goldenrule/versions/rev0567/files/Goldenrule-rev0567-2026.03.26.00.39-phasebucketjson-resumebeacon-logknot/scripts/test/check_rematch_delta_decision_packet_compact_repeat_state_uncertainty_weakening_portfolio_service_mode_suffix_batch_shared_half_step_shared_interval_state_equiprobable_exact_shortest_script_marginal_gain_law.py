#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_marginal_gain_law import (
    build_marginal_gain_validation_summary,
    compute_max_current_batch_length_for_state_target_marginal_gain,
    compute_universal_max_current_batch_length_for_target_marginal_gain,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_marginal_gain_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_gain_pairs'] == 153 * 8
    assert validation['audited_target_count'] == 5
    assert validation['validated_state_target_pairs'] == 153 * 5
    assert validation['validated_universal_targets'] == 5
    assert validation['validated_impossible_targets'] == 2
    assert validation['universal_lower_envelope_formula'] == '7/(n(n+1))'
    assert validation['universal_upper_envelope_formula'] == '8/(n(n+1))'
    assert _fraction(validation['minimum_marginal_gain_by_batch_length'][0]['minimum_marginal_gain_bits_per_script']) == Fraction(7, 2)
    assert _fraction(validation['maximum_marginal_gain_by_batch_length'][0]['maximum_marginal_gain_bits_per_script']) == Fraction(4, 1)

    universal_two = compute_universal_max_current_batch_length_for_target_marginal_gain(2)
    universal_one = compute_universal_max_current_batch_length_for_target_marginal_gain(1)
    universal_half = compute_universal_max_current_batch_length_for_target_marginal_gain(1, 2)
    universal_quarter = compute_universal_max_current_batch_length_for_target_marginal_gain(1, 4)
    universal_tenth = compute_universal_max_current_batch_length_for_target_marginal_gain(1, 10)
    universal_impossible = compute_universal_max_current_batch_length_for_target_marginal_gain(4)

    assert universal_two['maximum_current_batch_length'] == 1
    assert universal_one['maximum_current_batch_length'] == 2
    assert universal_half['maximum_current_batch_length'] == 3
    assert universal_quarter['maximum_current_batch_length'] == 4
    assert universal_tenth['maximum_current_batch_length'] == 7
    assert universal_impossible['maximum_current_batch_length'] is None
    assert universal_impossible['qualifying_batch_exists'] is False
    assert _fraction(universal_one['achieved_marginal_gain_bits_per_script']) == Fraction(7, 6)

    one_sided = compute_max_current_batch_length_for_state_target_marginal_gain((0, 16), 1, 2)
    assert one_sided['maximum_current_batch_length'] == 3
    assert _fraction(one_sided['achieved_marginal_gain_bits_per_script']) == Fraction(7, 12)
    assert _fraction(one_sided['next_nonqualifying_marginal_gain_bits_per_script']) == Fraction(7, 20)

    nonsingleton = compute_max_current_batch_length_for_state_target_marginal_gain((7, 12), 1, 4)
    assert nonsingleton['maximum_current_batch_length'] == 5
    assert _fraction(nonsingleton['achieved_marginal_gain_bits_per_script']) == Fraction(4, 15)
    assert _fraction(nonsingleton['next_nonqualifying_marginal_gain_bits_per_script']) == Fraction(4, 21)

    singleton = compute_max_current_batch_length_for_state_target_marginal_gain((8, 8), 1, 10)
    assert singleton['maximum_current_batch_length'] == 8
    assert _fraction(singleton['achieved_marginal_gain_bits_per_script']) == Fraction(1, 9)
    assert _fraction(singleton['next_nonqualifying_marginal_gain_bits_per_script']) == Fraction(4, 45)

    impossible_state = compute_max_current_batch_length_for_state_target_marginal_gain((15, 15), 5)
    assert impossible_state['maximum_current_batch_length'] is None
    assert impossible_state['qualifying_batch_exists'] is False

    gain = evaluate_shared_interval_state_equiprobable_exact_shortest_script_marginal_mean_cost_gain((1, 2), 3)
    assert _fraction(gain['equiprobable_marginal_mean_cost_gain_bits_per_script']) == Fraction(7, 12)

    print('shared-state equiprobable marginal-gain law checks passed')


if __name__ == '__main__':
    main()
