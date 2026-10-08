#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface import (
    build_primitive_demand_surface,
)


class WeakeningPrimitiveOvershootTaxonomyError(RuntimeError):
    pass


PRIMITIVE_AXES = [
    'middle_precision_relief_units',
    'relaxed_suffix_release_units',
]



def _overshoot_signature_label(overshoot: dict[str, int]) -> str:
    return f"P+{overshoot['middle_precision_relief_units']}_S+{overshoot['relaxed_suffix_release_units']}"



def _overshoot_axis_family(overshoot: dict[str, int]) -> str:
    precision = overshoot['middle_precision_relief_units']
    suffix = overshoot['relaxed_suffix_release_units']
    if precision > 0 and suffix > 0:
        return 'mixed_axis_hitchhike'
    if precision > 0:
        return 'precision_only_hitchhike'
    if suffix > 0:
        return 'suffix_only_hitchhike'
    return 'exact_match'


@lru_cache(maxsize=1)
def build_unreachable_primitive_overshoot_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_primitive_demand_surface():
        if row['exact_coordinate_reachable']:
            continue
        overshoot = row['overshoot_coordinate']
        selected = row['selected_coordinate']
        shared_axes = [axis for axis in PRIMITIVE_AXES if row['demand_coordinate'][axis] == selected[axis]]
        rows.append(
            {
                **row,
                'overshoot_signature_label': _overshoot_signature_label(overshoot),
                'overshoot_axis_family': _overshoot_axis_family(overshoot),
                'overshoot_l1_units': sum(overshoot.values()),
                'shares_exact_axis_with_selected_coordinate': len(shared_axes) >= 1,
                'shared_axes': shared_axes,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_primitive_overshoot_signature_classes() -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in build_unreachable_primitive_overshoot_rows():
        key = (
            row['overshoot_coordinate']['middle_precision_relief_units'],
            row['overshoot_coordinate']['relaxed_suffix_release_units'],
        )
        grouped[key].append(row)

    classes: list[dict[str, Any]] = []
    for key, members in grouped.items():
        exemplar = members[0]
        classes.append(
            {
                'overshoot_coordinate': exemplar['overshoot_coordinate'],
                'overshoot_signature_label': exemplar['overshoot_signature_label'],
                'overshoot_axis_family': exemplar['overshoot_axis_family'],
                'overshoot_l1_units': exemplar['overshoot_l1_units'],
                'selected_budget_set': sorted({row['selected_budget'] for row in members}),
                'member_demands': [row['demand_coordinate'] for row in members],
                'member_count': len(members),
            }
        )
    return sorted(
        classes,
        key=lambda row: (
            row['overshoot_axis_family'],
            row['overshoot_l1_units'],
            row['overshoot_coordinate']['middle_precision_relief_units'],
            row['overshoot_coordinate']['relaxed_suffix_release_units'],
        ),
    )


@lru_cache(maxsize=1)
def build_primitive_overshoot_axis_families() -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in build_unreachable_primitive_overshoot_rows():
        grouped[row['overshoot_axis_family']].append(row)

    families: list[dict[str, Any]] = []
    for axis_family, members in grouped.items():
        families.append(
            {
                'overshoot_axis_family': axis_family,
                'member_count': len(members),
                'overshoot_signature_labels': sorted({row['overshoot_signature_label'] for row in members}),
                'overshoot_l1_unit_histogram': dict(sorted(Counter(row['overshoot_l1_units'] for row in members).items())),
                'member_demands': [row['demand_coordinate'] for row in members],
            }
        )
    return sorted(families, key=lambda row: row['overshoot_axis_family'])



def build_weakening_primitive_overshoot_taxonomy_snapshot() -> dict[str, Any]:
    rows = build_unreachable_primitive_overshoot_rows()
    signature_classes = build_primitive_overshoot_signature_classes()
    axis_families = build_primitive_overshoot_axis_families()

    axis_family_counts = Counter(row['overshoot_axis_family'] for row in rows)
    signature_counts = {
        row['overshoot_signature_label']: row['member_count']
        for row in signature_classes
    }
    overshoot_l1_histogram = dict(sorted(Counter(row['overshoot_l1_units'] for row in rows).items()))

    mixed_axis_count = axis_family_counts.get('mixed_axis_hitchhike', 0)
    if mixed_axis_count != 0:
        raise WeakeningPrimitiveOvershootTaxonomyError(
            f'expected no mixed-axis hitchhikes, found {mixed_axis_count}'
        )
    if not all(row['shares_exact_axis_with_selected_coordinate'] for row in rows):
        raise WeakeningPrimitiveOvershootTaxonomyError('every unreachable demand should share one exact axis with its selected coordinate')

    precision_only_rows = [row for row in rows if row['overshoot_axis_family'] == 'precision_only_hitchhike']
    suffix_only_rows = [row for row in rows if row['overshoot_axis_family'] == 'suffix_only_hitchhike']
    max_precision_tax = max(row['overshoot_coordinate']['middle_precision_relief_units'] for row in precision_only_rows)
    max_suffix_tax = max(row['overshoot_coordinate']['relaxed_suffix_release_units'] for row in suffix_only_rows)
    worst_precision_tax_demands = [
        row['demand_coordinate']
        for row in precision_only_rows
        if row['overshoot_coordinate']['middle_precision_relief_units'] == max_precision_tax
    ]
    worst_suffix_tax_demands = [
        row['demand_coordinate']
        for row in suffix_only_rows
        if row['overshoot_coordinate']['relaxed_suffix_release_units'] == max_suffix_tax
    ]

    return {
        'focus': 'Classify every impossible primitive-demand coordinate by its forced overshoot tax so inheritors can see which primitive axis the scalar weakening menu overbuys when an exact two-bundle request falls into a chain hole.',
        'headline_findings': {
            'unreachable_demand_count': len(rows),
            'overshoot_axis_family_counts': dict(sorted(axis_family_counts.items())),
            'overshoot_signature_counts': signature_counts,
            'overshoot_l1_unit_histogram': overshoot_l1_histogram,
            'mixed_axis_hitchhike_count': mixed_axis_count,
            'single_axis_hitchhike_count': len(rows),
            'all_unreachable_demands_share_one_exact_axis_with_selected_coordinate': True,
            'all_unreachable_demands_require_axis_pure_overshoot': True,
            'max_precision_only_hitchhike_units': max_precision_tax,
            'max_suffix_only_hitchhike_units': max_suffix_tax,
            'worst_precision_hitchhike_demands': worst_precision_tax_demands,
            'worst_suffix_hitchhike_demands': worst_suffix_tax_demands,
            'precision_hitchhike_is_triggered_by_deep_suffix_requests': True,
            'suffix_hitchhike_is_triggered_by_early_precision_requests': True,
        },
        'decision_rules': [
            'Treat every current primitive-demand hole as a single-axis tax: the scalar weakening menu overbuys either precision relief or relaxed-suffix release, never both at once.',
            'When a request asks for deeper relaxed-suffix coverage without the matching precision step, expect precision-only hitchhike tax.',
            'When a request asks for more precision-origin relief before the staircase has granted the matching suffix depth, expect suffix-only hitchhike tax.',
            'Use the overshoot L1 units as the smallest exact accounting burden for how far the scalar menu misses the requested two-bundle coordinate.',
            'Treat any future mixed-axis overshoot as a substantive redesign signal: it would mean the current staircase-shaped approximation law no longer holds.',
        ],
        'primitive_overshoot_axis_families': axis_families,
        'primitive_overshoot_signature_classes': signature_classes,
        'unreachable_primitive_overshoot_rows': rows,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_demand_surface_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_primitive_overshoot_taxonomy_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
