#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_normal_form_snapshot_20260306.json'


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
    assert findings['policy_box_is_corner_certified'] is True
    assert findings['baseline_nonhazard_surplus_expression'] == (
        '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties'
    )
    assert findings['hazard_normalized_margin_definition_when_w_hazard_gt_0'] == (
        'rho = baseline_nonhazard_surplus / w_hazard'
    )
    assert findings['zero_hazard_weight_degenerate_rule'] == (
        'if w_hazard = 0, cap becomes irrelevant and the winner is whichever anchor makes baseline_nonhazard_surplus positive or negative'
    )
    assert findings['exact_strict_thresholds_in_increasing_order'] == [
        {'boundary_name': 'tau(10)', 'cap': 10, 'value': '-0.000463764'},
        {'boundary_name': 'tau(10000)', 'cap': 10000, 'value': '0.000033068'},
        {'boundary_name': 'tau(20)', 'cap': 20, 'value': '0.000313597'},
    ]
    assert findings['robustness_boundaries_are_first_and_last_strict_thresholds'] == ['-0.000463764', '0.000313597']
    assert findings['direct_zero_probe_classifier_available_when_weights_declared'] is True
    assert findings['fixed_black_box_signature_for_exact_strict_path'] == [10, 20, 10000]
    assert findings['adaptive_black_box_tree_for_exact_strict_path'] == {
        'first_probe': 10000,
        'after_M': 10,
        'after_S': 20,
    }
    assert findings['fixed_black_box_signature_for_overturn_risk'] == [10, 20]
    assert findings['most_compact_handoff_rule'] == (
        'if declared weights are available, classify directly from rho with zero cap probes; only use [10,20,10000] or its adaptive reductions when the choice must be diagnosed from winner symbols alone'
    )

    assert report['direct_strict_class_rows'] == [
        {
            'rho_interval': 'rho < -0.000463764',
            'strict_path_class': 'MMM',
            'winner_path_by_cap_growth': ['TTTMMMMMU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'material_robust_all_checked_caps',
        },
        {
            'rho_interval': '-0.000463764 < rho < 0.000033068',
            'strict_path_class': 'SMM',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'rho_interval': '0.000033068 < rho < 0.000313597',
            'strict_path_class': 'SMS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMUU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'rho_interval': 'rho > 0.000313597',
            'strict_path_class': 'SSS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMUU', 'TTTMMMMUU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'stability_robust_all_checked_caps',
        },
    ]

    assert report['route_rows'] == [
        {
            'available_information': 'declared preference weights including w_hazard, and certified family10 policy box applies',
            'question_class': 'exact_strict_path_or_overturn_risk',
            'minimal_contract': 'zero-probe direct classifier',
            'what_to_do': 'compute baseline_nonhazard_surplus, divide by w_hazard when w_hazard > 0, then compare rho against tau(10), tau(10000), and tau(20)',
            'worst_case_probe_count': 0,
        },
        {
            'available_information': 'only strict winner symbols from black-box cap probes',
            'question_class': 'exact_strict_path_portable_record',
            'minimal_contract': 'fixed nonadaptive signature',
            'what_to_do': 'probe caps [10, 20, 10000]',
            'worst_case_probe_count': 3,
        },
        {
            'available_information': 'only strict winner symbols from black-box cap probes',
            'question_class': 'exact_strict_path_live_diagnosis',
            'minimal_contract': 'adaptive decision tree',
            'what_to_do': 'probe 10000 first, then 10 after M or 20 after S',
            'worst_case_probe_count': 2,
        },
        {
            'available_information': 'only strict winner symbols from black-box cap probes',
            'question_class': 'cap_overturn_risk_portable_record',
            'minimal_contract': 'fixed nonadaptive signature',
            'what_to_do': 'probe caps [10, 20]',
            'worst_case_probe_count': 2,
        },
        {
            'available_information': 'only strict winner symbols from black-box cap probes',
            'question_class': 'cap_overturn_risk_live_diagnosis',
            'minimal_contract': 'symmetric early-stop adaptive tree',
            'what_to_do': 'probe 10 then 20 if expecting robust material, or 20 then 10 if expecting robust stability',
            'worst_case_probe_count': 2,
        },
    ]

    print('decision-normal-form: ok')


if __name__ == '__main__':
    main()
