#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law import (
    build_clock_basis_summary,
    build_clock_chain,
    build_clock_validation_summary,
    build_distance_examples,
    build_mode_clock_summary,
    build_rank_chain,
    build_rank_clock_rows,
    build_service_mode_suffix_rank_clock_snapshot,
    pairwise_path_distance,
    source_rank,
    terminal_distance_clock,
)

EXPECTED_CLOCK_CHAIN = [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
EXPECTED_RANK_CHAIN = list(range(17))
EXPECTED_BASIS = {
    'source_code': 'S10',
    'terminal_code': 'T0',
    'max_clock': 16,
    'exact_counter_support': [8, 5, 3, 1, 0],
    'shared_counter_support': [2],
    'clock_formula': 'counter + bridge_tail_count(counter) + current_bridge_tax(mode), with T0 fixed at 0',
    'bridge_tail_count_rule': 'count exact/shared supports at counters <= k-1',
    'current_bridge_tax_rule': {'suffix_only': 0, 'exact_only': 1, 'shared_diagonal': 1, 'terminal': 0},
}


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    snapshot = build_service_mode_suffix_rank_clock_snapshot()
    rows = build_rank_clock_rows()

    _assert_equal(build_clock_basis_summary(), EXPECTED_BASIS, 'clock basis summary mismatch')
    _assert_equal(build_clock_chain(), EXPECTED_CLOCK_CHAIN, 'clock chain mismatch')
    _assert_equal(build_rank_chain(), EXPECTED_RANK_CHAIN, 'rank chain mismatch')

    validation = build_clock_validation_summary()
    _assert_equal(validation['all_rows_match_archived_terminal_distance'], True, 'terminal distance row match mismatch')
    _assert_equal(validation['all_rows_match_archived_source_rank'], True, 'source rank row match mismatch')
    _assert_equal(validation['clock_chain_is_dense_16_to_0'], True, 'dense clock mismatch')
    _assert_equal(validation['rank_chain_is_dense_0_to_16'], True, 'dense rank mismatch')
    _assert_equal(validation['source_rank_plus_terminal_distance_equals_max_clock_everywhere'], True, 'rank+clock conservation mismatch')
    _assert_equal(validation['successor_decrements_clock_by_one_everywhere_except_absorbing_terminal'], True, 'successor clock decrement mismatch')
    _assert_equal(validation['strict_predecessor_increments_clock_by_one_everywhere_except_source_boundary'], True, 'predecessor clock increment mismatch')
    _assert_equal(validation['pairwise_path_distance_matches_absolute_clock_difference'], True, 'pairwise distance mismatch')
    _assert_equal(validation['pairwise_validation_count'], 136, 'pairwise validation count mismatch')

    _assert_equal(len(rows), 17, 'row count mismatch')
    _assert_equal(rows[0]['state_code'], 'S10', 'row 0 code mismatch')
    _assert_equal(rows[0]['predicted_terminal_distance_clock'], 16, 'S10 terminal distance mismatch')
    _assert_equal(rows[2]['state_code'], 'E8', 'row 2 code mismatch')
    _assert_equal(rows[2]['bridge_tail_count'], 5, 'E8 bridge tail mismatch')
    _assert_equal(rows[2]['current_bridge_tax'], 1, 'E8 bridge tax mismatch')
    _assert_equal(rows[11]['state_code'], 'D2', 'row 11 code mismatch')
    _assert_equal(rows[11]['predicted_terminal_distance_clock'], 5, 'D2 terminal distance mismatch')
    _assert_equal(rows[-1]['state_code'], 'T0', 'terminal code mismatch')
    _assert_equal(rows[-1]['predicted_source_rank'], 16, 'terminal source rank mismatch')

    _assert_equal(terminal_distance_clock('S10'), 16, 'S10 clock mismatch')
    _assert_equal(terminal_distance_clock('E8'), 14, 'E8 clock mismatch')
    _assert_equal(terminal_distance_clock('D2'), 5, 'D2 clock mismatch')
    _assert_equal(terminal_distance_clock('E0'), 1, 'E0 clock mismatch')
    _assert_equal(terminal_distance_clock('T0'), 0, 'T0 clock mismatch')
    _assert_equal(source_rank('S10'), 0, 'S10 source rank mismatch')
    _assert_equal(source_rank('E3'), 9, 'E3 source rank mismatch')
    _assert_equal(source_rank('T0'), 16, 'T0 source rank mismatch')

    _assert_equal(pairwise_path_distance('S10', 'T0'), 16, 'S10/T0 path distance mismatch')
    _assert_equal(pairwise_path_distance('E8', 'D2'), 9, 'E8/D2 path distance mismatch')
    _assert_equal(pairwise_path_distance('S8', 'E3'), 6, 'S8/E3 path distance mismatch')
    _assert_equal(pairwise_path_distance('D2', 'E0'), 4, 'D2/E0 path distance mismatch')

    mode_summary = build_mode_clock_summary()
    _assert_equal(mode_summary['terminal_distance_clock_support_by_mode']['exact_only'], [14, 10, 7, 3, 1], 'exact mode clock support mismatch')
    _assert_equal(mode_summary['terminal_distance_clock_support_by_mode']['shared_diagonal'], [5], 'shared mode clock support mismatch')
    _assert_equal(mode_summary['suffix_mode_fills_every_remaining_positive_clock'], True, 'suffix fill claim mismatch')

    examples = build_distance_examples()
    _assert_equal(examples[0]['pairwise_path_distance'], 16, 'example 0 path distance mismatch')
    _assert_equal(examples[1]['pairwise_path_distance'], 9, 'example 1 path distance mismatch')
    _assert_equal(examples[-1]['state_code'], 'T0', 'selector example terminal code mismatch')
    _assert_equal(examples[-1]['terminal_distance_clock'], 0, 'selector example terminal clock mismatch')

    _assert_equal(snapshot['headline_findings']['clock_chain'], EXPECTED_CLOCK_CHAIN, 'snapshot clock chain mismatch')

    print('ok')


if __name__ == '__main__':
    main()
