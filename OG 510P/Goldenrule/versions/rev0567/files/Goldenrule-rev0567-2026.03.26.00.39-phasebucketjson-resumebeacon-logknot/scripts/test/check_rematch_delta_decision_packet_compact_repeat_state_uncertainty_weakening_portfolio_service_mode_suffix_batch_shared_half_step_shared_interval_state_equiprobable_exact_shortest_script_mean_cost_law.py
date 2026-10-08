#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_mean_cost_law import (
    build_mean_cost_validation_summary,
    compute_min_batch_length_for_state_target_mean_cost,
    compute_universal_min_batch_length_for_target_mean_cost,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_mean_cost_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_cost_pairs'] == 153 * 8
    assert validation['audited_target_count'] == 5
    assert validation['validated_state_target_pairs'] == 153 * 5
    assert validation['validated_universal_targets'] == 5
    assert validation['validated_impossible_universal_targets'] == 2
    assert validation['universal_upper_envelope_formula'] == '38/9 + 8/n'
    assert _fraction(validation['universal_asymptotic_floor_bits_per_script']) == Fraction(38, 9)

    universal_five = compute_universal_min_batch_length_for_target_mean_cost(5)
    universal_six = compute_universal_min_batch_length_for_target_mean_cost(6)
    universal_seven = compute_universal_min_batch_length_for_target_mean_cost(7)
    universal_eight = compute_universal_min_batch_length_for_target_mean_cost(8)
    universal_nine = compute_universal_min_batch_length_for_target_mean_cost(9)
    universal_floor = compute_universal_min_batch_length_for_target_mean_cost(38, 9)

    assert universal_five['minimum_batch_length'] == 11
    assert universal_six['minimum_batch_length'] == 5
    assert universal_seven['minimum_batch_length'] == 3
    assert universal_eight['minimum_batch_length'] == 3
    assert universal_nine['minimum_batch_length'] == 2
    assert universal_floor['minimum_batch_length'] is None
    assert universal_floor['attainable_with_finite_batch'] is False
    assert _fraction(universal_six['achieved_mean_cost_bits_per_script']) == Fraction(262, 45)

    one_sided = compute_min_batch_length_for_state_target_mean_cost((0, 16), 4)
    assert one_sided['minimum_batch_length'] == 2
    assert _fraction(one_sided['achieved_mean_cost_bits_per_script']) == Fraction(7, 2)

    nonsingleton = compute_min_batch_length_for_state_target_mean_cost((7, 12), 5)
    assert nonsingleton['minimum_batch_length'] == 2
    assert _fraction(nonsingleton['previous_batch_mean_cost_bits_per_script']) == Fraction(9, 1)
    assert _fraction(nonsingleton['achieved_mean_cost_bits_per_script']) == Fraction(5, 1)

    singleton = compute_min_batch_length_for_state_target_mean_cost((8, 8), 5)
    assert singleton['minimum_batch_length'] == 11
    assert _fraction(singleton['previous_batch_mean_cost_bits_per_script']) == Fraction(226, 45)
    assert _fraction(singleton['achieved_mean_cost_bits_per_script']) == Fraction(490, 99)

    impossible = compute_min_batch_length_for_state_target_mean_cost((15, 15), 38, 9)
    assert impossible['minimum_batch_length'] is None
    assert impossible['attainable_with_finite_batch'] is False

    cost = evaluate_shared_interval_state_equiprobable_exact_shortest_script_mean_cost((1, 2), 3)
    assert _fraction(cost['equiprobable_mean_shared_state_transport_bits_per_script']) == Fraction(10, 3)

    print('shared-state equiprobable mean-cost law checks passed')


if __name__ == '__main__':
    main()
