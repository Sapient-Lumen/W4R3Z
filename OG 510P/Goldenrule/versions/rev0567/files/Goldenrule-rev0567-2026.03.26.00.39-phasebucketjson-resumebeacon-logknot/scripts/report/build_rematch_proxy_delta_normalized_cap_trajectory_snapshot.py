#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP_ROBUST_SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_delta_cap_robust_preference_snapshot.py'
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
HAZARD_THRESHOLD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
CAP_ROBUST_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_cap_robust_preference_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.md'
TARGET_FAMILY = [10, 20, 50, 100]
MATERIAL_ANCHOR = 'TTTMMMMMU'
STABILITY_ANCHOR = 'TTTMMMMUU'
T_CRIT_90_DF5 = 2.015048
MAX_DELTA = 0.02
MAX_CAP = 10000


def _load_cap_module():
    spec = importlib.util.spec_from_file_location('cap_robust_snapshot', CAP_ROBUST_SCRIPT)
    if spec is None or spec.loader is None:
        raise SystemExit(f'unable to load helper script: {CAP_ROBUST_SCRIPT}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAP_MOD = _load_cap_module()


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


def _interval_distance(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    if a_end >= b_start and b_end >= a_start:
        return 0.0
    if a_end < b_start:
        return b_start - a_end
    return a_start - b_end


def _hazard_intervals(panel_rows: list[dict[str, object]], additional_budget_cap: int) -> list[dict[str, object]]:
    intervals: list[dict[str, object]] = []
    for row in panel_rows:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        current_n = int(row['paired_seed_count'])
        radius = T_CRIT_90_DF5 * sd_gap / math.sqrt(current_n + additional_budget_cap)
        start_delta = max(0.0, mean_gap - radius)
        end_delta = min(MAX_DELTA, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        intervals.append(
            {
                'extortion': int(row['extortion']),
                'delay': int(row['delay']),
                'start_delta': start_delta,
                'end_delta': end_delta,
            }
        )
    return intervals


def _candidate_clearance(
    all_rows: list[dict[str, object]],
    panel_rows: list[dict[str, object]],
    width_floor: float,
    delta_ceiling: float,
    additional_budget_cap: int,
    topology_code: str,
) -> float:
    row = next(
        r for r in all_rows
        if r['covered_budget_caps'] == TARGET_FAMILY
        and r['topology_code'] == topology_code
        and float(r['shared_core_width']) >= width_floor
        and float(r['shared_core_end_delta']) < delta_ceiling
    )
    start = float(row['shared_core_start_delta'])
    end = float(row['shared_core_end_delta'])
    return min(
        _interval_distance(start, end, interval['start_delta'], interval['end_delta'])
        for interval in _hazard_intervals(panel_rows, additional_budget_cap)
    )


def _compress_caps(caps: list[int]) -> list[dict[str, int]]:
    if not caps:
        return []
    out: list[dict[str, int]] = []
    start = prev = caps[0]
    for cap in caps[1:]:
        if cap == prev + 1:
            prev = cap
            continue
        out.append({'start_cap': start, 'end_cap': prev})
        start = prev = cap
    out.append({'start_cap': start, 'end_cap': prev})
    return out


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    winner_certification = _load_json(WINNER_CERTIFICATION_PATH)
    hazard_threshold = _load_json(HAZARD_THRESHOLD_PATH)
    cap_robust = _load_json(CAP_ROBUST_PATH)

    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    policy_box = hazard_threshold['headline_findings']['full_shortlist_policy_box']
    faces = CAP_MOD._policy_box_faces(policy_box)
    min_cap = int(policy_box['minimum_additional_budget_cap_inclusive'])

    threshold_rows: list[dict[str, object]] = []
    exact_thresholds: list[tuple[int, float]] = []
    for additional_budget_cap in range(min_cap, MAX_CAP + 1):
        face_thresholds: list[float] = []
        for face in faces:
            material_clearance = _candidate_clearance(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                MATERIAL_ANCHOR,
            )
            stability_clearance = _candidate_clearance(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                STABILITY_ANCHOR,
            )
            face_thresholds.append(material_clearance - stability_clearance)
        spread = max(face_thresholds) - min(face_thresholds)
        if spread > 1e-12:
            raise SystemExit(
                f'policy-box faces disagree on normalized threshold at cap {additional_budget_cap}: {spread}'
            )
        exact_threshold = face_thresholds[0]
        exact_thresholds.append((additional_budget_cap, exact_threshold))
        if additional_budget_cap in {10, 14, 15, 20, 100, 1000, 10000}:
            threshold_rows.append(
                {
                    'additional_budget_cap': additional_budget_cap,
                    'normalized_threshold_for_stability': exact_threshold,
                }
            )

    increasing_to_peak = all(
        exact_thresholds[i + 1][1] > exact_thresholds[i][1]
        for i in range(0, 10)
    )
    decreasing_from_peak = all(
        exact_thresholds[i + 1][1] < exact_thresholds[i][1]
        for i in range(10, len(exact_thresholds) - 1)
    )
    if not increasing_to_peak or not decreasing_from_peak:
        raise SystemExit('normalized threshold curve is not strictly unimodal on checked caps')

    low_row = min(exact_thresholds, key=lambda item: item[1])
    peak_row = max(exact_thresholds, key=lambda item: item[1])
    tail_row = exact_thresholds[-1]

    class2_rho = 0.5 * (low_row[1] + tail_row[1])
    class3_rho = 0.5 * (tail_row[1] + peak_row[1])

    def stability_intervals(rho: float) -> list[dict[str, int]]:
        winning_caps = [cap for cap, threshold in exact_thresholds if rho > threshold]
        return _compress_caps(winning_caps)

    class_rows = [
        {
            'class_label': 'material_all_checked_caps',
            'strict_condition_on_rho_when_w_hazard_gt_0': f'rho < {low_row[1]:.9f}',
            'winner_pattern_over_checked_caps': MATERIAL_ANCHOR,
            'reversals_as_cap_increases': 0,
        },
        {
            'class_label': 'low_cap_stability_then_material',
            'strict_condition_on_rho_when_w_hazard_gt_0': f'{low_row[1]:.9f} < rho < {tail_row[1]:.9f}',
            'winner_pattern_over_checked_caps': f'{STABILITY_ANCHOR} on a low-cap prefix, then {MATERIAL_ANCHOR} thereafter',
            'reversals_as_cap_increases': 1,
            'representative_rho': class2_rho,
            'representative_stability_cap_intervals': stability_intervals(class2_rho),
        },
        {
            'class_label': 'stability_then_mid_cap_material_then_tail_stability',
            'strict_condition_on_rho_when_w_hazard_gt_0': f'{tail_row[1]:.9f} < rho < {peak_row[1]:.9f}',
            'winner_pattern_over_checked_caps': (
                f'{STABILITY_ANCHOR} on a low-cap prefix, {MATERIAL_ANCHOR} on a middle cap band, '
                f'then {STABILITY_ANCHOR} again on a high-cap suffix'
            ),
            'reversals_as_cap_increases': 2,
            'representative_rho': class3_rho,
            'representative_stability_cap_intervals': stability_intervals(class3_rho),
        },
        {
            'class_label': 'stability_all_checked_caps',
            'strict_condition_on_rho_when_w_hazard_gt_0': f'rho > {peak_row[1]:.9f}',
            'winner_pattern_over_checked_caps': STABILITY_ANCHOR,
            'reversals_as_cap_increases': 0,
        },
    ]

    return {
        'focus': 'Collapse the remaining cap-sensitive two-anchor choice into a single hazard-normalized scalar diagnostic and classify every possible winner trajectory over the checked additional-budget-cap range.',
        'method_note': 'Recomputed exact hazard-clearance thresholds without six-decimal distance rounding across all four representative width/ceiling faces in the certified family `10/20/50/100` policy box. Defined `rho = baseline_nonhazard_surplus / w_hazard` for `w_hazard > 0`, where stability beats material at cap `c` exactly when `rho` exceeds the cap-specific threshold `tau(c) = material_clearance(c) - stability_clearance(c)`. Then used the exact shape of `tau(c)` on caps 10..10000 to classify all possible winner trajectories as cap increases.',
        'headline_findings': {
            'stability_anchor': STABILITY_ANCHOR,
            'material_anchor': MATERIAL_ANCHOR,
            'policy_box_under_test': {
                'budget_family': TARGET_FAMILY,
                'width_floor_lower_exclusive': policy_box['width_floor_lower_exclusive'],
                'width_floor_upper_inclusive': policy_box['width_floor_upper_inclusive'],
                'delta_ceiling_lower_exclusive': policy_box['delta_ceiling_lower_exclusive'],
                'delta_ceiling_upper_inclusive': policy_box['delta_ceiling_upper_inclusive'],
                'minimum_additional_budget_cap_inclusive': min_cap,
                'maximum_additional_budget_cap_checked': MAX_CAP,
                'representative_face_count_checked_per_cap': len(faces),
            },
            'baseline_nonhazard_surplus_expression': cap_robust['headline_findings']['baseline_nonhazard_surplus_expression'],
            'hazard_normalized_margin_definition_when_w_hazard_gt_0': 'rho = baseline_nonhazard_surplus / w_hazard',
            'cap_specific_stability_rule_when_w_hazard_gt_0': 'choose TTTMMMMUU at cap c iff rho > tau(c), where tau(c) = material_clearance(c) - stability_clearance(c)',
            'zero_hazard_weight_degenerate_rule': 'if w_hazard = 0, cap becomes irrelevant and the winner is whichever anchor makes baseline_nonhazard_surplus positive or negative',
            'exact_threshold_curve_shape_over_checked_caps': 'strictly increasing on caps 10..20, then strictly decreasing on caps 20..10000',
            'minimum_tau_on_checked_caps': low_row[1],
            'cap_with_minimum_tau_on_checked_caps': low_row[0],
            'maximum_tau_on_checked_caps': peak_row[1],
            'cap_with_maximum_tau_on_checked_caps': peak_row[0],
            'tail_tau_at_cap_10000': tail_row[1],
            'strict_trajectory_class_count_when_w_hazard_gt_0': 4,
            'double_reversal_band_when_w_hazard_gt_0': f'{tail_row[1]:.9f} < rho < {peak_row[1]:.9f}',
            'single_reversal_band_when_w_hazard_gt_0': f'{low_row[1]:.9f} < rho < {tail_row[1]:.9f}',
        },
        'trajectory_classes': class_rows,
        'boundary_tie_cases': [
            {
                'rho_equals_tau': low_row[1],
                'tie_occurs_at_cap': low_row[0],
                'winner_pattern_away_from_tie': f'{MATERIAL_ANCHOR} for every larger checked cap',
            },
            {
                'rho_equals_tau': tail_row[1],
                'tie_occurs_at_cap': tail_row[0],
                'winner_pattern_away_from_tie': f'{STABILITY_ANCHOR} on low caps, {MATERIAL_ANCHOR} on a middle band, then tie at cap 10000',
            },
            {
                'rho_equals_tau': peak_row[1],
                'tie_occurs_at_cap': peak_row[0],
                'winner_pattern_away_from_tie': f'{STABILITY_ANCHOR} on every smaller and larger checked cap except the tie at cap {peak_row[0]}',
            },
        ],
        'representative_threshold_rows': threshold_rows,
        'source_reports': [
            str(PUBLISHABILITY_PATH.relative_to(ROOT)),
            str(WINNER_CERTIFICATION_PATH.relative_to(ROOT)),
            str(HAZARD_THRESHOLD_PATH.relative_to(ROOT)),
            str(CAP_ROBUST_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    class_rows = summary['trajectory_classes']
    threshold_rows = summary['representative_threshold_rows']
    boundary_rows = summary['boundary_tie_cases']
    lines = [
        '# Rematch-Proxy Delta Normalized Cap-Trajectory Snapshot (2026-03-06)',
        '',
        'Method:',
        '- recomputed exact hazard-clearance thresholds without six-decimal rounding across all four representative width/ceiling faces in the certified family `10/20/50/100` policy box',
        '- defined `rho = baseline_nonhazard_surplus / w_hazard` for `w_hazard > 0`',
        '- used the exact rule `TTTMMMMUU` at cap `c` iff `rho > tau(c)` where `tau(c) = material_clearance(c) - stability_clearance(c)`',
        '- then classified every strict winner trajectory over checked caps `10..10000` from the exact shape of `tau(c)`',
        '',
        'Headline findings:',
        f"- the normalized threshold curve is {findings['exact_threshold_curve_shape_over_checked_caps']}.",
        f"- exact checked-range extrema are `tau(10) = {findings['minimum_tau_on_checked_caps']:.9f}`, `tau(20) = {findings['maximum_tau_on_checked_caps']:.9f}`, and `tau(10000) = {findings['tail_tau_at_cap_10000']:.9f}`.",
        '- for `w_hazard > 0`, every possible winner path as cap increases falls into exactly `4` strict classes.',
        f"- single-reversal band: `{findings['single_reversal_band_when_w_hazard_gt_0']}`.",
        f"- double-reversal band: `{findings['double_reversal_band_when_w_hazard_gt_0']}`.",
        f"- if `w_hazard = 0`, cap disappears completely and only the sign of `{findings['baseline_nonhazard_surplus_expression']}` matters.",
        '',
        'Strict trajectory classes for `w_hazard > 0`:',
    ]
    for row in class_rows:
        lines.append(
            f"- `{row['class_label']}`: `{row['strict_condition_on_rho_when_w_hazard_gt_0']}` -> {row['winner_pattern_over_checked_caps']}"
        )
        if 'representative_rho' in row:
            intervals = ', '.join(
                f"{interval['start_cap']}..{interval['end_cap']}" if interval['start_cap'] != interval['end_cap'] else str(interval['start_cap'])
                for interval in row['representative_stability_cap_intervals']
            )
            lines.append(
                f"  - representative `rho = {row['representative_rho']:.9f}` gives stability on caps `{intervals}`."
            )
    lines.extend([
        '',
        'Boundary tie cases:',
    ])
    for row in boundary_rows:
        lines.append(
            f"- `rho = {row['rho_equals_tau']:.9f}` ties exactly at cap `{row['tie_occurs_at_cap']}`; away from that tie the pattern is {row['winner_pattern_away_from_tie']}."
        )
    lines.extend([
        '',
        'Representative exact threshold rows:',
    ])
    for row in threshold_rows:
        lines.append(
            f"- cap `{row['additional_budget_cap']}` -> `tau(c) = {row['normalized_threshold_for_stability']:.9f}`"
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The final cap-sensitive choice can now be handed off as one scalar diagnostic `rho`, not as a pile of loosely related weight statements.',
        '- This also exposes a new qualitative failure mode: some declared preferences produce **two** winner reversals as cap rises, so “check one low cap and one high cap” is not enough to understand the full path.',
        '- Future inheritors should therefore classify the declared preference by its normalized margin before narrating how added budget changes the final winner.',
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
