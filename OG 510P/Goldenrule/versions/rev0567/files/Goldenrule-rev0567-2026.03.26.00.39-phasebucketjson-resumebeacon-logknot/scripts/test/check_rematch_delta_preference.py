#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
PREFERENCE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_preference_snapshot_20260306.json'
PROFILE_NAME = 'family4_width0p0010_hazard1000_sub0p01'


def fail(message: str) -> int:
    print(f'rematch-delta-preference: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def dominates(a: dict[str, object], b: dict[str, object]) -> bool:
    comparisons = [
        float(a['shared_core_anchor_delta']) <= float(b['shared_core_anchor_delta']),
        float(a['shared_core_width']) >= float(b['shared_core_width']),
        float(a['shared_core_anchor_buffer_to_boundary']) >= float(b['shared_core_anchor_buffer_to_boundary']),
        float(a['min_separation_to_knife_edge_delta']) >= float(b['min_separation_to_knife_edge_delta']),
        float(a['min_separation_to_hazard_band_for_additional_budget_cap_1000']) >= float(b['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
        int(a['counts']['material_leader']) >= int(b['counts']['material_leader']),
        int(a['counts']['undecided']) <= int(b['counts']['undecided']),
        int(a['shared_core_anchor_tie_count']) <= int(b['shared_core_anchor_tie_count']),
        int(a['root_budget_cap_additional_paired_seeds']) <= int(b['root_budget_cap_additional_paired_seeds']),
    ]
    if not all(comparisons):
        return False
    strictly_better = [
        float(a['shared_core_anchor_delta']) < float(b['shared_core_anchor_delta']),
        float(a['shared_core_width']) > float(b['shared_core_width']),
        float(a['shared_core_anchor_buffer_to_boundary']) > float(b['shared_core_anchor_buffer_to_boundary']),
        float(a['min_separation_to_knife_edge_delta']) > float(b['min_separation_to_knife_edge_delta']),
        float(a['min_separation_to_hazard_band_for_additional_budget_cap_1000']) > float(b['min_separation_to_hazard_band_for_additional_budget_cap_1000']),
        int(a['counts']['material_leader']) > int(b['counts']['material_leader']),
        int(a['counts']['undecided']) < int(b['counts']['undecided']),
        int(a['shared_core_anchor_tie_count']) < int(b['shared_core_anchor_tie_count']),
        int(a['root_budget_cap_additional_paired_seeds']) < int(b['root_budget_cap_additional_paired_seeds']),
    ]
    return any(strictly_better)


def profile_sort_key(name: str, row: dict[str, object]) -> tuple[object, ...]:
    if name == 'material_first':
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
    if name == 'stability_first':
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
    if name == 'closure_conservative':
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
    raise AssertionError(name)


def main() -> int:
    for path in [PUBLISHABILITY_PATH, PREFERENCE_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    preference = load_json(PREFERENCE_PATH)

    rows = None
    for profile in publishability.get('guardrail_profiles', []):
        if profile.get('profile_name') == PROFILE_NAME:
            rows = profile.get('candidate_rows')
            break
    if not isinstance(rows, list) or not rows:
        return fail('publishability shortlist rows missing')
    rows = sorted(rows, key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))

    candidate_rows = preference.get('candidate_rows')
    tradeoff_rows = preference.get('tradeoff_rows')
    profile_outcomes = preference.get('priority_profile_outcomes')
    findings = preference.get('headline_findings')
    if candidate_rows != rows:
        return fail('candidate_rows mismatch')
    if not isinstance(tradeoff_rows, list) or len(tradeoff_rows) != len(rows):
        return fail('tradeoff_rows mismatch')
    if not isinstance(profile_outcomes, list) or len(profile_outcomes) != 3:
        return fail('priority_profile_outcomes mismatch')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')

    expected_pareto_codes = []
    for left in rows:
        dominated_by = []
        dominates_codes = []
        incomparables = []
        favorable = []
        unfavorable = []
        for right in rows:
            if left is right:
                continue
            if dominates(right, left):
                dominated_by.append(right['topology_code'])
            elif dominates(left, right):
                dominates_codes.append(right['topology_code'])
            else:
                incomparables.append(right['topology_code'])
                if float(left['shared_core_anchor_delta']) < float(right['shared_core_anchor_delta']):
                    favorable.append(f'lower_delta_than_{right["topology_code"]}')
                elif float(left['shared_core_anchor_delta']) > float(right['shared_core_anchor_delta']):
                    unfavorable.append(f'lower_delta_than_{right["topology_code"]}')
                if int(left['counts']['material_leader']) > int(right['counts']['material_leader']):
                    favorable.append(f'more_material_leaders_than_{right["topology_code"]}')
                elif int(left['counts']['material_leader']) < int(right['counts']['material_leader']):
                    unfavorable.append(f'more_material_leaders_than_{right["topology_code"]}')
                if int(left['counts']['undecided']) < int(right['counts']['undecided']):
                    favorable.append(f'fewer_undecided_than_{right["topology_code"]}')
                elif int(left['counts']['undecided']) > int(right['counts']['undecided']):
                    unfavorable.append(f'fewer_undecided_than_{right["topology_code"]}')
                if float(left['shared_core_width']) > float(right['shared_core_width']):
                    favorable.append(f'wider_shared_core_than_{right["topology_code"]}')
                elif float(left['shared_core_width']) < float(right['shared_core_width']):
                    unfavorable.append(f'wider_shared_core_than_{right["topology_code"]}')
                if float(left['shared_core_anchor_buffer_to_boundary']) > float(right['shared_core_anchor_buffer_to_boundary']):
                    favorable.append(f'larger_anchor_buffer_than_{right["topology_code"]}')
                elif float(left['shared_core_anchor_buffer_to_boundary']) < float(right['shared_core_anchor_buffer_to_boundary']):
                    unfavorable.append(f'larger_anchor_buffer_than_{right["topology_code"]}')
                if float(left['min_separation_to_knife_edge_delta']) > float(right['min_separation_to_knife_edge_delta']):
                    favorable.append(f'larger_knife_edge_separation_than_{right["topology_code"]}')
                elif float(left['min_separation_to_knife_edge_delta']) < float(right['min_separation_to_knife_edge_delta']):
                    unfavorable.append(f'larger_knife_edge_separation_than_{right["topology_code"]}')

        tradeoff = next((row for row in tradeoff_rows if row['topology_code'] == left['topology_code']), None)
        if tradeoff is None:
            return fail(f'missing tradeoff row for {left["topology_code"]}')
        for field in [
            'anchor_delta',
            'counts',
            'shared_core_width',
            'shared_core_anchor_buffer_to_boundary',
            'min_separation_to_knife_edge_delta',
            'min_separation_to_hazard_band_for_additional_budget_cap_1000',
            'shared_core_anchor_tie_count',
            'root_budget_cap_additional_paired_seeds',
        ]:
            source_key = field
            if field == 'anchor_delta':
                source_key = 'shared_core_anchor_delta'
            if tradeoff.get(field) != left.get(source_key):
                return fail(f'{field} mismatch for {left["topology_code"]}')
        if tradeoff.get('dominated_by') != dominated_by:
            return fail(f'dominated_by mismatch for {left["topology_code"]}')
        if tradeoff.get('dominates') != dominates_codes:
            return fail(f'dominates mismatch for {left["topology_code"]}')
        pareto = not dominated_by
        if bool(tradeoff.get('pareto_nondominated')) != pareto:
            return fail(f'pareto flag mismatch for {left["topology_code"]}')
        if tradeoff.get('incomparable_with') != incomparables:
            return fail(f'incomparable_with mismatch for {left["topology_code"]}')
        if tradeoff.get('favorable_axes_vs_incomparables') != favorable:
            return fail(f'favorable axes mismatch for {left["topology_code"]}')
        if tradeoff.get('unfavorable_axes_vs_incomparables') != unfavorable:
            return fail(f'unfavorable axes mismatch for {left["topology_code"]}')
        if pareto:
            expected_pareto_codes.append(left['topology_code'])

    expected_profiles = ['material_first', 'stability_first', 'closure_conservative']
    if [outcome.get('profile_name') for outcome in profile_outcomes] != expected_profiles:
        return fail('priority profile names mismatch')

    distinct_winners = set()
    for outcome in profile_outcomes:
        ordered = sorted(rows, key=lambda row: profile_sort_key(outcome['profile_name'], row))
        winner = ordered[0]
        if outcome.get('winner_topology_code') != winner['topology_code']:
            return fail(f'winner_topology_code mismatch for {outcome["profile_name"]}')
        if not approx(float(outcome['winner_anchor_delta']), float(winner['shared_core_anchor_delta'])):
            return fail(f'winner_anchor_delta mismatch for {outcome["profile_name"]}')
        for field in [
            'winner_counts',
            'winner_shared_core_width',
            'winner_shared_core_anchor_buffer_to_boundary',
            'winner_min_separation_to_knife_edge_delta',
            'winner_min_separation_to_hazard_band_for_additional_budget_cap_1000',
            'winner_shared_core_anchor_tie_count',
        ]:
            source_field = field.replace('winner_', '')
            if field == 'winner_counts':
                source_field = 'counts'
            if outcome.get(field) != winner.get(source_field):
                return fail(f'{field} mismatch for {outcome["profile_name"]}')
        if outcome.get('ordered_topology_codes') != [row['topology_code'] for row in ordered]:
            return fail(f'ordered_topology_codes mismatch for {outcome["profile_name"]}')
        if outcome.get('ordered_anchor_deltas') != [row['shared_core_anchor_delta'] for row in ordered]:
            return fail(f'ordered_anchor_deltas mismatch for {outcome["profile_name"]}')
        distinct_winners.add(winner['topology_code'])

    if int(findings.get('strict_sub0p01_candidate_count')) != len(rows):
        return fail('strict_sub0p01_candidate_count mismatch')
    if int(findings.get('strict_sub0p01_pareto_nondominated_count')) != len(expected_pareto_codes):
        return fail('strict_sub0p01_pareto_nondominated_count mismatch')
    if bool(findings.get('strict_sub0p01_unique_dominant_anchor_exists')) != (len(expected_pareto_codes) == 1):
        return fail('strict_sub0p01_unique_dominant_anchor_exists mismatch')
    if findings.get('material_first_winner') != profile_outcomes[0]:
        return fail('material_first_winner mismatch')
    if findings.get('stability_first_winner') != profile_outcomes[1]:
        return fail('stability_first_winner mismatch')
    if findings.get('closure_conservative_winner') != profile_outcomes[2]:
        return fail('closure_conservative_winner mismatch')
    if int(findings.get('distinct_profile_winner_count')) != len(distinct_winners):
        return fail('distinct_profile_winner_count mismatch')

    print(f'rematch-delta-preference: ok ({len(rows)} shortlist candidates, {len(distinct_winners)} distinct profile winners)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
