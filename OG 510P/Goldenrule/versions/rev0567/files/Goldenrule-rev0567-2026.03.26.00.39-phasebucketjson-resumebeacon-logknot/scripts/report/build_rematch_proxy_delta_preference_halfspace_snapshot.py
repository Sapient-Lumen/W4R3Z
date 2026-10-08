#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_BOX_CORNER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_policy_box_corner_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_halfspace_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_halfspace_snapshot_20260306.md'
MATERIAL_ANCHOR = 'TTTMMMMMU'
STABILITY_ANCHOR = 'TTTMMMMUU'


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


def _coefficients(corner: dict[str, object]) -> dict[str, object]:
    rows = {row['topology_code']: row for row in corner['candidate_rows']}
    material = rows[MATERIAL_ANCHOR]
    stability = rows[STABILITY_ANCHOR]
    return {
        'width_floor': corner['width_floor'],
        'additional_budget_cap': corner['additional_budget_cap'],
        'delta_ceiling': corner['delta_ceiling'],
        'stability_anchor': STABILITY_ANCHOR,
        'material_anchor': MATERIAL_ANCHOR,
        'stability_wins_iff': {
            'left_side_gains': {
                'width_gain_coefficient': round(float(stability['shared_core_width']) - float(material['shared_core_width']), 6),
                'anchor_buffer_gain_coefficient': round(float(stability['shared_core_anchor_buffer_to_boundary']) - float(material['shared_core_anchor_buffer_to_boundary']), 6),
                'knife_edge_separation_gain_coefficient': round(float(stability['min_separation_to_knife_edge_delta']) - float(material['min_separation_to_knife_edge_delta']), 6),
                'hazard_clearance_gain_coefficient': round(
                    float(stability['min_separation_to_hazard_band_for_additional_budget_cap'])
                    - float(material['min_separation_to_hazard_band_for_additional_budget_cap']),
                    6,
                ),
            },
            'right_side_costs': {
                'anchor_delta_cost_coefficient': round(float(stability['shared_core_anchor_delta']) - float(material['shared_core_anchor_delta']), 6),
                'material_leader_loss_coefficient': int(material['counts']['material_leader']) - int(stability['counts']['material_leader']),
                'additional_undecided_coefficient': int(stability['counts']['undecided']) - int(material['counts']['undecided']),
                'additional_anchor_tie_coefficient': int(stability['shared_core_anchor_tie_count']) - int(material['shared_core_anchor_tie_count']),
            },
        },
    }


def _expr_text(left: dict[str, object], right: dict[str, object]) -> str:
    hazard = float(left['hazard_clearance_gain_coefficient'])
    hazard_term = f"+ {hazard:.6f}*w_hazard" if hazard >= 0 else f"- {abs(hazard):.6f}*w_hazard"
    return (
        f"{float(left['width_gain_coefficient']):.5f}*w_width + "
        f"{float(left['anchor_buffer_gain_coefficient']):.5f}*w_buffer + "
        f"{float(left['knife_edge_separation_gain_coefficient']):.6f}*w_knife {hazard_term} > "
        f"{float(right['anchor_delta_cost_coefficient']):.5f}*w_delta + "
        f"{int(right['material_leader_loss_coefficient'])}*w_material + "
        f"{int(right['additional_undecided_coefficient'])}*w_undecided + "
        f"{int(right['additional_anchor_tie_coefficient'])}*w_ties"
    )


