#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fractions import Fraction

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_law import (
    build_affine_margin_family_summary,
    build_affine_margin_validation_summary,
    build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile,
    evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin,
)


def _fraction(payload: dict[str, int | float]) -> Fraction:
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    family_summary = build_affine_margin_family_summary()
    assert family_summary['family_count'] == 7
    assert family_summary['catalog_state_count'] == 153

    validation = build_affine_margin_validation_summary()
    assert validation['validated_state_batch_pairs'] == 153 * 8
    assert validation['universal_lower_envelope_formula'] == '43n/9 - 8'
    assert validation['strict_expected_universal_switch_batch_length'] == 2
    assert validation['one_word_tie_state_count'] == 32

    profile = build_shared_interval_state_equiprobable_exact_shortest_script_affine_margin_profile((15, 15))
    assert profile['affine_margin_family'] == 'fifteen_fifteen_exception_margin'
    assert profile['affine_margin_formula'] == '44n/9 - 8'

    assert _fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin((8, 8), 2)['affine_equiprobable_margin_bits']
    ) == Fraction(14, 9)
    assert _fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin((15, 15), 2)['affine_equiprobable_margin_bits']
    ) == Fraction(16, 9)
    assert _fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin((7, 12), 1)['affine_equiprobable_margin_bits']
    ) == Fraction(0, 1)
    assert _fraction(
        evaluate_shared_interval_state_equiprobable_exact_shortest_script_affine_margin((1, 2), 2)['affine_equiprobable_margin_bits']
    ) == Fraction(9, 1)

    minima = validation['minimum_margin_by_batch_length']
    assert minima[0]['representative_minimizer_state']['interval'] == [8, 8]
    assert _fraction(minima[0]['minimum_margin_bits']) == Fraction(-29, 9)
    assert _fraction(minima[1]['minimum_margin_bits']) == Fraction(14, 9)

    print('shared-state equiprobable affine-margin law checks passed')


if __name__ == '__main__':
    main()
