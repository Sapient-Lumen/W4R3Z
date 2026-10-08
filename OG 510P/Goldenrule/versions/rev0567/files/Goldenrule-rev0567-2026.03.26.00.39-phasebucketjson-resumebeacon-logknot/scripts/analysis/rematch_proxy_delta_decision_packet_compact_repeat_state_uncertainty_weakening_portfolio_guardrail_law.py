#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails import (
    build_guardrail_profile_partition,
    build_minimal_guardrail_profile_by_demand,
    build_overshoot_axis_guardrail_profiles,
)


class WeakeningPortfolioGuardrailLawError(RuntimeError):
    pass


PROFILE_ORDER = [
    'exact_only',
    'precision_hitchhike_only',
    'suffix_hitchhike_only',
    'any_single_axis_hitchhike',
]


def _coord_label(coord: dict[str, int]) -> str:
    return f"({coord['middle_precision_relief_units']},{coord['relaxed_suffix_release_units']})"


@lru_cache(maxsize=1)
def _profile_by_label() -> dict[str, dict[str, Any]]:
    return {row['profile_label']: row for row in build_overshoot_axis_guardrail_profiles()}


@lru_cache(maxsize=1)
def build_demand_family_catalog() -> dict[str, list[dict[str, int]]]:
    catalog = {label: [] for label in PROFILE_ORDER}
    for row in build_minimal_guardrail_profile_by_demand():
        catalog[row['minimal_profile_label']].append(row['demand_coordinate'])
    for label in catalog:
        catalog[label] = sorted(
            catalog[label],
            key=lambda coord: (coord['middle_precision_relief_units'], coord['relaxed_suffix_release_units']),
        )
    return catalog


@lru_cache(maxsize=1)
def _minimal_profile_lookup() -> dict[str, str]:
    return {
        _coord_label(row['demand_coordinate']): row['minimal_profile_label']
        for row in build_minimal_guardrail_profile_by_demand()
    }


@lru_cache(maxsize=1)
def build_portfolio_demand_universe() -> list[dict[str, int]]:
    coords: list[dict[str, int]] = []
    for partition_row in build_guardrail_profile_partition():
        coords.extend(partition_row['member_demands'])
    return sorted(coords, key=lambda coord: (coord['middle_precision_relief_units'], coord['relaxed_suffix_release_units']))


@lru_cache(maxsize=1)
def build_portfolio_signature_partition() -> list[dict[str, Any]]:
    catalog = build_demand_family_catalog()
    exact_count = len(catalog['exact_only'])
    precision_count = len(catalog['precision_hitchhike_only'])
    suffix_count = len(catalog['suffix_hitchhike_only'])

    rows = [
        {
            'signature_label': 'exact_only_portfolios',
            'requires_exact_demands_only': True,
            'requires_precision_hitchhike_family': False,
            'requires_suffix_hitchhike_family': False,
            'minimal_profile_label': 'exact_only',
            'portfolio_count': (2 ** exact_count) - 1,
            'count_formula': f'(2^{exact_count}) - 1',
        },
        {
            'signature_label': 'precision_family_only_portfolios',
            'requires_exact_demands_only': False,
            'requires_precision_hitchhike_family': True,
            'requires_suffix_hitchhike_family': False,
            'minimal_profile_label': 'precision_hitchhike_only',
            'portfolio_count': (2 ** exact_count) * ((2 ** precision_count) - 1),
            'count_formula': f'(2^{exact_count}) * ((2^{precision_count}) - 1)',
        },
        {
            'signature_label': 'suffix_family_only_portfolios',
            'requires_exact_demands_only': False,
            'requires_precision_hitchhike_family': False,
            'requires_suffix_hitchhike_family': True,
            'minimal_profile_label': 'suffix_hitchhike_only',
            'portfolio_count': (2 ** exact_count) * ((2 ** suffix_count) - 1),
            'count_formula': f'(2^{exact_count}) * ((2^{suffix_count}) - 1)',
        },
        {
            'signature_label': 'mixed_hole_family_portfolios',
            'requires_exact_demands_only': False,
            'requires_precision_hitchhike_family': True,
            'requires_suffix_hitchhike_family': True,
            'minimal_profile_label': 'any_single_axis_hitchhike',
            'portfolio_count': (2 ** exact_count) * ((2 ** precision_count) - 1) * ((2 ** suffix_count) - 1),
            'count_formula': f'(2^{exact_count}) * ((2^{precision_count}) - 1) * ((2^{suffix_count}) - 1)',
        },
    ]
    return rows


