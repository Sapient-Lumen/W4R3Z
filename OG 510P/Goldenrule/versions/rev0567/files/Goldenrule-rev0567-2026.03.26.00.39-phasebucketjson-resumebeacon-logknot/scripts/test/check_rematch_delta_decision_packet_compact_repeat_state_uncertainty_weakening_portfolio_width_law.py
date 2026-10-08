#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law import (
    build_portfolio_width_profile_rows,
    build_weakening_portfolio_width_law_snapshot,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    rows = build_portfolio_width_profile_rows()
    _assert_equal(len(rows), 15, 'portfolio width row count')
    _assert_equal(
        rows[0]['minimal_profile_counts'],
        {
            'exact_only': 6,
            'precision_hitchhike_only': 4,
            'suffix_hitchhike_only': 5,
            'any_single_axis_hitchhike': 0,
        },
        'width-1 profile counts',
    )
    _assert_equal(
        rows[3]['minimal_profile_counts'],
        {
            'exact_only': 15,
            'precision_hitchhike_only': 195,
            'suffix_hitchhike_only': 315,
            'any_single_axis_hitchhike': 840,
        },
        'width-4 profile counts',
    )
    _assert_equal(rows[3]['dual_axis_majority'], True, 'width-4 dual-axis majority')
    _assert_equal(
        rows[10]['minimal_profile_counts'],
        {
            'exact_only': 0,
            'precision_hitchhike_only': 0,
            'suffix_hitchhike_only': 1,
            'any_single_axis_hitchhike': 1364,
        },
        'width-11 profile counts',
    )
    _assert_equal(rows[11]['dual_axis_universal'], True, 'width-12 dual-axis universality')

    report = build_weakening_portfolio_width_law_snapshot()
    _assert_equal(report['headline_findings']['dual_axis_majority_begins_at_portfolio_size'], 4, 'majority threshold')
    _assert_equal(report['headline_findings']['dual_axis_universality_begins_at_portfolio_size'], 12, 'universality threshold')
    _assert_equal(report['headline_findings']['exact_only_last_possible_portfolio_size'], 6, 'exact-only last width')
    _assert_equal(report['headline_findings']['precision_only_last_possible_portfolio_size'], 10, 'precision-only last width')
    _assert_equal(report['headline_findings']['suffix_only_last_possible_portfolio_size'], 11, 'suffix-only last width')
    _assert_equal(report['headline_findings']['size_11_last_non_dual_axis_exception_count'], 1, 'width-11 exception count')
    _assert_equal(report['headline_findings']['size_12_and_above_force_dual_axis_permission'], True, 'width-12 universal flag')

    print('weakening portfolio width law checks passed')


if __name__ == '__main__':
    main()
