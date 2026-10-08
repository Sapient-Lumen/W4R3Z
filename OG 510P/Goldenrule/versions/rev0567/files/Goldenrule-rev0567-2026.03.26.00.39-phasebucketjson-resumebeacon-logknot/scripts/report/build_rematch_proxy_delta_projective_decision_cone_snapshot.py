#!/usr/bin/env python3
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_normal_form_snapshot_20260306.json'
TRAJECTORY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_projective_decision_cone_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_projective_decision_cone_snapshot_20260306.md'

TAU10 = Decimal('-0.000463764')
TAU10000 = Decimal('0.000033068')
TAU20 = Decimal('0.000313597')


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


def _classify(B: Decimal, H: Decimal) -> str:
    if H < 0:
        raise ValueError('classifier only defined here for nonnegative hazard weight')
    if H == 0:
        if B < 0:
            return 'MMM'
        if B > 0:
            return 'SSS'
        return 'TIE'
    if B < TAU10 * H:
        return 'MMM'
    if B == TAU10 * H:
        return 'TIE_tau10'
    if B < TAU10000 * H:
        return 'SMM'
    if B == TAU10000 * H:
        return 'TIE_tau10000'
    if B < TAU20 * H:
        return 'SMS'
    if B == TAU20 * H:
        return 'TIE_tau20'
    return 'SSS'


def _scale_invariance_examples() -> list[dict[str, object]]:
    rows = [
        ('axis_material', Decimal('-1'), Decimal('0')),
        ('positive_hazard_material', Decimal('-0.001'), Decimal('1')),
        ('positive_hazard_lowcap_stability_then_material', Decimal('-0.0002'), Decimal('1')),
        ('positive_hazard_double_reversal', Decimal('0.0001'), Decimal('1')),
        ('positive_hazard_stability', Decimal('0.001'), Decimal('1')),
        ('axis_stability', Decimal('1'), Decimal('0')),
    ]
    lam = Decimal('7')
    out = []
    for label, B, H in rows:
        base = _classify(B, H)
        scaled = _classify(B * lam, H * lam)
        if base != scaled:
            raise SystemExit(f'positive scale invariance failed for {label}: {base} vs {scaled}')
        out.append(
            {
                'example_label': label,
                'unscaled_point': {'baseline_nonhazard_surplus': str(B), 'w_hazard': str(H)},
                'scaled_by_lambda': str(lam),
                'scaled_point': {'baseline_nonhazard_surplus': str(B * lam), 'w_hazard': str(H * lam)},
                'strict_class_preserved': base,
            }
        )
    return out


