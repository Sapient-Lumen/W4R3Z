#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROBUSTNESS_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json'
ADAPTIVE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.json'
UNIQUE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.md'


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _build_summary() -> dict[str, object]:
    robustness = _load_json(ROBUSTNESS_PATH)
    adaptive = _load_json(ADAPTIVE_PATH)
    unique = _load_json(UNIQUE_PATH)

    robustness_findings = robustness['headline_findings']
    adaptive_findings = adaptive['headline_findings']
    unique_findings = unique['headline_findings']

    strict_fixed_caps = unique_findings['unique_minimal_sufficient_probe_caps_when_using_strict_winner_symbols']
    strict_adaptive_caps = adaptive_findings['unique_worst_case_optimal_adaptive_probe_tree_probe_caps']
    robustness_fixed_caps = robustness_findings['unique_minimal_nonadaptive_probe_caps']

    if strict_fixed_caps != [10, 20, 10000]:
        raise SystemExit(f'unexpected strict fixed caps: {strict_fixed_caps}')
    if strict_adaptive_caps != [10000, 10, 20]:
        raise SystemExit(f'unexpected strict adaptive caps: {strict_adaptive_caps}')
    if robustness_fixed_caps != [10, 20]:
        raise SystemExit(f'unexpected robustness fixed caps: {robustness_fixed_caps}')

    contract_rows = [
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

    implication_rows = [
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

    task_routing = {
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

    return {
        'focus': 'Compress the accumulated cap-probe results into one question-targeted contract stack so future inheritors can choose the smallest probe system that actually answers their question.',
        'method_note': 'Started from the unique minimal fixed-signature result for four strict classes, the unique worst-case-optimal adaptive strict classifier, and the smaller robustness-triage probe result. Compared the target partitions these contracts resolve, then built a minimal routing table from question type to required probe system. The key observation is that the tail boundary tau(10000) is only needed when the two cap-sensitive strict subclasses must be separated; it should disappear as soon as the question collapses to overturn-risk triage.',
        'headline_findings': {
            'stability_anchor': adaptive_findings['stability_anchor'],
            'material_anchor': adaptive_findings['material_anchor'],
            'strict_question_partition_size': adaptive_findings['strict_trajectory_class_count_when_w_hazard_gt_0'],
            'robustness_question_partition_size': robustness_findings['robustness_triage_class_count_when_w_hazard_gt_0'],
            'unique_fixed_signature_for_exact_strict_path': strict_fixed_caps,
            'unique_adaptive_tree_for_exact_strict_path': {
                'first_probe': 10000,
                'after_M': 10,
                'after_S': 20,
            },
            'unique_fixed_signature_for_overturn_risk': robustness_fixed_caps,
            'symmetric_adaptive_trees_for_overturn_risk': [
                {'first_probe': 10, 'second_probe_if_needed': 20},
                {'first_probe': 20, 'second_probe_if_needed': 10},
            ],
            'tail_boundary_needed_only_for_exact_strict_path': True,
            'portable_exact_path_cost_over_portable_overturn_risk': 1,
            'adaptive_exact_path_best_case_cost_over_adaptive_overturn_risk': 1,
            'why_question_targeting_matters': 'the exact-path contracts spend an extra boundary witness on tau(10000), but that witness only splits the already cap-sensitive middle region and adds no value when the real handoff question is merely whether cap can overturn the choice',
            'most_practical_rule': 'match the probe contract to the question: use [10,20] for overturn-risk triage and reserve 10000 for the narrower task of separating the two cap-sensitive strict subclasses',
        },
        'contract_rows': contract_rows,
        'implication_rows': implication_rows,
        'task_routing': task_routing,
        'source_reports': [
            str(ROBUSTNESS_PATH.relative_to(ROOT)),
            str(ADAPTIVE_PATH.relative_to(ROOT)),
            str(UNIQUE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    rows = summary['contract_rows']
    implications = summary['implication_rows']
    routing = summary['task_routing']
    lines = [
        '# Rematch-Proxy Delta Question-Targeted Probe Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the unique fixed three-cap strict-path witness, the unique adaptive strict-path tree, and the smaller robustness-triage probe result',
        '- compared the partitions those contracts actually resolve',
        '- then built one minimal routing table from question type to required probe system',
        '',
        'Headline findings:',
        f"- exact strict-path diagnosis resolves `{findings['strict_question_partition_size']}` classes, while overturn-risk triage resolves only `{findings['robustness_question_partition_size']}` classes.",
        f"- the unique fixed signature for the exact strict path is `{findings['unique_fixed_signature_for_exact_strict_path']}`.",
        f"- the unique fixed signature for overturn-risk triage is `{findings['unique_fixed_signature_for_overturn_risk']}`.",
        f"- `{findings['why_question_targeting_matters']}`.",
        f"- practical rule: {findings['most_practical_rule']}.",
        '',
        'Question-targeted contract stack:',
    ]
    for row in rows:
        lines.append(
            f"- `{row['question_class']}` -> `{row['minimal_contract_type']}` with probes `{row['required_probe_caps']}` "
            f"(best `{row['minimal_probe_count_best_case']}`, worst `{row['minimal_probe_count_worst_case']}`); {row['why_this_contract_is_needed']}."
        )
    lines.extend([
        '',
        'Why the finer exact-path contracts cost more:',
    ])
    for row in implications:
        extra = row.get('probe_overhead_vs_coarser_minimal_contract', row.get('probe_overhead_vs_coarser_minimal_contract_in_best_case'))
        lines.append(
            f"- `{row['finer_question_class']}` is strictly finer than `{row['coarser_question_class']}` because {row['strictly_finer_reason']}; minimum extra probe cost = `{extra}`."
        )
    lines.extend([
        '',
        'Minimal routing table:',
        f"- portable exact-path record -> `{routing['if_you_need_a_portable_fixed_record_of_the_exact_path']}`",
        f"- live exact-path diagnosis -> first `{routing['if_you_need_a_live_exact_path_diagnosis_with_minimal_worst_case_probes']['first_probe']}`, then `{routing['if_you_need_a_live_exact_path_diagnosis_with_minimal_worst_case_probes']['after_M']}` after `M` or `{routing['if_you_need_a_live_exact_path_diagnosis_with_minimal_worst_case_probes']['after_S']}` after `S`",
        f"- overturn-risk triage -> `{routing['if_you_only_need_to_know_whether_cap_can_ever_overturn_the_choice']}`",
        f"- material-first early stop -> first `{routing['if_you_expect_robust_material_and_want_fastest_early_stop']['first_probe']}`, then `{routing['if_you_expect_robust_material_and_want_fastest_early_stop']['only_if_first_probe_is_S_then_probe']}` only if needed",
        f"- stability-first early stop -> first `{routing['if_you_expect_robust_stability_and_want_fastest_early_stop']['first_probe']}`, then `{routing['if_you_expect_robust_stability_and_want_fastest_early_stop']['only_if_first_probe_is_M_then_probe']}` only if needed",
        '',
        'Implication for the archive:',
        '- do not default to the three-cap strict signature when the real handoff question is only whether additional budget can overturn the final two-anchor choice.',
        '- reserve cap `10000` for the narrower task of splitting the two cap-sensitive strict subclasses.',
    ])
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _round(_build_summary())
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
