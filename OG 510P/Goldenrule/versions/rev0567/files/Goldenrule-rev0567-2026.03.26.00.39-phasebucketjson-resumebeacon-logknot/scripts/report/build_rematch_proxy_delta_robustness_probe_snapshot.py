#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
UNIQUE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_robustness_probe_snapshot_20260306.md'

MATERIAL_CLASS = 'material_robust_all_checked_caps'
SENSITIVE_CLASS = 'cap_sensitive_across_checked_caps'
STABILITY_CLASS = 'stability_robust_all_checked_caps'

LOW_STRICT_CLASS = 'low_cap_stability_then_material'
DOUBLE_STRICT_CLASS = 'stability_then_mid_cap_material_then_tail_stability'


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
    unique = _load_json(UNIQUE_PATH)

    findings = normalized['headline_findings']
    strict_classes = normalized['trajectory_classes']
    strict_labels = [row['class_label'] for row in strict_classes]
    expected_strict_labels = [
        'material_all_checked_caps',
        LOW_STRICT_CLASS,
        DOUBLE_STRICT_CLASS,
        'stability_all_checked_caps',
    ]
    if strict_labels != expected_strict_labels:
        raise SystemExit(f'unexpected strict class order: {strict_labels}')

    boundary_rows = unique['boundary_necessity_rows']
    low_boundary = boundary_rows[0]
    tail_boundary = boundary_rows[1]
    peak_boundary = boundary_rows[2]
    if low_boundary['caps_realizing_required_threshold_exactly'] != [10]:
        raise SystemExit('expected cap 10 to be the unique lower robustness-boundary witness')
    if peak_boundary['caps_realizing_required_threshold_exactly'] != [20]:
        raise SystemExit('expected cap 20 to be the unique upper robustness-boundary witness')
    if tail_boundary['caps_realizing_required_threshold_exactly'] != [10000]:
        raise SystemExit('expected cap 10000 to witness only the strict middle boundary')

    robustness_signature_rows = [
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'MM',
            'diagnosed_robustness_class': MATERIAL_CLASS,
            'strict_rho_region_when_w_hazard_gt_0': f"rho < {low_boundary['required_exact_threshold_value_string']}",
        },
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'SM',
            'diagnosed_robustness_class': SENSITIVE_CLASS,
            'strict_rho_region_when_w_hazard_gt_0': (
                f"{low_boundary['required_exact_threshold_value_string']} < rho < {peak_boundary['required_exact_threshold_value_string']}"
            ),
        },
        {
            'probe_caps': [10, 20],
            'observed_symbols': 'SS',
            'diagnosed_robustness_class': STABILITY_CLASS,
            'strict_rho_region_when_w_hazard_gt_0': f"rho > {peak_boundary['required_exact_threshold_value_string']}",
        },
    ]

    adaptive_trees = [
        {
            'tree_name': 'material-first early-stop tree',
            'first_probe_cap': 10,
            'if_symbol_is_M': MATERIAL_CLASS,
            'if_symbol_is_S': {
                'second_probe_cap': 20,
                'if_symbol_is_M': SENSITIVE_CLASS,
                'if_symbol_is_S': STABILITY_CLASS,
            },
            'worst_case_probe_count': 2,
            'best_case_probe_count': 1,
        },
        {
            'tree_name': 'stability-first early-stop tree',
            'first_probe_cap': 20,
            'if_symbol_is_S': STABILITY_CLASS,
            'if_symbol_is_M': {
                'second_probe_cap': 10,
                'if_symbol_is_M': MATERIAL_CLASS,
                'if_symbol_is_S': SENSITIVE_CLASS,
            },
            'worst_case_probe_count': 2,
            'best_case_probe_count': 1,
        },
    ]

    boundary_witness_rows = [
        {
            'robustness_boundary': [MATERIAL_CLASS, SENSITIVE_CLASS],
            'required_exact_threshold_name': low_boundary['required_exact_threshold_name'],
            'required_exact_threshold_value_string': low_boundary['required_exact_threshold_value_string'],
            'unique_required_probe_cap': 10,
            'why_this_probe_cap_is_necessary': (
                'cap 20 returns material on both sides of the lower robustness boundary, so only cap 10 can distinguish robust material from cap-sensitive preferences by strict winner symbols'
            ),
        },
        {
            'robustness_boundary': [SENSITIVE_CLASS, STABILITY_CLASS],
            'required_exact_threshold_name': peak_boundary['required_exact_threshold_name'],
            'required_exact_threshold_value_string': peak_boundary['required_exact_threshold_value_string'],
            'unique_required_probe_cap': 20,
            'why_this_probe_cap_is_necessary': (
                'cap 10 returns stability on both sides of the upper robustness boundary, so only cap 20 can distinguish cap-sensitive preferences from robust stability by strict winner symbols'
            ),
        },
    ]

    return {
        'focus': 'Collapse the four strict hazard-normalized cap-path classes to a smaller robustness triage contract that only asks whether added budget can ever overturn the final two-anchor choice.',
        'method_note': 'Started from the exact strict rho-class boundaries tau(10), tau(10000), and tau(20). Merged the two middle strict classes because both are cap-sensitive rather than cap-robust. Then asked which cap probes are still needed to distinguish robust material, cap-sensitive, and robust stability. Because the middle strict boundary tau(10000) only separates the two cap-sensitive subclasses, it drops out entirely. The remaining adjacent robustness boundaries are tau(10) and tau(20), forcing caps 10 and 20 as the unique minimal non-adaptive probe pair.',
        'headline_findings': {
            'stability_anchor': findings['stability_anchor'],
            'material_anchor': findings['material_anchor'],
            'strict_trajectory_class_count_when_w_hazard_gt_0': findings['strict_trajectory_class_count_when_w_hazard_gt_0'],
            'robustness_triage_class_count_when_w_hazard_gt_0': 3,
            'cap_sensitive_strict_classes_collapsed_into_one_middle_class': [LOW_STRICT_CLASS, DOUBLE_STRICT_CLASS],
            'material_robust_region_when_w_hazard_gt_0': f"rho < {low_boundary['required_exact_threshold_value_string']}",
            'cap_sensitive_region_when_w_hazard_gt_0': (
                f"{low_boundary['required_exact_threshold_value_string']} < rho < {peak_boundary['required_exact_threshold_value_string']}"
            ),
            'stability_robust_region_when_w_hazard_gt_0': f"rho > {peak_boundary['required_exact_threshold_value_string']}",
            'minimum_nonadaptive_probe_count_for_universal_robustness_triage': 2,
            'unique_minimal_nonadaptive_probe_caps': [10, 20],
            'why_cap_10000_is_not_needed_for_robustness_triage': (
                'cap 10000 only separates the two cap-sensitive strict subclasses, and robustness triage merges them into one middle class'
            ),
            'minimum_adaptive_worst_case_probe_count_for_universal_robustness_triage': 2,
            'adaptive_best_case_probe_count_for_universal_robustness_triage': 1,
            'one_probe_universal_robustness_triage_is_impossible_reason': (
                'a single strict winner probe has only two symbols, but robustness triage has three classes'
            ),
            'number_of_symmetric_worst_case_optimal_adaptive_trees': 2,
            'uniform_robustness_class_prior_expected_probe_count_for_optimal_adaptive_tree': 5 / 3,
            'early_stop_certificate_after_M_at_cap_10': 'material is cap-robust across all checked caps',
            'early_stop_certificate_after_S_at_cap_20': 'stability is cap-robust across all checked caps',
            'most_practical_probe_contract': 'use caps 10 and 20 when the question is only whether additional budget can ever overturn the final choice',
        },
        'nonadaptive_signature_rows': robustness_signature_rows,
        'boundary_witness_rows': boundary_witness_rows,
        'symmetric_optimal_adaptive_trees': adaptive_trees,
        'strict_boundary_that_drops_out': {
            'required_exact_threshold_name': tail_boundary['required_exact_threshold_name'],
            'required_exact_threshold_value_string': tail_boundary['required_exact_threshold_value_string'],
            'unique_probe_cap_that_witnesses_it': 10000,
            'why_it_drops_out_of_robustness_triage': (
                'this boundary only splits low-cap one-reversal from double-reversal behavior inside the already cap-sensitive middle region'
            ),
        },
        'source_reports': [
            str(NORMALIZED_PATH.relative_to(ROOT)),
            str(UNIQUE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    signatures = summary['nonadaptive_signature_rows']
    boundaries = summary['boundary_witness_rows']
    trees = summary['symmetric_optimal_adaptive_trees']
    dropped = summary['strict_boundary_that_drops_out']
    lines = [
        '# Rematch-Proxy Delta Robustness-Probe Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the exact strict `rho` boundaries `tau(10)`, `tau(10000)`, and `tau(20)` from the hazard-normalized cap-path report',
        '- merged the two middle strict classes because both are cap-sensitive rather than cap-robust',
        '- asked which cap probes still matter when the only question is whether added budget can ever overturn the final two-anchor choice',
        '- then certified minimality and adaptive early-stop behavior for that smaller robustness triage problem',
        '',
        'Headline findings:',
        f"- the four strict classes collapse to `{findings['robustness_triage_class_count_when_w_hazard_gt_0']}` robustness classes once the two cap-sensitive middle classes are merged.",
        f"- the cap-sensitive middle region is `{findings['cap_sensitive_region_when_w_hazard_gt_0']}`.",
        f"- the unique minimal non-adaptive robustness probe pair is `{findings['unique_minimal_nonadaptive_probe_caps']}`.",
        f"- `{findings['why_cap_10000_is_not_needed_for_robustness_triage']}`.",
        f"- one-probe universal robustness triage is impossible because `{findings['one_probe_universal_robustness_triage_is_impossible_reason']}`.",
        f"- two symmetric worst-case-optimal adaptive trees remain, each with best-case `{findings['adaptive_best_case_probe_count_for_universal_robustness_triage']}` probe and worst-case `{findings['minimum_adaptive_worst_case_probe_count_for_universal_robustness_triage']}` probes.",
        '',
        'Non-adaptive signature contract on caps `[10, 20]`:',
    ]
    for row in signatures:
        lines.append(
            f"- `{row['observed_symbols']}` -> `{row['diagnosed_robustness_class']}` on `{row['strict_rho_region_when_w_hazard_gt_0']}`"
        )
    lines.extend([
        '',
        'Why caps 10 and 20 are forced:',
    ])
    for row in boundaries:
        left, right = row['robustness_boundary']
        lines.append(
            f"- boundary `{left}` vs `{right}` requires `{row['required_exact_threshold_name']} = {row['required_exact_threshold_value_string']}`, so cap `{row['unique_required_probe_cap']}` is forced because {row['why_this_probe_cap_is_necessary']}."
        )
    lines.extend([
        '',
        'Strict boundary that becomes unnecessary once we only triage robustness:',
        f"- `{dropped['required_exact_threshold_name']} = {dropped['required_exact_threshold_value_string']}` at cap `{dropped['unique_probe_cap_that_witnesses_it']}` drops out because {dropped['why_it_drops_out_of_robustness_triage']}",
        '',
        'Symmetric worst-case-optimal adaptive trees:',
    ])
    for tree in trees:
        if tree['first_probe_cap'] == 10:
            lines.append(
                f"- `{tree['tree_name']}`: probe `10`; `M` certifies `{tree['if_symbol_is_M']}` immediately; `S` then probes `20` to distinguish `{tree['if_symbol_is_S']['if_symbol_is_M']}` from `{tree['if_symbol_is_S']['if_symbol_is_S']}`."
            )
        else:
            lines.append(
                f"- `{tree['tree_name']}`: probe `20`; `S` certifies `{tree['if_symbol_is_S']}` immediately; `M` then probes `10` to distinguish `{tree['if_symbol_is_M']['if_symbol_is_M']}` from `{tree['if_symbol_is_M']['if_symbol_is_S']}`."
            )
    lines.extend([
        '',
        'Planning consequence:',
        '- keep the earlier three-cap or adaptive strict-class contracts when the exact cap path matters,',
        '- but when the real handoff question is only whether added budget can ever overturn the final choice, switch to the smaller `[10, 20]` robustness contract and stop early whenever cap `10` already returns `M` or cap `20` already returns `S`.',
        '',
        'Pointers:',
        f"- JSON: `{OUT_JSON.relative_to(ROOT)}`",
        f"- builder: `{Path(__file__).relative_to(ROOT)}`",
        '- validator: `scripts/test/check_rematch_delta_robustness_probes.py`',
    ])
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(OUT_JSON.relative_to(ROOT))
    print(OUT_MD.relative_to(ROOT))


if __name__ == '__main__':
    main()
