#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_primitive_overshoot_taxonomy import (
    build_primitive_overshoot_axis_families,
    build_primitive_overshoot_signature_classes,
    build_unreachable_primitive_overshoot_rows,
    build_weakening_primitive_overshoot_taxonomy_snapshot,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    rows = build_unreachable_primitive_overshoot_rows()
    _assert_equal(len(rows), 9, 'unreachable overshoot row count')
    _assert_equal(sum(1 for row in rows if row['overshoot_axis_family'] == 'precision_only_hitchhike'), 4, 'precision-only hitchhike count')
    _assert_equal(sum(1 for row in rows if row['overshoot_axis_family'] == 'suffix_only_hitchhike'), 5, 'suffix-only hitchhike count')
    _assert_equal(sum(1 for row in rows if row['overshoot_axis_family'] == 'mixed_axis_hitchhike'), 0, 'mixed-axis hitchhike count')
    _assert_equal(all(row['shares_exact_axis_with_selected_coordinate'] for row in rows), True, 'shared-axis purity flag')

    signature_classes = build_primitive_overshoot_signature_classes()
    _assert_equal(
        [(row['overshoot_signature_label'], row['member_count']) for row in signature_classes],
        [
            ('P+1_S+0', 3),
            ('P+2_S+0', 1),
            ('P+0_S+1', 2),
            ('P+0_S+2', 1),
            ('P+0_S+3', 1),
            ('P+0_S+4', 1),
        ],
        'overshoot signature class counts',
    )

    axis_families = build_primitive_overshoot_axis_families()
    _assert_equal(
        axis_families,
        [
            {
                'overshoot_axis_family': 'precision_only_hitchhike',
                'member_count': 4,
                'overshoot_signature_labels': ['P+1_S+0', 'P+2_S+0'],
                'overshoot_l1_unit_histogram': {1: 3, 2: 1},
                'member_demands': [
                    {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 2},
                    {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 3},
                    {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 4},
                    {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 4},
                ],
            },
            {
                'overshoot_axis_family': 'suffix_only_hitchhike',
                'member_count': 5,
                'overshoot_signature_labels': ['P+0_S+1', 'P+0_S+2', 'P+0_S+3', 'P+0_S+4'],
                'overshoot_l1_unit_histogram': {1: 2, 2: 1, 3: 1, 4: 1},
                'member_demands': [
                    {'middle_precision_relief_units': 1, 'relaxed_suffix_release_units': 0},
                    {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 0},
                    {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 1},
                    {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 2},
                    {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 3},
                ],
            },
        ],
        'overshoot axis families',
    )

    report = build_weakening_primitive_overshoot_taxonomy_snapshot()
    _assert_equal(report['headline_findings']['mixed_axis_hitchhike_count'], 0, 'headline mixed-axis count')
    _assert_equal(report['headline_findings']['single_axis_hitchhike_count'], 9, 'headline single-axis count')
    _assert_equal(report['headline_findings']['max_precision_only_hitchhike_units'], 2, 'headline max precision hitchhike')
    _assert_equal(report['headline_findings']['max_suffix_only_hitchhike_units'], 4, 'headline max suffix hitchhike')
    _assert_equal(report['headline_findings']['worst_precision_hitchhike_demands'], [
        {'middle_precision_relief_units': 0, 'relaxed_suffix_release_units': 4},
    ], 'headline worst precision hitchhike demands')
    _assert_equal(report['headline_findings']['worst_suffix_hitchhike_demands'], [
        {'middle_precision_relief_units': 2, 'relaxed_suffix_release_units': 0},
    ], 'headline worst suffix hitchhike demands')
    _assert_equal(report['headline_findings']['all_unreachable_demands_require_axis_pure_overshoot'], True, 'headline axis-pure flag')

    print('weakening primitive overshoot taxonomy checks passed')


if __name__ == '__main__':
    main()