def _build_summary() -> dict[str, object]:
    policy_box = _load_json(POLICY_BOX_CORNER_PATH)
    corner_rows = policy_box['corner_rows']
    if len(corner_rows) != 8:
        raise SystemExit(f'expected 8 representative corners, found {len(corner_rows)}')

    coefficient_rows = [_coefficients(corner) for corner in corner_rows]
    unique_patterns: dict[tuple[float, float, float, float, int, int, int, int], dict[str, object]] = {}
    for row in coefficient_rows:
        left = row['stability_wins_iff']['left_side_gains']
        right = row['stability_wins_iff']['right_side_costs']
        key = (
            float(left['width_gain_coefficient']),
            float(left['anchor_buffer_gain_coefficient']),
            float(left['knife_edge_separation_gain_coefficient']),
            float(left['hazard_clearance_gain_coefficient']),
            int(right['anchor_delta_cost_coefficient'] * 100000),
            int(right['material_leader_loss_coefficient']),
            int(right['additional_undecided_coefficient']),
            int(right['additional_anchor_tie_coefficient']),
        )
        bucket = unique_patterns.setdefault(
            key,
            {
                'coefficient_row': row,
                'representative_corners': [],
            },
        )
        bucket['representative_corners'].append(
            {
                'width_floor': row['width_floor'],
                'additional_budget_cap': row['additional_budget_cap'],
                'delta_ceiling': row['delta_ceiling'],
            }
        )

    patterns = []
    for bucket in sorted(unique_patterns.values(), key=lambda item: item['coefficient_row']['additional_budget_cap']):
        row = bucket['coefficient_row']
        left = row['stability_wins_iff']['left_side_gains']
        right = row['stability_wins_iff']['right_side_costs']
        patterns.append(
            {
                'additional_budget_cap': row['additional_budget_cap'],
                'representative_corner_count': len(bucket['representative_corners']),
                'representative_corners': bucket['representative_corners'],
                'left_side_gains': left,
                'right_side_costs': right,
                'stability_wins_iff_expression': _expr_text(left, right),
            }
        )

    low_cap_pattern = next(pattern for pattern in patterns if pattern['additional_budget_cap'] == 10)
    high_cap_pattern = next(pattern for pattern in patterns if pattern['additional_budget_cap'] == 10000)
    low_hazard = float(low_cap_pattern['left_side_gains']['hazard_clearance_gain_coefficient'])
    high_hazard = float(high_cap_pattern['left_side_gains']['hazard_clearance_gain_coefficient'])

    nonhazard_left = {
        key: low_cap_pattern['left_side_gains'][key]
        for key in ['width_gain_coefficient', 'anchor_buffer_gain_coefficient', 'knife_edge_separation_gain_coefficient']
    }
    right_costs = low_cap_pattern['right_side_costs']

    return {
        'focus': 'Collapse the remaining two-anchor preference choice inside the certified family10 policy box into explicit additive half-spaces instead of leaving it as a set of named but underspecified profiles.',
        'method_note': 'Started from the eight representative policy-box corners. Because every corner has the same two surviving anchors, treated the remaining decision as a generic monotone additive scalarization over only the metrics that still differ between `TTTMMMMMU` and `TTTMMMMUU`: anchor delta, material-leader count, undecided count, anchor-tie count, shared-core width, anchor buffer, knife-edge separation, and hazard clearance at the declared additional-budget cap. Subtracted the material-anchor score from the stability-anchor score and grouped identical coefficient vectors.',
        'headline_findings': {
            'representative_corner_count': len(corner_rows),
            'unique_preference_halfspace_pattern_count': len(patterns),
            'material_anchor': MATERIAL_ANCHOR,
            'stability_anchor': STABILITY_ANCHOR,
            'invariant_nonhazard_tradeoff_coefficients': {
                **nonhazard_left,
                **right_costs,
            },
            'hazard_clearance_gain_for_stability_at_cap_10': low_hazard,
            'hazard_clearance_gain_for_stability_at_cap_10000': high_hazard,
            'hazard_sensitivity_strip_width_per_unit_w_hazard': round(low_hazard - high_hazard, 6),
            'stability_anchor_wins_every_representative_corner_if': (
                f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.000033*w_hazard > "
                f"0.00142*w_delta + 1*w_material + 1*w_undecided + 1*w_ties"
            ),
            'material_anchor_wins_every_representative_corner_if': (
                f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife + 0.000464*w_hazard < "
                f"0.00142*w_delta + 1*w_material + 1*w_undecided + 1*w_ties"
            ),
            'interpretation': 'Inside the certified family10 policy box, width floor and delta ceiling no longer affect the remaining preference boundary at all. The whole residual judgment collapses to one almost-invariant additive half-space between `TTTMMMMMU` and `TTTMMMMUU`; only the hazard-clearance coefficient moves, and it does so over a narrow strip tied to the declared additional-budget cap. That means the archive can replace vague profile names with an explicit statement of which metric premiums are being allowed to outweigh one extra material-leader panel, one extra unresolved panel, one extra anchor tie, and 0.00142 more anchor delta.',
        },
        'halfspace_patterns': patterns,
        'coefficient_rows': coefficient_rows,
        'source_report': str(POLICY_BOX_CORNER_PATH.relative_to(ROOT)),
        'source_script': 'scripts/report/build_rematch_proxy_delta_preference_halfspace_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    patterns = summary['halfspace_patterns']
    lines = [
        '# Rematch-Proxy Delta Preference Half-Space Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the certified family `10/20/50/100` policy-box corners',
        '- used the fact that every representative corner leaves exactly the same two anchors alive: `TTTMMMMMU` and `TTTMMMMUU`',
        '- wrote the remaining choice as a generic monotone additive score difference using only metrics that still differ between those anchors',
        '- then grouped identical coefficient vectors to see whether width / ceiling / cap actually move the boundary',
        '',
        'Headline findings:',
        f"- checked `{int(findings['representative_corner_count'])}` representative corners and found `{int(findings['unique_preference_halfspace_pattern_count'])}` unique additive half-space patterns.",
        '- width floor and delta ceiling drop out entirely from the remaining preference boundary; only the hazard-clearance coefficient changes with the declared additional-budget cap.',
        f"- invariant non-hazard coefficients are: width `+{float(findings['invariant_nonhazard_tradeoff_coefficients']['width_gain_coefficient']):.5f}`, buffer `+{float(findings['invariant_nonhazard_tradeoff_coefficients']['anchor_buffer_gain_coefficient']):.5f}`, knife-edge separation `+{float(findings['invariant_nonhazard_tradeoff_coefficients']['knife_edge_separation_gain_coefficient']):.6f}`, anchor-delta cost `+{float(findings['invariant_nonhazard_tradeoff_coefficients']['anchor_delta_cost_coefficient']):.5f}`, material-leader loss `+{int(findings['invariant_nonhazard_tradeoff_coefficients']['material_leader_loss_coefficient'])}`, undecided cost `+{int(findings['invariant_nonhazard_tradeoff_coefficients']['additional_undecided_coefficient'])}`, anchor-tie cost `+{int(findings['invariant_nonhazard_tradeoff_coefficients']['additional_anchor_tie_coefficient'])}`.",
        f"- hazard-clearance gain for the stability anchor is `+{float(findings['hazard_clearance_gain_for_stability_at_cap_10']):.6f}` at cap `10` but `{float(findings['hazard_clearance_gain_for_stability_at_cap_10000']):.6f}` at cap `10000`, so the whole cap-sensitive ambiguity strip has width `{float(findings['hazard_sensitivity_strip_width_per_unit_w_hazard']):.6f} * w_hazard`.",
        f"- sufficient for `{findings['stability_anchor']}` at every representative corner: `{findings['stability_anchor_wins_every_representative_corner_if']}`.",
        f"- sufficient for `{findings['material_anchor']}` at every representative corner: `{findings['material_anchor_wins_every_representative_corner_if']}`.",
        '',
        'Unique half-space patterns:',
    ]
    for pattern in patterns:
        lines.append(
            f"- cap `{int(pattern['additional_budget_cap'])}` across `{int(pattern['representative_corner_count'])}` corners: `{pattern['stability_wins_iff_expression']}`."
        )
    lines.extend(
        [
            '',
            'Why this matters for the archive:',
            '- The remaining hidden judgment is no longer a mystery preference profile. It is an explicit inequality over declared metric premiums.',
            '- Future inheritors can now say exactly what must be valued enough to justify moving from `TTTMMMMMU` to `TTTMMMMUU`: more width, more buffer, more knife-edge clearance, and possibly more hazard clearance must jointly outweigh one lost material-leader panel, one extra unresolved panel, one extra anchor tie, and `0.00142` extra anchor delta.',
            '- Because width and ceiling do not change the boundary inside the certified box, later recomputation only needs to revisit this half-space if the live candidate pair changes or the hazard guardrail itself is redefined.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
