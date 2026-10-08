#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_plan_snapshot_20260306.json'
SCHEMA_PATH = ROOT / 'schemas' / 'canonicalization_plan.schema.json'
EXPECTED_SUPPORT_SIGNATURE_COUNT = 243
EXPECTED_MODE_IDS = ['none', 'opponent_tremble', 'focal_tremble', 'bilateral_tremble']


def fail(msg: str) -> int:
    print(f'cache-plan-contract: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def approx(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)


def main() -> int:
    if not SCHEMA_PATH.exists():
        return fail(f'missing {SCHEMA_PATH.relative_to(ROOT)}')
    if not REPORT_PATH.exists():
        return fail(f'missing {REPORT_PATH.relative_to(ROOT)}')

    schema = load_json(SCHEMA_PATH)
    if not isinstance(schema, dict) or schema.get('title') != 'Canonicalization Plan Manifest':
        return fail('schema title mismatch for canonicalization plan manifest')

    obj = load_json(REPORT_PATH)
    if not isinstance(obj, dict):
        return fail('report root must be object')

    world = obj.get('world')
    mode_rows = obj.get('mode_rows')
    summary = obj.get('summary')
    if not isinstance(world, dict):
        return fail('world must be object')
    if not isinstance(mode_rows, list) or not mode_rows:
        return fail('mode_rows must be non-empty list')
    if not isinstance(summary, dict):
        return fail('summary must be object')

    if world.get('kind') != 'rematch_proxy_cache_plan':
        return fail(f"unexpected world.kind: {world.get('kind')}")
    if world.get('support_signature_count') != EXPECTED_SUPPORT_SIGNATURE_COUNT:
        return fail('unexpected support_signature_count')

    naive = world.get('naive_cache_plan')
    if not isinstance(naive, dict):
        return fail('world.naive_cache_plan must be object')
    naive_horizon = naive.get('horizon')
    naive_signature_slots = naive.get('signature_slots')
    naive_key_depth_slots = naive.get('key_depth_slots')
    if naive_signature_slots != EXPECTED_SUPPORT_SIGNATURE_COUNT:
        return fail('naive signature slot count must match support signature count')
    if naive_key_depth_slots != naive_signature_slots * naive_horizon:
        return fail('naive key depth slots must equal signature_slots * horizon')

    if [row.get('id') for row in mode_rows] != EXPECTED_MODE_IDS:
        return fail('mode_rows must appear in expected stable order')

    summary_regime_counts = summary.get('regime_count_by_mode')
    summary_horizons = summary.get('minimal_exact_horizon_by_mode')
    summary_slots = summary.get('optimized_key_depth_slots_by_mode')
    summary_reduction = summary.get('key_depth_reduction_factor_by_mode')
    if not all(isinstance(x, dict) for x in [summary_regime_counts, summary_horizons, summary_slots, summary_reduction]):
        return fail('summary maps missing or malformed')

    reduction_factors: list[float] = []
    for row in mode_rows:
        if not isinstance(row, dict):
            return fail('each mode row must be object')
        mode_id = row['id']
        regime_rows = row.get('regime_rows')
        signature_to_regime = row.get('signature_to_regime')
        if not isinstance(regime_rows, list) or not regime_rows:
            return fail(f'{mode_id}: regime_rows must be non-empty list')
        if not isinstance(signature_to_regime, dict):
            return fail(f'{mode_id}: signature_to_regime must be object')
        if len(signature_to_regime) != EXPECTED_SUPPORT_SIGNATURE_COUNT:
            return fail(f'{mode_id}: signature_to_regime must cover all support signatures')

        regime_ids = []
        signature_count_total = 0
        initial_d_flags = set()
        initial_c_only_flags = set()
        for regime in regime_rows:
            if not isinstance(regime, dict):
                return fail(f'{mode_id}: regime row must be object')
            regime_id = regime.get('regime_id')
            regime_ids.append(regime_id)
            signature_count_total += int(regime.get('signature_count', 0))
            contains_initial_d_support = bool(regime.get('contains_initial_d_support'))
            all_initial_c_only = bool(regime.get('all_initial_c_only'))
            if contains_initial_d_support and all_initial_c_only:
                return fail(f'{mode_id}: regime cannot both contain initial-D support and be all-initial-C-only')
            initial_d_flags.add(contains_initial_d_support)
            initial_c_only_flags.add(all_initial_c_only)

        if len(set(regime_ids)) != len(regime_ids):
            return fail(f'{mode_id}: duplicate regime ids')
        if signature_count_total != EXPECTED_SUPPORT_SIGNATURE_COUNT:
            return fail(f'{mode_id}: regime_rows signature counts must sum to 243')
        if set(signature_to_regime.values()) != set(regime_ids):
            return fail(f'{mode_id}: signature_to_regime values must match regime_ids exactly')
        if row.get('regime_count') != len(regime_rows):
            return fail(f'{mode_id}: regime_count mismatch')
        if summary_regime_counts.get(mode_id) != row.get('regime_count'):
            return fail(f'{mode_id}: summary regime count mismatch')
        if summary_horizons.get(mode_id) != row.get('minimal_exact_horizon'):
            return fail(f'{mode_id}: summary horizon mismatch')
        if summary_slots.get(mode_id) != row.get('optimized_key_depth_slots'):
            return fail(f'{mode_id}: summary optimized key depth mismatch')

        optimized_signature_slots = row.get('optimized_signature_slots')
        minimal_exact_horizon = row.get('minimal_exact_horizon')
        optimized_key_depth_slots = row.get('optimized_key_depth_slots')
        if optimized_key_depth_slots != optimized_signature_slots * minimal_exact_horizon:
            return fail(f'{mode_id}: optimized_key_depth_slots must equal optimized_signature_slots * minimal_exact_horizon')

        signature_slot_reduction_factor = row.get('signature_slot_reduction_factor')
        if not approx(signature_slot_reduction_factor, naive_signature_slots / optimized_signature_slots):
            return fail(f'{mode_id}: signature slot reduction factor mismatch')

        key_depth_reduction_factor = row.get('key_depth_reduction_factor')
        if not approx(key_depth_reduction_factor, naive_key_depth_slots / optimized_key_depth_slots):
            return fail(f'{mode_id}: key depth reduction factor mismatch')
        if not approx(summary_reduction.get(mode_id), key_depth_reduction_factor):
            return fail(f'{mode_id}: summary reduction factor mismatch')
        reduction_factors.append(float(key_depth_reduction_factor))

        key_fields = row.get('recommended_key_fields')
        planner_kind = row.get('planner_kind')
        if mode_id == 'none':
            if planner_kind != 'lookup-table':
                return fail('none: expected lookup-table planner')
            if key_fields != ['noise_mode', 'support_regime_id']:
                return fail('none: unexpected recommended_key_fields')
            if row.get('regime_count') != 17:
                return fail('none: expected 17 regimes in current proxy')
        elif mode_id == 'opponent_tremble':
            if planner_kind != 'single-bucket' or key_fields != ['noise_mode']:
                return fail('opponent_tremble: expected single-bucket keyed only by noise_mode')
            if row.get('regime_count') != 1:
                return fail('opponent_tremble: expected one regime')
        elif mode_id == 'focal_tremble':
            if planner_kind != 'boolean-gate' or key_fields != ['noise_mode', 'entrant_initial_support_includes_D']:
                return fail('focal_tremble: expected boolean-gate keyed by initial-D support')
            if row.get('regime_count') != 2:
                return fail('focal_tremble: expected two regimes')
            if initial_d_flags != {False, True}:
                return fail('focal_tremble: expected both initial-D flag values across regimes')
        elif mode_id == 'bilateral_tremble':
            if planner_kind != 'single-bucket' or key_fields != ['noise_mode']:
                return fail('bilateral_tremble: expected single-bucket keyed only by noise_mode')
            if row.get('regime_count') != 1:
                return fail('bilateral_tremble: expected one regime')

    if not approx(summary.get('largest_reduction_factor'), max(reduction_factors)):
        return fail('summary largest_reduction_factor mismatch')
    if not approx(summary.get('smallest_reduction_factor'), min(reduction_factors)):
        return fail('summary smallest_reduction_factor mismatch')

    print(f'cache-plan-contract: ok ({len(mode_rows)} modes, {EXPECTED_SUPPORT_SIGNATURE_COUNT} signatures)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
