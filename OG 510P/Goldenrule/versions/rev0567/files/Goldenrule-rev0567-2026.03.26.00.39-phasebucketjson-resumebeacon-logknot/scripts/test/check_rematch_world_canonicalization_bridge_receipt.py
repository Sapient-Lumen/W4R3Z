#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'schemas' / 'rematch_world_canonicalization_bridge_receipt.schema.json'
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_canonicalization_bridge_receipt.json'
EXPECTED_ASSUMPTIONS = ['SA-004', 'SA-005', 'SA-006', 'SA-007', 'SA-009', 'SA-010']
EXPECTED_QUESTIONS = ['SQ-003', 'SQ-004', 'SQ-005', 'SQ-006', 'SQ-007', 'SQ-008', 'SQ-009', 'SQ-010', 'SQ-011']
EXPECTED_RISKS = [f'RK-{index:03d}' for index in range(7, 16)]
EXPECTED_MODES = {
    'none': {
        'recommended_key_fields': ['noise_mode', 'support_regime_id'],
        'minimal_exact_horizon': 3,
        'regime_count': 17,
    },
    'opponent_tremble': {
        'recommended_key_fields': ['noise_mode'],
        'minimal_exact_horizon': 2,
        'regime_count': 1,
    },
    'focal_tremble': {
        'recommended_key_fields': ['noise_mode', 'entrant_initial_support_includes_D'],
        'minimal_exact_horizon': 2,
        'regime_count': 2,
    },
    'bilateral_tremble': {
        'recommended_key_fields': ['noise_mode'],
        'minimal_exact_horizon': 1,
        'regime_count': 1,
    },
}
EXPECTED_RETAINED_PATHS = [
    'artifacts/reports/rematch_proxy_cache_plan_snapshot_20260306.json',
    'artifacts/reports/rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.json',
    'schemas/canonicalization_plan.schema.json',
    'schemas/zero_noise_rule_classifier.schema.json',
    'scripts/test/check_rematch_cache_plan_contract.py',
    'scripts/test/check_rematch_zero_noise_rule_contract.py',
]


def fail(msg: str) -> int:
    print(f'rematch-world-canonicalization-bridge: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approx(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)


def main() -> int:
    if not SCHEMA.exists():
        return fail(f'missing {SCHEMA.relative_to(ROOT)}')
    if not EXAMPLE.exists():
        return fail(f'missing {EXAMPLE.relative_to(ROOT)}')

    schema = load_json(SCHEMA)
    if schema.get('title') != 'Rematch World Canonicalization Bridge Receipt':
        return fail('schema title mismatch')

    receipt = load_json(EXAMPLE)
    if receipt.get('receipt_kind') != 'rematch_world_canonicalization_bridge_receipt':
        return fail('unexpected receipt_kind')
    if receipt.get('scope', {}).get('gap_id') != 'SG-003':
        return fail('expected SG-003 focus')
    if receipt.get('scope', {}).get('linked_open_item_count') != 24:
        return fail('expected 24 linked open items')

    assumptions = receipt['linked_open_items']['assumptions']
    questions = receipt['linked_open_items']['questions']
    risks = receipt['linked_open_items']['risks']
    if [row['id'] for row in assumptions] != EXPECTED_ASSUMPTIONS:
        return fail('assumption ids mismatch')
    if [row['id'] for row in questions] != EXPECTED_QUESTIONS:
        return fail('question ids mismatch')
    if [row['id'] for row in risks] != EXPECTED_RISKS:
        return fail('risk ids mismatch')
    if any(row['status'] != 'open' for row in assumptions + questions + risks):
        return fail('all linked items should remain open in this bridge receipt')

    naive = receipt['planner_contract']['naive_cache_plan']
    if naive['key_fields'] != ['noise_mode', 'entrant_support_signature']:
        return fail('unexpected naive cache key')
    if naive['horizon'] != 50 or naive['signature_slots'] != 243 or naive['key_depth_slots'] != 12150:
        return fail('unexpected naive cache plan dimensions')

    planner_modes = receipt['planner_contract']['mode_rows']
    if [row['id'] for row in planner_modes] != list(EXPECTED_MODES.keys()):
        return fail('planner modes out of order')
    for row in planner_modes:
        expected = EXPECTED_MODES[row['id']]
        if row['recommended_key_fields'] != expected['recommended_key_fields']:
            return fail(f"{row['id']}: recommended key fields mismatch")
        if row['minimal_exact_horizon'] != expected['minimal_exact_horizon']:
            return fail(f"{row['id']}: horizon mismatch")
        if row['regime_count'] != expected['regime_count']:
            return fail(f"{row['id']}: regime count mismatch")
        if row['optimized_key_depth_slots'] <= 0 or row['key_depth_reduction_factor'] <= 1:
            return fail(f"{row['id']}: expected meaningful key-depth compression")

    classifier = receipt['zero_noise_classifier_contract']
    if classifier['ordered_rule_count'] != 17 or classifier['support_signature_count'] != 243:
        return fail('unexpected zero-noise classifier dimensions')
    if not approx(classifier['dispatch_surface_reduction_factor'], 243 / 17):
        return fail('dispatch surface reduction mismatch')

    retained = receipt['retained_artifacts']
    if [row['path'] for row in retained] != EXPECTED_RETAINED_PATHS:
        return fail('retained artifact paths mismatch')
    for row in retained:
        path = ROOT / row['path']
        if not path.exists():
            return fail(f"missing retained artifact {row['path']}")
        if row['bytes'] != path.stat().st_size:
            return fail(f"byte count drift for {row['path']}")
        if row['sha256'] != sha256(path):
            return fail(f"sha256 drift for {row['path']}")

    if receipt['archive_posture']['prefer_citation_over_recopy'] is not True:
        return fail('archive posture should prefer citation over recopy')
    if len(receipt['recommended_next_moves']) != 3:
        return fail('expected exactly three recommended next moves')

    print('rematch-world-canonicalization-bridge: ok (24 linked open items, 4 planner modes, 6 retained artifacts)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
