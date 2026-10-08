#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_normalized_cap_trajectory_snapshot.py'
NORMALIZED_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
MINIMAL_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_unique_minimal_cap_probe_snapshot_20260306.md'
EPS = 1e-15


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f'unable to load helper script: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NORM = _load_module(NORMALIZED_SCRIPT, 'normalized_cap_trajectory_snapshot')


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


def _compute_exact_thresholds() -> list[tuple[int, float]]:
    publishability = NORM._load_json(NORM.PUBLISHABILITY_PATH)
    winner_certification = NORM._load_json(NORM.WINNER_CERTIFICATION_PATH)
    hazard_threshold = NORM._load_json(NORM.HAZARD_THRESHOLD_PATH)

    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    policy_box = hazard_threshold['headline_findings']['full_shortlist_policy_box']
    faces = NORM.CAP_MOD._policy_box_faces(policy_box)
    min_cap = int(policy_box['minimum_additional_budget_cap_inclusive'])

    exact_thresholds: list[tuple[int, float]] = []
    for additional_budget_cap in range(min_cap, NORM.MAX_CAP + 1):
        face_thresholds: list[float] = []
        for face in faces:
            material_clearance = NORM._candidate_clearance(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                NORM.MATERIAL_ANCHOR,
            )
            stability_clearance = NORM._candidate_clearance(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                NORM.STABILITY_ANCHOR,
            )
            face_thresholds.append(material_clearance - stability_clearance)
        spread = max(face_thresholds) - min(face_thresholds)
        if spread > 1e-12:
            raise SystemExit(
                f'policy-box faces disagree on normalized threshold at cap {additional_budget_cap}: {spread}'
            )
        exact_thresholds.append((additional_budget_cap, face_thresholds[0]))
    return exact_thresholds


def _caps_with_threshold(exact_thresholds: list[tuple[int, float]], target: float) -> list[int]:
    return [cap for cap, threshold in exact_thresholds if abs(threshold - target) <= EPS]


def _parse_boundary_strings(normalized: dict[str, object]) -> tuple[str, str, str]:
    findings = normalized['headline_findings']
    single = findings['single_reversal_band_when_w_hazard_gt_0']
    double = findings['double_reversal_band_when_w_hazard_gt_0']
    low, tail = [part.strip() for part in single.split('< rho <')]
    double_low, peak = [part.strip() for part in double.split('< rho <')]
    if tail != double_low:
        raise SystemExit('normalized bands disagree on the tail boundary threshold')
    return low, tail, peak


