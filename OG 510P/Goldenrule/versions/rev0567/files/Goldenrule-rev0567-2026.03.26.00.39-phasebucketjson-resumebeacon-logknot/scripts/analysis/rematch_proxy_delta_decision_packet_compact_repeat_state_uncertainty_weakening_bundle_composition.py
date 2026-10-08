#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes import (
    build_marginal_release_steps,
)


class WeakeningBundleCompositionError(RuntimeError):
    pass


PRIMITIVE_VALUE_CLASS_LABELS = {
    'relaxed_suffix_savings_bundle',
    'middle_precision_relief_bundle',
}
COMPOSITE_VALUE_CLASS_LABELS = {
    'full_precision_relaxed_release_bundle',
}


def _steps_by_budget() -> dict[int, dict[str, Any]]:
    rows = {row['budget_step']: row for row in build_marginal_release_steps()}
    expected = {1, 2, 3, 4, 5}
    if set(rows) != expected:
        raise WeakeningBundleCompositionError(f'unexpected marginal release steps: {sorted(rows)}')
    return rows



def _vector_add(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    keys = set(left) | set(right)
    return {key: int(left.get(key, 0)) + int(right.get(key, 0)) for key in sorted(keys)}



def _primitive_rows() -> list[dict[str, Any]]:
    rows = _steps_by_budget()
    representatives = [rows[2], rows[3]]
    labels = {row['value_class_label'] for row in representatives}
    if labels != PRIMITIVE_VALUE_CLASS_LABELS:
        raise WeakeningBundleCompositionError(f'unexpected primitive labels: {sorted(labels)}')
    return representatives



def _composite_row() -> dict[str, Any]:
    row = _steps_by_budget()[5]
    if row['value_class_label'] not in COMPOSITE_VALUE_CLASS_LABELS:
        raise WeakeningBundleCompositionError(f'unexpected composite label: {row["value_class_label"]}')
    return row



def build_bundle_primitives() -> list[dict[str, Any]]:
    rows = _primitive_rows()
    return [
        {
            'value_class_label': row['value_class_label'],
            'representative_budget_step': row['budget_step'],
            'representative_live_case_label': row['released_live_case_label'],
            'representative_current_state_label': row['current_state_label'],
            'representative_required_gain_share_floor': row['required_gain_share_floor'],
            'representative_threshold_unique_appends': row['threshold_unique_appends'],
            'representative_route_shift_unique_appends': row['released_route_shift_unique_appends'],
            'representative_route_unique_appends': row['released_route_unique_appends'],
            'recovered_steady_state_savings_vector': row['savings_vector'],
        }
        for row in rows
    ]



def build_bundle_composition_relations() -> list[dict[str, Any]]:
    rows = _steps_by_budget()
    precision_relief = rows[2]
    neutral_relaxed_release = rows[3]
    full_precision_release = rows[5]

    composed_vector = _vector_add(precision_relief['savings_vector'], neutral_relaxed_release['savings_vector'])
    if composed_vector != full_precision_release['savings_vector']:
        raise WeakeningBundleCompositionError('steady-state savings vector additivity failed')

    threshold_sum = precision_relief['threshold_unique_appends'] + neutral_relaxed_release['threshold_unique_appends']
    if threshold_sum != full_precision_release['threshold_unique_appends']:
        raise WeakeningBundleCompositionError('threshold additivity failed')

    route_shift_sum = (
        precision_relief['released_route_shift_unique_appends']
        + neutral_relaxed_release['released_route_shift_unique_appends']
    )
    if route_shift_sum != full_precision_release['released_route_shift_unique_appends']:
        raise WeakeningBundleCompositionError('route-shift additivity failed')

    canonical_anchor_chain = [2, 13, 25]
    canonical_leg_shifts_unique_appends = [
        precision_relief['released_route_shift_unique_appends'],
        neutral_relaxed_release['released_route_shift_unique_appends'],
    ]
    if sum(canonical_leg_shifts_unique_appends) != full_precision_release['released_route_shift_unique_appends']:
        raise WeakeningBundleCompositionError('canonical leg shift sum failed')

    return [
        {
            'composite_value_class_label': full_precision_release['value_class_label'],
            'composite_budget_step': full_precision_release['budget_step'],
            'composite_live_case_label': full_precision_release['released_live_case_label'],
            'component_budget_steps': [precision_relief['budget_step'], neutral_relaxed_release['budget_step']],
            'component_value_class_labels': [
                precision_relief['value_class_label'],
                neutral_relaxed_release['value_class_label'],
            ],
            'component_live_case_labels': [
                precision_relief['released_live_case_label'],
                neutral_relaxed_release['released_live_case_label'],
            ],
            'component_recovered_steady_state_savings_vectors': [
                precision_relief['savings_vector'],
                neutral_relaxed_release['savings_vector'],
            ],
            'component_thresholds_unique_appends': [
                precision_relief['threshold_unique_appends'],
                neutral_relaxed_release['threshold_unique_appends'],
            ],
            'component_route_shifts_unique_appends': canonical_leg_shifts_unique_appends,
            'component_canonical_anchor_chain': canonical_anchor_chain,
            'vector_sum_matches_composite': True,
            'threshold_sum_matches_composite': True,
            'route_shift_sum_matches_composite': True,
            'composite_recovered_steady_state_savings_vector': full_precision_release['savings_vector'],
            'summed_component_savings_vector': composed_vector,
            'composite_threshold_unique_appends': full_precision_release['threshold_unique_appends'],
            'composite_route_shift_unique_appends': full_precision_release['released_route_shift_unique_appends'],
            'composite_route_unique_appends': full_precision_release['released_route_unique_appends'],
            'notes': [
                'The full precision-to-relaxed release uses the same total unique-append burden as chaining middle-band precision relief with neutral-anchor relaxed release.',
                'The one-shot direct route can omit an explicit neutral-anchor stop while preserving exact additive burden in the scalar shift metric.',
            ],
        }
    ]



def build_weakening_bundle_composition_snapshot() -> dict[str, Any]:
    primitives = build_bundle_primitives()
    compositions = build_bundle_composition_relations()
    relation = compositions[0]

    return {
        'focus': 'Collapse the weakening release menu to primitive savings bundles plus exact composite relations so inheritors can reason about full precision relaxation as a bundle composition law instead of a separate primitive.',
        'headline_findings': {
            'primitive_value_bundle_count': len(primitives),
            'primitive_value_class_labels': [row['value_class_label'] for row in primitives],
            'composite_value_bundle_count': len(compositions),
            'composite_value_class_labels': [row['composite_value_class_label'] for row in compositions],
            'full_precision_release_is_exact_bundle_sum': relation['vector_sum_matches_composite'],
            'full_precision_release_is_exact_threshold_sum': relation['threshold_sum_matches_composite'],
            'full_precision_release_is_exact_route_shift_sum': relation['route_shift_sum_matches_composite'],
            'canonical_anchor_chain_for_composition': relation['component_canonical_anchor_chain'],
            'canonical_leg_thresholds_unique_appends': relation['component_thresholds_unique_appends'],
            'canonical_leg_route_shifts_unique_appends': relation['component_route_shifts_unique_appends'],
        },
        'decision_rules': [
            'Treat the weakening release menu as two primitive savings bundles plus one exact composite, not as three unrelated primitives.',
            'Use middle-band precision relief and neutral-anchor relaxed release as the canonical primitive legs when reasoning about full precision-anchor relaxed release.',
            'Read threshold 23 as the exact additive burden 11 + 12, and read the full relaxed release savings vector as the exact sum of the two primitive vectors.',
            'Do not infer that the composite must visit every intermediate live state explicitly; the one-shot direct route may compress the path while preserving the same scalar burden.',
            'Treat any future change that breaks vector, threshold, or route-shift additivity for the precision-anchor full release as a substantive redesign of the release algebra.',
        ],
        'bundle_primitives': primitives,
        'bundle_composition_relations': compositions,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_release_value_classes_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_bundle_composition_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
