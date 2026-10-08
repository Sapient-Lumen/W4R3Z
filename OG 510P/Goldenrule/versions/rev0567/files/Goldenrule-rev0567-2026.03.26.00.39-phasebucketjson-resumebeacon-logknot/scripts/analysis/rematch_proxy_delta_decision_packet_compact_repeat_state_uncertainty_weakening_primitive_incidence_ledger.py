#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from functools import lru_cache
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes import (
    build_marginal_release_steps,
)


class WeakeningPrimitiveIncidenceLedgerError(RuntimeError):
    pass


PRIMITIVE_AXES = [
    'middle_precision_relief_units',
    'relaxed_suffix_release_units',
]

VALUE_CLASS_TO_PRIMITIVE_SIGNATURE = {
    'middle_precision_relief_bundle': {
        'middle_precision_relief_units': 1,
        'relaxed_suffix_release_units': 0,
    },
    'relaxed_suffix_savings_bundle': {
        'middle_precision_relief_units': 0,
        'relaxed_suffix_release_units': 1,
    },
    'full_precision_relaxed_release_bundle': {
        'middle_precision_relief_units': 1,
        'relaxed_suffix_release_units': 1,
    },
}



def _primitive_signature_for_value_class(value_class_label: str) -> dict[str, int]:
    if value_class_label not in VALUE_CLASS_TO_PRIMITIVE_SIGNATURE:
        raise WeakeningPrimitiveIncidenceLedgerError(f'unrecognized value class: {value_class_label}')
    return dict(VALUE_CLASS_TO_PRIMITIVE_SIGNATURE[value_class_label])



@lru_cache(maxsize=1)
def build_marginal_release_factorizations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for step in build_marginal_release_steps():
        signature = _primitive_signature_for_value_class(step['value_class_label'])
        rows.append(
            {
                'budget_step': step['budget_step'],
                'threshold_unique_appends': step['threshold_unique_appends'],
                'current_state_unique_appends': step['current_state_unique_appends'],
                'current_state_label': step['current_state_label'],
                'required_gain_share_floor': step['required_gain_share_floor'],
                'released_live_case_label': step['released_live_case_label'],
                'released_route_shift_unique_appends': step['released_route_shift_unique_appends'],
                'released_route_unique_appends': step['released_route_unique_appends'],
                'value_class_label': step['value_class_label'],
                'primitive_signature': signature,
                'primitive_signature_label': (
                    f"P{signature['middle_precision_relief_units']}_"
                    f"S{signature['relaxed_suffix_release_units']}"
                ),
            }
        )
    return rows



@lru_cache(maxsize=1)
def build_primitive_signature_classes() -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in build_marginal_release_factorizations():
        key = (
            row['primitive_signature']['middle_precision_relief_units'],
            row['primitive_signature']['relaxed_suffix_release_units'],
        )
        grouped[key].append(row)

    classes: list[dict[str, Any]] = []
    for key, rows in grouped.items():
        exemplar = rows[0]
        classes.append(
            {
                'primitive_signature': exemplar['primitive_signature'],
                'primitive_signature_label': exemplar['primitive_signature_label'],
                'member_budget_steps': [row['budget_step'] for row in rows],
                'member_value_class_labels': [row['value_class_label'] for row in rows],
                'member_live_case_labels': [row['released_live_case_label'] for row in rows],
                'member_route_shifts_unique_appends': [row['released_route_shift_unique_appends'] for row in rows],
                'member_count': len(rows),
            }
        )
    return sorted(
        classes,
        key=lambda row: (
            -row['member_count'],
            -row['primitive_signature']['middle_precision_relief_units'],
            -row['primitive_signature']['relaxed_suffix_release_units'],
        ),
    )



