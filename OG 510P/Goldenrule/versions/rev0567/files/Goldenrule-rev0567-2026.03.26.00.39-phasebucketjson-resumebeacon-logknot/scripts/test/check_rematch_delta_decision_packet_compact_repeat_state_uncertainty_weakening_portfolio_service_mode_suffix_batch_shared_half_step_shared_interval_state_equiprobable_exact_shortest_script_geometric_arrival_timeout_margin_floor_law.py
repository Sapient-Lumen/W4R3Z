#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_timeout_margin_floor_law import (
    build_geometric_arrival_timeout_margin_floor_validation_summary,
    compute_capture_adjusted_effective_hold_cost_for_target_margin,
    compute_max_current_batch_length_for_state_capture_target_margin,
    compute_universal_max_current_batch_length_for_capture_target_margin,
    evaluate_timeout_margin_floor_policy_for_state_batch,
)


def _fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_timeout_margin_floor_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_batch_parameter_panels'] == 153 * 8 * 4 * 4 * 4 * 4
    assert validation['validated_state_parameter_schedules'] == 153 * 4 * 4 * 4 * 4
    assert validation['feasible_state_parameter_schedules'] == 37276
    assert validation['impossible_state_parameter_schedules'] == 1892
    assert validation['validated_universal_parameter_schedules'] == 4 * 4 * 4 * 4
    assert validation['feasible_universal_parameter_schedules'] == 242
    assert validation['impossible_universal_parameter_schedules'] == 14

    effective = compute_capture_adjusted_effective_hold_cost_for_target_margin(1, 2, 1, 10, 15, 16, 1, 2)
    assert _fraction(effective['capture_fraction_by_minimum_timeout']) == Fraction(15, 16)
    assert effective['minimum_timeout_ticks'] == 4
    assert _fraction(effective['effective_margin_tax_bits_per_script_per_tick']) == Fraction(4, 15)
    assert _fraction(effective['effective_hold_cost_bits_per_script_per_tick']) == Fraction(11, 30)

    state_one = compute_max_current_batch_length_for_state_capture_target_margin((0, 16), 1, 2, 1, 10, 15, 16, 1, 2)
    state_two = compute_max_current_batch_length_for_state_capture_target_margin((7, 12), 1, 2, 1, 10, 15, 16, 1, 1)
    singleton = compute_max_current_batch_length_for_state_capture_target_margin((8, 8), 3, 4, 1, 10, 7, 8, 1, 1)
    impossible = compute_universal_max_current_batch_length_for_capture_target_margin(1, 4, 1, 10, 1, 2, 4, 1)
    universal = compute_universal_max_current_batch_length_for_capture_target_margin(1, 1, 1, 10, 15, 16, 1, 1)

    assert state_one['margin_floor_feasible'] is True
    assert state_one['maximum_current_batch_length_meeting_target_margin'] == 2
    assert _fraction(state_one['achieved_margin_bits_per_script_at_maximum_batch_length']) == Fraction(29, 32)
    assert _fraction(state_one['next_margin_bits_per_script_after_maximum_batch_length']) == Fraction(23, 64)

    assert state_two['margin_floor_feasible'] is True
    assert state_two['maximum_current_batch_length_meeting_target_margin'] == 2
    assert _fraction(state_two['achieved_margin_bits_per_script_at_maximum_batch_length']) == Fraction(17, 16)
    assert _fraction(state_two['next_margin_bits_per_script_after_maximum_batch_length']) == Fraction(7, 16)

    assert singleton['margin_floor_feasible'] is True
    assert singleton['minimum_timeout_ticks'] == 2
    assert singleton['maximum_current_batch_length_meeting_target_margin'] == 2
    assert _fraction(singleton['achieved_margin_bits_per_script_at_maximum_batch_length']) == Fraction(9, 8)
    assert _fraction(singleton['next_margin_bits_per_script_after_maximum_batch_length']) == Fraction(1, 2)

    assert impossible['margin_floor_feasible'] is False
    assert impossible['maximum_current_batch_length_meeting_target_margin'] is None
    assert _fraction(impossible['strict_ratio_budget_ps_over_effective_cost']) < 2

    assert universal['margin_floor_feasible'] is True
    assert universal['maximum_current_batch_length_meeting_target_margin'] == 2
    assert universal['minimum_timeout_ticks'] == 1
    assert _fraction(universal['capture_fraction_by_minimum_timeout']) == Fraction(1, 1)

    panel = evaluate_timeout_margin_floor_policy_for_state_batch((0, 16), 2, 1, 2, 1, 10, 15, 16, 1, 2)
    next_panel = evaluate_timeout_margin_floor_policy_for_state_batch((0, 16), 3, 1, 2, 1, 10, 15, 16, 1, 2)
    assert panel['meets_target_margin'] is True
    assert next_panel['meets_target_margin'] is False
    assert _fraction(panel['achieved_margin_bits_per_script_by_minimum_timeout']) == Fraction(29, 32)
    assert _fraction(next_panel['achieved_margin_bits_per_script_by_minimum_timeout']) == Fraction(23, 64)

    print('shared-state equiprobable geometric-arrival timeout margin-floor law checks passed')


if __name__ == '__main__':
    main()
