#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORNER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_policy_box_corner_snapshot_20260306.json'
TRAJECTORY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
ROBUSTNESS_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json'
QUESTION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json'
UNIQUE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_normal_form_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_normal_form_snapshot_20260306.md'


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


def _canonical_policy_box(corner: dict[str, object], trajectory: dict[str, object]) -> dict[str, object]:
    corner_box = corner['headline_findings']['policy_box_under_test']
    trajectory_box = trajectory['headline_findings']['policy_box_under_test']

    if corner_box['covered_budget_caps'] != trajectory_box['budget_family']:
        raise SystemExit('budget family mismatch across source reports')
    if corner_box['width_floor_lower_exclusive'] != trajectory_box['width_floor_lower_exclusive']:
        raise SystemExit('width floor lower bound mismatch across source reports')
    if corner_box['width_floor_upper_inclusive'] != trajectory_box['width_floor_upper_inclusive']:
        raise SystemExit('width floor upper bound mismatch across source reports')
    if corner_box['delta_ceiling_lower_exclusive'] != trajectory_box['delta_ceiling_lower_exclusive']:
        raise SystemExit('delta ceiling lower bound mismatch across source reports')
    if corner_box['delta_ceiling_upper_inclusive'] != trajectory_box['delta_ceiling_upper_inclusive']:
        raise SystemExit('delta ceiling upper bound mismatch across source reports')
    if corner_box['minimum_additional_budget_cap_inclusive'] != trajectory_box['minimum_additional_budget_cap_inclusive']:
        raise SystemExit('minimum cap mismatch across source reports')

    return {
        'budget_family': corner_box['covered_budget_caps'],
        'width_floor_lower_exclusive': corner_box['width_floor_lower_exclusive'],
        'width_floor_upper_inclusive': corner_box['width_floor_upper_inclusive'],
        'width_floor_representatives': corner_box['width_floor_representatives'],
        'delta_ceiling_lower_exclusive': corner_box['delta_ceiling_lower_exclusive'],
        'delta_ceiling_upper_inclusive': corner_box['delta_ceiling_upper_inclusive'],
        'delta_ceiling_representatives': corner_box['delta_ceiling_representatives'],
        'minimum_additional_budget_cap_inclusive': corner_box['minimum_additional_budget_cap_inclusive'],
        'maximum_additional_budget_cap_checked': trajectory_box['maximum_additional_budget_cap_checked'],
        'representative_additional_budget_caps': corner_box['additional_budget_cap_representatives'],
        'representative_corner_count': corner['headline_findings']['corner_count_checked'],
    }


