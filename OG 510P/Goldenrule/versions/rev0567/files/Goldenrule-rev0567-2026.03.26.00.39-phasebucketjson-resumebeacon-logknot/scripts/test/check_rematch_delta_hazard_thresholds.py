#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
WINNER_CERTIFICATION_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
WIDTH_PLATEAU_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_width_floor_plateau_snapshot_20260306.json'
CEILING_PLATEAU_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_ceiling_plateau_snapshot_20260306.json'
SNAPSHOT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
T_CRIT_90_DF5 = 2.015048
TARGET_FAMILY = [10, 20, 50, 100]
MIN_SHARED_CORE_WIDTH = 0.0010
SUB_0P01_LIMIT = 0.01
MAX_DELTA = 0.02


def fail(message: str) -> int:
    print(f'rematch-delta-hazard-thresholds: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
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
        end_delta = min(MAX_DELTA, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        intervals.append((start_delta, end_delta))
    intervals.sort()
    return intervals


def base_rows(all_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = [
        row for row in all_rows
        if row['covered_budget_caps'] == TARGET_FAMILY
        and float(row['shared_core_width']) >= MIN_SHARED_CORE_WIDTH
        and float(row['shared_core_end_delta']) < SUB_0P01_LIMIT
    ]
    rows.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    return rows


def survivors_at_cap(rows: list[dict[str, object]], panel_rows: list[dict[str, object]], cap: int) -> list[tuple[str, float]]:
    intervals = hazard_intervals(panel_rows, cap)
    out = []
    for row in rows:
        distances = [interval_distance(float(row['shared_core_start_delta']), float(row['shared_core_end_delta']), start, end) for start, end in intervals]
        if min(distances) > 0.0:
            out.append((row['topology_code'], float(row['shared_core_anchor_delta'])))
    out.sort()
    return out


def first_clearance_cap(row: dict[str, object], panel_rows: list[dict[str, object]]) -> int:
    for cap in range(0, 100000):
        if survivors_at_cap([row], panel_rows, cap):
            return cap
    raise ValueError(f'failed to find clearance cap for {row["topology_code"]}')


def main() -> int:
    for path in [PUBLISHABILITY_PATH, WINNER_CERTIFICATION_PATH, WIDTH_PLATEAU_PATH, CEILING_PLATEAU_PATH, SNAPSHOT_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    publishability = load_json(PUBLISHABILITY_PATH)
    winner_certification = load_json(WINNER_CERTIFICATION_PATH)
    width_snapshot = load_json(WIDTH_PLATEAU_PATH)
    ceiling_snapshot = load_json(CEILING_PLATEAU_PATH)
    snapshot = load_json(SNAPSHOT_PATH)

    rows = base_rows(publishability.get('core_rows', []))
    panels = winner_certification.get('panel_rows', [])
    if [(r['topology_code'], r['shared_core_anchor_delta']) for r in rows] != [('TTTMMMMMU', 0.00602), ('TTTMMMMUU', 0.00744)]:
        return fail('unexpected base rows')

    if survivors_at_cap(rows, panels, 0) != []:
        return fail('cap 0 survivors mismatch')
    if survivors_at_cap(rows, panels, 4) != []:
        return fail('cap 4 survivors mismatch')
    if survivors_at_cap(rows, panels, 5) != [('TTTMMMMUU', 0.00744)]:
        return fail('cap 5 survivors mismatch')
    if survivors_at_cap(rows, panels, 9) != [('TTTMMMMUU', 0.00744)]:
        return fail('cap 9 survivors mismatch')
    if survivors_at_cap(rows, panels, 10) != [('TTTMMMMMU', 0.00602), ('TTTMMMMUU', 0.00744)]:
        return fail('cap 10 survivors mismatch')
    if survivors_at_cap(rows, panels, 100) != [('TTTMMMMMU', 0.00602), ('TTTMMMMUU', 0.00744)]:
        return fail('cap 100 survivors mismatch')

    thresholds = {row['topology_code']: first_clearance_cap(row, panels) for row in rows}
    if thresholds != {'TTTMMMMMU': 10, 'TTTMMMMUU': 5}:
        return fail('clearance threshold mismatch')

    findings = snapshot.get('headline_findings')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')
    if findings.get('full_shortlist_exact_minimum_additional_budget_cap') != 10:
        return fail('full shortlist threshold mismatch')
    if findings.get('first_sampled_hazard_cap') != 100:
        return fail('first sampled hazard cap mismatch')
    if findings.get('first_sampled_hazard_cap_minus_exact_full_shortlist_threshold') != 90:
        return fail('hazard cap slack mismatch')
    if not approx(float(findings.get('first_sampled_hazard_cap_over_exact_full_shortlist_threshold_ratio', -1.0)), 10.0):
        return fail('hazard cap ratio mismatch')

    clearance_rows = snapshot.get('clearance_rows')
    if not isinstance(clearance_rows, list) or len(clearance_rows) != 2:
        return fail('clearance_rows mismatch')
    by_code = {row['topology_code']: row for row in clearance_rows}
    if by_code['TTTMMMMUU']['minimum_additional_budget_cap_to_clear_hazard_band'] != 5:
        return fail('TTTMMMMUU threshold mismatch')
    if by_code['TTTMMMMMU']['minimum_additional_budget_cap_to_clear_hazard_band'] != 10:
        return fail('TTTMMMMMU threshold mismatch')

    plateaus = snapshot.get('hazard_cap_plateau_rows')
    if not isinstance(plateaus, list) or len(plateaus) != 3:
        return fail('hazard_cap_plateau_rows mismatch')
    empty, singleton, full = plateaus
    if (empty.get('hazard_cap_lower_inclusive'), empty.get('hazard_cap_upper_inclusive'), empty.get('candidate_count')) != (0, 4, 0):
        return fail('empty plateau mismatch')
    if (singleton.get('hazard_cap_lower_inclusive'), singleton.get('hazard_cap_upper_inclusive'), singleton.get('candidate_count')) != (5, 9, 1):
        return fail('singleton plateau mismatch')
    if (full.get('hazard_cap_lower_inclusive'), full.get('hazard_cap_upper_inclusive'), full.get('candidate_count')) != (10, None, 2):
        return fail('full plateau mismatch')
    if full.get('candidate_topology_codes') != ['TTTMMMMMU', 'TTTMMMMUU']:
        return fail('full plateau candidate_topology_codes mismatch')
    if full.get('candidate_anchor_deltas') != [0.00602, 0.00744]:
        return fail('full plateau candidate_anchor_deltas mismatch')
    if full.get('sampled_hazard_caps_inside_plateau') != [100, 500, 1000, 10000]:
        return fail('sampled_hazard_caps_inside_plateau mismatch')
    if bool(full.get('candidate_identity_invariant_across_sampled_hazard_caps')) is not True:
        return fail('candidate_identity_invariant_across_sampled_hazard_caps mismatch')

    material = findings.get('material_first_winner_on_full_shortlist_plateau', {})
    stability = findings.get('stability_first_winner_on_full_shortlist_plateau', {})
    closure = findings.get('closure_conservative_winner_on_full_shortlist_plateau', {})
    if (material.get('winner_topology_code'), material.get('winner_anchor_delta')) != ('TTTMMMMMU', 0.00602):
        return fail('material winner mismatch')
    if (stability.get('winner_topology_code'), stability.get('winner_anchor_delta')) != ('TTTMMMMUU', 0.00744):
        return fail('stability winner mismatch')
    if (closure.get('winner_topology_code'), closure.get('winner_anchor_delta')) != ('TTTMMMMMU', 0.00602):
        return fail('closure winner mismatch')

    width_two = width_snapshot['headline_findings']['caps_10_20_50_100_largest_two_candidate_plateau']
    ceiling_two = ceiling_snapshot['headline_findings']['caps_10_20_50_100_largest_two_candidate_plateau']
    policy_box = findings.get('full_shortlist_policy_box', {})
    if policy_box.get('covered_budget_caps') != TARGET_FAMILY:
        return fail('policy box family mismatch')
    if not approx(float(policy_box.get('width_floor_lower_exclusive', -1.0)), float(width_two['width_floor_lower_exclusive'])):
        return fail('policy box width lower mismatch')
    if not approx(float(policy_box.get('width_floor_upper_inclusive', -1.0)), float(width_two['width_floor_upper_inclusive'])):
        return fail('policy box width upper mismatch')
    if policy_box.get('minimum_additional_budget_cap_inclusive') != 10:
        return fail('policy box hazard threshold mismatch')
    if not approx(float(policy_box.get('delta_ceiling_lower_exclusive', -1.0)), float(ceiling_two['delta_ceiling_lower_exclusive'])):
        return fail('policy box ceiling lower mismatch')
    if not approx(float(policy_box.get('delta_ceiling_upper_inclusive', -1.0)), float(ceiling_two['delta_ceiling_upper_inclusive'])):
        return fail('policy box ceiling upper mismatch')
    if policy_box.get('candidate_topology_codes') != ['TTTMMMMMU', 'TTTMMMMUU']:
        return fail('policy box candidates mismatch')
    if policy_box.get('candidate_anchor_deltas') != [0.00602, 0.00744]:
        return fail('policy box candidate deltas mismatch')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
