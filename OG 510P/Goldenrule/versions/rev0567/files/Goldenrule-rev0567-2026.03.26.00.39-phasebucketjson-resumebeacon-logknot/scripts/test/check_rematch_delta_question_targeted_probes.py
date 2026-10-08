#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json'


def _load() -> dict[str, object]:
    return json.loads(REPORT_PATH.read_text(encoding='utf-8'))


def main() -> None:
    report = _load()
    findings = report['headline_findings']
    assert findings['stability_anchor'] == 'TTTMMMMUU'
    assert findings['material_anchor'] == 'TTTMMMMMU'
    assert findings['strict_question_partition_size'] == 4
    assert findings['robustness_question_partition_size'] == 3
    assert findings['unique_fixed_signature_for_exact_strict_path'] == [10, 20, 10000]
    assert findings['unique_adaptive_tree_for_exact_strict_path'] == {
        'first_probe': 10000,
        'after_M': 10,
        'after_S': 20,
    }
    assert findings['unique_fixed_signature_for_overturn_risk'] == [10, 20]
    assert findings['symmetric_adaptive_trees_for_overturn_risk'] == [
        {'first_probe': 10, 'second_probe_if_needed': 20},
        {'first_probe': 20, 'second_probe_if_needed': 10},
    ]
    assert findings['tail_boundary_needed_only_for_exact_strict_path'] is True
    assert findings['portable_exact_path_cost_over_portable_overturn_risk'] == 1
    assert findings['adaptive_exact_path_best_case_cost_over_adaptive_overturn_risk'] == 1
    assert findings['why_question_targeting_matters'] == (
        'the exact-path contracts spend an extra boundary witness on tau(10000), but that witness only splits the already cap-sensitive middle region and adds no value when the real handoff question is merely whether cap can overturn the choice'
    )
    assert findings['most_practical_rule'] == (
        'match the probe contract to the question: use [10,20] for overturn-risk triage and reserve 10000 for the narrower task of separating the two cap-sensitive strict subclasses'
    )

    assert report['contract_rows'] == [
        {
            'question_class': 'exact_strict_path_portable_record',
            'target_partition': 'four strict rho classes',
            'minimal_contract_type': 'nonadaptive signature',
            'minimal_probe_count_worst_case': 3,
            'minimal_probe_count_best_case': 3,
            'required_probe_caps': [10, 20, 10000],
            'uniqueness_status': 'unique',
            'why_this_contract_is_needed': 'portable ex-post records need one fixed signature that separates all four strict classes without branching',
        },
        {
            'question_class': 'exact_strict_path_live_diagnosis',
            'target_partition': 'four strict rho classes',
            'minimal_contract_type': 'adaptive decision tree',
            'minimal_probe_count_worst_case': 2,
            'minimal_probe_count_best_case': 2,
            'required_probe_caps': [10000, 10, 20],
            'uniqueness_status': 'unique worst-case-optimal tree',
            'why_this_contract_is_needed': 'live diagnosis can branch on the tail split first and finish with one exact boundary witness on the surviving branch',
        },
        {
            'question_class': 'cap_overturn_risk_portable_record',
            'target_partition': 'three robustness classes',
            'minimal_contract_type': 'nonadaptive signature',
            'minimal_probe_count_worst_case': 2,
            'minimal_probe_count_best_case': 2,
            'required_probe_caps': [10, 20],
            'uniqueness_status': 'unique',
            'why_this_contract_is_needed': 'the tail boundary tau(10000) only splits the already cap-sensitive middle region and is unnecessary when the question is only whether cap can ever overturn the choice',
        },
        {
            'question_class': 'cap_overturn_risk_live_diagnosis_material_first',
            'target_partition': 'three robustness classes',
            'minimal_contract_type': 'adaptive decision tree',
            'minimal_probe_count_worst_case': 2,
            'minimal_probe_count_best_case': 1,
            'required_probe_caps': [10, 20],
            'uniqueness_status': 'one of two symmetric worst-case-optimal trees',
            'why_this_contract_is_needed': 'probing cap 10 first gives an immediate certificate of robust material when the first symbol is material',
        },
        {
            'question_class': 'cap_overturn_risk_live_diagnosis_stability_first',
            'target_partition': 'three robustness classes',
            'minimal_contract_type': 'adaptive decision tree',
            'minimal_probe_count_worst_case': 2,
            'minimal_probe_count_best_case': 1,
            'required_probe_caps': [20, 10],
            'uniqueness_status': 'one of two symmetric worst-case-optimal trees',
            'why_this_contract_is_needed': 'probing cap 20 first gives an immediate certificate of robust stability when the first symbol is stability',
        },
    ]

    assert report['implication_rows'] == [
        {
            'finer_question_class': 'exact_strict_path_portable_record',
            'coarser_question_class': 'cap_overturn_risk_portable_record',
            'strictly_finer_reason': 'the three-cap fixed signature separates the two cap-sensitive strict subclasses that robustness triage intentionally merges',
            'probe_overhead_vs_coarser_minimal_contract': 1,
        },
        {
            'finer_question_class': 'exact_strict_path_live_diagnosis',
            'coarser_question_class': 'cap_overturn_risk_live_diagnosis_material_first_or_stability_first',
            'strictly_finer_reason': 'the adaptive strict tree spends its first probe on cap 10000, which never certifies a robustness class by itself but is required to split the two cap-sensitive strict subclasses',
            'probe_overhead_vs_coarser_minimal_contract_in_best_case': 1,
        },
    ]

    assert report['task_routing'] == {
        'if_you_need_a_portable_fixed_record_of_the_exact_path': [10, 20, 10000],
        'if_you_need_a_live_exact_path_diagnosis_with_minimal_worst_case_probes': {
            'first_probe': 10000,
            'after_M': 10,
            'after_S': 20,
        },
        'if_you_only_need_to_know_whether_cap_can_ever_overturn_the_choice': [10, 20],
        'if_you_expect_robust_material_and_want_fastest_early_stop': {
            'first_probe': 10,
            'only_if_first_probe_is_S_then_probe': 20,
        },
        'if_you_expect_robust_stability_and_want_fastest_early_stop': {
            'first_probe': 20,
            'only_if_first_probe_is_M_then_probe': 10,
        },
    }

    print('ok: rematch delta question-targeted probe snapshot')


if __name__ == '__main__':
    main()