def _build_summary() -> dict[str, object]:
    decision = _load_json(DECISION_PATH)
    trajectory = _load_json(TRAJECTORY_PATH)
    findings = decision['headline_findings']
    policy_box = findings['canonical_policy_box']
    thresholds = findings['exact_strict_thresholds_in_increasing_order']
    expected = [
        {'boundary_name': 'tau(10)', 'cap': 10, 'value': '-0.000463764'},
        {'boundary_name': 'tau(10000)', 'cap': 10000, 'value': '0.000033068'},
        {'boundary_name': 'tau(20)', 'cap': 20, 'value': '0.000313597'},
    ]
    if thresholds != expected:
        raise SystemExit(f'unexpected thresholds: {thresholds}')
    if trajectory['headline_findings']['zero_hazard_weight_degenerate_rule'] != findings['zero_hazard_weight_degenerate_rule']:
        raise SystemExit('zero-hazard rules disagree across source reports')

    sector_rows = [
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

    boundary_rows = [
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

    return {
        'focus': 'Remove the remaining divide-by-zero branch from the family10 direct classifier by rewriting the final handoff as a projective cone partition in the nonnegative (baseline_nonhazard_surplus, w_hazard) half-plane.',
        'method_note': 'Started from the decision normal form and the exact normalized threshold curve. Re-expressed the rho comparisons as homogeneous linear inequalities in B = baseline_nonhazard_surplus and H = w_hazard, made the zero-hazard axis explicit, and checked on representative points that positive global rescaling preserves the strict class exactly.',
        'headline_findings': {
            'material_anchor': findings['material_anchor'],
            'stability_anchor': findings['stability_anchor'],
            'canonical_policy_box': policy_box,
            'baseline_nonhazard_surplus_symbol': 'B',
            'hazard_weight_symbol': 'H',
            'baseline_nonhazard_surplus_expression': findings['baseline_nonhazard_surplus_expression'],
            'nonnegative_hazard_halfplane_under_test': 'H = w_hazard >= 0',
            'division_free_classifier_rule': 'classify directly in (B,H) by comparing B against tau(10)*H, tau(10000)*H, and tau(20)*H; division by H is optional rather than fundamental',
            'positive_global_rescaling_preserves_classification': True,
            'cap_sensitive_behavior_requires_positive_hazard_weight': True,
            'zero_hazard_axis_carries_only_robust_material_robust_stability_or_total_tie': True,
            'strict_threshold_rays_in_increasing_slope_order': thresholds,
            'projective_coordinate_when_H_gt_0': findings['hazard_normalized_margin_definition_when_w_hazard_gt_0'],
            'origin_rule': 'H = 0 and B = 0 gives an exact tie on every checked cap',
            'most_compact_handoff_rule': 'if declared weights are available, treat the final family10 choice as a cone problem in (B,H): classify by the sign of B and by whether B lies below tau(10)*H, between tau(10)*H and tau(10000)*H, between tau(10000)*H and tau(20)*H, or above tau(20)*H',
        },
        'strict_sector_rows': sector_rows,
        'boundary_rows': boundary_rows,
        'positive_scale_invariance_examples': _scale_invariance_examples(),
        'sources': [
            str(DECISION_PATH.relative_to(ROOT)),
            str(TRAJECTORY_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Delta Projective Decision Cone Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the decision normal form and the exact normalized threshold curve',
        '- rewrote the direct classifier in homogeneous coordinates `B = baseline_nonhazard_surplus`, `H = w_hazard` on the nonnegative half-plane `H >= 0`',
        '- then made the zero-hazard axis explicit and checked positive-scale invariance on representative points',
        '',
        'Headline findings:',
        f"- direct classification is now singularity-free: {findings['division_free_classifier_rule']}.",
        f"- positive global rescaling preserves the class: `{findings['positive_global_rescaling_preserves_classification']}`.",
        f"- cap-sensitive behavior requires positive hazard weight: `{findings['cap_sensitive_behavior_requires_positive_hazard_weight']}`.",
        f"- zero-hazard axis carries only robust material, robust stability, or total tie: `{findings['zero_hazard_axis_carries_only_robust_material_robust_stability_or_total_tie']}`.",
        f"- origin rule: `{findings['origin_rule']}`.",
        '',
        'Open sectors in the nonnegative `(B,H)` half-plane:',
    ]
    for row in summary['strict_sector_rows']:
        lines.append(
            f"- `{row['region_condition']}` -> strict class `{row['strict_path_class']}`, winner path `{row['winner_path_by_cap_growth']}`, robustness class `{row['overturn_risk_class']}`."
        )
    lines.extend([
        '',
        'Boundary rays / points:',
    ])
    for row in summary['boundary_rows']:
        lines.append(
            f"- `{row['region_condition']}` -> tie caps `{row['tie_caps']}`; away-from-boundary pattern: {row['winner_path_away_from_boundary']}."
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- the direct family10 handoff no longer needs a special divide-by-zero branch when `w_hazard = 0`.',
        '- only ratios of declared preference weights matter for the strict class, because the full classifier is homogeneous.',
        '- cap-sensitive sectors exist only off the zero-hazard axis, so no amount of cap probing is needed once an inheritor declares `w_hazard = 0`.',
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
