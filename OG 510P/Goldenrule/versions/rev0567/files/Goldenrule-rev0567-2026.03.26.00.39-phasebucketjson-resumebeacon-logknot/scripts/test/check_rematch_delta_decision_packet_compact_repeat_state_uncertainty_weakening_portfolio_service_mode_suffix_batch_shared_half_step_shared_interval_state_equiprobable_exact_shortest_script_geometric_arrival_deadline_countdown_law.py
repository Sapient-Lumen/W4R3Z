#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_countdown_law import (
    build_geometric_arrival_deadline_countdown_validation_summary,
    evaluate_checkpoint_remaining_horizon_decision_for_state,
    evaluate_universal_checkpoint_remaining_horizon_decision,
)


def main() -> None:
    finite = evaluate_checkpoint_remaining_horizon_decision_for_state(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(0, 1).numerator,
        Fraction(0, 1).denominator,
        0,
        1,
    )
    assert finite['schedule_class'] == 'finite'
    assert finite['minimum_remaining_horizon_ticks_for_target_margin'] == 1
    assert bool(finite['should_continue_from_remaining_horizon_threshold'])

    delayed = evaluate_checkpoint_remaining_horizon_decision_for_state(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 2).numerator,
        Fraction(1, 2).denominator,
        5,
        2,
    )
    assert not bool(delayed['elapsed_no_arrival_streak_changes_threshold'])

    impossible = evaluate_universal_checkpoint_remaining_horizon_decision(
        8,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 2).numerator,
        Fraction(1, 2).denominator,
        Fraction(2, 1).numerator,
        Fraction(2, 1).denominator,
        1,
        6,
    )
    assert impossible['schedule_class'] == 'impossible'
    assert not bool(impossible['should_continue_from_remaining_horizon_threshold'])

    summary = build_geometric_arrival_deadline_countdown_validation_summary()
    assert summary['validated_state_checkpoint_margin_panels'] > 0
    assert summary['finite_state_schedules'] > 0
    assert summary['impossible_state_schedules'] > 0
    print('shared-state equiprobable geometric-arrival deadline-countdown law checks passed')


if __name__ == '__main__':
    main()
