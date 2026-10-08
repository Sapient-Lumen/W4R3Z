#!/usr/bin/env python3
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_equiprobable_exact_shortest_script_geometric_arrival_checkpoint_extension_law import (
    build_geometric_arrival_checkpoint_extension_validation_summary,
    evaluate_checkpoint_extension_value_for_state,
    evaluate_ex_ante_extra_tick_value_for_state,
    evaluate_universal_checkpoint_extension_value,
)


def _fraction(payload: dict[str, int | float] | None) -> Fraction | None:
    if payload is None:
        return None
    return Fraction(int(payload['numerator']), int(payload['denominator']))


def main() -> None:
    validation = build_geometric_arrival_checkpoint_extension_validation_summary()
    assert validation['audited_state_count'] == 153
    assert validation['validated_state_checkpoint_panels'] == 153 * 8 * 4 * 4 * 6 * 6
    assert validation['validated_universal_lower_bound_panels'] == 153 * 8 * 4 * 4 * 6 * 6
    assert validation['validated_state_one_more_tick_panels'] == 153 * 8 * 4 * 4 * 6
    assert validation['validated_state_ex_ante_increment_panels'] == 153 * 8 * 4 * 4 * 6
    assert validation['validated_ex_ante_ratio_panels'] == 153 * 8 * 4 * 4 * 5

    start = evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 0, 3)
    streak = evaluate_checkpoint_extension_value_for_state((0, 16), 5, 1, 2, 1, 10, 4, 3)
    boundary = evaluate_checkpoint_extension_value_for_state((7, 12), 3, 1, 4, 1, 10, 5, 2)
    negative = evaluate_checkpoint_extension_value_for_state((0, 16), 4, 1, 4, 1, 10, 3, 1)
    universal = evaluate_universal_checkpoint_extension_value(3, 1, 2, 1, 10, 5, 2)
    increment = evaluate_ex_ante_extra_tick_value_for_state((0, 16), 5, 1, 2, 1, 10, 3)

    assert _fraction(start['conditional_expected_net_extension_value_bits_per_script']) == Fraction(7, 240)
    assert _fraction(streak['conditional_expected_net_extension_value_bits_per_script']) == Fraction(7, 240)
    assert _fraction(start['conditional_one_more_tick_extension_value_bits_per_script']) == Fraction(1, 60)
    assert _fraction(streak['conditional_one_more_tick_extension_value_bits_per_script']) == Fraction(1, 60)

    assert _fraction(boundary['conditional_expected_net_extension_value_bits_per_script']) == Fraction(7, 60)
    assert boundary['conditional_one_more_tick_sign'] == 'positive'

    assert _fraction(negative['conditional_expected_net_extension_value_bits_per_script']) == Fraction(-1, 80)
    assert _fraction(negative['conditional_one_more_tick_extension_value_bits_per_script']) == Fraction(-1, 80)
    assert negative['conditional_one_more_tick_sign'] == 'negative'

    assert _fraction(universal['conditional_expected_net_extension_value_bits_per_script']) == Fraction(23, 80)
    assert _fraction(universal['conditional_one_more_tick_extension_value_bits_per_script']) == Fraction(23, 120)

    assert _fraction(increment['start_of_wait_value_of_one_more_planned_tick_bits_per_script']) == Fraction(1, 480)
    assert _fraction(increment['checkpoint_value_if_that_tick_is_reached_bits_per_script']) == Fraction(1, 60)

    print('shared-state equiprobable geometric-arrival checkpoint-extension law checks passed')


if __name__ == '__main__':
    main()
