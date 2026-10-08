#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
PLATEAU_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_width_floor_plateau_snapshot_20260306.json'
EXPECTED_FAMILIES = {
    'caps_10_20_50_100_sub0p01_hazard1000': [10, 20, 50, 100],
    'caps_4_10_20_50_100_sub0p01_hazard1000': [4, 10, 20, 50, 100],
}
PRIORITY_NAMES = ['material_first', 'stability_first', 'closure_conservative']


def fail(message: str) -> int:
    print(f'rematch-delta-width-floor-plateaus: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def material_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -int(row['counts']['material_leader']),
        int(row['counts']['undecided']),
        float(row['shared_core_anchor_delta']),
        int(row['shared_core_anchor_tie_count']),
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
        int(row['root_budget_cap_additional_paired_seeds']),
        str(row['topology_code']),
    )


def stability_first_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        -float(row['shared_core_width']),
        -float(row['shared_core_anchor_buffer_to_boundary']),
        -float(row['min_separation_to_knife_edge_delta']),
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
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
        -float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
        str(row['topology_code']),
    )


SORTERS = {
    'material_first': material_first_key,
    'stability_first': stability_first_key,
    'closure_conservative': closure_conservative_key,
}


def exact_plateau(profile: dict[str, object], candidate_count: int) -> dict[str, object]:
    candidates = [row for row in profile['plateau_rows'] if int(row['candidate_count']) == candidate_count]
    if not candidates:
        raise ValueError(f'no plateau with candidate_count == {candidate_count}')
    return max(
        candidates,
        key=lambda row: (float(row['width_floor_span']), float(row['width_floor_upper_inclusive']), -float(row['width_floor_lower_exclusive'])),
    )


