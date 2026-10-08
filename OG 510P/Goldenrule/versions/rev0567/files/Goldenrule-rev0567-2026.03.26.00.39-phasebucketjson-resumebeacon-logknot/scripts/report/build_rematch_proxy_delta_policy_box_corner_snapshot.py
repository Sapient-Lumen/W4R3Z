#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
HAZARD_THRESHOLD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_policy_box_corner_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_policy_box_corner_snapshot_20260306.md'
TARGET_FAMILY = [10, 20, 50, 100]
DELTA_STEP = 0.00001
MAX_DELTA = 0.02
T_CRIT_90_DF5 = 2.015048
PRIORITY_NAMES = ['material_first', 'stability_first', 'closure_conservative']
HIGH_CAP_REPRESENTATIVE = 10000


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
    intervals.sort(key=lambda row: (float(row['leader_margin']), int(row['extortion']), int(row['delay'])))
    return intervals


def material_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(row['counts']['material_leader']),
        int(row['counts']['undecided']),
        float(row['shared_core_anchor_delta']),
        int(row['shared_core_anchor_tie_count']),
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        int(row['root_budget_cap_additional_paired_seeds']),
        str(row['topology_code']),
    )


def stability_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        int(row['shared_core_anchor_tie_count']),
        float(row['shared_core_anchor_delta']),
        -int(row['counts']['material_leader']),
        int(row['counts']['undecided']),
        int(row['root_budget_cap_additional_paired_seeds']),
        str(row['topology_code']),
    )


def closure_conservative_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        int(row['counts']['undecided']),
        int(row['shared_core_anchor_tie_count']),
        float(row['shared_core_anchor_delta']),
        -int(row['counts']['material_leader']),
        int(row['root_budget_cap_additional_paired_seeds']),
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap']),
        str(row['topology_code']),
    )


SORTERS = {
    'material_first': material_first_key,
    'stability_first': stability_first_key,
    'closure_conservative': closure_conservative_key,
}


def _priority_profile_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return [
            {
                'profile_name': name,
                'winner_topology_code': None,
                'winner_anchor_delta': None,
                'winner_counts': None,
                'winner_shared_core_width': None,
                'winner_shared_core_anchor_buffer_to_boundary': None,
                'winner_min_separation_to_hazard_band_for_additional_budget_cap': None,
                'winner_shared_core_anchor_tie_count': None,
                'ordered_topology_codes': [],
                'ordered_anchor_deltas': [],
            }
            for name in PRIORITY_NAMES
        ]
    outcomes: list[dict[str, object]] = []
    for name in PRIORITY_NAMES:
        ordered = sorted(rows, key=SORTERS[name])
        winner = ordered[0]
        outcomes.append(
            {
                'profile_name': name,
                'winner_topology_code': winner['topology_code'],
                'winner_anchor_delta': winner['shared_core_anchor_delta'],
                'winner_counts': winner['counts'],
                'winner_shared_core_width': winner['shared_core_width'],
                'winner_shared_core_anchor_buffer_to_boundary': winner['shared_core_anchor_buffer_to_boundary'],
                'winner_min_separation_to_hazard_band_for_additional_budget_cap': winner['min_separation_to_hazard_band_for_additional_budget_cap'],
                'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                'ordered_topology_codes': [row['topology_code'] for row in ordered],
                'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
            }
        )
    return outcomes


def _candidate_rows_for_corner(
    all_rows: list[dict[str, object]],
    panel_rows: list[dict[str, object]],
    width_floor: float,
    additional_budget_cap: int,
    delta_ceiling: float,
) -> list[dict[str, object]]:
    intervals = _hazard_intervals(panel_rows, additional_budget_cap)
    out: list[dict[str, object]] = []
    for row in all_rows:
        if row['covered_budget_caps'] != TARGET_FAMILY:
            continue
        if float(row['shared_core_width']) < width_floor:
            continue
        if float(row['shared_core_end_delta']) >= delta_ceiling:
            continue
        start = float(row['shared_core_start_delta'])
        end = float(row['shared_core_end_delta'])
        best_distance = math.inf
        best_interval: dict[str, object] | None = None
        for interval in intervals:
            hazard = interval['hazard_interval_within_delta_le_0_02']
            distance = _interval_distance(start, end, float(hazard['start_delta']), float(hazard['end_delta']))
            if distance < best_distance:
                best_distance = distance
                best_interval = interval
        if best_distance == 0.0:
            continue
        candidate = dict(row)
        candidate['additional_budget_cap_for_hazard_guardrail'] = additional_budget_cap
        candidate['min_separation_to_hazard_band_for_additional_budget_cap'] = round(best_distance, 6)
        if best_interval is not None:
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
        out.append(candidate)
    out.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return out


