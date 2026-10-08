#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_policy_box_corner_snapshot_20260306.json'
HAZARD_THRESHOLD_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_threshold_snapshot_20260306.json'
PUBLISHABILITY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_publishability_snapshot_20260306.json'
DELTA_STEP = 0.00001
TARGET_FAMILY = [10, 20, 50, 100]


def fail(message: str) -> int:
    print(f'rematch-delta-policy-box-corners: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def main() -> int:
    for path in [SNAPSHOT_PATH, HAZARD_THRESHOLD_PATH, PUBLISHABILITY_PATH]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')

    snapshot = load_json(SNAPSHOT_PATH)
    hazard_threshold = load_json(HAZARD_THRESHOLD_PATH)
    publishability = load_json(PUBLISHABILITY_PATH)

    findings = snapshot.get('headline_findings')
    if not isinstance(findings, dict):
        return fail('headline_findings missing')

    hazard_policy_box = hazard_threshold['headline_findings']['full_shortlist_policy_box']
    policy_box = findings.get('policy_box_under_test')
    if not isinstance(policy_box, dict):
        return fail('policy_box_under_test missing')
    if policy_box.get('covered_budget_caps') != TARGET_FAMILY:
        return fail('policy box family mismatch')

    expected_width_low = round(float(hazard_policy_box['width_floor_lower_exclusive']) + DELTA_STEP, 5)
    expected_width_high = round(float(hazard_policy_box['width_floor_upper_inclusive']), 5)
    expected_ceiling_low = round(float(hazard_policy_box['delta_ceiling_lower_exclusive']) + DELTA_STEP, 5)
    expected_ceiling_high = round(float(hazard_policy_box['delta_ceiling_upper_inclusive']), 5)
    expected_cap_low = int(hazard_policy_box['minimum_additional_budget_cap_inclusive'])

    if policy_box.get('width_floor_representatives') != [expected_width_low, expected_width_high]:
        return fail('width representatives mismatch')
    if policy_box.get('delta_ceiling_representatives') != [expected_ceiling_low, expected_ceiling_high]:
        return fail('delta ceiling representatives mismatch')
    if policy_box.get('additional_budget_cap_representatives') != [expected_cap_low, 10000]:
        return fail('hazard cap representatives mismatch')

    if bool(findings.get('candidate_identity_invariant_across_all_representative_corners')) is not True:
        return fail('candidate identity invariance mismatch')
    if bool(findings.get('priority_profile_winners_invariant_across_all_representative_corners')) is not True:
        return fail('priority profile invariance mismatch')
    if findings.get('corner_count_checked') != 8:
        return fail('corner count mismatch')

    corners = snapshot.get('corner_rows')
    if not isinstance(corners, list) or len(corners) != 8:
        return fail('corner_rows mismatch')

    candidate_signatures = {
        tuple(zip(row.get('candidate_topology_codes', []), row.get('candidate_anchor_deltas', [])))
        for row in corners
    }
    if candidate_signatures != {(('TTTMMMMMU', 0.00602), ('TTTMMMMUU', 0.00744))}:
        return fail('corner candidate signature mismatch')

    profile_signatures = {
        tuple((outcome['profile_name'], outcome['winner_topology_code'], outcome['winner_anchor_delta']) for outcome in row.get('priority_profile_outcomes', []))
        for row in corners
    }
    expected_profile_signature = (
        ('material_first', 'TTTMMMMMU', 0.00602),
        ('stability_first', 'TTTMMMMUU', 0.00744),
        ('closure_conservative', 'TTTMMMMMU', 0.00602),
    )
    if profile_signatures != {expected_profile_signature}:
        return fail('corner priority signature mismatch')

    strict = findings.get('strictest_representative_corner', {})
    permissive = findings.get('most_permissive_representative_corner', {})
    if (strict.get('width_floor'), strict.get('additional_budget_cap'), strict.get('delta_ceiling')) != (expected_width_high, expected_cap_low, expected_ceiling_low):
        return fail('strict corner parameters mismatch')
    if (permissive.get('width_floor'), permissive.get('additional_budget_cap'), permissive.get('delta_ceiling')) != (expected_width_low, 10000, expected_ceiling_high):
        return fail('permissive corner parameters mismatch')
    if strict.get('candidate_topology_codes') != ['TTTMMMMMU', 'TTTMMMMUU']:
        return fail('strict corner candidates mismatch')
    if permissive.get('candidate_topology_codes') != ['TTTMMMMMU', 'TTTMMMMUU']:
        return fail('permissive corner candidates mismatch')
    if not approx(float(strict.get('minimum_hazard_clearance_inside_corner', -1.0)), 0.000008):
        return fail('strict corner minimum hazard clearance mismatch')

    permissive_face = findings.get('permissive_width_ceiling_face_before_hazard_guardrail', {})
    if permissive_face.get('candidate_count_before_hazard_guardrail') != 2:
        return fail('permissive pre-hazard count mismatch')
    if permissive_face.get('candidate_topology_codes_before_hazard_guardrail') != ['TTTMMMMMU', 'TTTMMMMUU']:
        return fail('permissive pre-hazard candidate codes mismatch')
    if permissive_face.get('candidate_anchor_deltas_before_hazard_guardrail') != [0.00602, 0.00744]:
        return fail('permissive pre-hazard candidate deltas mismatch')

    binding = findings.get('binding_strict_corner_candidate_for_hazard_clearance', {})
    if (binding.get('topology_code'), binding.get('shared_core_anchor_delta')) != ('TTTMMMMMU', 0.00602):
        return fail('binding candidate mismatch')
    if not approx(float(binding.get('shared_core_width', -1.0)), expected_width_high):
        return fail('binding candidate width mismatch')
    if not approx(float(binding.get('shared_core_end_delta', -1.0)), 0.00666):
        return fail('binding candidate end delta mismatch')
    if not approx(float(binding.get('minimum_hazard_clearance_inside_strict_corner', -1.0)), 0.000008):
        return fail('binding candidate hazard clearance mismatch')

    material = findings.get('material_first_winner_across_representative_corners', {})
    stability = findings.get('stability_first_winner_across_representative_corners', {})
    closure = findings.get('closure_conservative_winner_across_representative_corners', {})
    if (material.get('winner_topology_code'), material.get('winner_anchor_delta')) != ('TTTMMMMMU', 0.00602):
        return fail('material winner mismatch')
    if (stability.get('winner_topology_code'), stability.get('winner_anchor_delta')) != ('TTTMMMMUU', 0.00744):
        return fail('stability winner mismatch')
    if (closure.get('winner_topology_code'), closure.get('winner_anchor_delta')) != ('TTTMMMMMU', 0.00602):
        return fail('closure winner mismatch')

    family_rows = [
        row for row in publishability.get('core_rows', [])
        if row.get('covered_budget_caps') == TARGET_FAMILY
        and float(row['shared_core_width']) >= expected_width_low
        and float(row['shared_core_end_delta']) < expected_ceiling_high
    ]
    family_rows.sort(key=lambda row: (float(row['shared_core_anchor_delta']), str(row['topology_code'])))
    if [(row['topology_code'], row['shared_core_anchor_delta']) for row in family_rows] != [('TTTMMMMMU', 0.00602), ('TTTMMMMUU', 0.00744)]:
        return fail('permissive face family rows mismatch')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
