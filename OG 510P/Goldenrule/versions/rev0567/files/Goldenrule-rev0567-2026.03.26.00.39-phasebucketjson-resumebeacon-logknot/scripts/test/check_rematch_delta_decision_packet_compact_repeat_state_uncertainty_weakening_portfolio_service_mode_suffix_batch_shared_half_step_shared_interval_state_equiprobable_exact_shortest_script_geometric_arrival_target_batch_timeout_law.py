#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_target_batch_timeout_law import (
    build_geometric_arrival_target_batch_timeout_validation_summary,
    compute_minimum_timeout_for_state_batch_target_margin,
    compute_universal_minimum_timeout_for_batch_target_margin,
)


def _fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_target_batch_timeout_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_parameter_panels'] == 153 * 8 * 4 * 4 * 5
    assert validation['finite_state_timeouts'] == 27878
    assert validation['asymptotic_only_state_schedules'] == 409
    assert validation['impossible_state_schedules'] == 69633
    assert validation['validated_universal_parameter_schedules'] == 8 * 4 * 4 * 5
    assert validation['finite_universal_timeouts'] == 176
    assert validation['asymptotic_only_universal_schedules'] == 3
    assert validation['impossible_universal_schedules'] == 461

    state_one = compute_minimum_timeout_for_state_batch_target_margin((0, 16), 2, 1, 2, 1, 10, 1, 2)
    state_two = compute_minimum_timeout_for_state_batch_target_margin((7, 12), 2, 1, 2, 1, 10, 1, 1)
    singleton = compute_minimum_timeout_for_state_batch_target_margin((8, 8), 2, 3, 4, 1, 10, 1, 1)
    asymptotic_only = compute_minimum_timeout_for_state_batch_target_margin((0, 16), 2, 1, 2, 1, 10, 29, 30)
    impossible = compute_minimum_timeout_for_state_batch_target_margin((0, 16), 4, 1, 4, 1, 10, 1, 2)
    universal = compute_universal_minimum_timeout_for_batch_target_margin(2, 1, 1, 1, 10, 1, 2)

    assert state_one['finite_timeout_exists'] is True
    assert state_one['minimum_timeout_ticks'] == 2
    assert _fraction(state_one['required_capture_fraction_of_asymptotic_positive_wait_value']) == Fraction(15, 29)
    assert _fraction(state_one['achieved_margin_bits_per_script_by_minimum_timeout']) == Fraction(29, 40)

    assert state_two['finite_timeout_exists'] is True
    assert state_two['minimum_timeout_ticks'] == 4
    assert _fraction(state_two['required_capture_fraction_of_asymptotic_positive_wait_value']) == Fraction(15, 17)
    assert _fraction(state_two['achieved_margin_bits_per_script_by_minimum_timeout']) == Fraction(17, 16)

    assert singleton['finite_timeout_exists'] is True
    assert singleton['minimum_timeout_ticks'] == 2
    assert _fraction(singleton['required_capture_fraction_of_asymptotic_positive_wait_value']) == Fraction(5, 6)
    assert _fraction(singleton['achieved_margin_bits_per_script_by_minimum_timeout']) == Fraction(9, 8)

    assert asymptotic_only['finite_timeout_exists'] is False
    assert asymptotic_only['asymptotically_feasible'] is True
    assert _fraction(asymptotic_only['required_capture_fraction_of_asymptotic_positive_wait_value']) == Fraction(1, 1)

    assert impossible['finite_timeout_exists'] is False
    assert impossible['asymptotically_feasible'] is False
    assert _fraction(impossible['asymptotic_margin_bits_per_script']) == Fraction(-1, 20)

    assert universal['finite_timeout_exists'] is True
    assert universal['minimum_timeout_ticks'] == 1
    assert _fraction(universal['required_capture_fraction_of_asymptotic_positive_wait_value']) == Fraction(15, 32)

    print('shared-state equiprobable geometric-arrival target-batch timeout law checks passed')


if __name__ == '__main__':
    main()
