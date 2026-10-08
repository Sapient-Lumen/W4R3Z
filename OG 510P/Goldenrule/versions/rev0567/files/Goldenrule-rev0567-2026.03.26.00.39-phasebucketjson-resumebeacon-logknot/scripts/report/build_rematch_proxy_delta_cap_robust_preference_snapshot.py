#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
HAZARD_THRESHOLD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
PREFERENCE_HALFSPACE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_halfspace_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_cap_robust_preference_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_cap_robust_preference_snapshot_20260306.md'
TARGET_FAMILY = [10, 20, 50, 100]
MATERIAL_ANCHOR = 'TTTMMMMMU'
STABILITY_ANCHOR = 'TTTMMMMUU'
DELTA_STEP = 0.00001
MAX_DELTA = 0.02
T_CRIT_90_DF5 = 2.015048
MAX_CAP = 10000


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
        return round(b_start - a_end, 6)
    return round(a_start - b_end, 6)


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
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_margin': mean_gap,
                'paired_margin_sd': sd_gap,
                'paired_seed_count': current_n,
                'hazard_interval_within_delta_le_0_02': {
                    'start_delta': start_delta,
                    'end_delta': end_delta,
                },
            }
        )
    return intervals


def _candidate_with_binding(
    all_rows: list[dict[str, object]],
    panel_rows: list[dict[str, object]],
    width_floor: float,
    delta_ceiling: float,
    additional_budget_cap: int,
    topology_code: str,
) -> dict[str, object]:
    row = next(
        r for r in all_rows
        if r['covered_budget_caps'] == TARGET_FAMILY
        and r['topology_code'] == topology_code
        and float(r['shared_core_width']) >= width_floor
        and float(r['shared_core_end_delta']) < delta_ceiling
    )
    start = float(row['shared_core_start_delta'])
    end = float(row['shared_core_end_delta'])
    best_distance = math.inf
    best_interval: dict[str, object] | None = None
    for interval in _hazard_intervals(panel_rows, additional_budget_cap):
        hazard = interval['hazard_interval_within_delta_le_0_02']
        distance = _interval_distance(start, end, float(hazard['start_delta']), float(hazard['end_delta']))
        if distance < best_distance:
            best_distance = distance
            best_interval = interval
    if best_interval is None:
        raise SystemExit(f'no binding interval found for {topology_code} at cap {additional_budget_cap}')
    candidate = dict(row)
    candidate['additional_budget_cap_for_hazard_guardrail'] = additional_budget_cap
    candidate['min_separation_to_hazard_band_for_additional_budget_cap'] = round(best_distance, 6)
    candidate['binding_hazard_panel'] = {
        'extortion': int(best_interval['extortion']),
        'delay': int(best_interval['delay']),
        'leader': best_interval['leader'],
        'runner_up': best_interval['runner_up'],
        'leader_margin': best_interval['leader_margin'],
        'paired_margin_sd': best_interval['paired_margin_sd'],
        'paired_seed_count': int(best_interval['paired_seed_count']),
        'hazard_interval_within_delta_le_0_02': best_interval['hazard_interval_within_delta_le_0_02'],
    }
    return candidate


def _policy_box_faces(policy_box: dict[str, object]) -> list[dict[str, object]]:
    width_floor_low = round(float(policy_box['width_floor_lower_exclusive']) + DELTA_STEP, 5)
    width_floor_high = round(float(policy_box['width_floor_upper_inclusive']), 5)
    delta_ceiling_low = round(float(policy_box['delta_ceiling_lower_exclusive']) + DELTA_STEP, 5)
    delta_ceiling_high = round(float(policy_box['delta_ceiling_upper_inclusive']), 5)
    return [
        {'width_floor': width_floor, 'delta_ceiling': delta_ceiling}
        for width_floor in [width_floor_low, width_floor_high]
        for delta_ceiling in [delta_ceiling_low, delta_ceiling_high]
    ]


def _signed_rhs(value: float) -> str:
    if value < 0:
        return f"-{abs(value):.6f}*w_hazard"
    return f"{value:.6f}*w_hazard"


