#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
VIABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_family_viability_snapshot_20260306.json'
WIDTH_FLOORS = [0.00025, 0.0005, 0.0010]
EXPECTED_FAMILIES = {
    'caps_10_20_50_100_sub0p01': [10, 20, 50, 100],
    'caps_4_10_20_50_100_sub0p01': [4, 10, 20, 50, 100],
}


def fail(message: str) -> int:
    print(f'rematch-delta-family-viability: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def main() -> int:
    for path in [PUBLISHABILITY_PATH, VIABILITY_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    viability = load_json(VIABILITY_PATH)

    base_rows = [
        row for row in publishability.get('core_rows', [])
        if bool(row.get('below_delta_0p01')) and not bool(row.get('overlaps_hazard_band_for_additional_budget_cap_1000'))
    ]
    profiles = viability.get('family_profiles')
    findings = viability.get('headline_findings')
    if not isinstance(profiles, list) or len(profiles) != len(EXPECTED_FAMILIES):
        return fail('family_profiles mismatch')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')

    by_name = {profile.get('profile_name'): profile for profile in profiles}
    if set(by_name) != set(EXPECTED_FAMILIES):
        return fail('unexpected family profile names')

    for name, caps in EXPECTED_FAMILIES.items():
        profile = by_name[name]
        if profile.get('covered_budget_caps') != caps:
            return fail(f'covered_budget_caps mismatch for {name}')
        expected_rows = sorted(
            [row for row in base_rows if row.get('covered_budget_caps') == caps],
            key=lambda row: (-float(row['shared_core_width']), float(row['shared_core_anchor_delta']), str(row['topology_code'])),
        )
        if profile.get('candidate_rows_before_width_floor') != expected_rows:
            return fail(f'candidate_rows_before_width_floor mismatch for {name}')
        if int(profile.get('candidate_count_before_width_floor', -1)) != len(expected_rows):
            return fail(f'candidate_count_before_width_floor mismatch for {name}')

        widths = [float(row['shared_core_width']) for row in expected_rows]
        max1 = widths[0] if widths else 0.0
        max2 = widths[1] if len(widths) >= 2 else 0.0
        if not approx(float(profile.get('maximum_width_floor_preserving_at_least_one_candidate', -1.0)), max1):
            return fail(f'maximum_width_floor_preserving_at_least_one_candidate mismatch for {name}')
        if not approx(float(profile.get('maximum_width_floor_preserving_at_least_two_candidates', -1.0)), max2):
            return fail(f'maximum_width_floor_preserving_at_least_two_candidates mismatch for {name}')

        width_profiles = profile.get('width_floor_profiles')
        if not isinstance(width_profiles, list) or len(width_profiles) != len(WIDTH_FLOORS):
            return fail(f'width_floor_profiles mismatch for {name}')
        for item, floor in zip(width_profiles, WIDTH_FLOORS):
            if not approx(float(item.get('minimum_shared_core_width', -1.0)), floor):
                return fail(f'minimum_shared_core_width mismatch for {name}')
            expected_candidates = [row for row in expected_rows if float(row['shared_core_width']) >= floor]
            if int(item.get('candidate_count', -1)) != len(expected_candidates):
                return fail(f'candidate_count mismatch for {name} at floor {floor}')
            if item.get('candidate_rows') != expected_candidates:
                return fail(f'candidate_rows mismatch for {name} at floor {floor}')

    family10 = by_name['caps_10_20_50_100_sub0p01']
    family4 = by_name['caps_4_10_20_50_100_sub0p01']
    if int(findings.get('caps_10_20_50_100_sub0p01_candidate_count_before_width_floor', -1)) != int(family10['candidate_count_before_width_floor']):
        return fail('family10 candidate_count_before_width_floor headline mismatch')
    if int(findings.get('caps_4_10_20_50_100_sub0p01_candidate_count_before_width_floor', -1)) != int(family4['candidate_count_before_width_floor']):
        return fail('family4 candidate_count_before_width_floor headline mismatch')

    floor10 = next(item for item in family10['width_floor_profiles'] if approx(float(item['minimum_shared_core_width']), 0.0010))
    floor4 = next(item for item in family4['width_floor_profiles'] if approx(float(item['minimum_shared_core_width']), 0.0010))
    if int(findings.get('caps_10_20_50_100_sub0p01_candidate_count_at_width_0p0010', -1)) != int(floor10['candidate_count']):
        return fail('family10 width_0p0010 headline mismatch')
    if int(findings.get('caps_4_10_20_50_100_sub0p01_candidate_count_at_width_0p0010', -1)) != int(floor4['candidate_count']):
        return fail('family4 width_0p0010 headline mismatch')

    for key, value in [
        ('caps_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate', family10['maximum_width_floor_preserving_at_least_one_candidate']),
        ('caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_one_candidate', family4['maximum_width_floor_preserving_at_least_one_candidate']),
        ('caps_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates', family10['maximum_width_floor_preserving_at_least_two_candidates']),
        ('caps_4_10_20_50_100_maximum_width_floor_preserving_at_least_two_candidates', family4['maximum_width_floor_preserving_at_least_two_candidates']),
    ]:
        if not approx(float(findings.get(key, -1.0)), float(value)):
            return fail(f'{key} headline mismatch')

    ratio1 = float(family10['maximum_width_floor_preserving_at_least_one_candidate']) / float(family4['maximum_width_floor_preserving_at_least_one_candidate'])
    ratio2 = float(family10['maximum_width_floor_preserving_at_least_two_candidates']) / float(family4['maximum_width_floor_preserving_at_least_two_candidates'])
    if not approx(float(findings.get('single_candidate_width_floor_ratio_family10_over_family4', -1.0)), round(ratio1, 6), eps=1e-6):
        return fail('single_candidate_width_floor_ratio mismatch')
    if not approx(float(findings.get('two_candidate_width_floor_ratio_family10_over_family4', -1.0)), round(ratio2, 6), eps=1e-6):
        return fail('two_candidate_width_floor_ratio mismatch')

    if int(floor10['candidate_count']) <= int(floor4['candidate_count']):
        return fail('expected family10 to retain more width-0.0010 candidates than family4')

    print('rematch-delta-family-viability: ok')
    print(f"family10_width0p0010_candidates={int(floor10['candidate_count'])}")
    print(f"family4_width0p0010_candidates={int(floor4['candidate_count'])}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
