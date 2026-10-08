#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_effective_horizon_law import (
    build_geometric_arrival_effective_horizon_validation_summary,
    evaluate_state_effective_horizon_profile,
    evaluate_universal_effective_horizon_profile,
)


def main() -> None:
    drift = evaluate_state_effective_horizon_profile((0, 0), 1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 2)
    assert drift['effective_blind_commit_horizon_ticks'] == 1
    assert drift['minimum_timeout_ticks_for_blind_commit_margin'] == 2
    assert drift['live_countdown_preserves_original_margin'] is False
    assert drift['blind_commit_at_effective_horizon_preserves_original_margin'] is False

    repaired = evaluate_state_effective_horizon_profile((0, 0), 1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 3)
    assert repaired['effective_blind_commit_horizon_ticks'] == 2
    assert repaired['live_countdown_preserves_original_margin'] is True
    assert repaired['blind_commit_at_effective_horizon_preserves_original_margin'] is True

    universal = evaluate_universal_effective_horizon_profile(1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 2)
    assert universal['effective_blind_commit_horizon_ticks'] == 1
    assert universal['live_countdown_preserves_original_margin'] is False

    pair = evaluate_universal_effective_horizon_profile(1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 3)
    pair_even = evaluate_universal_effective_horizon_profile(1, Fraction(1,4).numerator, Fraction(1,4).denominator, Fraction(1,20).numerator, Fraction(1,20).denominator, Fraction(1,1).numerator, Fraction(1,1).denominator, 4)
    assert pair['effective_blind_commit_horizon_ticks'] == pair_even['effective_blind_commit_horizon_ticks'] == 2
    assert pair['live_countdown_preserves_original_margin'] == pair_even['live_countdown_preserves_original_margin']

    summary = build_geometric_arrival_effective_horizon_validation_summary()
    assert summary['state_preserved_panels'] > 0
    assert summary['state_not_preserved_panels'] > 0
    assert summary['state_odd_even_pair_equivalent_panels'] > 0
    assert summary['universal_odd_even_pair_equivalent_panels'] > 0
    print('shared-state equiprobable geometric-arrival effective-horizon law checks passed')


if __name__ == '__main__':
    main()
