#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.md'
PROBE_CAPS = [10, 20, 10000]
SIGNATURE_CAP_PAIRS = [(10, 20), (10, 10000), (20, 10000)]
CLASS_ORDER = [
    'material_all_checked_caps',
    'low_cap_stability_then_material',
    'stability_then_mid_cap_material_then_tail_stability',
    'stability_all_checked_caps',
]
REPRESENTATIVE_RHO = {
    'material_all_checked_caps': -0.0007,
    'low_cap_stability_then_material': -0.000215348,
    'stability_then_mid_cap_material_then_tail_stability': 0.000173333,
    'stability_all_checked_caps': 0.0005,
}


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


def _winner_symbol(rho: float, tau: float) -> str:
    return 'S' if rho > tau else 'M'


def _class_caption(label: str) -> str:
    captions = {
        'material_all_checked_caps': 'material at every checked cap',
        'low_cap_stability_then_material': 'stability on low caps, then material',
        'stability_then_mid_cap_material_then_tail_stability': 'stability, then mid-cap material, then tail stability',
        'stability_all_checked_caps': 'stability at every checked cap',
    }
    return captions[label]


def _build_summary() -> dict[str, object]:
    normalized = _load_json(NORMALIZED_PATH)
    findings = normalized['headline_findings']
    threshold_lookup = {
        int(row['additional_budget_cap']): float(row['normalized_threshold_for_stability'])
        for row in normalized['representative_threshold_rows']
    }
    taus = {cap: threshold_lookup[cap] for cap in PROBE_CAPS}

    if not (taus[10] < taus[10000] < taus[20]):
        raise SystemExit('probe thresholds no longer satisfy tau(10) < tau(10000) < tau(20)')

    class_rows: list[dict[str, object]] = []
    signature_lookup: dict[str, str] = {}
    for label in CLASS_ORDER:
        rho = REPRESENTATIVE_RHO[label]
        signature = ''.join(_winner_symbol(rho, taus[cap]) for cap in PROBE_CAPS)
        signature_lookup[label] = signature
        class_rows.append(
            {
                'class_label': label,
                'class_caption': _class_caption(label),
                'representative_rho': rho,
                'signature_on_probe_caps_10_20_10000': signature,
            }
        )

    if len(set(signature_lookup.values())) != len(CLASS_ORDER):
        raise SystemExit('three-cap probe signatures are not unique across strict classes')

    pair_rows: list[dict[str, object]] = []
    for left_cap, right_cap in SIGNATURE_CAP_PAIRS:
        pair_signatures = {
            label: ''.join(_winner_symbol(REPRESENTATIVE_RHO[label], taus[cap]) for cap in (left_cap, right_cap))
            for label in CLASS_ORDER
        }
        unique_count = len(set(pair_signatures.values()))
        if unique_count >= len(CLASS_ORDER):
            raise SystemExit(f'two-cap probe pair unexpectedly distinguishes all classes: {(left_cap, right_cap)}')
        pair_rows.append(
            {
                'probe_caps': [left_cap, right_cap],
                'realized_strict_signatures': sorted(set(pair_signatures.values())),
                'strict_signature_count': unique_count,
                'class_to_signature': pair_signatures,
            }
        )

    decision_tree = [
        {
            'step': 1,
            'probe_cap': 20,
            'if_symbol_is_S': 'stability_all_checked_caps',
            'if_symbol_is_M': 'go_to_step_2',
        },
        {
            'step': 2,
            'probe_cap': 10,
            'if_symbol_is_M': 'material_all_checked_caps',
            'if_symbol_is_S': 'go_to_step_3',
        },
        {
            'step': 3,
            'probe_cap': 10000,
            'if_symbol_is_S': 'stability_then_mid_cap_material_then_tail_stability',
            'if_symbol_is_M': 'low_cap_stability_then_material',
        },
    ]

    return {
        'focus': 'Reduce the hazard-normalized cap-trajectory contract to a minimal finite probe set that classifies every strict winner path without scanning the full cap range.',
        'method_note': 'Started from the normalized cap-trajectory snapshot. Used the strict class decomposition induced by the exact threshold curve `tau(c)` and asked for the smallest set of additional-budget caps whose material/stability winner symbols can distinguish all four strict classes. Because ordered thresholds from any two caps realize at most three strict signatures, two probes can never separate four strict classes. The caps `{10, 20, 10000}` do separate all four, so they form a minimal sufficient probe set.',
        'headline_findings': {
            'stability_anchor': findings['stability_anchor'],
            'material_anchor': findings['material_anchor'],
            'strict_trajectory_class_count_when_w_hazard_gt_0': findings['strict_trajectory_class_count_when_w_hazard_gt_0'],
            'minimum_probe_count_needed_for_strict_classification': 3,
            'why_two_probes_are_globally_insufficient': 'for any ordered threshold pair tau(a) and tau(b), only three strict winner signatures are realizable because one mixed pattern is impossible',
            'minimal_sufficient_probe_caps': PROBE_CAPS,
            'ordered_probe_thresholds': {
                'tau_at_cap_10': taus[10],
                'tau_at_cap_20': taus[20],
                'tau_at_cap_10000': taus[10000],
                'strict_order': 'tau(10) < tau(10000) < tau(20)',
            },
            'probe_signature_legend': {'S': findings['stability_anchor'], 'M': findings['material_anchor']},
            'recommended_three_probe_decision_order': [20, 10, 10000],
        },
        'strict_class_probe_signatures': class_rows,
        'two_probe_insufficiency_rows': pair_rows,
        'three_probe_decision_tree': decision_tree,
        'source_reports': [str(NORMALIZED_PATH.relative_to(ROOT))],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    class_rows = summary['strict_class_probe_signatures']
    pair_rows = summary['two_probe_insufficiency_rows']
    decision_tree = summary['three_probe_decision_tree']
    lines = [
        '# Rematch-Proxy Delta Minimal Cap-Probe Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the hazard-normalized cap-trajectory report for the certified family `10/20/50/100` policy box',
        '- asked for the smallest finite set of caps whose material/stability winner symbols can distinguish all `4` strict trajectory classes',
        '- used the exact threshold order `tau(10) < tau(10000) < tau(20)` to prove any two cap probes are insufficient',
        '- then certified that the three caps `{10, 20, 10000}` uniquely identify every strict class',
        '',
        'Headline findings:',
        '- the minimal sufficient strict-class probe count is `3`.',
        f"- a working minimal probe set is `{findings['minimal_sufficient_probe_caps']}`.",
        f"- probe thresholds satisfy `{findings['ordered_probe_thresholds']['strict_order']}`.",
        '- any two cap probes can realize at most `3` strict signatures, so they cannot distinguish all `4` strict classes.',
        '- the recommended decision order is: check cap `20`, then cap `10`, then cap `10000` only if needed.',
        '',
        'Three-probe signature table on caps `(10, 20, 10000)`:',
        '| class | caption | representative rho | signature |',
        '| --- | --- | ---: | --- |',
    ]
    for row in class_rows:
        lines.append(
            f"| `{row['class_label']}` | {row['class_caption']} | `{row['representative_rho']:.9f}` | `{row['signature_on_probe_caps_10_20_10000']}` |"
        )
    lines.extend([
        '',
        'Why each two-probe subset fails:',
        '| probe caps | realized signatures | collision that remains |',
        '| --- | --- | --- |',
    ])
    collision_text = {
        (10, 20): '`SM` is shared by the one-reversal and two-reversal classes',
        (10, 10000): '`SS` is shared by the two-reversal and all-stability classes',
        (20, 10000): '`MM` is shared by the all-material and one-reversal classes',
    }
    for row in pair_rows:
        caps = tuple(row['probe_caps'])
        realized = ', '.join(f'`{sig}`' for sig in row['realized_strict_signatures'])
        lines.append(f"| `{caps[0]}, {caps[1]}` | {realized} | {collision_text[caps]} |")
    lines.extend([
        '',
        'Minimal decision tree:',
    ])
    for row in decision_tree:
        lines.append(
            f"- step `{row['step']}`: probe cap `{row['probe_cap']}` -> `S` means `{row['if_symbol_is_S']}`, `M` means `{row['if_symbol_is_M']}`"
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The inheritor no longer needs to scan or plot the entire cap range just to classify the remaining cap-sensitive choice.',
        '- Endpoint-only checking is now formally insufficient, not merely heuristicly risky.',
        '- A three-cap witness set is enough to classify the whole strict trajectory shape, and two caps can never do so.',
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
