#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['strict_trajectory_class_count_when_w_hazard_gt_0'] == 4
    assert findings['nonadaptive_minimal_probe_count_for_universal_strict_classification'] == 3
    assert findings['adaptive_minimal_worst_case_probe_count_for_universal_strict_classification'] == 2
    assert findings['binary_lower_bound_reason'] == (
        'four strict classes cannot be universally classified with fewer than two binary probes'
    )
    assert findings['adaptive_probe_savings_vs_nonadaptive_worst_case'] == 1
    assert findings['unique_worst_case_optimal_first_probe_cap'] == 10000
    assert findings['why_cap_10000_must_be_first'] == (
        'only cap 10000 realizes tau(10000), the shared boundary between the lower two and upper two strict rho classes, so every other first probe leaves a three-class branch'
    )
    assert findings['unique_second_probe_after_M_at_cap_10000'] == 10
    assert findings['unique_second_probe_after_S_at_cap_10000'] == 20
    assert findings['unique_worst_case_optimal_adaptive_probe_tree_probe_caps'] == [10000, 10, 20]
    assert findings['uniform_strict_class_prior_expected_probe_count'] == 2.0
    assert findings['why_this_is_stronger_than_the_three_probe_result'] == (
        'the archive no longer needs a fixed three-symbol signature to classify the strict class; one tail probe plus one branch-specific boundary probe always suffices'
    )

    tree = report['adaptive_decision_tree']
    assert tree == [
        {
            'step': 1,
            'probe_cap': 10000,
            'boundary_threshold_witnessed_exactly': 'tau(10000)',
            'if_symbol_is_M': {
                'remaining_classes': [
                    'material_all_checked_caps',
                    'low_cap_stability_then_material',
                ],
                'go_to_step': 2,
            },
            'if_symbol_is_S': {
                'remaining_classes': [
                    'stability_then_mid_cap_material_then_tail_stability',
                    'stability_all_checked_caps',
                ],
                'go_to_step': 3,
            },
        },
        {
            'step': 2,
            'applies_after': 'M at cap 10000',
            'probe_cap': 10,
            'boundary_threshold_witnessed_exactly': 'tau(10)',
            'if_symbol_is_M': 'material_all_checked_caps',
            'if_symbol_is_S': 'low_cap_stability_then_material',
        },
        {
            'step': 3,
            'applies_after': 'S at cap 10000',
            'probe_cap': 20,
            'boundary_threshold_witnessed_exactly': 'tau(20)',
            'if_symbol_is_M': 'stability_then_mid_cap_material_then_tail_stability',
            'if_symbol_is_S': 'stability_all_checked_caps',
        },
    ]

    branches = report['first_probe_branch_rows']
    assert branches == [
        {
            'first_probe_symbol_at_cap_10000': 'M',
            'strict_rho_region': 'rho < 0.000033068',
            'remaining_classes': [
                'material_all_checked_caps',
                'low_cap_stability_then_material',
            ],
            'required_second_probe_cap': 10,
            'why_this_second_probe_is_forced': (
                'within the lower pair, the only remaining shared class boundary is tau(10), and only cap 10 realizes it exactly'
            ),
        },
        {
            'first_probe_symbol_at_cap_10000': 'S',
            'strict_rho_region': 'rho > 0.000033068',
            'remaining_classes': [
                'stability_then_mid_cap_material_then_tail_stability',
                'stability_all_checked_caps',
            ],
            'required_second_probe_cap': 20,
            'why_this_second_probe_is_forced': (
                'within the upper pair, the only remaining shared class boundary is tau(20), and only cap 20 realizes it exactly'
            ),
        },
    ]

    support = report['supporting_boundaries']
    assert support == {
        'low_pair_boundary': 'tau(10) = -0.000463764',
        'middle_pair_boundary': 'tau(10000) = 0.000033068',
        'upper_pair_boundary': 'tau(20) = 0.000313597',
        'exact_boundary_witness_caps': [10, 20, 10000],
    }

    print('ok: rematch delta adaptive cap probes snapshot')


if __name__ == '__main__':
    main()
