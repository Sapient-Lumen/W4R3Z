#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law import (
    build_automaton_validation_summary,
    build_generated_chain_from_start,
    build_service_mode_suffix_successor_snapshot,
    build_successor_examples,
    build_successor_rows,
    build_successor_rule_summary,
    build_support_basis_summary,
    successor_state_code,
)

EXPECTED_CHAIN = ['S10', 'S9', 'E8', 'S8', 'S7', 'S6', 'E5', 'S5', 'S4', 'E3', 'S3', 'D2', 'S2', 'E1', 'S1', 'E0', 'T0']
EXPECTED_SUPPORT = {
    'exact_counter_support': [8, 5, 3, 1, 0],
    'shared_counter_support': [2],
    'suffix_stay_current_counters': [10, 8, 7, 5],
    'suffix_exact_handoff_current_counters': [9, 6, 4, 2, 1],
    'suffix_shared_handoff_current_counters': [3],
    'bridge_exact_current_counters': [8, 5, 3, 1],
    'terminal_exact_current_counter': [0],
    'bridge_shared_current_counters': [2],
}


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    snapshot = build_service_mode_suffix_successor_snapshot()
    rows = build_successor_rows()

    _assert_equal(build_generated_chain_from_start(), EXPECTED_CHAIN, 'generated chain mismatch')
    _assert_equal(build_support_basis_summary(), EXPECTED_SUPPORT, 'support basis mismatch')

    summary = build_successor_rule_summary()
    _assert_equal(summary['support_basis_size'], 6, 'support basis size mismatch')
    _assert_equal(summary['closed_form_successor_needs_only_two_support_sets'], True, 'closed form support claim mismatch')

    validation = build_automaton_validation_summary()
    _assert_equal(validation['all_rows_match_archived_chain_successor'], True, 'rowwise successor match mismatch')
    _assert_equal(validation['matched_row_count'], 17, 'matched row count mismatch')
    _assert_equal(validation['generated_chain_matches_archived_chain'], True, 'generated chain archive match mismatch')
    _assert_equal(validation['terminal_is_absorbing_under_closed_form'], True, 'terminal absorbing mismatch')

    _assert_equal(successor_state_code('S10'), 'S9', 'S10 successor mismatch')
    _assert_equal(successor_state_code('S9'), 'E8', 'S9 successor mismatch')
    _assert_equal(successor_state_code('S3'), 'D2', 'S3 successor mismatch')
    _assert_equal(successor_state_code('D2'), 'S2', 'D2 successor mismatch')
    _assert_equal(successor_state_code('E1'), 'S1', 'E1 successor mismatch')
    _assert_equal(successor_state_code('E0'), 'T0', 'E0 successor mismatch')
    _assert_equal(successor_state_code('T0'), 'T0', 'T0 successor mismatch')

    _assert_equal(len(rows), 17, 'row count mismatch')
    _assert_equal(all(row['prediction_matches_archived_chain'] for row in rows), True, 'rowwise prediction mismatch')

    examples = build_successor_examples()
    _assert_equal(examples[0]['current_signature'], 'E1_S2', 'selector example 0 signature mismatch')
    _assert_equal(examples[0]['predicted_next_state_code'], 'S7', 'selector example 0 next code mismatch')
    _assert_equal(examples[2]['current_signature'], 'E3_S8', 'selector example 2 signature mismatch')
    _assert_equal(examples[2]['predicted_next_state_code'], 'S2', 'selector example 2 next code mismatch')
    _assert_equal(examples[-1]['current_signature'], 'E6_S11', 'terminal example signature mismatch')
    _assert_equal(examples[-1]['predicted_next_state_code'], 'T0', 'terminal example next code mismatch')

    _assert_equal(snapshot['headline_findings']['automaton_validation_summary']['generated_chain_terminal'], 'T0', 'snapshot terminal mismatch')

    print('ok')


if __name__ == '__main__':
    main()