def _build_summary() -> dict[str, object]:
    normalized = _load_json(NORMALIZED_PATH)
    minimal = _load_json(MINIMAL_PATH)
    exact_thresholds = _compute_exact_thresholds()

    low_value = min(exact_thresholds, key=lambda item: item[1])[1]
    peak_value = max(exact_thresholds, key=lambda item: item[1])[1]
    tail_value = next(threshold for cap, threshold in exact_thresholds if cap == 10000)

    cap10_only = _caps_with_threshold(exact_thresholds, low_value)
    cap20_only = _caps_with_threshold(exact_thresholds, peak_value)
    cap10000_only = _caps_with_threshold(exact_thresholds, tail_value)

    if cap10_only != [10]:
        raise SystemExit(f'expected tau(10) to be unique, got {cap10_only}')
    if cap20_only != [20]:
        raise SystemExit(f'expected tau(20) to be unique, got {cap20_only}')
    if cap10000_only != [10000]:
        raise SystemExit(f'expected tau(10000) to be unique, got {cap10000_only}')

    low_str, tail_str, peak_str = _parse_boundary_strings(normalized)
    findings = normalized['headline_findings']
    probe_findings = minimal['headline_findings']

    boundary_rows = [
        {
            'adjacent_class_pair': ['material_all_checked_caps', 'low_cap_stability_then_material'],
            'required_exact_threshold_name': 'tau(10)',
            'required_exact_threshold_value': low_value,
            'required_exact_threshold_value_string': low_str,
            'why_this_boundary_is_necessary': (
                'without a probe exactly at tau(10), the first two open rho intervals approach the same side of every chosen threshold and cannot be separated by strict winner symbols'
            ),
            'caps_realizing_required_threshold_exactly': cap10_only,
        },
        {
            'adjacent_class_pair': ['low_cap_stability_then_material', 'stability_then_mid_cap_material_then_tail_stability'],
            'required_exact_threshold_name': 'tau(10000)',
            'required_exact_threshold_value': tail_value,
            'required_exact_threshold_value_string': tail_str,
            'why_this_boundary_is_necessary': (
                'without a probe exactly at tau(10000), the one-reversal and two-reversal open rho intervals collapse because one probe threshold lies wholly above or wholly below their shared boundary'
            ),
            'caps_realizing_required_threshold_exactly': cap10000_only,
        },
        {
            'adjacent_class_pair': ['stability_then_mid_cap_material_then_tail_stability', 'stability_all_checked_caps'],
            'required_exact_threshold_name': 'tau(20)',
            'required_exact_threshold_value': peak_value,
            'required_exact_threshold_value_string': peak_str,
            'why_this_boundary_is_necessary': (
                'without a probe exactly at tau(20), the last two open rho intervals approach the same side of every chosen threshold and cannot be separated by strict winner symbols'
            ),
            'caps_realizing_required_threshold_exactly': cap20_only,
        },
    ]

    return {
        'focus': 'Strengthen the minimal cap-probe result from mere sufficiency to a uniqueness certificate for universally classifying the strict hazard-normalized winner paths.',
        'method_note': 'Started from the normalized cap-trajectory report and its four strict rho classes. Recomputed exact thresholds tau(c) for every integral additional-budget cap on the certified family10 policy box, then used the open-interval class boundaries to prove a universal-separation rule: to distinguish two adjacent strict classes for all rho in both classes using only strict winner symbols, some chosen probe must realize their shared boundary threshold exactly. Finally checked which caps realize each required threshold exactly.',
        'headline_findings': {
            'stability_anchor': findings['stability_anchor'],
            'material_anchor': findings['material_anchor'],
            'strict_trajectory_class_count_when_w_hazard_gt_0': findings['strict_trajectory_class_count_when_w_hazard_gt_0'],
            'universally_required_boundary_thresholds_in_order': [low_str, tail_str, peak_str],
            'universal_separation_rule_for_adjacent_open_classes': 'to distinguish two adjacent strict rho classes for every rho in both classes using only strict winner symbols, some probe threshold must equal their shared boundary exactly',
            'unique_minimal_sufficient_probe_caps_when_using_strict_winner_symbols': probe_findings['minimal_sufficient_probe_caps'],
            'why_the_probe_set_is_unique': 'each of the three adjacent class boundaries requires an exact threshold witness, and the only caps realizing tau(10), tau(10000), and tau(20) exactly are 10, 10000, and 20 respectively',
            'no_neighboring_cap_can_substitute_for_cap_10': 'every cap above 10 has tau(c) > tau(10), so some rho just above tau(10) would remain material on that probe and collapse the first two classes',
            'no_neighboring_cap_can_substitute_for_cap_10000': 'every cap other than 10000 has tau(c) != tau(10000), so either some one-reversal rho turns stable there or some two-reversal rho turns material there',
            'no_neighboring_cap_can_substitute_for_cap_20': 'every cap below 20 or above 20 has tau(c) < tau(20), so some rho just below tau(20) would remain stable on that probe and collapse the last two classes',
        },
        'boundary_necessity_rows': boundary_rows,
        'supporting_threshold_witnesses': {
            'tau_at_cap_10': low_value,
            'tau_at_cap_20': peak_value,
            'tau_at_cap_10000': tail_value,
            'caps_realizing_tau_at_cap_10_exactly': cap10_only,
            'caps_realizing_tau_at_cap_20_exactly': cap20_only,
            'caps_realizing_tau_at_cap_10000_exactly': cap10000_only,
        },
        'source_reports': [
            str(NORMALIZED_PATH.relative_to(ROOT)),
            str(MINIMAL_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    rows = summary['boundary_necessity_rows']
    lines = [
        '# Rematch-Proxy Delta Unique Minimal Cap-Probe Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the hazard-normalized cap-trajectory report and the minimal three-probe witness result',
        '- used the open-interval class boundaries to prove a universal-separation rule: adjacent strict classes require a probe whose threshold equals their shared boundary exactly',
        '- recomputed exact `tau(c)` for every checked cap and asked which caps realize the three required class-boundary thresholds exactly',
        '- then certified whether any alternate three-cap witness set could replace `[10, 20, 10000]` without losing universal strict-class separation',
        '',
        'Headline findings:',
        '- the earlier three-cap witness set is not just sufficient; it is uniquely forced by the strict class boundaries.',
        f"- the unique minimal sufficient probe caps are `{findings['unique_minimal_sufficient_probe_caps_when_using_strict_winner_symbols']}`.",
        f"- the required adjacent-class boundary thresholds are `{findings['universally_required_boundary_thresholds_in_order']}` in order.",
        '- each boundary must be witnessed exactly by some chosen probe threshold, because the strict rho classes are open and can approach the boundary arbitrarily closely from either side.',
        '- the only caps realizing those three exact thresholds are `10`, `10000`, and `20` respectively, so no neighboring cap can substitute.',
        '',
        'Boundary-by-boundary necessity:',
        '| adjacent classes | required exact threshold | only realizing caps | why omission fails |',
        '| --- | --- | ---: | --- |',
    ]
    for row in rows:
        pair = ' / '.join(f'`{label}`' for label in row['adjacent_class_pair'])
        lines.append(
            f"| {pair} | `{row['required_exact_threshold_name']} = {row['required_exact_threshold_value_string']}` | `{row['caps_realizing_required_threshold_exactly']}` | {row['why_this_boundary_is_necessary']} |"
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The inheritor no longer has to treat `[10, 20, 10000]` as a convenient witness set among many; it is the only universally valid strict-winner probe triple on the checked cap range.',
        '- Replacing cap `10000` with a merely “high” interior cap is unsound: the one-reversal and two-reversal classes can still collide arbitrarily close to `tau(10000)`.',
        '- Replacing cap `10` or `20` with nearby values is equally unsound for the first or last adjacent class pair, so the handoff contract is now exact rather than heuristic.',
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
