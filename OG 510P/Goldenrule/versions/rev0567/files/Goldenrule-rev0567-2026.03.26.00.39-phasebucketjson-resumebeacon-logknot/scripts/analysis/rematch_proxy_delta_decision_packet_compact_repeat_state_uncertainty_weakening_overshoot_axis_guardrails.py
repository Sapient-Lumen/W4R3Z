#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface import (
    build_primitive_demand_surface,
)


class WeakeningOvershootAxisGuardrailsError(RuntimeError):
    pass


PROFILES: list[dict[str, Any]] = [
    {
        'profile_label': 'exact_only',
        'allow_precision_hitchhike': False,
        'allow_suffix_hitchhike': False,
        'description': 'Admit only exact primitive coordinates with zero hitchhike tax.',
    },
    {
        'profile_label': 'precision_hitchhike_only',
        'allow_precision_hitchhike': True,
        'allow_suffix_hitchhike': False,
        'description': 'Allow deeper suffix requests to hitchhike extra precision relief, but forbid suffix overshoot.',
    },
    {
        'profile_label': 'suffix_hitchhike_only',
        'allow_precision_hitchhike': False,
        'allow_suffix_hitchhike': True,
        'description': 'Allow early precision requests to hitchhike extra relaxed-suffix release, but forbid precision overshoot.',
    },
    {
        'profile_label': 'any_single_axis_hitchhike',
        'allow_precision_hitchhike': True,
        'allow_suffix_hitchhike': True,
        'description': 'Allow either single-axis hitchhike family; mixed-axis overshoot would still be rejected if it ever appeared.',
    },
]


def _row_is_admissible_under_profile(row: dict[str, Any], profile: dict[str, Any]) -> bool:
    if row['exact_coordinate_reachable']:
        return True
    overshoot = row['overshoot_coordinate']
    precision = overshoot['middle_precision_relief_units']
    suffix = overshoot['relaxed_suffix_release_units']
    if precision > 0 and suffix > 0:
        return profile['allow_precision_hitchhike'] and profile['allow_suffix_hitchhike']
    if precision > 0:
        return profile['allow_precision_hitchhike']
    if suffix > 0:
        return profile['allow_suffix_hitchhike']
    return True


@lru_cache(maxsize=1)
def build_overshoot_axis_guardrail_profiles() -> list[dict[str, Any]]:
    surface = build_primitive_demand_surface()
    profiles: list[dict[str, Any]] = []
    for profile in PROFILES:
        admitted_rows = [row for row in surface if _row_is_admissible_under_profile(row, profile)]
        rejected_rows = [row for row in surface if not _row_is_admissible_under_profile(row, profile)]
        admitted_hitchhike_rows = [row for row in admitted_rows if not row['exact_coordinate_reachable']]
        admitted_hitchhike_axis_families = sorted(
            {
                'precision_only_hitchhike'
                if row['overshoot_coordinate']['middle_precision_relief_units'] > 0
                else 'suffix_only_hitchhike'
                for row in admitted_hitchhike_rows
            }
        )
        profile_rows = {
            **profile,
            'admitted_coordinate_count': len(admitted_rows),
            'rejected_coordinate_count': len(rejected_rows),
            'admits_full_primitive_box': len(rejected_rows) == 0,
            'admitted_exact_coordinate_count': sum(1 for row in admitted_rows if row['exact_coordinate_reachable']),
            'admitted_hitchhike_coordinate_count': len(admitted_hitchhike_rows),
            'admitted_hitchhike_axis_families': admitted_hitchhike_axis_families,
            'admitted_demands': [row['demand_coordinate'] for row in admitted_rows],
            'rejected_demands': [row['demand_coordinate'] for row in rejected_rows],
            'admitted_budget_set': sorted({row['selected_budget'] for row in admitted_rows}),
            'max_admitted_precision_hitchhike_units': max(
                [row['overshoot_coordinate']['middle_precision_relief_units'] for row in admitted_hitchhike_rows],
                default=0,
            ),
            'max_admitted_suffix_hitchhike_units': max(
                [row['overshoot_coordinate']['relaxed_suffix_release_units'] for row in admitted_hitchhike_rows],
                default=0,
            ),
        }
        profiles.append(profile_rows)
    return profiles


