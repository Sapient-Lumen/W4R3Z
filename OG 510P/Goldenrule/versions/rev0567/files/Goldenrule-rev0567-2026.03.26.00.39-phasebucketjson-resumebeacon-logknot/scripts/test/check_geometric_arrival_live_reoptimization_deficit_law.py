#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_live_reoptimization_deficit_law import (
    build_geometric_arrival_live_reoptimization_deficit_validation_summary,
    evaluate_state_live_reoptimization_deficit_profile,
    evaluate_universal_live_reoptimization_deficit_profile,
)


def main() -> None:
    one_tick = evaluate_state_live_reoptimization_deficit_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 2).numerator,
        Fraction(1, 2).denominator,
        1,
    )
    assert one_tick['minimum_timeout_ticks_for_blind_commit_margin'] == 1
    assert one_tick['same_horizon_live_deficit_bits_per_script']['numerator'] == 0

    drift = evaluate_state_live_reoptimization_deficit_profile(
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
    assert drift['same_horizon_live_deficit_bits_per_script']['numerator'] == 99
    assert drift['same_horizon_live_deficit_bits_per_script']['denominator'] == 160

    later = evaluate_state_live_reoptimization_deficit_profile(
        (0, 0),
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        5,
    )
    assert later['same_horizon_live_deficit_bits_per_script']['numerator'] == 2673
    assert later['same_horizon_live_deficit_bits_per_script']['denominator'] == 10240

    universal = evaluate_universal_live_reoptimization_deficit_profile(
        1,
        Fraction(1, 4).numerator,
        Fraction(1, 4).denominator,
        Fraction(1, 20).numerator,
        Fraction(1, 20).denominator,
        Fraction(1, 1).numerator,
        Fraction(1, 1).denominator,
        2,
    )
    assert universal['same_horizon_live_deficit_bits_per_script']['numerator'] == 99
    assert universal['same_horizon_live_deficit_bits_per_script']['denominator'] == 160

    summary = build_geometric_arrival_live_reoptimization_deficit_validation_summary()
    assert summary['positive_state_deficit_panels'] > 0
    assert summary['zero_state_deficit_panels'] > 0
    assert summary['positive_universal_deficit_panels'] > 0
    print('shared-state equiprobable geometric-arrival live-reoptimization deficit law checks passed')


if __name__ == '__main__':
    main()
