#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_time_consistency_law import (
    build_geometric_arrival_time_consistency_validation_summary,
    evaluate_state_time_consistency_profile,
    evaluate_universal_time_consistency_profile,
)


def main() -> None:
    consistent = evaluate_state_time_consistency_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 2).numerator,
        Fraction(1, 2).denominator,
    )
    assert consistent['schedule_class'] == 'finite'
    assert consistent['minimum_timeout_ticks_for_blind_commit_margin'] == 1
    assert bool(consistent['live_policy_is_time_consistent_for_original_margin'])
    assert bool(consistent['live_boundary_preserves_original_margin'])

    drift = evaluate_state_time_consistency_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
    )
    assert drift['schedule_class'] == 'finite'
    assert drift['minimum_timeout_ticks_for_blind_commit_margin'] == 2
    assert not bool(drift['live_policy_is_time_consistent_for_original_margin'])
    assert not bool(drift['live_boundary_preserves_original_margin'])
    assert drift['drift_interval_under_live_reoptimization'] == {'start_remaining_horizon': 2, 'end_remaining_horizon': 2}

    universal_drift = evaluate_universal_time_consistency_profile(
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
    )
    assert not bool(universal_drift['live_policy_is_time_consistent_for_original_margin'])

    summary = build_geometric_arrival_time_consistency_validation_summary()
    assert summary['drift_prone_state_schedules'] > 0
    assert summary['time_consistent_state_schedules'] > 0
    assert summary['drift_prone_universal_schedules'] > 0
    print('shared-state equiprobable geometric-arrival time-consistency law checks passed')


if __name__ == '__main__':
    main()
