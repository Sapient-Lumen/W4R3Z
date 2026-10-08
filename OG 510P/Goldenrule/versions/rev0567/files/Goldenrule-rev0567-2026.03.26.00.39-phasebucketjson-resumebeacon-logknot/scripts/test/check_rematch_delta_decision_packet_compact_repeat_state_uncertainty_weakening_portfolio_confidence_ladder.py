#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder import (
    build_dual_axis_confidence_thresholds,
    build_portfolio_confidence_rows,
    build_suffix_tail_confidence_thresholds,
)


def main() -> int:
    dual = {row['confidence_level']: row['minimum_portfolio_size'] for row in build_dual_axis_confidence_thresholds()}
    suffix = {row['suffix_tail_share_level']: row['minimum_portfolio_size'] for row in build_suffix_tail_confidence_thresholds()}
    expected_dual = {0.5: 4, 0.75: 5, 0.9: 7, 0.95: 8, 0.99: 10, 0.999: 11}
    expected_suffix = {0.5: 3, 0.75: 8, 0.9: 10, 1.0: 11}
    if dual != expected_dual:
        print(f'portfolio-confidence-ladder: unexpected dual thresholds {dual}', file=sys.stderr)
        return 1
    if suffix != expected_suffix:
        print(f'portfolio-confidence-ladder: unexpected suffix thresholds {suffix}', file=sys.stderr)
        return 1

    rows = build_portfolio_confidence_rows()
    if not all(row['suffix_dominates_non_dual_tail'] for row in rows if row['portfolio_size'] >= 2 and row['non_dual_count']):
        print('portfolio-confidence-ladder: suffix should dominate every non-dual tail from width 2 onward', file=sys.stderr)
        return 1
    if not all(
        rows[i]['dual_axis_share']['value'] <= rows[i + 1]['dual_axis_share']['value']
        for i in range(len(rows) - 1)
    ):
        print('portfolio-confidence-ladder: dual-axis share should be nondecreasing with width', file=sys.stderr)
        return 1
    if not all(
        rows[i]['dual_axis_share']['value'] < rows[i + 1]['dual_axis_share']['value']
        for i in range(11)
    ):
        print('portfolio-confidence-ladder: dual-axis share should increase strictly through the universal width cutoff', file=sys.stderr)
        return 1

    width_11 = next(row for row in rows if row['portfolio_size'] == 11)
    if width_11['tail_profile_shares']['suffix_hitchhike_only']['value'] != 1.0:
        print('portfolio-confidence-ladder: width 11 should have a pure suffix-only tail', file=sys.stderr)
        return 1

    print('portfolio-confidence-ladder: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
