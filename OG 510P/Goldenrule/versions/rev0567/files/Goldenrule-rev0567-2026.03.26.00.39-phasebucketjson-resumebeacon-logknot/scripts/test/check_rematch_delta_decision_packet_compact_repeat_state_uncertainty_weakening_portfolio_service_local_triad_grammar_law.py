#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law import (
    build_positive_service_local_triad_rows,
    build_service_local_triad_grammar_snapshot,
    build_shared_visibility_summary,
    build_triad_family_histogram,
    build_triad_histogram,
    select_local_corridor_triad,
)


EXPECTED_TRIAD_HISTOGRAM = {
    'S-E-S': 8,
    'E-S-E': 3,
    'E-S-D': 1,
    'S-D-S': 1,
    'D-S-E': 1,
    'S-E-T': 1,
    'E-T-T': 1,
    'T-T-T': 1,
}

EXPECTED_TRIAD_FAMILY_HISTOGRAM = {
    'alternating_bridge_core': 11,
    'diagonal_neighborhood': 3,
    'terminal_tail': 2,
    'terminal': 1,
}



def _assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(f'{message}: expected {expected!r}, got {actual!r}')



def main() -> None:
    snapshot = build_service_local_triad_grammar_snapshot()
    rows = build_positive_service_local_triad_rows()

    _assert_equal(build_triad_histogram(), EXPECTED_TRIAD_HISTOGRAM, 'triad histogram mismatch')
    _assert_equal(build_triad_family_histogram(), EXPECTED_TRIAD_FAMILY_HISTOGRAM, 'triad family histogram mismatch')

    visibility = build_shared_visibility_summary()
    _assert_equal(visibility['shared_visible_current_count'], 1, 'shared current count mismatch')
    _assert_equal(visibility['shared_visible_next_count'], 1, 'shared next count mismatch')
    _assert_equal(visibility['shared_visible_second_next_count'], 1, 'shared second-next count mismatch')
    _assert_equal(visibility['shared_visible_current_signatures'], ['E3_S8'], 'shared current signatures mismatch')
    _assert_equal(visibility['shared_visible_next_signatures'], ['E3_S7'], 'shared next signatures mismatch')
    _assert_equal(visibility['shared_visible_second_next_signatures'], ['E2_S7'], 'shared second-next signatures mismatch')

    _assert_equal(len(rows), 17, 'unexpected positive-service triad row count')
    _assert_equal(snapshot['headline_findings']['triad_consistency_summary']['triad_support_count'], 8, 'triad support mismatch')

    e2s7 = select_local_corridor_triad(0.05)
    _assert_equal(e2s7['current_signature'], 'E2_S7', 'E2_S7 selector signature mismatch')
    _assert_equal(e2s7['corridor_triad_signature'], 'E-S-D', 'E2_S7 triad mismatch')

    e3s7 = select_local_corridor_triad(0.0348)
    _assert_equal(e3s7['current_signature'], 'E3_S7', 'E3_S7 selector signature mismatch')
    _assert_equal(e3s7['corridor_triad_signature'], 'S-D-S', 'E3_S7 triad mismatch')

    e3s8 = select_local_corridor_triad(0.0184)
    _assert_equal(e3s8['current_signature'], 'E3_S8', 'E3_S8 selector signature mismatch')
    _assert_equal(e3s8['corridor_triad_signature'], 'D-S-E', 'E3_S8 triad mismatch')

    terminal = select_local_corridor_triad(0.0001)
    _assert_equal(terminal['current_signature'], 'E6_S11', 'terminal selector signature mismatch')
    _assert_equal(terminal['corridor_triad_signature'], 'T-T-T', 'terminal triad mismatch')

    print('ok')


if __name__ == '__main__':
    main()
