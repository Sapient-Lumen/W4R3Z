#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector import (
    select_weakening_regime_by_recovered_case_budget,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger import (
    build_cumulative_primitive_budget_path,
)


class WeakeningPrimitiveDemandSurfaceError(RuntimeError):
    pass


PRIMITIVE_AXES = [
    'middle_precision_relief_units',
    'relaxed_suffix_release_units',
]


@lru_cache(maxsize=1)
def build_budget_coordinate_path() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_cumulative_primitive_budget_path():
        selector = select_weakening_regime_by_recovered_case_budget(row['budget'])
        coordinate = row['cumulative_primitive_signature']
        rows.append(
            {
                'budget': row['budget'],
                'threshold_unique_appends': selector['selected_threshold_unique_appends'],
                'selected_regime_label': selector['selected_regime_label'],
                'coordinate': coordinate,
            }
        )
    return rows



def select_budget_by_primitive_demand(
    minimum_middle_precision_relief_units: int,
    minimum_relaxed_suffix_release_units: int,
) -> dict[str, Any]:
    if minimum_middle_precision_relief_units < 0 or minimum_relaxed_suffix_release_units < 0:
        raise WeakeningPrimitiveDemandSurfaceError('primitive demand counts must be non-negative')

    demand = {
        'middle_precision_relief_units': minimum_middle_precision_relief_units,
        'relaxed_suffix_release_units': minimum_relaxed_suffix_release_units,
    }
    for row in build_budget_coordinate_path():
        coordinate = row['coordinate']
        if all(coordinate[axis] >= demand[axis] for axis in PRIMITIVE_AXES):
            overshoot = {
                axis: coordinate[axis] - demand[axis]
                for axis in PRIMITIVE_AXES
            }
            return {
                'demand_coordinate': demand,
                'selected_budget': row['budget'],
                'selected_threshold_unique_appends': row['threshold_unique_appends'],
                'selected_regime_label': row['selected_regime_label'],
                'selected_coordinate': coordinate,
                'exact_coordinate_reachable': overshoot == {
                    'middle_precision_relief_units': 0,
                    'relaxed_suffix_release_units': 0,
                },
                'overshoot_coordinate': overshoot,
            }
    raise WeakeningPrimitiveDemandSurfaceError(f'no budget satisfies demand {demand}')



@lru_cache(maxsize=1)
def build_primitive_demand_surface() -> list[dict[str, Any]]:
    path = build_budget_coordinate_path()
    max_precision = max(row['coordinate']['middle_precision_relief_units'] for row in path)
    max_suffix = max(row['coordinate']['relaxed_suffix_release_units'] for row in path)

    rows: list[dict[str, Any]] = []
    for precision in range(max_precision + 1):
        for suffix in range(max_suffix + 1):
            selection = select_budget_by_primitive_demand(precision, suffix)
            rows.append(selection)
    return rows



@lru_cache(maxsize=1)
def build_unreachable_demand_classes() -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in build_primitive_demand_surface():
        if row['exact_coordinate_reachable']:
            continue
        key = (
            row['selected_budget'],
            row['overshoot_coordinate']['middle_precision_relief_units'],
            row['overshoot_coordinate']['relaxed_suffix_release_units'],
        )
        grouped[key].append(row)

    classes: list[dict[str, Any]] = []
    for key, rows in grouped.items():
        exemplar = rows[0]
        classes.append(
            {
                'selected_budget': exemplar['selected_budget'],
                'selected_threshold_unique_appends': exemplar['selected_threshold_unique_appends'],
                'selected_coordinate': exemplar['selected_coordinate'],
                'overshoot_coordinate': exemplar['overshoot_coordinate'],
                'member_demands': [row['demand_coordinate'] for row in rows],
                'member_count': len(rows),
            }
        )
    return sorted(
        classes,
        key=lambda row: (
            row['selected_budget'],
            row['overshoot_coordinate']['middle_precision_relief_units'],
            row['overshoot_coordinate']['relaxed_suffix_release_units'],
        ),
    )



