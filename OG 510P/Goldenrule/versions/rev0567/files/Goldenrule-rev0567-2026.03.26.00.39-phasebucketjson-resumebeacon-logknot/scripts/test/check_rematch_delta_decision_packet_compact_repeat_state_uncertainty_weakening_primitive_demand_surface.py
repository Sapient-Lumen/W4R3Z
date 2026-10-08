#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface import (
    build_budget_coordinate_path,
    build_primitive_demand_surface,
    build_unreachable_demand_classes,
    build_weakening_primitive_demand_surface_snapshot,
    select_budget_by_primitive_demand,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    budget_path = build_budget_coordinate_path()
    _assert_equal(
        [row['coordinate'] for row in budget_path],
        [
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 2},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 3},
            {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 4},
        ],
        'budget coordinate path',
    )

    surface = build_primitive_demand_surface()
    _assert_equal(len(surface), 15, 'primitive demand surface size')
    _assert_equal(sum(1 for row in surface if row['exact_coordinate_reachable']), 6, 'exact reachable coordinate count')
    _assert_equal(sum(1 for row in surface if not row['exact_coordinate_reachable']), 9, 'unreachable coordinate count')

    _assert_equal(
        select_budget_by_primitive_demand(0, 2),
        {
            'demand_coordinate': {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
            'selected_budget': 3,
            'selected_threshold_unique_appends': 12,
            'selected_regime_label': 'staged relaxed release',
            'selected_coordinate': {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 2},
            'exact_coordinate_reachable': False,
            'overshoot_coordinate': {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
        },
        'selector for demand (0,2)',
    )
    _assert_equal(
        select_budget_by_primitive_demand(1, 0),
        {
            'demand_coordinate': {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
            'selected_budget': 2,
            'selected_threshold_unique_appends': 11,
            'selected_regime_label': 'middle-only precision relief',
            'selected_coordinate': {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
            'exact_coordinate_reachable': False,
            'overshoot_coordinate': {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1},
        },
        'selector for demand (1,0)',
    )
    _assert_equal(
        select_budget_by_primitive_demand(2, 1),
        {
            'demand_coordinate': {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 1},
            'selected_budget': 5,
            'selected_threshold_unique_appends': 23,
            'selected_regime_label': 'full release',
            'selected_coordinate': {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 4},
            'exact_coordinate_reachable': False,
            'overshoot_coordinate': {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 3},
        },
        'selector for demand (2,1)',
    )

    unreachable_classes = build_unreachable_demand_classes()
    _assert_equal(len(unreachable_classes), 9, 'unreachable demand class count')

    report = build_weakening_primitive_demand_surface_snapshot()
    _assert_equal(report['headline_findings']['primitive_box_point_count'], 15, 'headline box point count')
    _assert_equal(report['headline_findings']['hole_families']['deep_suffix_without_precision_demands'], [
        {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
        {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 3},
        {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 4},
    ], 'headline deep suffix hole family')
    _assert_equal(report['headline_findings']['exact_reachable_coordinate_count'], 6, 'headline exact reachable count')
    _assert_equal(report['headline_findings']['exact_unreachable_coordinate_count'], 9, 'headline exact unreachable count')
    _assert_equal(report['headline_findings']['scalar_menu_is_chain_not_product'], True, 'headline chain flag')
    _assert_equal(report['headline_findings']['all_unreachable_demands_require_hitchhiking_overshoot'], True, 'headline overshoot flag')

    print('weakening primitive demand surface checks passed')


if __name__ == '__main__':
    main()
