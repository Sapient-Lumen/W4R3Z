#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law import (
    build_portfolio_guardrail_profile_counts,
    build_portfolio_signature_partition,
    build_weakening_portfolio_guardrail_law_snapshot,
    select_minimal_guardrail_profile_for_portfolio,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')


def main() -> None:
    _assert_equal(
        build_portfolio_guardrail_profile_counts(),
        {
            'exact_only': 63,
            'precision_hitchhike_only': 960,
            'suffix_hitchhike_only': 1984,
            'any_single_axis_hitchhike': 29760,
        },
        'portfolio minimal-profile counts',
    )

    _assert_equal(
        [(row['signature_label'], row['minimal_profile_label'], row['portfolio_count']) for row in build_portfolio_signature_partition()],
        [
            ('exact_only_portfolios', 'exact_only', 63),
            ('precision_family_only_portfolios', 'precision_hitchhike_only', 960),
            ('suffix_family_only_portfolios', 'suffix_hitchhike_only', 1984),
            ('mixed_hole_family_portfolios', 'any_single_axis_hitchhike', 29760),
        ],
        'portfolio signature partition',
    )

    _assert_equal(
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
        ])['minimal_profile_label'],
        'exact_only',
        'exact-only portfolio profile',
    )
    _assert_equal(
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 3},
        ])['minimal_profile_label'],
        'precision_hitchhike_only',
        'deep suffix portfolio profile',
    )
    _assert_equal(
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 1},
        ])['minimal_profile_label'],
        'suffix_hitchhike_only',
        'early precision portfolio profile',
    )
    mixed = select_minimal_guardrail_profile_for_portfolio([
        {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
        {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
    ])
    _assert_equal(mixed['minimal_profile_label'], 'any_single_axis_hitchhike', 'mixed-family portfolio profile')
    _assert_equal(mixed['dual_axis_permission_is_minimally_necessary'], True, 'mixed-family dual-axis necessity')

    report = build_weakening_portfolio_guardrail_law_snapshot()
    _assert_equal(
        report['headline_findings']['minimal_profile_count_by_portfolio'],
        {
            'exact_only': 63,
            'precision_hitchhike_only': 960,
            'suffix_hitchhike_only': 1984,
            'any_single_axis_hitchhike': 29760,
        },
        'headline portfolio counts',
    )
    _assert_equal(
        report['headline_findings']['singleton_portfolios_requiring_dual_axis_permission'],
        0,
        'headline singleton dual-axis count',
    )
    _assert_equal(
        report['headline_findings']['dual_axis_permission_is_minimal_exactly_when_both_one_axis_hole_families_appear'],
        True,
        'headline mixed-family exactness flag',
    )

    print('weakening portfolio guardrail law checks passed')


if __name__ == '__main__':
    main()
