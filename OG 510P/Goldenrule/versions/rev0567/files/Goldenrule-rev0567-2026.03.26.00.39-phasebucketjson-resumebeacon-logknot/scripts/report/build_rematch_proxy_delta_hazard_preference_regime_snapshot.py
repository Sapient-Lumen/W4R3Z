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
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_preference_regime_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_preference_regime_snapshot_20260306.md'
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


def _hazard_gain_sign(value: float) -> str:
    if value > 0:
        return 'positive_for_stability'
    if value < 0:
        return 'negative_for_material'
    return 'exact_tie'


def _binding_key(face_row: dict[str, object]) -> tuple[object, ...]:
    material_panel = face_row['material_anchor']['binding_hazard_panel']
    stability_panel = face_row['stability_anchor']['binding_hazard_panel']
    return (
        face_row['hazard_gain_for_stability'],
        _hazard_gain_sign(float(face_row['hazard_gain_for_stability'])),
        int(material_panel['extortion']),
        int(material_panel['delay']),
        int(stability_panel['extortion']),
        int(stability_panel['delay']),
    )


def _limit_clearance(candidate: dict[str, object]) -> float:
    panel = candidate['binding_hazard_panel']
    mean = float(panel['leader_margin'])
    start = float(candidate['shared_core_start_delta'])
    end = float(candidate['shared_core_end_delta'])
    if mean < start:
        return round(start - mean, 6)
    if mean > end:
        return round(mean - end, 6)
    return 0.0


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
        face_rows = []
        face_keys = []
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
            if float(material['min_separation_to_hazard_band_for_additional_budget_cap']) <= 0.0:
                raise SystemExit(f'{MATERIAL_ANCHOR} not hazard-clear at cap {additional_budget_cap}')
            if float(stability['min_separation_to_hazard_band_for_additional_budget_cap']) <= 0.0:
                raise SystemExit(f'{STABILITY_ANCHOR} not hazard-clear at cap {additional_budget_cap}')
            face_row = {
                'width_floor': face['width_floor'],
                'delta_ceiling': face['delta_ceiling'],
                'material_anchor': material,
                'stability_anchor': stability,
                'hazard_gain_for_stability': round(
                    float(stability['min_separation_to_hazard_band_for_additional_budget_cap'])
                    - float(material['min_separation_to_hazard_band_for_additional_budget_cap']),
                    6,
                ),
            }
            face_rows.append(face_row)
            face_keys.append(_binding_key(face_row))
        if len(set(face_keys)) != 1:
            raise SystemExit(f'width/ceiling faces disagree at cap {additional_budget_cap}: {face_keys}')
        representative = face_rows[0]
        cap_rows.append(
            {
                'additional_budget_cap': additional_budget_cap,
                'hazard_gain_for_stability': representative['hazard_gain_for_stability'],
                'hazard_gain_sign': _hazard_gain_sign(float(representative['hazard_gain_for_stability'])),
                'material_anchor_clearance': representative['material_anchor']['min_separation_to_hazard_band_for_additional_budget_cap'],
                'stability_anchor_clearance': representative['stability_anchor']['min_separation_to_hazard_band_for_additional_budget_cap'],
                'material_anchor_binding_hazard_panel': {
                    'extortion': representative['material_anchor']['binding_hazard_panel']['extortion'],
                    'delay': representative['material_anchor']['binding_hazard_panel']['delay'],
                    'leader_margin': representative['material_anchor']['binding_hazard_panel']['leader_margin'],
                    'paired_seed_count': representative['material_anchor']['binding_hazard_panel']['paired_seed_count'],
                },
                'stability_anchor_binding_hazard_panel': {
                    'extortion': representative['stability_anchor']['binding_hazard_panel']['extortion'],
                    'delay': representative['stability_anchor']['binding_hazard_panel']['delay'],
                    'leader_margin': representative['stability_anchor']['binding_hazard_panel']['leader_margin'],
                    'paired_seed_count': representative['stability_anchor']['binding_hazard_panel']['paired_seed_count'],
                },
                'representative_face_count_checked': len(face_rows),
            }
        )

    regimes: list[dict[str, object]] = []
    for row in cap_rows:
        key = (
            row['hazard_gain_sign'],
            row['material_anchor_binding_hazard_panel']['extortion'],
            row['material_anchor_binding_hazard_panel']['delay'],
            row['stability_anchor_binding_hazard_panel']['extortion'],
            row['stability_anchor_binding_hazard_panel']['delay'],
        )
        if not regimes or regimes[-1]['_key'] != key or int(row['additional_budget_cap']) != int(regimes[-1]['cap_end_inclusive']) + 1:
            regimes.append(
                {
                    '_key': key,
                    'cap_start_inclusive': row['additional_budget_cap'],
                    'cap_end_inclusive': row['additional_budget_cap'],
                    'hazard_gain_sign': row['hazard_gain_sign'],
                    'material_anchor_binding_hazard_panel': row['material_anchor_binding_hazard_panel'],
                    'stability_anchor_binding_hazard_panel': row['stability_anchor_binding_hazard_panel'],
                    'hazard_gain_for_stability_at_regime_start': row['hazard_gain_for_stability'],
                    'hazard_gain_for_stability_at_regime_end': row['hazard_gain_for_stability'],
                    'material_anchor_clearance_at_regime_start': row['material_anchor_clearance'],
                    'material_anchor_clearance_at_regime_end': row['material_anchor_clearance'],
                    'stability_anchor_clearance_at_regime_start': row['stability_anchor_clearance'],
                    'stability_anchor_clearance_at_regime_end': row['stability_anchor_clearance'],
                }
            )
        else:
            regimes[-1]['cap_end_inclusive'] = row['additional_budget_cap']
            regimes[-1]['hazard_gain_for_stability_at_regime_end'] = row['hazard_gain_for_stability']
            regimes[-1]['material_anchor_clearance_at_regime_end'] = row['material_anchor_clearance']
            regimes[-1]['stability_anchor_clearance_at_regime_end'] = row['stability_anchor_clearance']

    for regime in regimes:
        del regime['_key']

    positive_regime = next(regime for regime in regimes if regime['hazard_gain_sign'] == 'positive_for_stability')
    negative_regime_first = next(regime for regime in regimes if regime['cap_start_inclusive'] == positive_regime['cap_end_inclusive'] + 1)
    switch_regime = next(regime for regime in regimes if regime['material_anchor_binding_hazard_panel']['extortion'] == 20)

    switch_cap = int(switch_regime['cap_start_inclusive'])
    switch_material = _candidate_with_binding(
        all_rows,
        panel_rows,
        float(faces[0]['width_floor']),
        float(faces[0]['delta_ceiling']),
        switch_cap,
        MATERIAL_ANCHOR,
    )
    switch_stability = _candidate_with_binding(
        all_rows,
        panel_rows,
        float(faces[0]['width_floor']),
        float(faces[0]['delta_ceiling']),
        switch_cap,
        STABILITY_ANCHOR,
    )
    asymptotic_hazard_gain_for_stability = round(_limit_clearance(switch_stability) - _limit_clearance(switch_material), 6)

    representative_caps = [min_cap, positive_regime['cap_end_inclusive'], negative_regime_first['cap_start_inclusive'], negative_regime_first['cap_end_inclusive'], switch_cap, MAX_CAP]
    representative_rows = [row for row in cap_rows if int(row['additional_budget_cap']) in set(representative_caps)]

    return {
        'focus': 'Treat the hazard term in the final two-anchor preference inequality as its own declared regime contract by locating the exact additional-budget caps where its sign flips and where the binding hazard panel changes.',
        'method_note': 'Started from the certified family10 policy box and the explicit two-anchor preference half-space. Checked all four representative width/ceiling faces across every integral additional-budget cap from the exact full-shortlist threshold through 10000, recomputing the binding hazard interval for `TTTMMMMMU` and `TTTMMMMUU` at each cap. Grouped contiguous caps only when the hazard-gain sign and the two binding hazard panels stayed unchanged on every checked face.',
        'headline_findings': {
            'policy_box_under_test': {
                'budget_family': TARGET_FAMILY,
                'width_floor_representatives': sorted({face['width_floor'] for face in faces}),
                'delta_ceiling_representatives': sorted({face['delta_ceiling'] for face in faces}),
                'minimum_additional_budget_cap_inclusive': min_cap,
                'maximum_additional_budget_cap_checked': MAX_CAP,
            },
            'representative_face_count_checked_per_cap': len(faces),
            'hazard_preference_regime_count': len(regimes),
            'largest_cap_where_hazard_clearance_still_favors_stability': positive_regime['cap_end_inclusive'],
            'smallest_cap_where_hazard_clearance_favors_material': negative_regime_first['cap_start_inclusive'],
            'material_anchor_binding_hazard_panel_switch_cap': switch_cap,
            'positive_hazard_gain_for_stability_at_full_shortlist_threshold': positive_regime['hazard_gain_for_stability_at_regime_start'],
            'positive_hazard_gain_for_stability_just_before_sign_flip': positive_regime['hazard_gain_for_stability_at_regime_end'],
            'negative_hazard_gain_for_stability_at_first_material_favoring_cap': negative_regime_first['hazard_gain_for_stability_at_regime_start'],
            'negative_hazard_gain_for_stability_at_binding_panel_switch_cap': switch_regime['hazard_gain_for_stability_at_regime_start'],
            'negative_hazard_gain_for_stability_at_cap_10000': next(row['hazard_gain_for_stability'] for row in cap_rows if int(row['additional_budget_cap']) == MAX_CAP),
            'asymptotic_hazard_gain_for_stability_after_binding_panel_switch': asymptotic_hazard_gain_for_stability,
            'binding_panel_before_switch_for_material_anchor': positive_regime['material_anchor_binding_hazard_panel'],
            'binding_panel_after_switch_for_material_anchor': switch_regime['material_anchor_binding_hazard_panel'],
            'binding_panel_for_stability_anchor_across_all_regimes': positive_regime['stability_anchor_binding_hazard_panel'],
            'interpretation': 'Inside the certified family10 policy box, the hazard term is not a single stable coefficient. It lives in three exact cap regimes that are invariant across representative width/ceiling faces. Caps 10–14 still give the stability anchor more hazard clearance than the material anchor; caps 15–19 reverse that ranking while keeping the same binding hazard panels; and from cap 20 onward the material anchor binds against a different, much closer panel. After that switch the hazard term still favors the material anchor, but only weakly, shrinking toward an asymptotic edge of about -0.000018 rather than growing without bound.',
        },
        'regime_rows': regimes,
        'representative_cap_rows': representative_rows,
        'source_reports': [
            str(HAZARD_THRESHOLD_PATH.relative_to(ROOT)),
            str(PREFERENCE_HALFSPACE_PATH.relative_to(ROOT)),
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_hazard_preference_regime_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    regimes = summary['regime_rows']
    representative_rows = summary['representative_cap_rows']
    lines = [
        '# Rematch-Proxy Delta Hazard Preference Regime Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the certified family `10/20/50/100` policy box and the explicit two-anchor preference half-space',
        '- checked all four representative width/ceiling faces inside that box for every integral additional-budget cap from `10` through `10000`',
        '- recomputed the binding hazard panel for `TTTMMMMMU` and `TTTMMMMUU` at each cap',
        '- grouped caps only when the hazard-gain sign and both binding hazard panels stayed identical on every checked face',
        '',
        'Headline findings:',
        f"- checked `{int(findings['representative_face_count_checked_per_cap'])}` representative width/ceiling faces per cap and found `{int(findings['hazard_preference_regime_count'])}` exact hazard-preference regimes.",
        f"- hazard clearance favors `TTTMMMMUU` only through cap `{int(findings['largest_cap_where_hazard_clearance_still_favors_stability'])}`; it first favors `TTTMMMMMU` at cap `{int(findings['smallest_cap_where_hazard_clearance_favors_material'])}`.",
        f"- the material anchor's binding hazard panel switches at cap `{int(findings['material_anchor_binding_hazard_panel_switch_cap'])}` from `(extortion={int(findings['binding_panel_before_switch_for_material_anchor']['extortion'])}, delay={int(findings['binding_panel_before_switch_for_material_anchor']['delay'])})` to `(extortion={int(findings['binding_panel_after_switch_for_material_anchor']['extortion'])}, delay={int(findings['binding_panel_after_switch_for_material_anchor']['delay'])})`.",
        f"- hazard gain for the stability anchor moves from `+{float(findings['positive_hazard_gain_for_stability_at_full_shortlist_threshold']):.6f}` at cap `10` to `+{float(findings['positive_hazard_gain_for_stability_just_before_sign_flip']):.6f}` at cap `{int(findings['largest_cap_where_hazard_clearance_still_favors_stability'])}`, then to `{float(findings['negative_hazard_gain_for_stability_at_first_material_favoring_cap']):.6f}` at cap `{int(findings['smallest_cap_where_hazard_clearance_favors_material'])}` and `{float(findings['negative_hazard_gain_for_stability_at_binding_panel_switch_cap']):.6f}` at the switch cap `{int(findings['material_anchor_binding_hazard_panel_switch_cap'])}`.",
        f"- by cap `10000`, the hazard term is still slightly material-favoring at `{float(findings['negative_hazard_gain_for_stability_at_cap_10000']):.6f}`, and after the binding-panel switch its asymptotic limit is only `{float(findings['asymptotic_hazard_gain_for_stability_after_binding_panel_switch']):.6f}`.",
        '',
        'Exact hazard-preference regimes:',
    ]
    for regime in regimes:
        lines.append(
            f"- caps `{int(regime['cap_start_inclusive'])}..{int(regime['cap_end_inclusive'])}`: sign `{regime['hazard_gain_sign']}`, hazard gain for stability from `{float(regime['hazard_gain_for_stability_at_regime_start']):.6f}` to `{float(regime['hazard_gain_for_stability_at_regime_end']):.6f}`, material binding panel `(extortion={int(regime['material_anchor_binding_hazard_panel']['extortion'])}, delay={int(regime['material_anchor_binding_hazard_panel']['delay'])})`, stability binding panel `(extortion={int(regime['stability_anchor_binding_hazard_panel']['extortion'])}, delay={int(regime['stability_anchor_binding_hazard_panel']['delay'])})`."
        )
    lines.extend([
        '',
        'Representative caps:',
    ])
    for row in representative_rows:
        lines.append(
            f"- cap `{int(row['additional_budget_cap'])}`: material clearance `{float(row['material_anchor_clearance']):.6f}` vs stability clearance `{float(row['stability_anchor_clearance']):.6f}` so the hazard contribution to `TTTMMMMUU - TTTMMMMMU` is `{float(row['hazard_gain_for_stability']):.6f}`; binding panels are material `(extortion={int(row['material_anchor_binding_hazard_panel']['extortion'])}, delay={int(row['material_anchor_binding_hazard_panel']['delay'])})` and stability `(extortion={int(row['stability_anchor_binding_hazard_panel']['extortion'])}, delay={int(row['stability_anchor_binding_hazard_panel']['delay'])})`."
        )
    lines.extend([
        '',
        'Why this matters for the archive:',
        '- The remaining cap-sensitive ambiguity in the final preference inequality is now an exact discrete regime contract, not a vague “hazard matters a bit” caveat.',
        '- Future inheritors can publish one clean statement: once the full shortlist appears at cap `10`, hazard clearance helps the stability anchor only for `10..14`, flips against it for `15..19`, and from `20` onward remains weakly material-favoring under a different binding panel.',
        '- Because these regimes are invariant across representative width/ceiling faces inside the certified box, later recomputation only needs to revisit them if the live anchor pair or the hazard-band construction itself changes.',
        '',
    ])
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