def main() -> int:
    for path in [PUBLISHABILITY_PATH, PLATEAU_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    plateau = load_json(PLATEAU_PATH)

    base_rows = [
        row for row in publishability.get('core_rows', [])
        if bool(row.get('below_delta_0p01')) and not bool(row.get('overlaps_hazard_band_for_additional_budget_cap_1000'))
    ]
    family_profiles = plateau.get('family_profiles')
    headline = plateau.get('headline_findings')
    if not isinstance(family_profiles, list) or len(family_profiles) != len(EXPECTED_FAMILIES):
        return fail('family_profiles mismatch')
    if not isinstance(headline, dict):
        return fail('headline_findings missing')

    by_name = {profile.get('profile_name'): profile for profile in family_profiles}
    if set(by_name) != set(EXPECTED_FAMILIES):
        return fail('unexpected family profile names')

    for name, caps in EXPECTED_FAMILIES.items():
        profile = by_name[name]
        if profile.get('covered_budget_caps') != caps:
            return fail(f'covered_budget_caps mismatch for {name}')
        expected_rows = sorted(
            [row for row in base_rows if row.get('covered_budget_caps') == caps],
            key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        if profile.get('candidate_rows_before_width_floor') != expected_rows:
            return fail(f'candidate_rows_before_width_floor mismatch for {name}')

        expected_cutoffs = sorted({float(row['shared_core_width']) for row in expected_rows})
        plateau_rows = profile.get('plateau_rows')
        if not isinstance(plateau_rows, list) or len(plateau_rows) != len(expected_cutoffs):
            return fail(f'plateau_rows length mismatch for {name}')

        previous_cutoff = 0.0
        for index, (plateau_row, cutoff) in enumerate(zip(plateau_rows, expected_cutoffs), start=1):
            if int(plateau_row.get('plateau_index', -1)) != index:
                return fail(f'plateau_index mismatch for {name} row {index}')
            expected_candidates = sorted(
                [row for row in expected_rows if float(row['shared_core_width']) >= cutoff],
                key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
            )
            if plateau_row.get('candidate_rows') != expected_candidates:
                return fail(f'candidate_rows mismatch for {name} row {index}')
            if int(plateau_row.get('candidate_count', -1)) != len(expected_candidates):
                return fail(f'candidate_count mismatch for {name} row {index}')
            if not approx(float(plateau_row.get('width_floor_upper_inclusive', -1.0)), cutoff):
                return fail(f'width_floor_upper_inclusive mismatch for {name} row {index}')
            if not approx(float(plateau_row.get('width_floor_lower_exclusive', -1.0)), previous_cutoff):
                return fail(f'width_floor_lower_exclusive mismatch for {name} row {index}')
            if bool(plateau_row.get('width_floor_lower_inclusive')) != (index == 1):
                return fail(f'width_floor_lower_inclusive mismatch for {name} row {index}')
            if not approx(float(plateau_row.get('width_floor_span', -1.0)), cutoff - previous_cutoff):
                return fail(f'width_floor_span mismatch for {name} row {index}')
            if plateau_row.get('candidate_topology_codes') != [row['topology_code'] for row in expected_candidates]:
                return fail(f'candidate_topology_codes mismatch for {name} row {index}')
            if plateau_row.get('candidate_anchor_deltas') != [row['shared_core_anchor_delta'] for row in expected_candidates]:
                return fail(f'candidate_anchor_deltas mismatch for {name} row {index}')
            if int(plateau_row.get('distinct_candidate_topology_count', -1)) != len({str(row['topology_code']) for row in expected_candidates}):
                return fail(f'distinct_candidate_topology_count mismatch for {name} row {index}')
            if bool(plateau_row.get('contains_material_core_candidate')) != any(int(row['counts']['material_leader']) > 0 for row in expected_candidates):
                return fail(f'contains_material_core_candidate mismatch for {name} row {index}')

            outcomes = plateau_row.get('priority_profile_outcomes')
            if not isinstance(outcomes, list) or [outcome.get('profile_name') for outcome in outcomes] != PRIORITY_NAMES:
                return fail(f'priority_profile_outcomes mismatch for {name} row {index}')
            winners = set()
            for outcome in outcomes:
                ordered = sorted(expected_candidates, key=SORTERS[outcome['profile_name']])
                winner = ordered[0]
                if outcome.get('winner_topology_code') != winner['topology_code']:
                    return fail(f'winner_topology_code mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if not approx(float(outcome.get('winner_anchor_delta', -1.0)), float(winner['shared_core_anchor_delta'])):
                    return fail(f'winner_anchor_delta mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if outcome.get('winner_counts') != winner['counts']:
                    return fail(f'winner_counts mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if not approx(float(outcome.get('winner_shared_core_width', -1.0)), float(winner['shared_core_width'])):
                    return fail(f'winner_shared_core_width mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if not approx(float(outcome.get('winner_shared_core_anchor_buffer_to_boundary', -1.0)), float(winner['shared_core_anchor_buffer_to_boundary'])):
                    return fail(f'winner_shared_core_anchor_buffer_to_boundary mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if int(outcome.get('winner_shared_core_anchor_tie_count', -1)) != int(winner['shared_core_anchor_tie_count']):
                    return fail(f'winner_shared_core_anchor_tie_count mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if outcome.get('ordered_topology_codes') != [row['topology_code'] for row in ordered]:
                    return fail(f'ordered_topology_codes mismatch for {name} row {index} profile {outcome["profile_name"]}')
                if outcome.get('ordered_anchor_deltas') != [row['shared_core_anchor_delta'] for row in ordered]:
                    return fail(f'ordered_anchor_deltas mismatch for {name} row {index} profile {outcome["profile_name"]}')
                winners.add((winner['topology_code'], float(winner['shared_core_anchor_delta'])))

            if int(plateau_row.get('distinct_priority_winner_count', -1)) != len(winners):
                return fail(f'distinct_priority_winner_count mismatch for {name} row {index}')
            if bool(plateau_row.get('all_priority_profiles_agree')) != (len(winners) == 1):
                return fail(f'all_priority_profiles_agree mismatch for {name} row {index}')

            previous_cutoff = cutoff

    family10 = by_name['caps_10_20_50_100_sub0p01_hazard1000']
    family4 = by_name['caps_4_10_20_50_100_sub0p01_hazard1000']
    family10_two = exact_plateau(family10, 2)
    family4_two = exact_plateau(family4, 2)
    family10_one = exact_plateau(family10, 1)
    family4_one = exact_plateau(family4, 1)

    for key, plateau_row in [
        ('caps_10_20_50_100_largest_two_candidate_plateau', family10_two),
        ('caps_4_10_20_50_100_largest_two_candidate_plateau', family4_two),
        ('caps_10_20_50_100_largest_one_candidate_plateau', family10_one),
        ('caps_4_10_20_50_100_largest_one_candidate_plateau', family4_one),
    ]:
        if headline.get(key) != plateau_row:
            return fail(f'{key} headline mismatch')

    ratio = round(float(family10_two['width_floor_span']) / float(family4_two['width_floor_span']), 6)
    if not approx(float(headline.get('two_candidate_plateau_span_ratio_family10_over_family4', -1.0)), ratio, eps=1e-6):
        return fail('two_candidate_plateau_span_ratio_family10_over_family4 mismatch')

    for key, profile_name in [
        ('family10_material_first_winner_on_two_candidate_plateau', 'material_first'),
        ('family10_stability_first_winner_on_two_candidate_plateau', 'stability_first'),
        ('family10_closure_conservative_winner_on_two_candidate_plateau', 'closure_conservative'),
    ]:
        expected = next(item for item in family10_two['priority_profile_outcomes'] if item['profile_name'] == profile_name)
        if headline.get(key) != expected:
            return fail(f'{key} mismatch')

    family4_tttmmmmmu_width = next(
        float(row['shared_core_width'])
        for row in family4['candidate_rows_before_width_floor']
        if str(row['topology_code']) == 'TTTMMMMMU'
    )
    if not approx(float(headline.get('family4_tttmmmmmu_survives_only_up_to_width_floor', -1.0)), family4_tttmmmmmu_width):
        return fail('family4_tttmmmmmu_survives_only_up_to_width_floor mismatch')

    print('rematch-delta-width-floor-plateaus: ok')
    print(f"family10_two_candidate_plateau={family10_two['width_floor_lower_exclusive']}..{family10_two['width_floor_upper_inclusive']}")
    print(f"family4_two_candidate_plateau={family4_two['width_floor_lower_exclusive']}..{family4_two['width_floor_upper_inclusive']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
