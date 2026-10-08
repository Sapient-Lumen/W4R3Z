#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PERSISTENCE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_persistence_snapshot_20260306.json'
HAZARD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_snapshot_20260306.json'
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
MIN_CAP_COUNT = 4
SUB_0P01_LIMIT = 0.01


def fail(message: str) -> int:
    print(f'rematch-delta-publishability: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def interval_distance(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    if a_end >= b_start and b_end >= a_start:
        return 0.0
    if a_end < b_start:
        return round(b_start - a_end, 6)
    return round(a_start - b_end, 6)


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def main() -> int:
    for path in [PERSISTENCE_PATH, HAZARD_PATH, PUBLISHABILITY_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    persistence = load_json(PERSISTENCE_PATH)
    hazard = load_json(HAZARD_PATH)
    publishability = load_json(PUBLISHABILITY_PATH)

    ladder_rows = persistence.get('ladder_rows')
    core_rows = publishability.get('core_rows')
    profiles = publishability.get('guardrail_profiles')
    findings = publishability.get('headline_findings')
    if not isinstance(ladder_rows, list) or not ladder_rows:
        return fail('persistence ladder_rows must be non-empty')
    if not isinstance(core_rows, list) or not core_rows:
        return fail('core_rows must be non-empty')
    if not isinstance(profiles, list) or not profiles:
        return fail('guardrail_profiles must be non-empty')
    if not isinstance(findings, dict):
        return fail('headline_findings must be an object')

    hazard_rows = hazard.get('panel_hazard_rows_for_additional_budget_cap_1000')
    knife_rows = hazard.get('knife_edge_rows')
    if not isinstance(hazard_rows, list) or not isinstance(knife_rows, list):
        return fail('hazard report missing required rows')
    hazard_intervals = [
        (
            float(row['hazard_interval_within_delta_le_0_02']['start_delta']),
            float(row['hazard_interval_within_delta_le_0_02']['end_delta']),
        )
        for row in hazard_rows
    ]
    knife_edges = [float(row['leader_margin']) for row in knife_rows]

    expected = {}
    for row in ladder_rows:
        if int(row['covered_budget_cap_count']) < MIN_CAP_COUNT:
            continue
        key = (
            str(row['topology_code']),
            float(row['shared_core_start_delta']),
            float(row['shared_core_end_delta']),
        )
        current = expected.get(key)
        if current is None or int(row['root_budget_cap_additional_paired_seeds']) < int(current['root_budget_cap_additional_paired_seeds']):
            expected[key] = row

    if len(core_rows) != len(expected):
        return fail('core_rows length mismatch')

    seen = set()
    for row in core_rows:
        key = (
            str(row['topology_code']),
            float(row['shared_core_start_delta']),
            float(row['shared_core_end_delta']),
        )
        if key in seen:
            return fail(f'duplicate core row {key}')
        seen.add(key)
        source = expected.get(key)
        if source is None:
            return fail(f'unexpected core row {key}')

        if int(row['root_budget_cap_additional_paired_seeds']) != int(source['root_budget_cap_additional_paired_seeds']):
            return fail(f'root budget cap mismatch for {key}')
        for field in [
            'covered_budget_caps',
            'covered_budget_cap_count',
            'covers_all_larger_declared_caps',
            'topology_code',
            'counts',
            'shared_core_width',
            'shared_core_gridpoint_count',
            'shared_core_anchor_delta',
            'shared_core_anchor_tie_count',
            'shared_core_anchor_buffer_to_boundary',
            'single_grid_point_shared_core',
        ]:
            if row.get(field) != source.get(field):
                return fail(f'{field} mismatch for {key}')
        if bool(row['below_delta_0p01']) != (float(row['shared_core_end_delta']) < SUB_0P01_LIMIT):
            return fail(f'below_delta_0p01 mismatch for {key}')

        expected_hazard_sep = min(
            interval_distance(
                float(row['shared_core_start_delta']),
                float(row['shared_core_end_delta']),
                h0,
                h1,
            )
            for h0, h1 in hazard_intervals
        )
        if not approx(float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']), expected_hazard_sep):
            return fail(f'hazard separation mismatch for {key}')
        if bool(row['overlaps_hazard_band_for_additional_budget_cap_1000']) != (expected_hazard_sep == 0.0):
            return fail(f'hazard overlap mismatch for {key}')

        expected_knife_sep = min(abs(float(row['shared_core_anchor_delta']) - edge) for edge in knife_edges)
        if not approx(float(row['min_separation_to_knife_edge_delta']), round(expected_knife_sep, 6)):
            return fail(f'knife-edge separation mismatch for {key}')

    profile_lookup = {profile['profile_name']: profile for profile in profiles}
    expected_specs = {
        'family4_width0p0005_hazard1000': (0.0005, False),
        'family4_width0p0010_hazard1000': (0.0010, False),
        'family4_width0p0010_hazard1000_sub0p01': (0.0010, True),
    }
    if set(profile_lookup) != set(expected_specs):
        return fail('unexpected guardrail profile names')

    for name, (width_floor, sub_0p01_only) in expected_specs.items():
        profile = profile_lookup[name]
        if int(profile['minimum_covered_budget_cap_count']) != MIN_CAP_COUNT:
            return fail(f'minimum_covered_budget_cap_count mismatch for {name}')
        if not approx(float(profile['minimum_shared_core_width']), width_floor):
            return fail(f'minimum_shared_core_width mismatch for {name}')
        if int(profile['requires_no_overlap_with_hazard_band_for_additional_budget_cap']) != 1000:
            return fail(f'hazard threshold mismatch for {name}')
        if bool(profile['sub_0p01_only']) != sub_0p01_only:
            return fail(f'sub_0p01_only mismatch for {name}')
        expected_candidates = [
            row for row in core_rows
            if float(row['shared_core_width']) >= width_floor
            and not bool(row['overlaps_hazard_band_for_additional_budget_cap_1000'])
            and (not sub_0p01_only or bool(row['below_delta_0p01']))
        ]
        if profile.get('candidate_rows') != expected_candidates:
            return fail(f'candidate_rows mismatch for {name}')
        if int(profile['candidate_count']) != len(expected_candidates):
            return fail(f'candidate_count mismatch for {name}')

    if int(findings['canonical_family_core_count_covering_at_least_four_caps']) != len(core_rows):
        return fail('canonical family core count mismatch')
    if int(findings['family4_width0p0005_hazard1000_candidate_count']) != int(profile_lookup['family4_width0p0005_hazard1000']['candidate_count']):
        return fail('broad candidate count mismatch')
    if int(findings['family4_width0p0010_hazard1000_candidate_count']) != int(profile_lookup['family4_width0p0010_hazard1000']['candidate_count']):
        return fail('strict candidate count mismatch')
    if int(findings['family4_width0p0010_hazard1000_sub0p01_candidate_count']) != int(profile_lookup['family4_width0p0010_hazard1000_sub0p01']['candidate_count']):
        return fail('strict sub-0.01 candidate count mismatch')
    if findings['family4_width0p0010_hazard1000_sub0p01_candidates'] != profile_lookup['family4_width0p0010_hazard1000_sub0p01']['candidate_rows']:
        return fail('strict sub-0.01 candidate rows mismatch')

    strict_rows = profile_lookup['family4_width0p0010_hazard1000']['candidate_rows']
    expected_min_sep = min(float(row['min_separation_to_hazard_band_for_additional_budget_cap_1000']) for row in strict_rows)
    if not approx(float(findings['strict_shortlist_min_hazard_separation']), expected_min_sep):
        return fail('strict shortlist min hazard separation mismatch')
    expected_max_root_cap = max(int(row['root_budget_cap_additional_paired_seeds']) for row in strict_rows)
    if int(findings['strict_shortlist_max_root_budget_cap']) != expected_max_root_cap:
        return fail('strict shortlist max root budget cap mismatch')

    print(f'rematch-delta-publishability: ok ({len(core_rows)} canonical cores, {len(strict_rows)} strict candidates)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