@lru_cache(maxsize=1)
def build_cumulative_primitive_budget_path() -> list[dict[str, Any]]:
    rows = build_marginal_release_factorizations()
    path: list[dict[str, Any]] = [
        {
            'budget': 0,
            'threshold_unique_appends': 0,
            'cumulative_primitive_signature': {
                'middle_precision_relief_units': 0,
                'relaxed_suffix_release_units': 0,
            },
            'released_budget_step': None,
            'released_live_case_label': None,
        }
    ]
    cumulative = {
        'middle_precision_relief_units': 0,
        'relaxed_suffix_release_units': 0,
    }
    for row in rows:
        for axis in PRIMITIVE_AXES:
            cumulative[axis] += row['primitive_signature'][axis]
        path.append(
            {
                'budget': row['budget_step'],
                'threshold_unique_appends': row['threshold_unique_appends'],
                'cumulative_primitive_signature': dict(cumulative),
                'released_budget_step': row['budget_step'],
                'released_live_case_label': row['released_live_case_label'],
                'released_primitive_signature': row['primitive_signature'],
                'released_primitive_signature_label': row['primitive_signature_label'],
            }
        )
    return path



def build_weakening_primitive_incidence_ledger_snapshot() -> dict[str, Any]:
    factorizations = build_marginal_release_factorizations()
    signature_classes = build_primitive_signature_classes()
    path = build_cumulative_primitive_budget_path()

    suffix_only = next(
        row for row in signature_classes if row['primitive_signature'] == {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 1}
    )
    precision_only = next(
        row for row in signature_classes if row['primitive_signature'] == {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0}
    )
    composite = next(
        row for row in signature_classes if row['primitive_signature'] == {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 1}
    )

    cumulative_precision = [row['cumulative_primitive_signature']['middle_precision_relief_units'] for row in path]
    cumulative_suffix = [row['cumulative_primitive_signature']['relaxed_suffix_release_units'] for row in path]
    if cumulative_precision != [0, 0, 1, 1, 1, 2]:
        raise WeakeningPrimitiveIncidenceLedgerError(f'unexpected cumulative precision path: {cumulative_precision}')
    if cumulative_suffix != [0, 1, 1, 2, 3, 4]:
        raise WeakeningPrimitiveIncidenceLedgerError(f'unexpected cumulative suffix path: {cumulative_suffix}')

    return {
        'focus': 'Encode every weakening-budget release in the two-primitive bundle basis so inheritors can govern the menu as a tiny factor ledger rather than as five unrelated live cases.',
        'headline_findings': {
            'primitive_axis_labels': PRIMITIVE_AXES,
            'marginal_release_step_count': len(factorizations),
            'primitive_signature_class_count': len(signature_classes),
            'suffix_only_budget_steps': suffix_only['member_budget_steps'],
            'precision_only_budget_steps': precision_only['member_budget_steps'],
            'composite_budget_steps': composite['member_budget_steps'],
            'cumulative_primitive_budget_path': {
                str(row['budget']): row['cumulative_primitive_signature'] for row in path
            },
            'precision_axis_stalls_across_budgets': [2, 3, 4],
            'suffix_axis_deepens_across_budgets': [1, 3, 4, 5],
            'no_second_precision_unit_without_extra_suffix_unit': True,
            'no_budget_between_two_precision_levels': [3, 4],
        },
        'decision_rules': [
            'Read each weakening release as a coefficient vector in the two-bundle basis: middle-band precision relief and relaxed-suffix release.',
            'Treat the current menu as three suffix-only cases, one precision-only case, and one exact composite case rather than as five incomparable exceptions.',
            'Use the cumulative primitive budget path to see what each budget level has actually bought: (0,0)->(0,1)->(1,1)->(1,2)->(1,3)->(2,4).',
            'Notice the structural asymmetry: after budget 2, governance can buy more relaxed-suffix coverage at budgets 3 and 4, but it cannot buy a second precision-origin release without also buying another suffix unit at budget 5.',
            'Treat any future redesign that creates a pure second precision step or changes a release step\'s primitive signature as a substantive change to the weakening factor basis.',
        ],
        'marginal_release_factorizations': factorizations,
        'primitive_signature_classes': signature_classes,
        'cumulative_primitive_budget_path': path,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_incidence_ledger.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_primitive_incidence_ledger_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
