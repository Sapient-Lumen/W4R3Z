#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law import (
    build_counter_dynamics_summary,
    build_decoder_summary,
    build_mode_histogram,
    build_mode_support_summary,
    build_positive_service_mode_suffix_counter_rows,
    build_service_mode_suffix_counter_snapshot,
    build_state_code_chain,
    build_transition_class_histogram,
    select_service_mode_suffix_counter,
)

EXPECTED_CHAIN = ['S10', 'S9', 'E8', 'S8', 'S7', 'S6', 'E5', 'S5', 'S4', 'E3', 'S3', 'D2', 'S2', 'E1', 'S1', 'E0', 'T0']
EXPECTED_MODE_HISTOGRAM = {
    'suffix_only': 10,
    'exact_only': 5,
    'shared_diagonal': 1,
    'terminal': 1,
}
EXPECTED_TRANSITION_CLASS_HISTOGRAM = {
    'suffix_consume_and_stay_suffix': 4,
    'suffix_consume_and_handoff_to_exact': 5,
    'suffix_consume_and_handoff_to_shared': 1,
    'exact_bridge_preserve_counter': 4,
    'shared_bridge_preserve_counter': 1,
    'terminal_entry_preserve_zero': 1,
}


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    snapshot = build_service_mode_suffix_counter_snapshot()
    rows = build_positive_service_mode_suffix_counter_rows()

    _assert_equal(build_state_code_chain(), EXPECTED_CHAIN, 'state code chain mismatch')
    _assert_equal(build_mode_histogram(), EXPECTED_MODE_HISTOGRAM, 'mode histogram mismatch')
    _assert_equal(build_transition_class_histogram(), EXPECTED_TRANSITION_CLASS_HISTOGRAM, 'transition class histogram mismatch')

    support = build_mode_support_summary()
    _assert_equal(support['suffix_mode_counter_support'], [10, 9, 8, 7, 6, 5, 4, 3, 2, 1], 'suffix support mismatch')
    _assert_equal(support['exact_mode_counter_support'], [8, 5, 3, 1, 0], 'exact support mismatch')
    _assert_equal(support['shared_mode_counter_support'], [2], 'shared support mismatch')
    _assert_equal(support['terminal_mode_counter_support'], [0], 'terminal support mismatch')

    decoder = build_decoder_summary()
    _assert_equal(decoder['state_code_count'], 17, 'state code count mismatch')
    _assert_equal(decoder['state_codes_are_unique'], True, 'state code uniqueness mismatch')
    _assert_equal(decoder['state_code_decodes_full_signature'], True, 'signature decode mismatch')
    _assert_equal(decoder['state_code_decodes_full_residual_budget'], True, 'residual decode mismatch')

    dynamics = build_counter_dynamics_summary()
    _assert_equal(dynamics['counter_delta_support'], [-1, 0], 'counter delta support mismatch')
    _assert_equal(dynamics['every_nonterminal_step_keeps_or_decrements_suffix_counter_by_one'], True, 'counter monotonicity mismatch')
    _assert_equal(dynamics['only_suffix_mode_consumes_counter'], True, 'counter consumption mode mismatch')
    _assert_equal(dynamics['non_suffix_modes_are_zero_consumption_bridge_states'], True, 'bridge zero-consumption mismatch')

    _assert_equal(len(rows), 17, 'row count mismatch')
    _assert_equal(snapshot['headline_findings']['decoder_summary']['exact_counter_is_not_needed_as_a_primitive_coordinate'], True, 'primitive coordinate claim mismatch')

    e2s7 = select_service_mode_suffix_counter(0.05)
    _assert_equal(e2s7['current_signature'], 'E2_S7', 'E2_S7 selector signature mismatch')
    _assert_equal(e2s7['state_code'], 'E3', 'E2_S7 selector code mismatch')

    e3s8 = select_service_mode_suffix_counter(0.0184)
    _assert_equal(e3s8['current_signature'], 'E3_S8', 'E3_S8 selector signature mismatch')
    _assert_equal(e3s8['state_code'], 'D2', 'E3_S8 selector code mismatch')

    terminal = select_service_mode_suffix_counter(0.0001)
    _assert_equal(terminal['current_signature'], 'E6_S11', 'terminal selector signature mismatch')
    _assert_equal(terminal['state_code'], 'T0', 'terminal selector code mismatch')

    print('ok')


if __name__ == '__main__':
    main()
