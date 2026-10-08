#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_batch_cap_law import (
    build_geometric_arrival_timeout_batch_cap_validation_summary,
    compute_maximum_batch_length_for_state_timeout_target_margin,
    compute_universal_maximum_batch_length_for_timeout_target_margin,
)


def _fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_timeout_batch_cap_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_parameter_panels'] == 153 * 4 * 4 * 6 * 5 * 12
    assert validation['validated_state_schedule_inversions'] == 153 * 4 * 4 * 6 * 5
    assert validation['validated_state_timeout_ladders'] == 153 * 4 * 4 * 5
    assert validation['validated_universal_parameter_schedules'] == 4 * 4 * 6 * 5 * 12
    assert validation['validated_universal_schedule_inversions'] == 4 * 4 * 6 * 5
    assert validation['validated_universal_timeout_ladders'] == 4 * 4 * 5

    state_one = compute_maximum_batch_length_for_state_timeout_target_margin((0, 16), 1, 2, 1, 10, 2, 1, 2)
    state_two = compute_maximum_batch_length_for_state_timeout_target_margin((7, 12), 1, 2, 1, 10, 4, 1, 1)
    singleton = compute_maximum_batch_length_for_state_timeout_target_margin((8, 8), 3, 4, 1, 20, 3, 1, 2)
    impossible = compute_maximum_batch_length_for_state_timeout_target_margin((0, 16), 1, 4, 1, 2, 1, 1, 2)
    universal = compute_universal_maximum_batch_length_for_timeout_target_margin(1, 2, 1, 10, 2, 1, 2)
    one_tick = compute_universal_maximum_batch_length_for_timeout_target_margin(1, 4, 1, 10, 1, 1, 4)

    assert state_one['maximum_admissible_batch_length'] == 2
    assert _fraction(state_one['capture_fraction_by_timeout']) == Fraction(3, 4)
    assert _fraction(state_one['effective_hold_cost_bits_per_script_per_tick']) == Fraction(13, 30)

    assert state_two['maximum_admissible_batch_length'] == 2
    assert _fraction(state_two['capture_fraction_by_timeout']) == Fraction(15, 16)
    assert _fraction(state_two['effective_hold_cost_bits_per_script_per_tick']) == Fraction(19, 30)

    assert singleton['maximum_admissible_batch_length'] == 3
    assert _fraction(singleton['capture_fraction_by_timeout']) == Fraction(63, 64)
    assert _fraction(singleton['effective_hold_cost_bits_per_script_per_tick']) == Fraction(181, 420)

    assert impossible['maximum_admissible_batch_length'] == 0
    assert impossible['finite_positive_batch_exists'] is False

    assert universal['maximum_admissible_batch_length'] == 2
    assert _fraction(universal['capture_fraction_by_timeout']) == Fraction(3, 4)
    assert _fraction(universal['effective_hold_cost_bits_per_script_per_tick']) == Fraction(13, 30)

    assert one_tick['maximum_admissible_batch_length'] == 1
    assert _fraction(one_tick['capture_fraction_by_timeout']) == Fraction(1, 4)
    assert _fraction(one_tick['effective_hold_cost_bits_per_script_per_tick']) == Fraction(7, 20)

    print('shared-state equiprobable geometric-arrival timeout-batch-cap law checks passed')


if __name__ == '__main__':
    main()
