#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
MINIMAL_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.json'
UNIQUE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.md'

MATERIAL_CLASS = 'material_all_checked_caps'
LOW_STABILITY_CLASS = 'low_cap_stability_then_material'
DOUBLE_REVERSAL_CLASS = 'stability_then_mid_cap_material_then_tail_stability'
STABILITY_CLASS = 'stability_all_checked_caps'


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
    normalized = _load_json(NORMALIZED_PATH)
    minimal = _load_json(MINIMAL_PATH)
    unique = _load_json(UNIQUE_PATH)

    findings = normalized['headline_findings']
    probe_findings = minimal['headline_findings']
    unique_findings = unique['headline_findings']
    boundary_rows = unique['boundary_necessity_rows']

    low_boundary = boundary_rows[0]
    tail_boundary = boundary_rows[1]
    peak_boundary = boundary_rows[2]

    if tail_boundary['caps_realizing_required_threshold_exactly'] != [10000]:
        raise SystemExit('expected cap 10000 to be the unique tail-boundary witness')
    if low_boundary['caps_realizing_required_threshold_exactly'] != [10]:
        raise SystemExit('expected cap 10 to be the unique low-boundary witness')
    if peak_boundary['caps_realizing_required_threshold_exactly'] != [20]:
        raise SystemExit('expected cap 20 to be the unique peak-boundary witness')

    classes = normalized['trajectory_classes']
    class_order = [row['class_label'] for row in classes]
    expected_class_order = [
        MATERIAL_CLASS,
        LOW_STABILITY_CLASS,
        DOUBLE_REVERSAL_CLASS,
        STABILITY_CLASS,
    ]
    if class_order != expected_class_order:
        raise SystemExit(f'unexpected class order: {class_order}')

    decision_tree = [
        {
            'step': 1,
            'probe_cap': 10000,
            'boundary_threshold_witnessed_exactly': tail_boundary['required_exact_threshold_name'],
            'if_symbol_is_M': {
                'remaining_classes': [MATERIAL_CLASS, LOW_STABILITY_CLASS],
                'go_to_step': 2,
            },
            'if_symbol_is_S': {
                'remaining_classes': [DOUBLE_REVERSAL_CLASS, STABILITY_CLASS],
                'go_to_step': 3,
            },
        },
        {
            'step': 2,
            'applies_after': 'M at cap 10000',
            'probe_cap': 10,
            'boundary_threshold_witnessed_exactly': low_boundary['required_exact_threshold_name'],
            'if_symbol_is_M': MATERIAL_CLASS,
            'if_symbol_is_S': LOW_STABILITY_CLASS,
        },
        {
            'step': 3,
            'applies_after': 'S at cap 10000',
            'probe_cap': 20,
            'boundary_threshold_witnessed_exactly': peak_boundary['required_exact_threshold_name'],
            'if_symbol_is_M': DOUBLE_REVERSAL_CLASS,
            'if_symbol_is_S': STABILITY_CLASS,
        },
    ]

    branch_rows = [
        {
            'first_probe_symbol_at_cap_10000': 'M',
            'strict_rho_region': f"rho < {tail_boundary['required_exact_threshold_value_string']}",
            'remaining_classes': [MATERIAL_CLASS, LOW_STABILITY_CLASS],
            'required_second_probe_cap': 10,
            'why_this_second_probe_is_forced': (
                'within the lower pair, the only remaining shared class boundary is tau(10), and only cap 10 realizes it exactly'
            ),
        },
        {
            'first_probe_symbol_at_cap_10000': 'S',
            'strict_rho_region': f"rho > {tail_boundary['required_exact_threshold_value_string']}",
            'remaining_classes': [DOUBLE_REVERSAL_CLASS, STABILITY_CLASS],
            'required_second_probe_cap': 20,
            'why_this_second_probe_is_forced': (
                'within the upper pair, the only remaining shared class boundary is tau(20), and only cap 20 realizes it exactly'
            ),
        },
    ]

    return {
        'focus': 'Compress the strict cap-sensitive class diagnosis from a non-adaptive three-probe witness set to a worst-case-optimal adaptive decision tree.',
        'method_note': 'Started from the four strict hazard-normalized rho classes, the minimal non-adaptive probe result, and the uniqueness certificate for exact boundary witnesses. Used the fact that a binary adaptive classifier for four open classes needs depth at least 2, then checked whether some first probe cleanly splits the classes into two exact pairs with one unique boundary-witnessing follow-up on each branch. The tail boundary tau(10000) is the only candidate root split, and the lower and upper branches are then uniquely completed by caps 10 and 20 respectively.',
        'headline_findings': {
            'stability_anchor': findings['stability_anchor'],
            'material_anchor': findings['material_anchor'],
            'strict_trajectory_class_count_when_w_hazard_gt_0': findings['strict_trajectory_class_count_when_w_hazard_gt_0'],
            'nonadaptive_minimal_probe_count_for_universal_strict_classification': probe_findings['minimum_probe_count_needed_for_strict_classification'],
            'adaptive_minimal_worst_case_probe_count_for_universal_strict_classification': 2,
            'binary_lower_bound_reason': 'four strict classes cannot be universally classified with fewer than two binary probes',
            'adaptive_probe_savings_vs_nonadaptive_worst_case': 1,
            'unique_worst_case_optimal_first_probe_cap': 10000,
            'why_cap_10000_must_be_first': 'only cap 10000 realizes tau(10000), the shared boundary between the lower two and upper two strict rho classes, so every other first probe leaves a three-class branch',
            'unique_second_probe_after_M_at_cap_10000': 10,
            'unique_second_probe_after_S_at_cap_10000': 20,
            'unique_worst_case_optimal_adaptive_probe_tree_probe_caps': [10000, 10, 20],
            'uniform_strict_class_prior_expected_probe_count': 2.0,
            'why_this_is_stronger_than_the_three_probe_result': 'the archive no longer needs a fixed three-symbol signature to classify the strict class; one tail probe plus one branch-specific boundary probe always suffices',
        },
        'adaptive_decision_tree': decision_tree,
        'first_probe_branch_rows': branch_rows,
        'supporting_boundaries': {
            'low_pair_boundary': f"tau(10) = {low_boundary['required_exact_threshold_value_string']}",
            'middle_pair_boundary': f"tau(10000) = {tail_boundary['required_exact_threshold_value_string']}",
            'upper_pair_boundary': f"tau(20) = {peak_boundary['required_exact_threshold_value_string']}",
            'exact_boundary_witness_caps': unique_findings['unique_minimal_sufficient_probe_caps_when_using_strict_winner_symbols'],
        },
        'source_reports': [
            str(NORMALIZED_PATH.relative_to(ROOT)),
            str(MINIMAL_PATH.relative_to(ROOT)),
            str(UNIQUE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }



def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    tree = summary['adaptive_decision_tree']
    branches = summary['first_probe_branch_rows']
    support = summary['supporting_boundaries']
    lines = [
        '# Rematch-Proxy Delta Adaptive Cap-Probe Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the four strict hazard-normalized `rho` classes, the non-adaptive minimal three-probe result, and the unique exact-boundary witness report',
        '- used the binary lower bound that four strict classes need at least two binary probes in any universal adaptive classifier',
        '- asked whether some first cap probe splits the classes into two exact pairs so that one unique follow-up probe can finish each branch',
        '- then certified whether that optimal adaptive tree is uniquely forced by the class-boundary thresholds',
        '',
        'Headline findings:',
        f"- non-adaptive universal strict classification needs `{findings['nonadaptive_minimal_probe_count_for_universal_strict_classification']}` probes, but adaptive universal strict classification only needs `{findings['adaptive_minimal_worst_case_probe_count_for_universal_strict_classification']}`.",
        f"- the unique worst-case-optimal first probe is cap `{findings['unique_worst_case_optimal_first_probe_cap']}` because `{findings['why_cap_10000_must_be_first']}`.",
        f"- after `M` at cap `10000`, the unique forced follow-up is cap `{findings['unique_second_probe_after_M_at_cap_10000']}`.",
        f"- after `S` at cap `10000`, the unique forced follow-up is cap `{findings['unique_second_probe_after_S_at_cap_10000']}`.",
        f"- this saves `{findings['adaptive_probe_savings_vs_nonadaptive_worst_case']}` probe in the worst case versus the fixed-signature contract.",
        '',
        'Exact boundary witnesses behind the tree:',
        f"- lower pair boundary: `{support['low_pair_boundary']}`",
        f"- lower/upper split boundary: `{support['middle_pair_boundary']}`",
        f"- upper pair boundary: `{support['upper_pair_boundary']}`",
        '',
        'Adaptive decision tree:',
        '| step | when it applies | probe cap | if `M` | if `S` |',
        '| --- | --- | ---: | --- | --- |',
        f"| 1 | always | `{tree[0]['probe_cap']}` | {tree[0]['if_symbol_is_M']['remaining_classes']} -> step 2 | {tree[0]['if_symbol_is_S']['remaining_classes']} -> step 3 |",
        f"| 2 | `{tree[1]['applies_after']}` | `{tree[1]['probe_cap']}` | `{tree[1]['if_symbol_is_M']}` | `{tree[1]['if_symbol_is_S']}` |",
        f"| 3 | `{tree[2]['applies_after']}` | `{tree[2]['probe_cap']}` | `{tree[2]['if_symbol_is_M']}` | `{tree[2]['if_symbol_is_S']}` |",
        '',
        'Why each second probe is forced:',
        '| first probe result at 10000 | surviving classes | forced follow-up | why |',
        '| --- | --- | ---: | --- |',
    ]
    for row in branches:
        lines.append(
            f"| `{row['first_probe_symbol_at_cap_10000']}` | `{row['remaining_classes']}` | `{row['required_second_probe_cap']}` | {row['why_this_second_probe_is_forced']} |"
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The inheritor no longer has to collect a full three-symbol signature just to classify the strict path class.',
        '- The operational contract is now tighter: probe cap `10000` first, then use cap `10` or `20` only on the branch that remains live.',
        '- This clarifies a subtle distinction that future sessions could otherwise miss: three probes are minimal for a fixed non-adaptive signature, but two probes are already enough once probing is allowed to branch on the first result.',
    ])
    return '\n'.join(lines) + '\n'



def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