def _expression(comparator: str, rhs_value: float) -> str:
    return (
        f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - "
        f"0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties {comparator} "
        f"{_signed_rhs(rhs_value)}"
    )


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    winner_certification = _load_json(WINNER_CERTIFICATION_PATH)
    hazard_threshold = _load_json(HAZARD_THRESHOLD_PATH)
    preference_halfspace = _load_json(PREFERENCE_HALFSPACE_PATH)

    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    policy_box = hazard_threshold['headline_findings']['full_shortlist_policy_box']
    faces = _policy_box_faces(policy_box)
    min_cap = int(policy_box['minimum_additional_budget_cap_inclusive'])

    cap_rows: list[dict[str, object]] = []
    for additional_budget_cap in range(min_cap, MAX_CAP + 1):
        face_gains: list[tuple[float, dict[str, object], dict[str, object], dict[str, object]]] = []
        for face in faces:
            material = _candidate_with_binding(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                MATERIAL_ANCHOR,
            )
            stability = _candidate_with_binding(
                all_rows,
                panel_rows,
                float(face['width_floor']),
                float(face['delta_ceiling']),
                additional_budget_cap,
                STABILITY_ANCHOR,
            )
            gain = round(
                float(stability['min_separation_to_hazard_band_for_additional_budget_cap'])
                - float(material['min_separation_to_hazard_band_for_additional_budget_cap']),
                6,
            )
            face_gains.append((gain, face, material, stability))
        gain_values = {item[0] for item in face_gains}
        if len(gain_values) != 1:
            raise SystemExit(f'policy-box faces disagree at cap {additional_budget_cap}: {sorted(gain_values)}')
        gain, face, material, stability = face_gains[0]
        cap_rows.append(
            {
                'additional_budget_cap': additional_budget_cap,
                'hazard_gain_for_stability': gain,
                'representative_face': face,
                'material_anchor_clearance': material['min_separation_to_hazard_band_for_additional_budget_cap'],
                'stability_anchor_clearance': stability['min_separation_to_hazard_band_for_additional_budget_cap'],
                'material_anchor_binding_hazard_panel': {
                    'extortion': material['binding_hazard_panel']['extortion'],
                    'delay': material['binding_hazard_panel']['delay'],
                },
                'stability_anchor_binding_hazard_panel': {
                    'extortion': stability['binding_hazard_panel']['extortion'],
                    'delay': stability['binding_hazard_panel']['delay'],
                },
            }
        )

    max_row = max(cap_rows, key=lambda row: (float(row['hazard_gain_for_stability']), -int(row['additional_budget_cap'])))
    min_row = min(cap_rows, key=lambda row: (float(row['hazard_gain_for_stability']), int(row['additional_budget_cap'])))

    invariant = preference_halfspace['headline_findings']['invariant_nonhazard_tradeoff_coefficients']
    endpoint_strip = float(preference_halfspace['headline_findings']['hazard_sensitivity_strip_width_per_unit_w_hazard'])
    full_strip = round(float(max_row['hazard_gain_for_stability']) - float(min_row['hazard_gain_for_stability']), 6)
    relative_widening = round(full_strip / endpoint_strip - 1.0, 6)

    tail_false_stability_low = abs(float(preference_halfspace['headline_findings']['hazard_clearance_gain_for_stability_at_cap_10000']))
    tail_false_stability_high = abs(float(min_row['hazard_gain_for_stability']))
    low_cap_false_material_low = abs(float(max_row['hazard_gain_for_stability']))
    low_cap_false_material_high = abs(float(preference_halfspace['headline_findings']['hazard_clearance_gain_for_stability_at_cap_10000']))

    return {
        'focus': 'Tighten the final two-anchor handoff from endpoint-only preference half-spaces to an all-caps robustness certificate across the full additional-budget-cap range inside the certified family10 policy box.',
        'method_note': 'Recomputed the hazard-clearance advantage `TTTMMMMUU - TTTMMMMMU` for every integral additional-budget cap from the full-shortlist threshold through 10000 across all four representative width/ceiling faces of the certified family `10/20/50/100` policy box. Then combined the global maximum and minimum hazard coefficients with the invariant non-hazard preference coefficients to derive true cap-robust sufficient conditions and the exact cap-sensitive ambiguity strip.',
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
            'baseline_nonhazard_surplus_expression': '0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties',
            'invariant_nonhazard_tradeoff_coefficients': invariant,
            'largest_hazard_gain_for_stability': max_row['hazard_gain_for_stability'],
            'cap_with_largest_hazard_gain_for_stability': max_row['additional_budget_cap'],
            'smallest_hazard_gain_for_stability': min_row['hazard_gain_for_stability'],
            'cap_with_smallest_hazard_gain_for_stability': min_row['additional_budget_cap'],
            'true_cap_sensitive_ambiguity_strip_width_per_unit_w_hazard': full_strip,
            'endpoint_only_ambiguity_strip_width_per_unit_w_hazard': endpoint_strip,
            'additional_width_missed_by_endpoint_only_check_per_unit_w_hazard': round(full_strip - endpoint_strip, 6),
            'relative_widening_over_endpoint_only_check': relative_widening,
            'stability_anchor_cap_robust_if': _expression('>', abs(float(min_row['hazard_gain_for_stability']))),
            'material_anchor_cap_robust_if': _expression('<', -abs(float(max_row['hazard_gain_for_stability']))),
            'cap_sensitive_if': (
                f"-{abs(float(max_row['hazard_gain_for_stability'])):.6f}*w_hazard <= "
                f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties <= "
                f"{abs(float(min_row['hazard_gain_for_stability'])):.6f}*w_hazard"
            ),
            'tail_false_stability_safety_band_if_using_only_cap_10000': (
                f"{tail_false_stability_low:.6f}*w_hazard < "
                f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties <= "
                f"{tail_false_stability_high:.6f}*w_hazard"
            ),
            'low_cap_false_material_safety_band_if_using_only_cap_10000': (
                f"-{low_cap_false_material_low:.6f}*w_hazard <= "
                f"0.00027*w_width + 0.00013*w_buffer + 0.000122*w_knife - 0.00142*w_delta - 1*w_material - 1*w_undecided - 1*w_ties < "
                f"-{low_cap_false_material_high:.6f}*w_hazard"
            ),
            'interpretation': 'The true cap-robust preference certificate is stricter than the earlier endpoint-only picture. The most stability-favoring hazard coefficient still occurs at cap 10, but the most material-favoring coefficient occurs at cap 20 rather than at the asymptotic tail. So checking only caps 10 and 10000 understates how much declared cap can still swing the final choice. Inside the resulting strip, cap declaration remains a live selector even after family, width floor, delta ceiling, and live-anchor pair have all been fixed.',
        },
        'extremal_cap_rows': {
            'largest_hazard_gain_for_stability_row': max_row,
            'smallest_hazard_gain_for_stability_row': min_row,
        },
        'robustness_regions': [
            {
                'region_label': 'cap_robust_material',
                'winner': MATERIAL_ANCHOR,
                'condition': _expression('<', -abs(float(max_row['hazard_gain_for_stability']))),
                'decisive_cap': max_row['additional_budget_cap'],
            },
            {
                'region_label': 'cap_sensitive_ambiguity_strip',
                'winner': 'depends_on_declared_additional_budget_cap',
                'condition': (
                    f"-{abs(float(max_row['hazard_gain_for_stability'])):.6f}*w_hazard <= baseline_nonhazard_surplus <= "
                    f"{abs(float(min_row['hazard_gain_for_stability'])):.6f}*w_hazard"
                ),
                'strip_width_per_unit_w_hazard': full_strip,
            },
            {
                'region_label': 'cap_robust_stability',
                'winner': STABILITY_ANCHOR,
                'condition': _expression('>', abs(float(min_row['hazard_gain_for_stability']))),
                'decisive_cap': min_row['additional_budget_cap'],
            },
        ],
        'source_reports': [
            str(PREFERENCE_HALFSPACE_PATH.relative_to(ROOT)),
            str(HAZARD_THRESHOLD_PATH.relative_to(ROOT)),
            str(PUBLISHABILITY_PATH.relative_to(ROOT)),
            str(WINNER_CERTIFICATION_PATH.relative_to(ROOT)),
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_cap_robust_preference_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    max_row = summary['extremal_cap_rows']['largest_hazard_gain_for_stability_row']
    min_row = summary['extremal_cap_rows']['smallest_hazard_gain_for_stability_row']
    lines = [
        '# Rematch-Proxy Delta Cap-Robust Preference Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the certified family `10/20/50/100` policy box and the explicit two-anchor preference inequality',
        '- recomputed the hazard-clearance advantage `TTTMMMMUU - TTTMMMMMU` for every integral additional-budget cap from `10` through `10000`',
        '- required all four representative width/ceiling faces to agree at every checked cap',
        '- then combined the global maximum and minimum hazard coefficients with the invariant non-hazard tradeoff coefficients to derive true all-caps robustness conditions',
        '',
        'Headline findings:',
        f"- the most stability-favoring hazard term is still at cap `{int(max_row['additional_budget_cap'])}` with gain `{float(max_row['hazard_gain_for_stability']):.6f}` for `TTTMMMMUU`.",
        f"- the most material-favoring hazard term is **not** the asymptotic tail; it occurs at cap `{int(min_row['additional_budget_cap'])}` with gain `{float(min_row['hazard_gain_for_stability']):.6f}` for `TTTMMMMUU`.",
        f"- the true all-caps ambiguity strip therefore has width `{float(findings['true_cap_sensitive_ambiguity_strip_width_per_unit_w_hazard']):.6f} * w_hazard`, not merely `{float(findings['endpoint_only_ambiguity_strip_width_per_unit_w_hazard']):.6f} * w_hazard` from comparing only caps `10` and `10000`.",
        f"- endpoint-only checking misses `{float(findings['additional_width_missed_by_endpoint_only_check_per_unit_w_hazard']):.6f} * w_hazard` of live cap sensitivity, so the true strip is `{100*float(findings['relative_widening_over_endpoint_only_check']):.2f}%` wider.",
        f"- cap-robust stability condition: `{findings['stability_anchor_cap_robust_if']}`.",
        f"- cap-robust material condition: `{findings['material_anchor_cap_robust_if']}`.",
        f"- cap-sensitive strip: `{findings['cap_sensitive_if']}`.",
        '',
        'Mid-cap correction bands:',
        f"- false stability safety if you checked only cap `10000`: `{findings['tail_false_stability_safety_band_if_using_only_cap_10000']}`.",
        f"- false material safety if you checked only cap `10000`: `{findings['low_cap_false_material_safety_band_if_using_only_cap_10000']}`.",
        '',
        'Why this matters for the archive:',
        '- The archive can now hand off one exact answer to a practical question the previous notes still left loose: when does the declared additional-budget cap still have the power to reverse the final two-anchor choice?',
        '- The answer is: only inside the true all-caps ambiguity strip. Outside it, the winner is cap-robust and the inheritor can certify the choice without appealing to a particular cap sample.',
        '- This also exposes a concrete failure mode of endpoint-only reasoning: the asymptotic tail can make stability or material look safe even though an interior cap still overturns that verdict.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