@lru_cache(maxsize=1)
def build_minimal_guardrail_profile_by_demand() -> list[dict[str, Any]]:
    surface = build_primitive_demand_surface()
    profiles = build_overshoot_axis_guardrail_profiles()
    rows: list[dict[str, Any]] = []
    for demand_row in surface:
        minimal_profile = next(
            profile for profile in profiles if demand_row['demand_coordinate'] in profile['admitted_demands']
        )
        rows.append(
            {
                'demand_coordinate': demand_row['demand_coordinate'],
                'selected_budget': demand_row['selected_budget'],
                'selected_threshold_unique_appends': demand_row['selected_threshold_unique_appends'],
                'exact_coordinate_reachable': demand_row['exact_coordinate_reachable'],
                'overshoot_coordinate': demand_row['overshoot_coordinate'],
                'minimal_profile_label': minimal_profile['profile_label'],
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_guardrail_profile_partition() -> list[dict[str, Any]]:
    minimal_rows = build_minimal_guardrail_profile_by_demand()
    counts = Counter(row['minimal_profile_label'] for row in minimal_rows)
    partition: list[dict[str, Any]] = []
    for profile in build_overshoot_axis_guardrail_profiles():
        members = [row['demand_coordinate'] for row in minimal_rows if row['minimal_profile_label'] == profile['profile_label']]
        partition.append(
            {
                'profile_label': profile['profile_label'],
                'member_count': counts.get(profile['profile_label'], 0),
                'member_demands': members,
            }
        )
    return partition


def select_budget_by_primitive_demand_under_axis_guardrails(
    minimum_middle_precision_relief_units: int,
    minimum_relaxed_suffix_release_units: int,
    *,
    allow_precision_hitchhike: bool,
    allow_suffix_hitchhike: bool,
) -> dict[str, Any]:
    demand = {
        'middle_precision_relief_units': minimum_middle_precision_relief_units,
        'relaxed_suffix_release_units': minimum_relaxed_suffix_release_units,
    }
    matching_rows = [
        row for row in build_primitive_demand_surface()
        if row['demand_coordinate'] == demand
    ]
    if len(matching_rows) != 1:
        raise WeakeningOvershootAxisGuardrailsError(f'expected one demand row for {demand}, found {len(matching_rows)}')
    row = matching_rows[0]
    profile = {
        'allow_precision_hitchhike': allow_precision_hitchhike,
        'allow_suffix_hitchhike': allow_suffix_hitchhike,
    }
    admissible = _row_is_admissible_under_profile(row, profile)
    return {
        **row,
        'admissible_under_axis_guardrails': admissible,
        'allow_precision_hitchhike': allow_precision_hitchhike,
        'allow_suffix_hitchhike': allow_suffix_hitchhike,
    }



def build_weakening_overshoot_axis_guardrails_snapshot() -> dict[str, Any]:
    profiles = build_overshoot_axis_guardrail_profiles()
    minimal_partition = build_guardrail_profile_partition()
    minimal_by_demand = build_minimal_guardrail_profile_by_demand()

    coverage_counts = {
        row['profile_label']: row['admitted_coordinate_count']
        for row in profiles
    }
    if coverage_counts != {
        'exact_only': 6,
        'precision_hitchhike_only': 10,
        'suffix_hitchhike_only': 11,
        'any_single_axis_hitchhike': 15,
    }:
        raise WeakeningOvershootAxisGuardrailsError(f'unexpected coverage counts: {coverage_counts}')

    no_dual_axis_necessity = all(row['minimal_profile_label'] != 'any_single_axis_hitchhike' for row in minimal_by_demand)
    if not no_dual_axis_necessity:
        raise WeakeningOvershootAxisGuardrailsError('expected no demand to require both hitchhike permissions simultaneously')

    return {
        'focus': 'Turn the single-axis primitive-overshoot taxonomy into explicit admission profiles so inheritors can govern which hitchhike axes are allowed when an exact weakening demand falls into a scalar-menu hole.',
        'headline_findings': {
            'coverage_count_by_guardrail_profile': coverage_counts,
            'full_primitive_box_point_count': len(minimal_by_demand),
            'minimal_profile_partition_counts': {
                row['profile_label']: row['member_count'] for row in minimal_partition
            },
            'no_demand_requires_both_hitchhike_permissions_simultaneously': no_dual_axis_necessity,
            'dual_axis_permission_is_portfolio_level_not_single_request_level': True,
            'precision_hitchhike_only_profile_extends_exact_coverage_by': coverage_counts['precision_hitchhike_only'] - coverage_counts['exact_only'],
            'suffix_hitchhike_only_profile_extends_exact_coverage_by': coverage_counts['suffix_hitchhike_only'] - coverage_counts['exact_only'],
            'suffix_hitchhike_only_covers_more_demands_than_precision_hitchhike_only': True,
        },
        'decision_rules': [
            'Use `exact_only` when hitchhike tax is forbidden; it covers only the six exact staircase coordinates.',
            'Use `precision_hitchhike_only` when deep relaxed-suffix requests may overbuy precision relief but suffix overshoot is unacceptable.',
            'Use `suffix_hitchhike_only` when early precision-origin requests may overbuy relaxed-suffix release but precision overshoot is unacceptable.',
            'Use `any_single_axis_hitchhike` only when you need portfolio-wide coverage across both hole families; no single current demand needs both permissions at once.',
            'Treat any future demand whose minimal profile becomes `any_single_axis_hitchhike` as a redesign signal: it would mean mixed-axis admission is no longer purely optional aggregation.',
        ],
        'guardrail_profiles': profiles,
        'minimal_guardrail_profile_partition': minimal_partition,
        'minimal_guardrail_profile_by_demand': minimal_by_demand,
        'selector_examples': [
            select_budget_by_primitive_demand_under_axis_guardrails(0, 2, allow_precision_hitchhike=False, allow_suffix_hitchhike=False),
            select_budget_by_primitive_demand_under_axis_guardrails(0, 2, allow_precision_hitchhike=True, allow_suffix_hitchhike=False),
            select_budget_by_primitive_demand_under_axis_guardrails(2, 1, allow_precision_hitchhike=False, allow_suffix_hitchhike=True),
            select_budget_by_primitive_demand_under_axis_guardrails(2, 1, allow_precision_hitchhike=True, allow_suffix_hitchhike=False),
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_overshoot_axis_guardrails_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
