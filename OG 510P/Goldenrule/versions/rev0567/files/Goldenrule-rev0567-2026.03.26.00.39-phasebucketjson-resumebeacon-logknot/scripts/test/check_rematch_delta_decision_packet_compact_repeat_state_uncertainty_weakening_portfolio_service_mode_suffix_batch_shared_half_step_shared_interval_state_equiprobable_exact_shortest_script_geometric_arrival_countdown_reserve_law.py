#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_countdown_reserve_law import (
    build_geometric_arrival_countdown_reserve_validation_summary,
    evaluate_state_countdown_reserve_profile,
    evaluate_universal_countdown_reserve_profile,
)


def main() -> None:
    drift = evaluate_state_countdown_reserve_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        2,
    )
    assert drift['minimum_timeout_ticks_for_blind_commit_margin'] == 2
    assert bool(drift['blind_commit_meets_original_margin_floor'])
    assert bool(drift['live_countdown_policy_continues'])
    assert not bool(drift['live_countdown_policy_meets_original_margin_floor'])
    assert drift['usable_wait_window_ticks_under_live_countdown_policy'] == 1
    assert drift['minimum_remaining_horizon_ticks_to_preserve_original_margin_under_live_countdown'] == 3

    preserved = evaluate_state_countdown_reserve_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        3,
    )
    assert bool(preserved['live_countdown_policy_meets_original_margin_floor'])
    assert preserved['usable_wait_window_ticks_under_live_countdown_policy'] == 2

    universal = evaluate_universal_countdown_reserve_profile(
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        3,
    )
    assert universal['minimum_remaining_horizon_ticks_to_preserve_original_margin_under_live_countdown'] is not None

    summary = build_geometric_arrival_countdown_reserve_validation_summary()
    assert summary['validated_state_panels'] > 0
    assert summary['state_live_margin_drift_panels'] > 0
    assert summary['universal_live_margin_drift_panels'] > 0
    print('shared-state equiprobable geometric-arrival countdown reserve law checks passed')


if __name__ == '__main__':
    main()
