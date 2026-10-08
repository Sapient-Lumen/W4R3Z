#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_target_margin_law import (
    build_target_margin_validation_summary,
    compute_min_batch_length_for_state_target_margin,
    compute_universal_min_batch_length_for_target_margin,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_target_margin_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['audited_target_count'] == 6
    assert validation['validated_state_target_pairs'] == 153 * 6
    assert validation['validated_universal_targets'] == 6
    assert validation['universal_guarantee_formula'] == 'ceil(9(target_bits + 8) / 43)'

    universal_zero = compute_universal_min_batch_length_for_target_margin(0)
    universal_two = compute_universal_min_batch_length_for_target_margin(2)
    universal_five = compute_universal_min_batch_length_for_target_margin(5)
    universal_ten = compute_universal_min_batch_length_for_target_margin(10)
    universal_twenty = compute_universal_min_batch_length_for_target_margin(20)

    assert universal_zero['minimum_batch_length'] == 2
    assert universal_two['minimum_batch_length'] == 3
    assert universal_five['minimum_batch_length'] == 3
    assert universal_ten['minimum_batch_length'] == 4
    assert universal_twenty['minimum_batch_length'] == 6
    assert _fraction(universal_two['achieved_margin_bits']) == Fraction(19, 3)

    state = compute_min_batch_length_for_state_target_margin((7, 12), 1)
    assert state['minimum_batch_length'] == 2
    assert _fraction(state['previous_margin_bits']) == Fraction(0, 1)
    assert _fraction(state['achieved_margin_bits']) == Fraction(8, 1)

    singleton = compute_min_batch_length_for_state_target_margin((8, 8), 2)
    assert singleton['minimum_batch_length'] == 3
    assert _fraction(singleton['previous_margin_bits']) == Fraction(14, 9)
    assert _fraction(singleton['achieved_margin_bits']) == Fraction(19, 3)

    edge = compute_min_batch_length_for_state_target_margin((15, 15), 2)
    assert edge['minimum_batch_length'] == 3
    assert _fraction(edge['previous_margin_bits']) == Fraction(16, 9)
    assert _fraction(edge['achieved_margin_bits']) == Fraction(20, 3)

    one_sided = compute_min_batch_length_for_state_target_margin((0, 16), 10)
    assert one_sided['minimum_batch_length'] == 2
    assert _fraction(one_sided['achieved_margin_bits']) == Fraction(11, 1)

    print('shared-state equiprobable target-margin law checks passed')


if __name__ == '__main__':
    main()