def select_minimal_guardrail_profile_for_portfolio(demand_coordinates: list[dict[str, int]]) -> dict[str, Any]:
    if not demand_coordinates:
        raise WeakeningPortfolioGuardrailLawError('portfolio must contain at least one demand coordinate')

    lookup = _minimal_profile_lookup()
    labels = sorted({_coord_label(coord) for coord in demand_coordinates})
    if len(labels) != len(demand_coordinates):
        raise WeakeningPortfolioGuardrailLawError('portfolio contains duplicate demand coordinates')

    families = Counter(lookup[label] for label in labels)
    profile_by_label = _profile_by_label()
    for profile_label in PROFILE_ORDER:
        admitted = profile_by_label[profile_label]['admitted_demands']
        if all(coord in admitted for coord in demand_coordinates):
            return {
                'portfolio_demands': [
                    coord for coord in build_portfolio_demand_universe() if _coord_label(coord) in labels
                ],
                'portfolio_coordinate_labels': labels,
                'portfolio_size': len(labels),
                'minimal_profile_label': profile_label,
                'family_counts': {
                    'exact_only': families.get('exact_only', 0),
                    'precision_hitchhike_only': families.get('precision_hitchhike_only', 0),
                    'suffix_hitchhike_only': families.get('suffix_hitchhike_only', 0),
                },
                'contains_precision_hole_family': families.get('precision_hitchhike_only', 0) > 0,
                'contains_suffix_hole_family': families.get('suffix_hitchhike_only', 0) > 0,
                'dual_axis_permission_is_minimally_necessary': profile_label == 'any_single_axis_hitchhike',
            }
    raise WeakeningPortfolioGuardrailLawError(f'no guardrail profile admits portfolio {labels}')


@lru_cache(maxsize=1)
def build_portfolio_guardrail_profile_counts() -> dict[str, int]:
    universe = build_portfolio_demand_universe()
    counts = Counter()
    for size in range(1, len(universe) + 1):
        for combo in combinations(universe, size):
            selection = select_minimal_guardrail_profile_for_portfolio(list(combo))
            counts[selection['minimal_profile_label']] += 1
    return {label: counts.get(label, 0) for label in PROFILE_ORDER}



def build_weakening_portfolio_guardrail_law_snapshot() -> dict[str, Any]:
    family_catalog = build_demand_family_catalog()
    signature_partition = build_portfolio_signature_partition()
    enumerated_counts = build_portfolio_guardrail_profile_counts()
    formula_counts = {
        row['minimal_profile_label']: row['portfolio_count']
        for row in signature_partition
    }
    if enumerated_counts != formula_counts:
        raise WeakeningPortfolioGuardrailLawError(
            f'portfolio counts drifted from closed-form partition: enumerated={enumerated_counts}, formula={formula_counts}'
        )

    universe_size = len(build_portfolio_demand_universe())
    total_nonempty_portfolios = (2 ** universe_size) - 1
    if sum(enumerated_counts.values()) != total_nonempty_portfolios:
        raise WeakeningPortfolioGuardrailLawError(
            f'portfolio count mismatch: {sum(enumerated_counts.values())} vs {total_nonempty_portfolios}'
        )

    exact_count = len(family_catalog['exact_only'])
    precision_count = len(family_catalog['precision_hitchhike_only'])
    suffix_count = len(family_catalog['suffix_hitchhike_only'])

    selector_examples = [
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1},
        ]),
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 3},
        ]),
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
            {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 1},
        ]),
        select_minimal_guardrail_profile_for_portfolio([
            {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
            {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
        ]),
    ]

    return {
        'focus': 'Lift single-demand overshoot-axis guardrails to portfolio selection so inheritors can choose the weakest admissible profile for whole batches of weakening demands instead of reasoning one point at a time.',
        'headline_findings': {
            'demand_family_counts': {
                'exact_only': exact_count,
                'precision_hitchhike_only': precision_count,
                'suffix_hitchhike_only': suffix_count,
            },
            'nonempty_portfolio_count': total_nonempty_portfolios,
            'minimal_profile_count_by_portfolio': enumerated_counts,
            'mixed_hole_family_portfolios_require_dual_axis_permission': True,
            'dual_axis_permission_is_minimal_exactly_when_both_one_axis_hole_families_appear': True,
            'singleton_portfolios_requiring_dual_axis_permission': 0,
            'dual_axis_portfolio_share': {
                'numerator': enumerated_counts['any_single_axis_hitchhike'],
                'denominator': total_nonempty_portfolios,
            },
            'closed_form_partition_matches_enumeration': True,
        },
        'decision_rules': [
            'Choose `exact_only` for a batch only when every requested demand coordinate is one of the six exact staircase points.',
            'Choose `precision_hitchhike_only` for a batch when it may contain deep suffix holes but contains no suffix-hitchhike demands that need extra relaxed-suffix release.',
            'Choose `suffix_hitchhike_only` for a batch when it may contain early or extra-precision holes but contains no deep suffix holes that need precision hitchhike.',
            'Choose `any_single_axis_hitchhike` exactly when the batch mixes at least one precision-hitchhike-only demand with at least one suffix-hitchhike-only demand.',
            'Treat the current dual-axis profile as a workload-level necessity only for mixed hole-family portfolios; no singleton demand currently justifies it.',
        ],
        'portfolio_signature_partition': signature_partition,
        'demand_family_catalog': {
            label: {
                'member_count': len(coords),
                'member_labels': [_coord_label(coord) for coord in coords],
                'member_demands': coords,
            }
            for label, coords in family_catalog.items()
        },
        'selector_examples': selector_examples,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_guardrail_law_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
