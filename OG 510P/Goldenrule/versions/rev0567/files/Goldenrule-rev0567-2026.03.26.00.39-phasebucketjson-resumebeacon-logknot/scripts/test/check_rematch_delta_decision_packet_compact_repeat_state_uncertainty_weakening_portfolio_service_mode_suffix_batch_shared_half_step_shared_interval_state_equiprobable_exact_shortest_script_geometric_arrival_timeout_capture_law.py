#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_capture_law import (
    build_geometric_arrival_timeout_capture_validation_summary,
    compute_minimum_timeout_for_capture_fraction,
    evaluate_positive_wait_timeout_capture_policy_for_state_batch,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_timeout_capture_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['positive_wait_panels'] == 10910
    assert validation['negative_wait_panels'] == 8574
    assert validation['zero_wait_panels'] == 100
    assert validation['validated_positive_wait_capture_panels'] == 10910 * 5
    assert validation['validated_arrival_target_schedules'] == 4 * 5

    quarter_half = compute_minimum_timeout_for_capture_fraction(1, 4, 1, 2)
    quarter_three_quarters = compute_minimum_timeout_for_capture_fraction(1, 4, 3, 4)
    quarter_fifteen_sixteenths = compute_minimum_timeout_for_capture_fraction(1, 4, 15, 16)
    half_fifteen_sixteenths = compute_minimum_timeout_for_capture_fraction(1, 2, 15, 16)
    three_quarter_thirty_one_thirty_seconds = compute_minimum_timeout_for_capture_fraction(3, 4, 31, 32)

    assert quarter_half['minimum_timeout_ticks'] == 3
    assert quarter_three_quarters['minimum_timeout_ticks'] == 5
    assert quarter_fifteen_sixteenths['minimum_timeout_ticks'] == 10
    assert half_fifteen_sixteenths['minimum_timeout_ticks'] == 4
    assert three_quarter_thirty_one_thirty_seconds['minimum_timeout_ticks'] == 3
    assert _fraction(half_fifteen_sixteenths['achieved_capture_fraction_by_minimum_timeout']) == Fraction(15, 16)
    assert _fraction(three_quarter_thirty_one_thirty_seconds['achieved_capture_fraction_by_minimum_timeout']) == Fraction(63, 64)

    state_one = evaluate_positive_wait_timeout_capture_policy_for_state_batch((0, 16), 5, 1, 2, 1, 10, 15, 16)
    state_two = evaluate_positive_wait_timeout_capture_policy_for_state_batch((7, 12), 3, 1, 2, 1, 10, 15, 16)
    singleton = evaluate_positive_wait_timeout_capture_policy_for_state_batch((8, 8), 3, 1, 4, 1, 10, 7, 8)
    sharp = evaluate_positive_wait_timeout_capture_policy_for_state_batch((15, 15), 1, 1, 4, 1, 2, 31, 32)

    assert state_one['positive_wait_exists'] is True
    assert state_two['positive_wait_exists'] is True
    assert state_one['minimum_timeout_ticks'] == 4
    assert state_two['minimum_timeout_ticks'] == 4
    assert _fraction(state_one['achieved_capture_fraction_by_minimum_timeout']) == Fraction(15, 16)
    assert _fraction(state_two['achieved_capture_fraction_by_minimum_timeout']) == Fraction(15, 16)
    assert singleton['minimum_timeout_ticks'] == 8
    assert _fraction(singleton['achieved_capture_fraction_by_minimum_timeout']) == Fraction(58975, 65536)
    assert sharp['minimum_timeout_ticks'] == 13
    assert _fraction(sharp['achieved_capture_fraction_by_minimum_timeout']) == Fraction(65514541, 67108864)

    print('shared-state equiprobable geometric-arrival timeout-capture law checks passed')


if __name__ == '__main__':
    main()
