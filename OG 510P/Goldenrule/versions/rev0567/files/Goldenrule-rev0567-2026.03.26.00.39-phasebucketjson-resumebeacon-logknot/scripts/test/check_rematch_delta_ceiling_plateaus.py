#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
SNAPSHOT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_ceiling_plateau_snapshot_20260306.json'
MIN_SHARED_CORE_WIDTH = 0.0010
MAX_DELTA_CEILING = 0.02
EXPECTED_FAMILIES = {
    'caps_10_20_50_100_width0p0010_hazard1000': [10, 20, 50, 100],
    'caps_4_10_20_50_100_width0p0010_hazard1000': [4, 10, 20, 50, 100],
}
PRIORITY_NAMES = ['material_first', 'stability_first', 'closure_conservative']


def fail(message: str) -> int:
    print(f'rematch-delta-ceiling-plateaus: {message}', file=sys.stderr)
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


def expected_plateaus(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    cutoffs = sorted({float(row['shared_core_end_delta']) for row in rows} | {MAX_DELTA_CEILING})
    out = []
    previous = 0.0
    for cutoff in cutoffs:
        candidates = sorted(
            [row for row in rows if float(row['shared_core_end_delta']) < cutoff],
            key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        outcomes = []
        distinct_winners = set()
        for name in PRIORITY_NAMES:
            if candidates:
                ordered = sorted(candidates, key=SORTERS[name])
                winner = ordered[0]
                distinct_winners.add((winner['topology_code'], winner['shared_core_anchor_delta']))
                outcomes.append(
                    {
                        'profile_name': name,
                        'winner_topology_code': winner['topology_code'],
                        'winner_anchor_delta': winner['shared_core_anchor_delta'],
                        'winner_counts': winner['counts'],
                        'winner_shared_core_width': winner['shared_core_width'],
                        'winner_shared_core_anchor_buffer_to_boundary': winner['shared_core_anchor_buffer_to_boundary'],
                        'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000': winner['min_separation_to_hazard_band_for_additional_budget_cap_1000'],
                        'winner_shared_core_anchor_tie_count': winner['shared_core_anchor_tie_count'],
                        'ordered_topology_codes': [row['topology_code'] for row in ordered],
                        'ordered_anchor_deltas': [row['shared_core_anchor_delta'] for row in ordered],
                    }
                )
            else:
                outcomes.append(
                    {
                        'profile_name': name,
                        'winner_topology_code': None,
                        'winner_anchor_delta': None,
                        'winner_counts': None,
                        'winner_shared_core_width': None,
                        'winner_shared_core_anchor_buffer_to_boundary': None,
                        'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000': None,
                        'winner_shared_core_anchor_tie_count': None,
                        'ordered_topology_codes': [],
                        'ordered_anchor_deltas': [],
                    }
                )
        out.append(
            {
                'delta_ceiling_lower_exclusive': round(previous, 6),
                'delta_ceiling_upper_inclusive': round(cutoff, 6),
                'delta_ceiling_span': round(cutoff - previous, 6),
                'candidate_count': len(candidates),
                'candidate_rows': candidates,
                'candidate_topology_codes': [row['topology_code'] for row in candidates],
                'candidate_anchor_deltas': [row['shared_core_anchor_delta'] for row in candidates],
                'priority_profile_outcomes': outcomes,
                'distinct_priority_winner_count': len(distinct_winners),
                'all_priority_profiles_agree': len(distinct_winners) <= 1,
            }
        )
        previous = cutoff
    return out


def select_plateau(plateaus: list[dict[str, object]], candidate_count: int) -> dict[str, object] | None:
    eligible = [row for row in plateaus if int(row['candidate_count']) == candidate_count]
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda row: (
            float(row['delta_ceiling_span']),
            float(row['delta_ceiling_upper_inclusive']),
            -float(row['delta_ceiling_lower_exclusive']),
        ),
    )


def main() -> int:
    for path in [PUBLISHABILITY_PATH, SNAPSHOT_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    snapshot = load_json(SNAPSHOT_PATH)
    all_rows = publishability.get('core_rows', [])
    family_profiles = snapshot.get('family_profiles')
    findings = snapshot.get('headline_findings')
    if not isinstance(family_profiles, list) or len(family_profiles) != len(EXPECTED_FAMILIES):
        return fail('family_profiles mismatch')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')

    by_name = {profile.get('profile_name'): profile for profile in family_profiles}
    if set(by_name) != set(EXPECTED_FAMILIES):
        return fail('unexpected family profile names')

    expected_plateaus_by_name = {}
    for name, caps in EXPECTED_FAMILIES.items():
        profile = by_name[name]
        if profile.get('covered_budget_caps') != caps:
            return fail(f'covered_budget_caps mismatch for {name}')
        if not approx(float(profile.get('minimum_shared_core_width', -1.0)), MIN_SHARED_CORE_WIDTH):
            return fail(f'minimum_shared_core_width mismatch for {name}')
        if int(profile.get('hazard_guardrail_additional_budget_cap', -1)) != 1000:
            return fail(f'hazard guardrail mismatch for {name}')

        expected_rows = sorted(
            [
                row for row in all_rows
                if row.get('covered_budget_caps') == caps
                and float(row.get('shared_core_width', 0.0)) >= MIN_SHARED_CORE_WIDTH
                and not bool(row.get('overlaps_hazard_band_for_additional_budget_cap_1000'))
            ],
            key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        if profile.get('candidate_rows_before_delta_ceiling') != expected_rows:
            return fail(f'candidate_rows_before_delta_ceiling mismatch for {name}')
        if int(profile.get('candidate_count_before_delta_ceiling', -1)) != len(expected_rows):
            return fail(f'candidate_count_before_delta_ceiling mismatch for {name}')

        expected_plateaus_rows = expected_plateaus(expected_rows)
        expected_plateaus_by_name[name] = expected_plateaus_rows
        if profile.get('plateau_rows') != expected_plateaus_rows:
            return fail(f'plateau_rows mismatch for {name}')

    family10_plateaus = expected_plateaus_by_name['caps_10_20_50_100_width0p0010_hazard1000']
    family4_plateaus = expected_plateaus_by_name['caps_4_10_20_50_100_width0p0010_hazard1000']
    family10_two = select_plateau(family10_plateaus, 2)
    family10_one = select_plateau(family10_plateaus, 1)
    family10_three = select_plateau(family10_plateaus, 3)
    family4_zero = select_plateau(family4_plateaus, 0)
    if family10_two is None or family10_one is None or family10_three is None or family4_zero is None:
        return fail('expected plateau counts missing')

    if findings.get('caps_10_20_50_100_largest_two_candidate_plateau') != family10_two:
        return fail('largest two-candidate plateau mismatch')
    if findings.get('caps_10_20_50_100_largest_one_candidate_plateau') != family10_one:
        return fail('largest one-candidate plateau mismatch')
    if findings.get('caps_10_20_50_100_largest_three_candidate_plateau') != family10_three:
        return fail('largest three-candidate plateau mismatch')
    if findings.get('caps_4_10_20_50_100_only_zero_candidate_plateau') != family4_zero:
        return fail('family4 zero-candidate plateau mismatch')

    if bool(findings.get('current_sub0p01_ceiling_lies_inside_family10_two_candidate_plateau')) is not True:
        return fail('expected current sub0p01 ceiling to lie inside family10 two-candidate plateau')
    if not approx(float(findings.get('family10_two_candidate_plateau_slack_above_current_sub0p01_ceiling', -1.0)), round(float(family10_two['delta_ceiling_upper_inclusive']) - 0.01, 6)):
        return fail('family10 two-candidate plateau slack mismatch')
    if not approx(float(findings.get('family10_two_candidate_plateau_span_over_one_candidate_plateau_span', -1.0)), round(float(family10_two['delta_ceiling_span']) / float(family10_one['delta_ceiling_span']), 6)):
        return fail('plateau span ratio mismatch')

    family10_two_outcomes = family10_two['priority_profile_outcomes']
    family10_three_outcomes = family10_three['priority_profile_outcomes']
    material = next(item for item in family10_two_outcomes if item['profile_name'] == 'material_first')
    stability = next(item for item in family10_two_outcomes if item['profile_name'] == 'stability_first')
    closure = next(item for item in family10_two_outcomes if item['profile_name'] == 'closure_conservative')
    stability_after_three = next(item for item in family10_three_outcomes if item['profile_name'] == 'stability_first')

    if findings.get('family10_material_first_winner_on_two_candidate_plateau') != material:
        return fail('material_first winner mismatch')
    if findings.get('family10_stability_first_winner_on_two_candidate_plateau') != stability:
        return fail('stability_first winner mismatch')
    if findings.get('family10_closure_conservative_winner_on_two_candidate_plateau') != closure:
        return fail('closure_conservative winner mismatch')
    if findings.get('family10_stability_first_winner_after_third_candidate_enters') != stability_after_three:
        return fail('stability winner after third candidate mismatch')

    if stability_after_three.get('winner_topology_code') == stability.get('winner_topology_code') and approx(float(stability_after_three.get('winner_anchor_delta', -1.0)), float(stability.get('winner_anchor_delta', -2.0))):
        return fail('expected stability_first winner to change after third candidate enters')

    print('rematch-delta-ceiling-plateaus: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
