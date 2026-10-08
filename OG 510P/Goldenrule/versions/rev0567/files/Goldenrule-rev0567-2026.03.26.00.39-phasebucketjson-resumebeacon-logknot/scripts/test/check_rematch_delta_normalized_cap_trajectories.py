#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    policy_box = findings['policy_box_under_test']
    assert policy_box['budget_family'] == [10, 20, 50, 100]
    assert policy_box['minimum_additional_budget_cap_inclusive'] == 10
    assert policy_box['maximum_additional_budget_cap_checked'] == 10000
    assert policy_box['representative_face_count_checked_per_cap'] == 4

    assert findings['hazard_normalized_margin_definition_when_w_hazard_gt_0'] == 'rho = baseline_nonhazard_surplus / w_hazard'
    assert findings['cap_specific_stability_rule_when_w_hazard_gt_0'] == 'choose TTTMMMMUU at cap c iff rho > tau(c), where tau(c) = material_clearance(c) - stability_clearance(c)'
    assert findings['zero_hazard_weight_degenerate_rule'] == 'if w_hazard = 0, cap becomes irrelevant and the winner is whichever anchor makes baseline_nonhazard_surplus positive or negative'
    assert findings['exact_threshold_curve_shape_over_checked_caps'] == 'strictly increasing on caps 10..20, then strictly decreasing on caps 20..10000'
    assert findings['minimum_tau_on_checked_caps'] == -0.000464
    assert findings['cap_with_minimum_tau_on_checked_caps'] == 10
    assert findings['maximum_tau_on_checked_caps'] == 0.000314
    assert findings['cap_with_maximum_tau_on_checked_caps'] == 20
    assert findings['tail_tau_at_cap_10000'] == 0.000033
    assert findings['strict_trajectory_class_count_when_w_hazard_gt_0'] == 4
    assert findings['single_reversal_band_when_w_hazard_gt_0'] == '-0.000463764 < rho < 0.000033068'
    assert findings['double_reversal_band_when_w_hazard_gt_0'] == '0.000033068 < rho < 0.000313597'

    classes = report['trajectory_classes']
    assert [row['class_label'] for row in classes] == [
        'material_all_checked_caps',
        'low_cap_stability_then_material',
        'stability_then_mid_cap_material_then_tail_stability',
        'stability_all_checked_caps',
    ]
    assert classes[0]['reversals_as_cap_increases'] == 0
    assert classes[1]['reversals_as_cap_increases'] == 1
    assert classes[1]['representative_rho'] == -0.000215
    assert classes[1]['representative_stability_cap_intervals'] == [{'start_cap': 10, 'end_cap': 12}]
    assert classes[2]['reversals_as_cap_increases'] == 2
    assert classes[2]['representative_rho'] == 0.000173
    assert classes[2]['representative_stability_cap_intervals'] == [
        {'start_cap': 10, 'end_cap': 17},
        {'start_cap': 89, 'end_cap': 10000},
    ]
    assert classes[3]['reversals_as_cap_increases'] == 0

    boundary = report['boundary_tie_cases']
    assert [row['tie_occurs_at_cap'] for row in boundary] == [10, 10000, 20]
    assert boundary[0]['rho_equals_tau'] == -0.000464
    assert boundary[1]['rho_equals_tau'] == 0.000033
    assert boundary[2]['rho_equals_tau'] == 0.000314

    rows = report['representative_threshold_rows']
    lookup = {row['additional_budget_cap']: row['normalized_threshold_for_stability'] for row in rows}
    assert lookup == {
        10: -0.000464,
        14: -0.000064,
        15: 0.000017,
        20: 0.000314,
        100: 0.000164,
        1000: 0.000066,
        10000: 0.000033,
    }

    print('ok: rematch delta normalized cap trajectories snapshot')


if __name__ == '__main__':
    main()
