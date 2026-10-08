#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law import (
    build_full_automaton_incoming_summary,
    build_predecessor_examples,
    build_predecessor_rows,
    build_predecessor_rule_summary,
    build_predecessor_support_summary,
    build_reverse_generated_chain_from_terminal,
    build_reverse_validation_summary,
    build_service_mode_suffix_predecessor_snapshot,
    strict_predecessor_state_code,
)

EXPECTED_REVERSE_CHAIN = ['T0', 'E0', 'S1', 'E1', 'S2', 'D2', 'S3', 'E3', 'S4', 'S5', 'E5', 'S6', 'S7', 'S8', 'E8', 'S9', 'S10']
EXPECTED_SUPPORT = {
    'source_code': 'S10',
    'terminal_code': 'T0',
    'exact_counter_support': [8, 5, 3, 1, 0],
    'shared_counter_support': [2],
    'suffix_states_with_suffix_predecessor': [9, 7, 6, 4],
    'suffix_states_with_exact_predecessor': [8, 5, 3, 1],
    'suffix_states_with_shared_predecessor': [2],
    'strict_predecessor_uses_same_two_support_sets_plus_boundaries': True,
}


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    snapshot = build_service_mode_suffix_predecessor_snapshot()
    rows = build_predecessor_rows()

    _assert_equal(build_predecessor_support_summary(), EXPECTED_SUPPORT, 'predecessor support summary mismatch')
    _assert_equal(build_reverse_generated_chain_from_terminal(), EXPECTED_REVERSE_CHAIN, 'reverse generated chain mismatch')

    summary = build_predecessor_rule_summary()
    _assert_equal(summary['strict_predecessor_uses_same_two_support_sets_as_successor'], True, 'support reuse claim mismatch')

    validation = build_reverse_validation_summary()
    _assert_equal(validation['all_rows_match_archived_chain_predecessor'], True, 'rowwise predecessor match mismatch')
    _assert_equal(validation['matched_row_count'], 17, 'matched row count mismatch')
    _assert_equal(validation['reverse_generated_chain_matches_archive_when_reversed'], True, 'reverse chain archive match mismatch')
    _assert_equal(validation['source_is_only_strict_null_predecessor'], True, 'source predecessor boundary mismatch')

    incoming = build_full_automaton_incoming_summary()
    _assert_equal(incoming['source_has_no_strict_predecessor'], True, 'source strict predecessor mismatch')
    _assert_equal(incoming['every_non_source_code_has_unique_strict_predecessor'], True, 'unique strict predecessor mismatch')
    _assert_equal(incoming['terminal_full_automaton_incoming_edges'], ['E0', 'T0'], 'terminal incoming edges mismatch')
    _assert_equal(incoming['terminal_is_only_code_with_absorbing_self_incoming_edge'], True, 'terminal absorbing edge mismatch')

    _assert_equal(strict_predecessor_state_code('S10'), None, 'S10 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('S9'), 'S10', 'S9 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('E8'), 'S9', 'E8 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('S8'), 'E8', 'S8 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('D2'), 'S3', 'D2 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('S2'), 'D2', 'S2 predecessor mismatch')
    _assert_equal(strict_predecessor_state_code('T0'), 'E0', 'T0 predecessor mismatch')

    _assert_equal(len(rows), 17, 'row count mismatch')
    _assert_equal(all(row['prediction_matches_archived_chain'] for row in rows), True, 'rowwise prediction mismatch')

    examples = build_predecessor_examples()
    _assert_equal(examples[0]['current_signature'], 'E1_S2', 'selector example 0 signature mismatch')
    _assert_equal(examples[0]['predicted_strict_predecessor_state_code'], 'E8', 'selector example 0 predecessor mismatch')
    _assert_equal(examples[1]['current_signature'], 'E3_S8', 'selector example 1 signature mismatch')
    _assert_equal(examples[1]['predicted_strict_predecessor_state_code'], 'S3', 'selector example 1 predecessor mismatch')
    _assert_equal(examples[-1]['current_signature'], 'terminal_absorbing', 'terminal example signature mismatch')
    _assert_equal(examples[-1]['predicted_strict_predecessor_state_code'], 'E0', 'terminal example predecessor mismatch')

    _assert_equal(snapshot['headline_findings']['reverse_validation_summary']['reverse_generated_chain_source'], 'S10', 'snapshot source mismatch')

    print('ok')


if __name__ == '__main__':
    main()