def build_weakening_primitive_demand_surface_snapshot() -> dict[str, Any]:
    budget_path = build_budget_coordinate_path()
    surface = build_primitive_demand_surface()
    unreachable_classes = build_unreachable_demand_classes()

    exact_rows = [row for row in surface if row['exact_coordinate_reachable']]
    unreachable_rows = [row for row in surface if not row['exact_coordinate_reachable']]
    exact_coordinates = [row['demand_coordinate'] for row in exact_rows]
    exact_coordinate_labels = [
        f"({row['demand_coordinate']['middle_precision_relief_units']},{row['demand_coordinate']['relaxed_suffix_release_units']})"
        for row in exact_rows
    ]

    budget_to_exact_count: dict[str, int] = {}
    budget_to_unreachable_count: dict[str, int] = {}
    for budget in [row['budget'] for row in budget_path]:
        budget_to_exact_count[str(budget)] = sum(1 for row in exact_rows if row['selected_budget'] == budget)
        budget_to_unreachable_count[str(budget)] = sum(1 for row in unreachable_rows if row['selected_budget'] == budget)

    if len(exact_rows) != len(budget_path):
        raise WeakeningPrimitiveDemandSurfaceError(
            f'exact reachable coordinate count should match budget path length: {len(exact_rows)} vs {len(budget_path)}'
        )

    hole_families = {
        'precision_without_suffix_demands': [
            row['demand_coordinate']
            for row in unreachable_rows
            if row['demand_coordinate']['middle_precision_relief_units'] > 0
            and row['demand_coordinate']['relaxed_suffix_release_units'] == 0
        ],
        'deep_suffix_without_precision_demands': [
            row['demand_coordinate']
            for row in unreachable_rows
            if row['demand_coordinate']['middle_precision_relief_units'] == 0
            and row['demand_coordinate']['relaxed_suffix_release_units'] > 1
        ],
        'second_precision_before_final_suffix_demands': [
            row['demand_coordinate']
            for row in unreachable_rows
            if row['demand_coordinate']['middle_precision_relief_units'] == 2
            and row['demand_coordinate']['relaxed_suffix_release_units'] < 4
        ],
        'final_suffix_without_final_precision_demands': [
            row['demand_coordinate']
            for row in unreachable_rows
            if row['demand_coordinate']['middle_precision_relief_units'] == 1
            and row['demand_coordinate']['relaxed_suffix_release_units'] == 4
        ],
    }

    return {
        'focus': 'Map primitive-demand requests into the current scalar weakening menu so inheritors can see which two-bundle coordinates are exactly reachable and which ones require hitchhiking overshoot along the budget chain.',
        'headline_findings': {
            'primitive_budget_path_coordinates': [row['coordinate'] for row in budget_path],
            'primitive_budget_path_coordinate_labels': [
                f"({row['coordinate']['middle_precision_relief_units']},{row['coordinate']['relaxed_suffix_release_units']})"
                for row in budget_path
            ],
            'primitive_box_shape': {
                'middle_precision_relief_units': [0, max(row['coordinate']['middle_precision_relief_units'] for row in budget_path)],
                'relaxed_suffix_release_units': [0, max(row['coordinate']['relaxed_suffix_release_units'] for row in budget_path)],
            },
            'primitive_box_point_count': len(surface),
            'exact_reachable_coordinate_count': len(exact_rows),
            'exact_unreachable_coordinate_count': len(unreachable_rows),
            'exact_reachable_coordinate_labels': exact_coordinate_labels,
            'unreachable_coordinate_count_by_selected_budget': budget_to_unreachable_count,
            'exact_coordinate_count_by_selected_budget': budget_to_exact_count,
            'hole_families': hole_families,
            'scalar_menu_is_chain_not_product': True,
            'all_unreachable_demands_require_hitchhiking_overshoot': True,
        },
        'decision_rules': [
            'Treat the current weakening menu as a monotone chain through two-bundle space, not as an independent selector over precision and relaxed-suffix coordinates.',
            'When a desired primitive coordinate is exactly on the chain, select its matching budget directly; there are only six such exact coordinates in the current 3x5 box.',
            'When a desired primitive coordinate falls in a hole, choose the least dominating budget-chain point and record the overshoot explicitly as hitchhiked capability that the scalar menu forces you to buy.',
            'Read the hole structure as policy expressiveness: deep suffix-only requests beyond one unit and second-precision requests below the final suffix level are not directly representable today.',
            'Treat any future redesign that fills one of the current holes or changes the least-dominating overshoot for a demand coordinate as a substantive change to the weakening factor surface.',
        ],
        'budget_coordinate_path': budget_path,
        'primitive_demand_surface': surface,
        'unreachable_demand_classes': unreachable_classes,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_primitive_demand_surface_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
