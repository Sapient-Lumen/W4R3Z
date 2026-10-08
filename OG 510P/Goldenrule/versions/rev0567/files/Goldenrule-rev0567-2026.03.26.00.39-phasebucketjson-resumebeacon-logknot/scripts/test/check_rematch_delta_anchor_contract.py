#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json'
ANCHOR_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_anchor_contract_snapshot_20260306.json'


def fail(msg: str) -> int:
    print(f'rematch-delta-anchor-contract: {msg}', file=sys.stderr)
    return 1


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {path.relative_to(ROOT)}: {exc}'))


def approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(a, b, abs_tol=tol, rel_tol=0.0)


def main() -> int:
    if not TOPOLOGY_PATH.exists():
        return fail(f'missing {TOPOLOGY_PATH.relative_to(ROOT)}')
    if not ANCHOR_PATH.exists():
        return fail(f'missing {ANCHOR_PATH.relative_to(ROOT)}')

    topology = load_json(TOPOLOGY_PATH)
    anchor = load_json(ANCHOR_PATH)
    if not isinstance(topology, dict) or not isinstance(anchor, dict):
        return fail('both reports must be JSON objects')

    topo_rows = topology.get('band_rows')
    anchor_rows = anchor.get('band_rows')
    findings = anchor.get('headline_findings')
    if not isinstance(topo_rows, list) or not topo_rows:
        return fail('topology band_rows must be non-empty list')
    if not isinstance(anchor_rows, list) or len(anchor_rows) != len(topo_rows):
        return fail('anchor band_rows must match topology band_rows count')
    if not isinstance(findings, dict):
        return fail('headline_findings must be object')

    topo_index = {
        (
            int(row['budget_cap_additional_paired_seeds']),
            float(row['parent_band_start_delta']),
            float(row['parent_band_end_delta']),
        ): row
        for row in topo_rows
    }

    improved = 0
    same_topology = 0
    same_counts = 0
    within_cap = 0
    same_exact = 0
    zero_buffer = 0
    non_improving = []

    for row in anchor_rows:
        if not isinstance(row, dict):
            return fail('each anchor row must be object')
        key = (
            int(row['budget_cap_additional_paired_seeds']),
            float(row['parent_band_start_delta']),
            float(row['parent_band_end_delta']),
        )
        source = topo_index.get(key)
        if not isinstance(source, dict):
            return fail(f'missing matching topology row for key {key}')

        parent_anchor = row.get('parent_anchor')
        stable_anchor = row.get('topology_preserving_anchor')
        if not isinstance(parent_anchor, dict) or not isinstance(stable_anchor, dict):
            return fail('anchor rows must contain parent_anchor and topology_preserving_anchor objects')

        parent_delta = float(parent_anchor['delta'])
        matching_subbands = [
            sub for sub in source['topology_subbands']
            if float(sub['start_delta']) - 1e-12 <= parent_delta <= float(sub['end_delta']) + 1e-12
            and str(sub['topology_code']) == str(source['parent_anchor_topology_code'])
        ]
        if not matching_subbands:
            return fail(f'no source topology subband contains parent anchor for key {key}')
        subband = matching_subbands[0]

        if parent_anchor.get('topology_code') != source.get('parent_anchor_topology_code'):
            return fail(f'parent topology mismatch for key {key}')
        if parent_anchor.get('counts') != source.get('parent_anchor_counts'):
            return fail(f'parent counts mismatch for key {key}')
        if not approx(float(parent_anchor['buffer_to_nearest_topology_boundary']), float(source['parent_anchor_buffer_to_nearest_topology_boundary'])):
            return fail(f'parent buffer mismatch for key {key}')
        if int(parent_anchor['total_additional_paired_seeds']) != int(source['parent_anchor_total_additional_paired_seeds']):
            return fail(f'parent additional-paired-seed mismatch for key {key}')

        if not approx(float(stable_anchor['delta']), float(subband['stability_anchor_delta'])):
            return fail(f'stable anchor delta mismatch for key {key}')
        if not approx(float(stable_anchor['topology_subband_start_delta']), float(subband['start_delta'])):
            return fail(f'stable anchor start mismatch for key {key}')
        if not approx(float(stable_anchor['topology_subband_end_delta']), float(subband['end_delta'])):
            return fail(f'stable anchor end mismatch for key {key}')
        if not approx(float(stable_anchor['topology_subband_width']), float(subband['width'])):
            return fail(f'stable anchor width mismatch for key {key}')
        if stable_anchor.get('topology_code') != subband.get('topology_code'):
            return fail(f'stable anchor topology mismatch for key {key}')
        if stable_anchor.get('counts') != subband.get('counts'):
            return fail(f'stable anchor counts mismatch for key {key}')
        if not approx(float(stable_anchor['buffer_to_nearest_topology_boundary']), float(subband['stability_anchor_buffer_to_nearest_topology_boundary'])):
            return fail(f'stable anchor buffer mismatch for key {key}')
        if int(stable_anchor['total_additional_paired_seeds']) != int(subband['stability_anchor_total_additional_paired_seeds']):
            return fail(f'stable anchor additional-paired-seed mismatch for key {key}')

        expected_gain = float(subband['stability_anchor_buffer_to_nearest_topology_boundary']) - float(source['parent_anchor_buffer_to_nearest_topology_boundary'])
        if not approx(float(stable_anchor['buffer_gain_vs_parent']), expected_gain, tol=1e-6):
            return fail(f'buffer gain mismatch for key {key}')

        expected_same_topology = str(subband['topology_code']) == str(source['parent_anchor_topology_code'])
        expected_same_counts = subband['counts'] == source['parent_anchor_counts']
        expected_same_exact = int(subband['stability_anchor_total_additional_paired_seeds']) == int(source['parent_anchor_total_additional_paired_seeds'])
        expected_within_cap = int(subband['stability_anchor_total_additional_paired_seeds']) <= int(source['budget_cap_additional_paired_seeds'])

        if bool(stable_anchor['same_topology_as_parent']) != expected_same_topology:
            return fail(f'same_topology_as_parent mismatch for key {key}')
        if bool(stable_anchor['same_counts_as_parent']) != expected_same_counts:
            return fail(f'same_counts_as_parent mismatch for key {key}')
        if bool(stable_anchor['same_exact_additional_paired_seeds_as_parent']) != expected_same_exact:
            return fail(f'same_exact_additional_paired_seeds_as_parent mismatch for key {key}')
        if bool(stable_anchor['stays_within_budget_cap']) != expected_within_cap:
            return fail(f'stays_within_budget_cap mismatch for key {key}')

        if float(parent_anchor['buffer_to_nearest_topology_boundary']) == 0.0:
            zero_buffer += 1
        if float(stable_anchor['buffer_gain_vs_parent']) > 0:
            improved += 1
        else:
            non_improving.append(
                {
                    'budget_cap_additional_paired_seeds': key[0],
                    'parent_band_start_delta': key[1],
                    'parent_band_end_delta': key[2],
                    'parent_anchor_delta': parent_delta,
                }
            )
        same_topology += int(expected_same_topology)
        same_counts += int(expected_same_counts)
        same_exact += int(expected_same_exact)
        within_cap += int(expected_within_cap)

    if findings.get('parent_band_count') != len(anchor_rows):
        return fail('headline parent_band_count mismatch')
    if findings.get('fragmented_parent_band_count') != sum(1 for row in anchor_rows if row.get('fragmented_parent_band')):
        return fail('headline fragmented_parent_band_count mismatch')
    if findings.get('parent_anchor_zero_topology_buffer_count') != zero_buffer:
        return fail('headline parent_anchor_zero_topology_buffer_count mismatch')
    if findings.get('topology_preserving_anchor_improves_buffer_count') != improved:
        return fail('headline topology_preserving_anchor_improves_buffer_count mismatch')
    if findings.get('topology_preserving_anchor_same_topology_count') != same_topology:
        return fail('headline topology_preserving_anchor_same_topology_count mismatch')
    if findings.get('topology_preserving_anchor_same_counts_count') != same_counts:
        return fail('headline topology_preserving_anchor_same_counts_count mismatch')
    if findings.get('topology_preserving_anchor_within_budget_cap_count') != within_cap:
        return fail('headline topology_preserving_anchor_within_budget_cap_count mismatch')
    if findings.get('topology_preserving_anchor_same_exact_additional_seed_count') != same_exact:
        return fail('headline topology_preserving_anchor_same_exact_additional_seed_count mismatch')
    if findings.get('only_non_improving_band') != (non_improving[0] if non_improving else None):
        return fail('headline only_non_improving_band mismatch')

    print(f'rematch-delta-anchor-contract: ok ({len(anchor_rows)} bands validated)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