def _build_summary() -> dict[str, object]:
    corner = _load_json(CORNER_PATH)
    trajectory = _load_json(TRAJECTORY_PATH)
    robustness = _load_json(ROBUSTNESS_PATH)
    question = _load_json(QUESTION_PATH)
    unique = _load_json(UNIQUE_PATH)

    corner_findings = corner['headline_findings']
    trajectory_findings = trajectory['headline_findings']
    robustness_findings = robustness['headline_findings']
    question_findings = question['headline_findings']
    unique_findings = unique['headline_findings']

    policy_box = _canonical_policy_box(corner, trajectory)
    strict_thresholds = unique_findings['universally_required_boundary_thresholds_in_order']
    if strict_thresholds != ['-0.000463764', '0.000033068', '0.000313597']:
        raise SystemExit(f'unexpected strict thresholds: {strict_thresholds}')

    direct_strict_rows = [
        {
            'rho_interval': f"rho < {strict_thresholds[0]}",
            'strict_path_class': 'MMM',
            'winner_path_by_cap_growth': ['TTTMMMMMU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'material_robust_all_checked_caps',
        },
        {
            'rho_interval': f"{strict_thresholds[0]} < rho < {strict_thresholds[1]}",
            'strict_path_class': 'SMM',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMMU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'rho_interval': f"{strict_thresholds[1]} < rho < {strict_thresholds[2]}",
            'strict_path_class': 'SMS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMMU', 'TTTMMMMUU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'cap_sensitive_across_checked_caps',
        },
        {
            'rho_interval': f"rho > {strict_thresholds[2]}",
            'strict_path_class': 'SSS',
            'winner_path_by_cap_growth': ['TTTMMMMUU', 'TTTMMMMUU', 'TTTMMMMUU'],
            'portable_probe_contract_if_black_box_only': [10, 20, 10000],
            'overturn_risk_class': 'stability_robust_all_checked_caps',
        },
    ]

    route_rows = [
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

    return {
        'focus': 'Collapse the scattered family10 rematch-delta handoff into one operator-grade normal form: certify the box, classify directly from declared weights when possible, and only then fall back to the smallest probe contract matched to the question.',
        'method_note': 'Started from the certified family10 policy box, the hazard-normalized cap-trajectory thresholds, the unique exact boundary witnesses, and the question-targeted probe-routing contract. Canonicalized the policy-box fields because earlier reports carried the same box under slightly different key names, then assembled one normal form that prefers zero-probe direct rho classification whenever declared weights are available and otherwise routes to the smallest black-box probe system that answers the actual question.',
        'headline_findings': {
            'material_anchor': trajectory_findings['material_anchor'],
            'stability_anchor': trajectory_findings['stability_anchor'],
            'canonical_policy_box': policy_box,
            'policy_box_is_corner_certified': corner_findings['candidate_identity_invariant_across_all_representative_corners'] and corner_findings['priority_profile_winners_invariant_across_all_representative_corners'],
            'baseline_nonhazard_surplus_expression': trajectory_findings['baseline_nonhazard_surplus_expression'],
            'hazard_normalized_margin_definition_when_w_hazard_gt_0': trajectory_findings['hazard_normalized_margin_definition_when_w_hazard_gt_0'],
            'zero_hazard_weight_degenerate_rule': trajectory_findings['zero_hazard_weight_degenerate_rule'],
            'exact_strict_thresholds_in_increasing_order': [
                {'boundary_name': 'tau(10)', 'cap': 10, 'value': strict_thresholds[0]},
                {'boundary_name': 'tau(10000)', 'cap': 10000, 'value': strict_thresholds[1]},
                {'boundary_name': 'tau(20)', 'cap': 20, 'value': strict_thresholds[2]},
            ],
            'robustness_boundaries_are_first_and_last_strict_thresholds': [strict_thresholds[0], strict_thresholds[2]],
            'direct_zero_probe_classifier_available_when_weights_declared': True,
            'fixed_black_box_signature_for_exact_strict_path': question_findings['unique_fixed_signature_for_exact_strict_path'],
            'adaptive_black_box_tree_for_exact_strict_path': question_findings['unique_adaptive_tree_for_exact_strict_path'],
            'fixed_black_box_signature_for_overturn_risk': question_findings['unique_fixed_signature_for_overturn_risk'],
            'most_compact_handoff_rule': 'if declared weights are available, classify directly from rho with zero cap probes; only use [10,20,10000] or its adaptive reductions when the choice must be diagnosed from winner symbols alone',
            'why_this_normal_form_matters': 'it removes the last routing ambiguity by separating direct weight-based classification from black-box probe-based diagnosis, so future inheritors no longer have to infer whether probes are necessary at all',
        },
        'direct_strict_class_rows': direct_strict_rows,
        'route_rows': route_rows,
        'source_reports': [
            str(CORNER_PATH.relative_to(ROOT)),
            str(TRAJECTORY_PATH.relative_to(ROOT)),
            str(ROBUSTNESS_PATH.relative_to(ROOT)),
            str(QUESTION_PATH.relative_to(ROOT)),
            str(UNIQUE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    strict_rows = summary['direct_strict_class_rows']
    route_rows = summary['route_rows']
    policy_box = findings['canonical_policy_box']
    lines = [
        '# Rematch-Proxy Delta Decision Normal Form Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the corner-certified family10 policy box, the hazard-normalized threshold curve, the exact boundary-witness probe results, and the question-targeted routing note',
        '- canonicalized the policy-box fields because earlier reports described the same box under slightly different key names',
        '- then assembled one operator-grade normal form that prefers zero-probe direct classification whenever declared weights are available',
        '',
        'Headline findings:',
        f"- certified policy box: family `{policy_box['budget_family']}`, width floor `({policy_box['width_floor_lower_exclusive']}, {policy_box['width_floor_upper_inclusive']}]`, ceiling `({policy_box['delta_ceiling_lower_exclusive']}, {policy_box['delta_ceiling_upper_inclusive']}]`, cap range `[{policy_box['minimum_additional_budget_cap_inclusive']}, {policy_box['maximum_additional_budget_cap_checked']}]`.",
        f"- direct classifier available when weights are declared: `{findings['direct_zero_probe_classifier_available_when_weights_declared']}`.",
        f"- baseline surplus: `{findings['baseline_nonhazard_surplus_expression']}`.",
        f"- when `w_hazard > 0`, classify by `{findings['hazard_normalized_margin_definition_when_w_hazard_gt_0']}` and compare to `tau(10) = {findings['exact_strict_thresholds_in_increasing_order'][0]['value']}`, `tau(10000) = {findings['exact_strict_thresholds_in_increasing_order'][1]['value']}`, `tau(20) = {findings['exact_strict_thresholds_in_increasing_order'][2]['value']}`.",
        f"- practical rule: {findings['most_compact_handoff_rule']}.",
        '',
        'Direct rho classification (no cap probes needed when weights are known):',
    ]
    for row in strict_rows:
        lines.append(
            f"- `{row['rho_interval']}` -> strict class `{row['strict_path_class']}`, winner path `{row['winner_path_by_cap_growth']}`, robustness class `{row['overturn_risk_class']}`."
        )
    lines.extend([
        '',
        'Fallback routing when only black-box winner symbols are available:',
    ])
    for row in route_rows:
        lines.append(
            f"- `{row['question_class']}` with `{row['available_information']}` -> `{row['minimal_contract']}`; {row['what_to_do']}; worst-case probes `{row['worst_case_probe_count']}`."
        )
    lines.extend([
        '',
        'Implication for the archive:',
        '- stop treating cap probes as the default interface to the final family10 choice.',
        '- probes are now explicitly the fallback path for black-box diagnosis; the primary path is direct rho comparison whenever declared weights are known.',
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
