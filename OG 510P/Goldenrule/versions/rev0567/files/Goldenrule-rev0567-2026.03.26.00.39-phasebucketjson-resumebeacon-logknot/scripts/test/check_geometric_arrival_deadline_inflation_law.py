#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_deadline_inflation_law import (
    build_geometric_arrival_deadline_inflation_validation_summary,
    evaluate_state_deadline_inflation_profile,
    evaluate_universal_deadline_inflation_profile,
)


def main() -> None:
    drift = evaluate_state_deadline_inflation_profile((0, 0), 1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 2)
    assert drift['minimum_timeout_ticks_for_blind_commit_margin'] == 2
    assert drift['deadline_inflation_ticks'] == 1
    assert drift['required_live_horizon_ticks_for_value_equivalence'] == 3
    assert drift['blind_commit_value_bits_per_script'] == drift['value_equivalent_live_reoptimization_value_bits_per_script']

    zero = evaluate_state_deadline_inflation_profile((0, 0), 1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,2).numerator, Fraction(1,2).denominator, 2)
    assert zero['minimum_timeout_ticks_for_blind_commit_margin'] == 1
    assert zero['deadline_inflation_ticks'] == 0

    universal = evaluate_universal_deadline_inflation_profile(1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 2)
    assert universal['deadline_inflation_ticks'] == 1

    summary = build_geometric_arrival_deadline_inflation_validation_summary()
    assert summary['positive_inflation_state_panels'] > 0
    assert summary['zero_inflation_state_panels'] > 0
    assert summary['positive_inflation_universal_panels'] > 0
    print('shared-state equiprobable geometric-arrival deadline-inflation law checks passed')


if __name__ == '__main__':
    main()
