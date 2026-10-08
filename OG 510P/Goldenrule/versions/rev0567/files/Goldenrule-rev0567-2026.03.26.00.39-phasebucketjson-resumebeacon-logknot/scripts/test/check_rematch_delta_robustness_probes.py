#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['strict_trajectory_class_count_when_w_hazard_gt_0'] == 4
    assert findings['robustness_triage_class_count_when_w_hazard_gt_0'] == 3
    assert findings['cap_sensitive_strict_classes_collapsed_into_one_middle_class'] == [
        'low_cap_stability_then_material',
        'stability_then_mid_cap_material_then_tail_stability',
    ]
    assert findings['material_robust_region_when_w_hazard_gt_0'] == 'rho < -0.000463764'
    assert findings['cap_sensitive_region_when_w_hazard_gt_0'] == '-0.000463764 < rho < 0.000313597'
    assert findings['stability_robust_region_when_w_hazard_gt_0'] == 'rho > 0.000313597'
    assert findings['minimum_nonadaptive_probe_count_for_universal_robustness_triage'] == 2
    assert findings['unique_minimal_nonadaptive_probe_caps'] == [10, 20]
    assert findings['why_cap_10000_is_not_needed_for_robustness_triage'] == (
        'cap 10000 only separates the two cap-sensitive strict subclasses, and robustness triage merges them into one middle class'
    )
    assert findings['minimum_adaptive_worst_case_probe_count_for_universal_robustness_triage'] == 2
    assert findings['adaptive_best_case_probe_count_for_universal_robustness_triage'] == 1
    assert findings['one_probe_universal_robustness_triage_is_impossible_reason'] == (
        'a single strict winner probe has only two symbols, but robustness triage has three classes'
    )
    assert findings['number_of_symmetric_worst_case_optimal_adaptive_trees'] == 2
    assert findings['uniform_robustness_class_prior_expected_probe_count_for_optimal_adaptive_tree'] == 1.666667
    assert findings['early_stop_certificate_after_M_at_cap_10'] == 'material is cap-robust across all checked caps'
    assert findings['early_stop_certificate_after_S_at_cap_20'] == 'stability is cap-robust across all checked caps'
    assert findings['most_practical_probe_contract'] == (
        'use caps 10 and 20 when the question is only whether additional budget can ever overturn the final choice'
    )

    assert report['nonadaptive_signature_rows'] == [
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'MM',
            'diagnosed_robustness_class': 'material_robust_all_checked_caps',
            'strict_rho_region_when_w_hazard_gt_0': 'rho < -0.000463764',
        },
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'SM',
            'diagnosed_robustness_class': 'cap_sensitive_across_checked_caps',
            'strict_rho_region_when_w_hazard_gt_0': '-0.000463764 < rho < 0.000313597',
        },
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'SS',
            'diagnosed_robustness_class': 'stability_robust_all_checked_caps',
            'strict_rho_region_when_w_hazard_gt_0': 'rho > 0.000313597',
        },
    ]

    assert report['boundary_witness_rows'] == [
        {
            'robustness_boundary': [
                'material_robust_all_checked_caps',
                'cap_sensitive_across_checked_caps',
            ],
            'required_exact_threshold_name': 'tau(10)',
            'required_exact_threshold_value_string': '-0.000463764',
            'unique_required_probe_cap': 10,
            'why_this_probe_cap_is_necessary': (
                'cap 20 returns material on both sides of the lower robustness boundary, so only cap 10 can distinguish robust material from cap-sensitive preferences by strict winner symbols'
            ),
        },
        {
            'robustness_boundary': [
                'cap_sensitive_across_checked_caps',
                'stability_robust_all_checked_caps',
            ],
            'required_exact_threshold_name': 'tau(20)',
            'required_exact_threshold_value_string': '0.000313597',
            'unique_required_probe_cap': 20,
            'why_this_probe_cap_is_necessary': (
                'cap 10 returns stability on both sides of the upper robustness boundary, so only cap 20 can distinguish cap-sensitive preferences from robust stability by strict winner symbols'
            ),
        },
    ]

    assert report['symmetric_optimal_adaptive_trees'] == [
        {
            'tree_name': 'material-first early-stop tree',
            'first_probe_cap': 10,
            'if_symbol_is_M': 'material_robust_all_checked_caps',
            'if_symbol_is_S': {
                'second_probe_cap': 20,
                'if_symbol_is_M': 'cap_sensitive_across_checked_caps',
                'if_symbol_is_S': 'stability_robust_all_checked_caps',
            },
            'worst_case_probe_count': 2,
            'best_case_probe_count': 1,
        },
        {
            'tree_name': 'stability-first early-stop tree',
            'first_probe_cap': 20,
            'if_symbol_is_S': 'stability_robust_all_checked_caps',
            'if_symbol_is_M': {
                'second_probe_cap': 10,
                'if_symbol_is_M': 'material_robust_all_checked_caps',
                'if_symbol_is_S': 'cap_sensitive_across_checked_caps',
            },
            'worst_case_probe_count': 2,
            'best_case_probe_count': 1,
        },
    ]

    assert report['strict_boundary_that_drops_out'] == {
        'required_exact_threshold_name': 'tau(10000)',
        'required_exact_threshold_value_string': '0.000033068',
        'unique_probe_cap_that_witnesses_it': 10000,
        'why_it_drops_out_of_robustness_triage': (
            'this boundary only splits low-cap one-reversal from double-reversal behavior inside the already cap-sensitive middle region'
        ),
    }

    print('ok: rematch delta robustness probes snapshot')


if __name__ == '__main__':
    main()