def _pre_hazard_rows_for_face(all_rows: list[dict[str, object]], width_floor: float, delta_ceiling: float) -> list[dict[str, object]]:
    rows = [
        row for row in all_rows
        if row['covered_budget_caps'] == TARGET_FAMILY
        and float(row['shared_core_width']) >= width_floor
        and float(row['shared_core_end_delta']) < delta_ceiling
    ]
    rows.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return rows


def _profile_map(outcomes: list[dict[str, object]]) -> dict[str, tuple[object, object]]:
    return {row['profile_name']: (row['winner_topology_code'], row['winner_anchor_delta']) for row in outcomes}


def _build_summary() -> dict[str, object]:
    publishability = _load_json(PUBLISHABILITY_PATH)
    winner_certification = _load_json(WINNER_CERTIFICATION_PATH)
    hazard_threshold = _load_json(HAZARD_THRESHOLD_PATH)
    all_rows = publishability['core_rows']
    panel_rows = winner_certification['panel_rows']
    policy_box = hazard_threshold['headline_findings']['full_shortlist_policy_box']

    width_floor_low = round(float(policy_box['width_floor_lower_exclusive']) + DELTA_STEP, 5)
    width_floor_high = round(float(policy_box['width_floor_upper_inclusive']), 5)
    delta_ceiling_low = round(float(policy_box['delta_ceiling_lower_exclusive']) + DELTA_STEP, 5)
    delta_ceiling_high = round(float(policy_box['delta_ceiling_upper_inclusive']), 5)
    hazard_cap_low = int(policy_box['minimum_additional_budget_cap_inclusive'])
    hazard_cap_high = HIGH_CAP_REPRESENTATIVE

    pre_hazard_easy_rows = _pre_hazard_rows_for_face(all_rows, width_floor_low, delta_ceiling_high)

    corner_rows: list[dict[str, object]] = []
    for width_floor, additional_budget_cap, delta_ceiling in product(
        [width_floor_low, width_floor_high],
        [hazard_cap_low, hazard_cap_high],
        [delta_ceiling_low, delta_ceiling_high],
    ):
        candidate_rows = _candidate_rows_for_corner(all_rows, panel_rows, width_floor, additional_budget_cap, delta_ceiling)
        outcomes = _priority_profile_outcomes(candidate_rows)
        distinct_winners = {
            (outcome['winner_topology_code'], outcome['winner_anchor_delta'])
            for outcome in outcomes if outcome['winner_topology_code'] is not None
        }
        corner_rows.append(
            {
                'width_floor': width_floor,
                'additional_budget_cap': additional_budget_cap,
                'delta_ceiling': delta_ceiling,
                'candidate_count': len(candidate_rows),
                'candidate_topology_codes': [row['topology_code'] for row in candidate_rows],
                'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidate_rows],
                'candidate_rows': candidate_rows,
                'priority_profile_outcomes': outcomes,
                'distinct_priority_winner_count': len(distinct_winners),
                'all_priority_profiles_agree': len(distinct_winners) <= 1,
                'minimum_hazard_clearance_inside_corner': None if not candidate_rows else min(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in candidate_rows),
            }
        )
    corner_rows.sort(key=lambda row: (float(row['width_floor']), int(row['additional_budget_cap']), float(row['delta_ceiling'])))

    strict_corner = next(
        row for row in corner_rows
        if float(row['width_floor']) == width_floor_high
        and int(row['additional_budget_cap']) == hazard_cap_low
        and float(row['delta_ceiling']) == delta_ceiling_low
    )
    permissive_corner = next(
        row for row in corner_rows
        if float(row['width_floor']) == width_floor_low
        and int(row['additional_budget_cap']) == hazard_cap_high
        and float(row['delta_ceiling']) == delta_ceiling_high
    )

    candidate_identity_set = {
        tuple((code, delta) for code, delta in zip(row['candidate_topology_codes'], row['candidate_anchor_deltas']))
        for row in corner_rows
    }
    priority_identity_set = {
        tuple((outcome['profile_name'], outcome['winner_topology_code'], outcome['winner_anchor_delta']) for outcome in row['priority_profile_outcomes'])
        for row in corner_rows
    }
    profile_maps = [_profile_map(row['priority_profile_outcomes']) for row in corner_rows]
    all_profile_maps_identical = len({tuple(sorted(m.items())) for m in profile_maps}) == 1

    stability_binding_candidate = min(
        strict_corner['candidate_rows'],
        key=lambda row: (float(row['min_separation_to_hazard_band_for_additional_budget_cap']), float(row['shared_core_anchor_delta']), str(row['topology_code'])),
    )

    return {
        'focus': 'Certify that the synthesized family10 policy box is a real interaction-stable region rather than an accidental intersection of separate one-dimensional plateaus.',
        'method_note': 'Started from the family `10/20/50/100` shared-core rows in the publishability snapshot, then took the already-derived policy box from the hazard-threshold pass. On the archive\'s `0.00001` delta lattice, converted the box\'s exclusive lower bounds into the first interior representatives (`0.00027` for width floor and `0.00823` for delta ceiling), evaluated all eight representative box corners over width `{0.00027, 0.00129}`, hazard cap `{10, 10000}`, and ceiling `{0.00823, 0.01944}`, and compared candidate identity plus declared priority-profile winners at every corner.',
        'headline_findings': {
            'policy_box_under_test': {
                'covered_budget_caps': TARGET_FAMILY,
                'width_floor_representatives': [width_floor_low, width_floor_high],
                'width_floor_lower_exclusive': policy_box['width_floor_lower_exclusive'],
                'width_floor_upper_inclusive': policy_box['width_floor_upper_inclusive'],
                'additional_budget_cap_representatives': [hazard_cap_low, hazard_cap_high],
                'minimum_additional_budget_cap_inclusive': hazard_cap_low,
                'delta_ceiling_representatives': [delta_ceiling_low, delta_ceiling_high],
                'delta_ceiling_lower_exclusive': policy_box['delta_ceiling_lower_exclusive'],
                'delta_ceiling_upper_inclusive': policy_box['delta_ceiling_upper_inclusive'],
            },
            'strictest_representative_corner': strict_corner,
            'most_permissive_representative_corner': permissive_corner,
            'permissive_width_ceiling_face_before_hazard_guardrail': {
                'width_floor': width_floor_low,
                'delta_ceiling': delta_ceiling_high,
                'candidate_count_before_hazard_guardrail': len(pre_hazard_easy_rows),
                'candidate_topology_codes_before_hazard_guardrail': [row['topology_code'] for row in pre_hazard_easy_rows],
                'candidate_anchor_deltas_before_hazard_guardrail': [row['shared_core_anchor_delta'] for row in pre_hazard_easy_rows],
                'candidate_rows_before_hazard_guardrail': pre_hazard_easy_rows,
            },
            'candidate_identity_invariant_across_all_representative_corners': len(candidate_identity_set) == 1,
            'priority_profile_winners_invariant_across_all_representative_corners': all_profile_maps_identical,
            'corner_count_checked': len(corner_rows),
            'binding_strict_corner_candidate_for_hazard_clearance': {
                'topology_code': stability_binding_candidate['topology_code'],
                'shared_core_anchor_delta': stability_binding_candidate['shared_core_anchor_delta'],
                'shared_core_width': stability_binding_candidate['shared_core_width'],
                'shared_core_end_delta': stability_binding_candidate['shared_core_end_delta'],
                'minimum_hazard_clearance_inside_strict_corner': stability_binding_candidate['min_separation_to_hazard_band_for_additional_budget_cap'],
                'binding_hazard_panel': stability_binding_candidate['binding_hazard_panel'],
            },
            'material_first_winner_across_representative_corners': next(row for row in strict_corner['priority_profile_outcomes'] if row['profile_name'] == 'material_first'),
            'stability_first_winner_across_representative_corners': next(row for row in strict_corner['priority_profile_outcomes'] if row['profile_name'] == 'stability_first'),
            'closure_conservative_winner_across_representative_corners': next(row for row in strict_corner['priority_profile_outcomes'] if row['profile_name'] == 'closure_conservative'),
            'interpretation': 'The family10 policy box is interaction-stable on its representative corners, not merely pairwise plausible. Every tested corner inside width floor `(0.00026, 0.00129]`, hazard cap `>=10`, and ceiling `(0.00822, 0.01944]` produces the same two-anchor shortlist and the same declared priority winners. Moreover, the most permissive width/ceiling face already contains only those two family rows even before the hazard guardrail is applied, so no hidden third anchor is waiting to appear only after several knobs are relaxed together. The genuinely binding face is the strict hazard edge: at corner `(width=0.00129, cap=10, ceiling=0.00823)`, `TTTMMMMMU` survives by only `0.000008` delta against the nearest hazard interval while also sitting exactly on the width-floor boundary.',
        },
        'corner_rows': corner_rows,
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_publishability_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_hazard_threshold_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_policy_box_corner_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    policy_box = findings['policy_box_under_test']
    strict_corner = findings['strictest_representative_corner']
    permissive_corner = findings['most_permissive_representative_corner']
    permissive_face = findings['permissive_width_ceiling_face_before_hazard_guardrail']
    binding = findings['binding_strict_corner_candidate_for_hazard_clearance']
    material_first = findings['material_first_winner_across_representative_corners']
    stability_first = findings['stability_first_winner_across_representative_corners']
    closure_conservative = findings['closure_conservative_winner_across_representative_corners']

    lines = [
        '# Rematch-Proxy Delta Policy-Box Corner Snapshot (2026-03-06)',
        '',
        'Method:',
        '- started from the synthesized family `10/20/50/100` policy box from the hazard-threshold pass',
        '- converted the exclusive lower bounds onto the archive\'s `0.00001` delta lattice, giving representative interior values `0.00027` for width floor and `0.00823` for delta ceiling',
        '- evaluated all eight representative corners over width `{0.00027, 0.00129}`, hazard cap `{10, 10000}`, and ceiling `{0.00823, 0.01944}`',
        '- compared candidate identity plus declared priority-profile winners at every corner, and separately checked the most permissive width/ceiling face before applying the hazard guardrail',
        '',
        'Headline findings:',
        f"- all `{int(findings['corner_count_checked'])}` representative corners produce the same shortlist: `{strict_corner['candidate_topology_codes'][0]}` at `{float(strict_corner['candidate_anchor_deltas'][0]):.5f}` plus `{strict_corner['candidate_topology_codes'][1]}` at `{float(strict_corner['candidate_anchor_deltas'][1]):.5f}`.",
        f"- candidate identity is invariant across all checked corners: `{bool(findings['candidate_identity_invariant_across_all_representative_corners'])}`.",
        f"- declared priority-profile winners are invariant across all checked corners: `{bool(findings['priority_profile_winners_invariant_across_all_representative_corners'])}`.",
        f"- the strictest representative corner `(width={float(strict_corner['width_floor']):.5f}, cap={int(strict_corner['additional_budget_cap'])}, ceiling={float(strict_corner['delta_ceiling']):.5f})` already keeps the full shortlist, with minimum hazard clearance `{float(strict_corner['minimum_hazard_clearance_inside_corner']):.6f}`.",
        f"- the most permissive representative corner `(width={float(permissive_corner['width_floor']):.5f}, cap={int(permissive_corner['additional_budget_cap'])}, ceiling={float(permissive_corner['delta_ceiling']):.5f})` yields the same shortlist and winners.",
        f"- even before hazard filtering, the permissive width/ceiling face `(width={float(permissive_face['width_floor']):.5f}, ceiling={float(permissive_face['delta_ceiling']):.5f})` contains only `{int(permissive_face['candidate_count_before_hazard_guardrail'])}` family candidates: `{', '.join(f'{code}@{float(delta):.5f}' for code, delta in zip(permissive_face['candidate_topology_codes_before_hazard_guardrail'], permissive_face['candidate_anchor_deltas_before_hazard_guardrail']))}`.",
        f"- the binding strict-corner candidate is `{binding['topology_code']}` at `{float(binding['shared_core_anchor_delta']):.5f}`: width `{float(binding['shared_core_width']):.5f}`, end delta `{float(binding['shared_core_end_delta']):.5f}`, hazard clearance `{float(binding['minimum_hazard_clearance_inside_strict_corner']):.6f}`.",
        '',
        'Priority-profile outcomes (unchanged across all representative corners):',
        f"- `material_first` -> `{material_first['winner_topology_code']}` at `{float(material_first['winner_anchor_delta']):.5f}`.",
        f"- `stability_first` -> `{stability_first['winner_topology_code']}` at `{float(stability_first['winner_anchor_delta']):.5f}`.",
        f"- `closure_conservative` -> `{closure_conservative['winner_topology_code']}` at `{float(closure_conservative['winner_anchor_delta']):.5f}`.",
        '',
        'Why this matters for the archive:',
        '- Pairwise plateau intersections are not automatically trustworthy policy regions; dimensions can interact and admit latent candidates only when several knobs are relaxed together.',
        '- This proxy now has a tighter result: the family10 policy box survives a direct corner certification, so the archive can publish it as one real contract rather than as three separate caveated bands.',
        '- The face to monitor first is the strict hazard edge, not the permissive ceiling edge. Future recomputation is most likely to disturb `TTTMMMMMU` near cap `10`, where its hazard clearance is only `0.000008` and its width sits exactly at the published upper boundary `0.00129`.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> None:
    summary = _round(_build_summary())
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    _write_markdown(summary)


if __name__ == '__main__':
    main()
