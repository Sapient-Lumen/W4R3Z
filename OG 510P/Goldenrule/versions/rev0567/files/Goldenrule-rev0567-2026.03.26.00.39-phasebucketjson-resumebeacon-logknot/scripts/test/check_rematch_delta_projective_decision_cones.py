#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_projective_decision_cone_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['canonical_policy_box'] == {
        'budget_family': [10, 20, 50, 100],
        'width_floor_lower_exclusive': 0.00026,
        'width_floor_upper_inclusive': 0.00129,
        'width_floor_representatives': [0.00027, 0.00129],
        'delta_ceiling_lower_exclusive': 0.00822,
        'delta_ceiling_upper_inclusive': 0.01944,
        'delta_ceiling_representatives': [0.00823, 0.01944],
        'minimum_additional_budget_cap_inclusive': 10,
        'maximum_additional_budget_cap_checked': 10000,
        'representative_additional_budget_caps': [10, 10000],
        'representative_corner_count': 8,
    }
    assert findings['baseline_nonhazard_surplus_symbol'] == 'B'
    assert findings['hazard_weight_symbol'] == 'H'
    assert findings['baseline_nonhazard_surplus_expression'] == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties'
    )
    assert findings['nonnegative_hazard_halfplane_under_test'] == 'H = w_hazard >= 0'
    assert findings['division_free_classifier_rule'] == (
        'classify directly in (B,H) by comparing B against tau(10)*H, tau(10000)*H, and tau(20)*H; division by H is optional rather than fundamental'
    )
    assert findings['positive_global_rescaling_preserves_classification'] is True
    assert findings['cap_sensitive_behavior_requires_positive_hazard_weight'] is True
    assert findings['zero_hazard_axis_carries_only_robust_material_robust_stability_or_total_tie'] is True
    assert findings['strict_threshold_rays_in_increasing_slope_order'] == [
        {'boundary_name': 'tau(10)', 'cap': 10, 'value': '-0.000463764'},
        {'boundary_name': 'tau(10000)', 'cap': 10000, 'value': '0.000033068'},
        {'boundary_name': 'tau(20)', 'cap': 20, 'value': '0.000313597'},
    ]
    assert findings['projective_coordinate_when_H_gt_0'] == 'rho = baseline_nonhazard_surplus / w_hazard'
    assert findings['origin_rule'] == 'H = 0 and B = 0 gives an exact tie on every checked cap'
    assert findings['most_compact_handoff_rule'] == (
        'if declared weights are available, treat the final family10 choice as a cone problem in (B,H): classify by the sign of B and by whether B lies below tau(10)*H, between tau(10)*H and tau(10000)*H, between tau(10000)*H and tau(20)*H, or above tau(20)*H'
    )

    assert report['strict_sector_rows'] == [
        {
            'sector_label': 'zero_hazard_axis_material_ray',
            'region_condition': 'w_hazard = 0 and baseline_nonhazard_surplus < 0',
            'strict_path_class': 'MMM',
            'winner_path_by_cap_growth': ['TTTMMMMMU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'overturn_risk_class': 'material_robust_all_checked_caps',
        },
        {
            'sector_label': 'positive_hazard_material_cone',
            'region_condition': 'w_hazard > 0 and baseline_nonhazard_surplus < -0.000463764*w_hazard',
            'strict_path_class': 'MMM',
            'winner_path_by_cap_growth': ['TTTMMMMMU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'overturn_risk_class': 'material_robust_all_checked_caps',
        },
        {
            'sector_label': 'positive_hazard_single_reversal_cone',
            'region_condition': 'w_hazard > 0 and -0.000463764*w_hazard < baseline_nonhazard_surplus < 0.000033068*w_hazard',
            'strict_path_class': 'SMM',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'sector_label': 'positive_hazard_double_reversal_cone',
            'region_condition': 'w_hazard > 0 and 0.000033068*w_hazard < baseline_nonhazard_surplus < 0.000313597*w_hazard',
            'strict_path_class': 'SMS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMUU'],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'sector_label': 'positive_hazard_stability_cone',
            'region_condition': 'w_hazard > 0 and baseline_nonhazard_surplus > 0.000313597*w_hazard',
            'strict_path_class': 'SSS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMUU', 'TTTMMMMUU'],
            'overturn_risk_class': 'stability_robust_all_checked_caps',
        },
        {
            'sector_label': 'zero_hazard_axis_stability_ray',
            'region_condition': 'w_hazard = 0 and baseline_nonhazard_surplus > 0',
            'strict_path_class': 'SSS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMUU', 'TTTMMMMUU'],
            'overturn_risk_class': 'stability_robust_all_checked_caps',
        },
    ]

    assert report['boundary_rows'] == [
        {
            'boundary_label': 'origin_all_cap_tie_point',
            'region_condition': 'w_hazard = 0 and baseline_nonhazard_surplus = 0',
            'tie_caps': 'all checked caps 10..10000',
            'winner_path_away_from_boundary': 'none; this is total indifference on the checked cap range',
        },
        {
            'boundary_label': 'tau10_boundary_ray',
            'region_condition': 'w_hazard > 0 and baseline_nonhazard_surplus = -0.000463764*w_hazard',
            'tie_caps': [10],
            'winner_path_away_from_boundary': 'TTTMMMMMU at every larger checked cap',
        },
        {
            'boundary_label': 'tau10000_boundary_ray',
            'region_condition': 'w_hazard > 0 and baseline_nonhazard_surplus = 0.000033068*w_hazard',
            'tie_caps': [10000],
            'winner_path_away_from_boundary': 'TTTMMMMUU on low caps, TTTMMMMMU on a middle cap band, then tie at cap 10000',
        },
        {
            'boundary_label': 'tau20_boundary_ray',
            'region_condition': 'w_hazard > 0 and baseline_nonhazard_surplus = 0.000313597*w_hazard',
            'tie_caps': [20],
            'winner_path_away_from_boundary': 'TTTMMMMUU on every smaller and larger checked cap except the tie at cap 20',
        },
    ]

    examples = report['positive_scale_invariance_examples']
    assert [row['example_label'] for row in examples] == [
        'axis_material',
        'positive_hazard_material',
        'positive_hazard_lowcap_stability_then_material',
        'positive_hazard_double_reversal',
        'positive_hazard_stability',
        'axis_stability',
    ]
    assert all(row['scaled_by_lambda'] == '7' for row in examples)
    assert [row['strict_class_preserved'] for row in examples] == ['MMM', 'MMM', 'SMM', 'SMS', 'SSS', 'SSS']

    print('projective-decision-cones: ok')


if __name__ == '__main__':
    main()
