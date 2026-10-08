#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_bundle_composition import (
    build_bundle_composition_relations,
    build_bundle_primitives,
    build_weakening_bundle_composition_snapshot,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')


def main() -> None:
    primitives = build_bundle_primitives()
    _assert_equal(len(primitives), 2, 'primitive bundle count')
    _assert_equal(
        [row['value_class_label'] for row in primitives],
        ['middle_precision_relief_bundle', 'relaxed_suffix_savings_bundle'],
        'primitive bundle labels',
    )
    _assert_equal(
        [row['representative_budget_step'] for row in primitives],
        [2, 3],
        'primitive representative budget steps',
    )

    compositions = build_bundle_composition_relations()
    _assert_equal(len(compositions), 1, 'composition relation count')
    relation = compositions[0]
    _assert_equal(relation['composite_value_class_label'], 'full_precision_relaxed_release_bundle', 'composite label')
    _assert_equal(relation['component_budget_steps'], [2, 3], 'component budget steps')
    _assert_equal(relation['component_value_class_labels'], ['middle_precision_relief_bundle', 'relaxed_suffix_savings_bundle'], 'component labels')
    _assert_equal(relation['component_thresholds_unique_appends'], [11, 12], 'component thresholds')
    _assert_equal(relation['component_route_shifts_unique_appends'], [11, 12], 'component route shifts')
    _assert_equal(relation['component_canonical_anchor_chain'], [2, 13, 25], 'component canonical anchor chain')
    _assert_equal(relation['vector_sum_matches_composite'], True, 'vector additivity')
    _assert_equal(relation['threshold_sum_matches_composite'], True, 'threshold additivity')
    _assert_equal(relation['route_shift_sum_matches_composite'], True, 'route-shift additivity')
    _assert_equal(
        relation['composite_recovered_steady_state_savings_vector'],
        {
            'exact_dwell_band_width_units': 13,
            'exact_hard_cap_units': 8,
            'minimum_anchor_slack_units': 6,
            'mode_specific_checkpoint_units': 9,
        },
        'composite savings vector',
    )
    _assert_equal(relation['summed_component_savings_vector'], relation['composite_recovered_steady_state_savings_vector'], 'summed component vector')
    _assert_equal(relation['composite_threshold_unique_appends'], 23, 'composite threshold')
    _assert_equal(relation['composite_route_shift_unique_appends'], 23, 'composite route shift')

    report = build_weakening_bundle_composition_snapshot()
    _assert_equal(report['headline_findings']['primitive_value_bundle_count'], 2, 'headline primitive count')
    _assert_equal(report['headline_findings']['composite_value_bundle_count'], 1, 'headline composite count')
    _assert_equal(report['headline_findings']['full_precision_release_is_exact_bundle_sum'], True, 'headline vector additivity')
    _assert_equal(report['headline_findings']['canonical_anchor_chain_for_composition'], [2, 13, 25], 'headline canonical chain')

    print('weakening bundle composition checks passed')


if __name__ == '__main__':
    main()
