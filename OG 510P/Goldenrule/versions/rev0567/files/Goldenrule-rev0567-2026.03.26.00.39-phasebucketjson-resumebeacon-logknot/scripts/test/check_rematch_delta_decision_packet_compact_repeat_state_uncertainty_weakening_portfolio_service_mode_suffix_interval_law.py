#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law import (
    build_interval_examples,
    build_interval_validation_summary,
    build_service_mode_suffix_interval_snapshot,
    build_segment_examples,
    select_clock_segment,
    select_mode_suffix_clock_interval,
)


def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')


def main() -> None:
    snapshot = build_service_mode_suffix_interval_snapshot()
    validation = build_interval_validation_summary()

    _assert_equal(validation['window_validation_count'], 4913, 'window validation count mismatch')
    _assert_equal(validation['every_bounded_neighborhood_is_a_contiguous_rank_interval'], True, 'contiguous interval claim mismatch')
    _assert_equal(validation['every_segment_cardinality_matches_distance_plus_one'], True, 'segment cardinality claim mismatch')
    _assert_equal(validation['maximum_interval_cardinality'], 17, 'maximum interval cardinality mismatch')
    _assert_equal(validation['full_chain_is_realized_as_one_interval'], True, 'full chain interval mismatch')
    _assert_equal(validation['clipped_forward_validation_count'], 2312, 'clipped forward count mismatch')
    _assert_equal(validation['clipped_backward_validation_count'], 2312, 'clipped backward count mismatch')

    interval = select_mode_suffix_clock_interval('E3', max_forward_steps=2, max_backward_steps=3)
    _assert_equal(interval['lower_source_rank'], 6, 'E3 interval lower rank mismatch')
    _assert_equal(interval['upper_source_rank'], 11, 'E3 interval upper rank mismatch')
    _assert_equal(interval['lower_terminal_distance_clock'], 5, 'E3 interval lower clock mismatch')
    _assert_equal(interval['upper_terminal_distance_clock'], 10, 'E3 interval upper clock mismatch')
    _assert_equal(interval['interval_cardinality'], 6, 'E3 interval cardinality mismatch')
    _assert_equal(interval['boundary_backward_code'], 'E5', 'E3 backward boundary mismatch')
    _assert_equal(interval['boundary_forward_code'], 'D2', 'E3 forward boundary mismatch')
    _assert_equal(interval['interval_state_codes'], ['E5', 'S5', 'S4', 'E3', 'S3', 'D2'], 'E3 interval codes mismatch')
    _assert_equal(interval['interval_matches_replay_union'], True, 'E3 replay union mismatch')

    source_window = select_mode_suffix_clock_interval('S10', max_forward_steps=4, max_backward_steps=3)
    _assert_equal(source_window['boundary_backward_code'], 'S10', 'source backward clipping mismatch')
    _assert_equal(source_window['boundary_forward_code'], 'S7', 'source forward boundary mismatch')
    _assert_equal(source_window['interval_cardinality'], 5, 'source interval cardinality mismatch')

    terminal_window = select_mode_suffix_clock_interval('T0', max_forward_steps=2, max_backward_steps=4)
    _assert_equal(terminal_window['boundary_backward_code'], 'S2', 'terminal backward boundary mismatch')
    _assert_equal(terminal_window['boundary_forward_code'], 'T0', 'terminal forward clipping mismatch')
    _assert_equal(terminal_window['interval_state_codes'], ['S2', 'E1', 'S1', 'E0', 'T0'], 'terminal interval codes mismatch')

    segment = select_clock_segment('E8', 'D2')
    _assert_equal(segment['segment_cardinality'], 10, 'E8/D2 segment cardinality mismatch')
    _assert_equal(segment['pairwise_path_distance'], 9, 'E8/D2 distance mismatch')
    _assert_equal(segment['segment_cardinality_matches_distance_plus_one'], True, 'E8/D2 segment law mismatch')

    examples = build_interval_examples()
    _assert_equal(examples[0]['state_code'], 'S8', 'example 0 state mismatch')
    _assert_equal(examples[0]['interval_cardinality'], 4, 'example 0 interval cardinality mismatch')
    _assert_equal(examples[-1]['state_code'], 'T0', 'example final state mismatch')
    _assert_equal(examples[-1]['boundary_backward_code'], 'E1', 'example final backward boundary mismatch')

    segments = build_segment_examples()
    _assert_equal(segments[0]['segment_cardinality'], 17, 'full-chain segment mismatch')
    _assert_equal(segments[-1]['segment_state_codes'], ['D2', 'S2', 'E1', 'S1', 'E0'], 'tail segment mismatch')

    _assert_equal(snapshot['headline_findings']['max_clock'], 16, 'snapshot max clock mismatch')

    print('ok')


if __name__ == '__main__':
    main()
