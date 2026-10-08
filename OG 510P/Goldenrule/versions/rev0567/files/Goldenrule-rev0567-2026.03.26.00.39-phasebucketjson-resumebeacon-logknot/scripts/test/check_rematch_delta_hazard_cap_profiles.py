#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
PROFILE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_cap_profile_snapshot_20260306.json'
T_CRIT_90_DF5 = 2.015048
MIN_SHARED_CORE_WIDTH = 0.0010
SUB_0P01_LIMIT = 0.01
HAZARD_CAPS = [100, 500, 1000, 10000]
EXPECTED_FAMILIES = {
    'caps_10_20_50_100_width0p0010_sub0p01': [10, 20, 50, 100],
    'caps_4_10_20_50_100_width0p0010_sub0p01': [4, 10, 20, 50, 100],
}
PRIORITY_NAMES = ['material_first', 'stability_first', 'closure_conservative']


def fail(message: str) -> int:
    print(f'rematch-delta-hazard-cap-profiles: {message}', file=sys.stderr)
    return 1


def approx(a: float | None, b: float | None, eps: float = 1e-9) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= eps


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def interval_distance(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    if a_end >= b_start and b_end >= a_start:
        return 0.0
    if a_end < b_start:
        return round(b_start - a_end, 6)
    return round(a_start - b_end, 6)


def hazard_intervals(panel_rows: list[dict[str, object]], additional_budget_cap: int) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    for row in panel_rows:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        current_n = int(row['paired_seed_count'])
        radius = T_CRIT_90_DF5 * sd_gap / math.sqrt(current_n + additional_budget_cap)
        start_delta = max(0.0, mean_gap - radius)
        end_delta = min(SUB_0P01_LIMIT * 2, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        intervals.append((start_delta, end_delta))
    intervals.sort()
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


def main() -> int:
    for path in [PUBLISHABILITY_PATH, WINNER_CERTIFICATION_PATH, PROFILE_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    winner_certification = load_json(WINNER_CERTIFICATION_PATH)
    profile_snapshot = load_json(PROFILE_PATH)

    all_rows = publishability.get('core_rows', [])
    panel_rows = winner_certification.get('panel_rows', [])
    family_profiles = profile_snapshot.get('family_profiles')
    findings = profile_snapshot.get('headline_findings')
    if not isinstance(family_profiles, list) or len(family_profiles) != len(EXPECTED_FAMILIES):
        return fail('family_profiles mismatch')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')

    by_name = {profile.get('profile_name'): profile for profile in family_profiles}
    if set(by_name) != set(EXPECTED_FAMILIES):
        return fail('unexpected family profile names')

    for name, caps in EXPECTED_FAMILIES.items():
        profile = by_name[name]
        if profile.get('covered_budget_caps') != caps:
            return fail(f'covered_budget_caps mismatch for {name}')
        if not approx(float(profile.get('minimum_shared_core_width', -1.0)), MIN_SHARED_CORE_WIDTH):
            return fail(f'minimum_shared_core_width mismatch for {name}')
        if bool(profile.get('sub_0p01_only')) is not True:
            return fail(f'sub_0p01_only mismatch for {name}')

        expected_base_rows = sorted(
            [
                row for row in all_rows
                if row.get('covered_budget_caps') == caps
                and float(row.get('shared_core_width', 0.0)) >= MIN_SHARED_CORE_WIDTH
                and float(row.get('shared_core_end_delta', 1.0)) < SUB_0P01_LIMIT
            ],
            key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        if profile.get('candidate_rows_before_hazard_guardrail') != expected_base_rows:
            return fail(f'candidate_rows_before_hazard_guardrail mismatch for {name}')
        if int(profile.get('candidate_count_before_hazard_guardrail', -1)) != len(expected_base_rows):
            return fail(f'candidate_count_before_hazard_guardrail mismatch for {name}')

        hazard_cap_profiles = profile.get('hazard_cap_profiles')
        if not isinstance(hazard_cap_profiles, list) or [item.get('additional_budget_cap') for item in hazard_cap_profiles] != HAZARD_CAPS:
            return fail(f'hazard_cap_profiles mismatch for {name}')

        candidate_identities = []
        winner_signatures = {priority_name: [] for priority_name in PRIORITY_NAMES}
        minima = []
        maxima = []
        for cap_profile in hazard_cap_profiles:
            cap = int(cap_profile['additional_budget_cap'])
            intervals = hazard_intervals(panel_rows, cap)
            expected_candidates = []
            for row in expected_base_rows:
                distances = [interval_distance(float(row['shared_core_start_delta']), float(row['shared_core_end_delta']), start, end) for start, end in intervals]
                min_distance = min(distances) if distances else math.inf
                if min_distance == 0.0:
                    continue
                candidate = dict(row)
                candidate['additional_budget_cap_for_hazard_guardrail'] = cap
                candidate['min_separation_to_hazard_band_for_additional_budget_cap'] = round(min_distance, 6)
                expected_candidates.append(candidate)
            expected_candidates.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))

            if int(cap_profile.get('candidate_count', -1)) != len(expected_candidates):
                return fail(f'candidate_count mismatch for {name} cap {cap}')
            if cap_profile.get('candidate_rows') != expected_candidates:
                return fail(f'candidate_rows mismatch for {name} cap {cap}')
            if cap_profile.get('candidate_topology_codes') != [row['topology_code'] for row in expected_candidates]:
                return fail(f'candidate_topology_codes mismatch for {name} cap {cap}')
            if cap_profile.get('candidate_anchor_deltas') != [row['shared_core_anchor_delta'] for row in expected_candidates]:
                return fail(f'candidate_anchor_deltas mismatch for {name} cap {cap}')

            outcomes = cap_profile.get('priority_profile_outcomes')
            if not isinstance(outcomes, list) or [outcome.get('profile_name') for outcome in outcomes] != PRIORITY_NAMES:
                return fail(f'priority_profile_outcomes mismatch for {name} cap {cap}')
            winners = set()
            for outcome in outcomes:
                if expected_candidates:
                    ordered = sorted(expected_candidates, key=SORTERS[outcome['profile_name']])
                    winner = ordered[0]
                    if outcome.get('winner_topology_code') != winner['topology_code']:
                        return fail(f'winner_topology_code mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if not approx(float(outcome.get('winner_anchor_delta', -1.0)), float(winner['shared_core_anchor_delta'])):
                        return fail(f'winner_anchor_delta mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_counts') != winner['counts']:
                        return fail(f'winner_counts mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if not approx(float(outcome.get('winner_shared_core_width', -1.0)), float(winner['shared_core_width'])):
                        return fail(f'winner_shared_core_width mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if not approx(float(outcome.get('winner_shared_core_anchor_buffer_to_boundary', -1.0)), float(winner['shared_core_anchor_buffer_to_boundary'])):
                        return fail(f'winner_shared_core_anchor_buffer_to_boundary mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if not approx(float(outcome.get('winner_min_separation_to_hazard_band_for_additional_budget_cap', -1.0)), float(winner['min_separation_to_hazard_band_for_additional_budget_cap'])):
                        return fail(f'winner_min_separation_to_hazard_band_for_additional_budget_cap mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if int(outcome.get('winner_shared_core_anchor_tie_count', -1)) != int(winner['shared_core_anchor_tie_count']):
                        return fail(f'winner_shared_core_anchor_tie_count mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('ordered_topology_codes') != [row['topology_code'] for row in ordered]:
                        return fail(f'ordered_topology_codes mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('ordered_anchor_deltas') != [row['shared_core_anchor_delta'] for row in ordered]:
                        return fail(f'ordered_anchor_deltas mismatch for {name} cap {cap} profile {outcome["profile_name"]}')
                    winners.add((winner['topology_code'], float(winner['shared_core_anchor_delta'])))
                else:
                    if outcome.get('winner_topology_code') is not None or outcome.get('winner_anchor_delta') is not None:
                        return fail(f'expected empty winner for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_counts') is not None:
                        return fail(f'expected empty winner_counts for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_shared_core_width') is not None:
                        return fail(f'expected empty winner_shared_core_width for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_shared_core_anchor_buffer_to_boundary') is not None:
                        return fail(f'expected empty winner_shared_core_anchor_buffer_to_boundary for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_min_separation_to_hazard_band_for_additional_budget_cap') is not None:
                        return fail(f'expected empty winner_min_separation_to_hazard_band_for_additional_budget_cap for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('winner_shared_core_anchor_tie_count') is not None:
                        return fail(f'expected empty winner_shared_core_anchor_tie_count for {name} cap {cap} profile {outcome["profile_name"]}')
                    if outcome.get('ordered_topology_codes') != [] or outcome.get('ordered_anchor_deltas') != []:
                        return fail(f'expected empty ordered lists for {name} cap {cap} profile {outcome["profile_name"]}')

                winner_signatures[outcome['profile_name']].append((outcome.get('winner_topology_code'), outcome.get('winner_anchor_delta')))

            if int(cap_profile.get('distinct_priority_winner_count', -1)) != len(winners):
                return fail(f'distinct_priority_winner_count mismatch for {name} cap {cap}')
            if bool(cap_profile.get('all_priority_profiles_agree')) != (len(winners) <= 1):
                return fail(f'all_priority_profiles_agree mismatch for {name} cap {cap}')

            candidate_identities.append(tuple((row['topology_code'], row['shared_core_anchor_delta']) for row in expected_candidates))
            if expected_candidates:
                minima.append(min(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in expected_candidates))
                maxima.append(max(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in expected_candidates))

        if bool(profile.get('invariant_candidate_identity_across_hazard_caps')) != (len(set(candidate_identities)) <= 1):
            return fail(f'invariant_candidate_identity_across_hazard_caps mismatch for {name}')
        for key, priority_name in [
            ('invariant_material_first_winner_across_hazard_caps', 'material_first'),
            ('invariant_stability_first_winner_across_hazard_caps', 'stability_first'),
            ('invariant_closure_conservative_winner_across_hazard_caps', 'closure_conservative'),
        ]:
            if bool(profile.get(key)) != (len(set(winner_signatures[priority_name])) <= 1):
                return fail(f'{key} mismatch for {name}')

        expected_min = min(minima) if minima else None
        expected_max = max(maxima) if maxima else None
        if not approx(profile.get('minimum_hazard_separation_across_all_hazard_caps'), expected_min, eps=1e-6):
            return fail(f'minimum_hazard_separation_across_all_hazard_caps mismatch for {name}')
        if not approx(profile.get('maximum_hazard_separation_across_all_hazard_caps'), expected_max, eps=1e-6):
            return fail(f'maximum_hazard_separation_across_all_hazard_caps mismatch for {name}')

    family10 = by_name['caps_10_20_50_100_width0p0010_sub0p01']
    family4 = by_name['caps_4_10_20_50_100_width0p0010_sub0p01']
    family10_profiles = family10['hazard_cap_profiles']
    family4_profiles = family4['hazard_cap_profiles']
    if findings.get('hazard_caps_evaluated') != HAZARD_CAPS:
        return fail('hazard_caps_evaluated mismatch')
    if findings.get('caps_10_20_50_100_width0p0010_sub0p01_candidate_counts_by_hazard_cap') != [
        {'additional_budget_cap': profile['additional_budget_cap'], 'candidate_count': profile['candidate_count']} for profile in family10_profiles
    ]:
        return fail('family10 candidate_counts_by_hazard_cap headline mismatch')
    if findings.get('caps_4_10_20_50_100_width0p0010_sub0p01_candidate_counts_by_hazard_cap') != [
        {'additional_budget_cap': profile['additional_budget_cap'], 'candidate_count': profile['candidate_count']} for profile in family4_profiles
    ]:
        return fail('family4 candidate_counts_by_hazard_cap headline mismatch')
    if bool(findings.get('caps_10_20_50_100_width0p0010_sub0p01_invariant_shortlist_across_hazard_caps')) != bool(family10.get('invariant_candidate_identity_across_hazard_caps')):
        return fail('family10 invariant_shortlist headline mismatch')
    if bool(findings.get('caps_4_10_20_50_100_width0p0010_sub0p01_invariant_empty_shortlist_across_hazard_caps')) != all(int(profile['candidate_count']) == 0 for profile in family4_profiles):
        return fail('family4 invariant_empty_shortlist headline mismatch')

    family10_cap100 = next(profile for profile in family10_profiles if int(profile['additional_budget_cap']) == 100)
    family10_cap10000 = next(profile for profile in family10_profiles if int(profile['additional_budget_cap']) == 10000)
    for key, priority_name in [
        ('caps_10_20_50_100_width0p0010_sub0p01_material_first_winner', 'material_first'),
        ('caps_10_20_50_100_width0p0010_sub0p01_stability_first_winner', 'stability_first'),
        ('caps_10_20_50_100_width0p0010_sub0p01_closure_conservative_winner', 'closure_conservative'),
    ]:
        expected = next(outcome for outcome in family10_cap100['priority_profile_outcomes'] if outcome['profile_name'] == priority_name)
        if findings.get(key) != expected:
            return fail(f'{key} headline mismatch')

    if not approx(float(findings.get('caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_100', -1.0)), min(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in family10_cap100['candidate_rows']), eps=1e-6):
        return fail('family10 min_hazard_separation_at_cap_100 headline mismatch')
    if not approx(float(findings.get('caps_10_20_50_100_width0p0010_sub0p01_minimum_hazard_separation_at_cap_10000', -1.0)), min(float(row['min_separation_to_hazard_band_for_additional_budget_cap']) for row in family10_cap10000['candidate_rows']), eps=1e-6):
        return fail('family10 min_hazard_separation_at_cap_10000 headline mismatch')

    if int(family10_cap100['candidate_count']) != 2 or int(family10_cap10000['candidate_count']) != 2:
        return fail('expected family10 to keep two candidates at caps 100 and 10000')
    if any(int(profile['candidate_count']) != 0 for profile in family4_profiles):
        return fail('expected family4 to stay empty at width 0.0010 for all hazard caps')

    print('rematch-delta-hazard-cap-profiles: ok')
    print(f"family10_candidate_counts={[int(profile['candidate_count']) for profile in family10_profiles]}")
    print(f"family4_candidate_counts={[int(profile['candidate_count']) for profile in family4_profiles]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
