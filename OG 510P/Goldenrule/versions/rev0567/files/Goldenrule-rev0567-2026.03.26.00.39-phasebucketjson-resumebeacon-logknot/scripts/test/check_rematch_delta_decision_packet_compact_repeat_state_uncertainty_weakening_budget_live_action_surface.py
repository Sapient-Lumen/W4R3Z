#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface import (
    build_budget_action_surface,
    build_marginal_live_flips,
    build_weakening_budget_live_action_surface_snapshot,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    surface = build_budget_action_surface()
    _assert_equal(len(surface), 6, 'budget surface size')
    _assert_equal([row['released_live_weakening_count'] for row in surface], [0, 1, 2, 3, 4, 5], 'released live weakening counts')
    _assert_equal([row['action_counts']['strengthen'] for row in surface], [7, 7, 7, 7, 7, 7], 'strengthen counts')
    _assert_equal([row['action_counts']['hold'] for row in surface], [6, 6, 5, 4, 4, 3], 'hold counts')
    _assert_equal([row['action_counts']['stabilize'] for row in surface], [5, 4, 4, 4, 3, 3], 'stabilize counts')
    _assert_equal([row['action_counts']['weaken'] for row in surface], [0, 1, 2, 3, 4, 5], 'weaken counts')

    flips = build_marginal_live_flips()
    _assert_equal(len(flips), 5, 'marginal flip count')
    _assert_equal([row['from_action_family'] for row in flips], ['stabilize', 'hold', 'hold', 'stabilize', 'hold'], 'flip source families')
    _assert_equal([row['to_action_family'] for row in flips], ['weaken', 'weaken', 'weaken', 'weaken', 'weaken'], 'flip target families')
    _assert_equal(
        [(row['current_state_unique_appends'], row['required_gain_share_floor']) for row in flips],
        [(18, '0.84'), (2, '0.95'), (13, '0.84'), (8, '0.84'), (2, '0.84')],
        'flip cases in order',
    )

    report = build_weakening_budget_live_action_surface_snapshot()
    _assert_equal(report['headline_findings']['live_matrix_case_count'], 18, 'live matrix case count')
    _assert_equal(report['headline_findings']['constant_strengthening_count_across_budgets'], 7, 'constant strengthening count')
    _assert_equal(report['headline_findings']['exactly_one_live_matrix_flip_per_budget_step'], True, 'single flip per step')

    print('weakening budget live-action surface checks passed')


if __name__ == '__main__':
    main()
