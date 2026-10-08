#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json'
PERSISTENCE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_persistence_snapshot_20260306.json'
DELTA_STEP = 0.00001


def fail(message: str) -> int:
    print(f'rematch-delta-persistence: {message}', file=sys.stderr)
    return 1


def approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def to_step(delta: float) -> int:
    return int(round(delta / DELTA_STEP))


def from_step(step: int) -> float:
    return round(step * DELTA_STEP, 5)


def width_from_steps(start_step: int, end_step: int) -> float:
    return round((end_step - start_step + 1) * DELTA_STEP, 5)


def max_buffer_steps(anchor_step: int, start_step: int, end_step: int) -> int:
    return min(anchor_step - start_step, end_step - anchor_step)


def discrete_center(start_step: int, end_step: int) -> tuple[int, int, int]:
    point_count = end_step - start_step + 1
    anchor = (start_step + end_step) // 2
    tie_count = 1 if point_count % 2 == 1 else 2
    return anchor, tie_count, max_buffer_steps(anchor, start_step, end_step)


def best_overlap(core_start_step: int, core_end_step: int, candidates: list[dict[str, object]]) -> dict[str, object] | None:
    overlaps = [
        cand for cand in candidates
        if int(cand['start_step']) <= core_end_step and int(cand['end_step']) >= core_start_step
    ]
    if not overlaps:
        return None
    return max(
        overlaps,
        key=lambda cand: (
            min(core_end_step, int(cand['end_step'])) - max(core_start_step, int(cand['start_step'])) + 1,
            -int(cand['start_step']),
        ),
    )


def load_topology() -> tuple[list[int], dict[int, list[dict[str, object]]], set[tuple[object, ...]]]:
    try:
        topology = json.loads(TOPOLOGY_PATH.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {TOPOLOGY_PATH.relative_to(ROOT)}: {exc}'))

    cap_to_rows: dict[int, list[dict[str, object]]] = {}
    root_keys: set[tuple[object, ...]] = set()
    for parent_row in topology['band_rows']:
        cap = int(parent_row['budget_cap_additional_paired_seeds'])
        bucket = cap_to_rows.setdefault(cap, [])
        for subband in parent_row['topology_subbands']:
            row = {
                'topology_code': str(subband['topology_code']),
                'counts': subband['counts'],
                'start_step': to_step(float(subband['start_delta'])),
                'end_step': to_step(float(subband['end_delta'])),
            }
            bucket.append(row)
            root_keys.add(
                (
                    cap,
                    float(parent_row['parent_band_start_delta']),
                    float(parent_row['parent_band_end_delta']),
                    float(subband['start_delta']),
                    float(subband['end_delta']),
                    str(subband['topology_code']),
                )
            )
    return sorted(cap_to_rows), cap_to_rows, root_keys


def main() -> int:
    if not TOPOLOGY_PATH.exists():
        return fail(f'missing {TOPOLOGY_PATH.relative_to(ROOT)}')
    if not PERSISTENCE_PATH.exists():
        return fail(f'missing {PERSISTENCE_PATH.relative_to(ROOT)}')

    caps, cap_to_rows, root_keys = load_topology()
    try:
        persistence = json.loads(PERSISTENCE_PATH.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f'invalid JSON in {PERSISTENCE_PATH.relative_to(ROOT)}: {exc}'))

    ladder_rows = persistence.get('ladder_rows')
    findings = persistence.get('headline_findings')
    if not isinstance(ladder_rows, list) or not ladder_rows:
        return fail('ladder_rows must be a non-empty list')
    if not isinstance(findings, dict):
        return fail('headline_findings must be an object')

    rooted_ladders = 0
    cover4 = 0
    cover4_non_single = 0
    cover4_single = 0
    focal_lookup = {}

    for row in ladder_rows:
        if not isinstance(row, dict):
            return fail('each ladder row must be an object')
        root_key = (
            int(row['root_budget_cap_additional_paired_seeds']),
            float(row['root_parent_band_start_delta']),
            float(row['root_parent_band_end_delta']),
            float(row['root_topology_subband_start_delta']),
            float(row['root_topology_subband_end_delta']),
            str(row['topology_code']),
        )
        if root_key not in root_keys:
            return fail(f'missing root topology subband for {root_key}')

        root_cap = int(row['root_budget_cap_additional_paired_seeds'])
        code = str(row['topology_code'])
        root_start_step = to_step(float(row['root_topology_subband_start_delta']))
        root_end_step = to_step(float(row['root_topology_subband_end_delta']))
        core_start_step = to_step(float(row['shared_core_start_delta']))
        core_end_step = to_step(float(row['shared_core_end_delta']))
        covered_caps = row.get('covered_budget_caps')
        if not isinstance(covered_caps, list) or not covered_caps:
            return fail('covered_budget_caps must be a non-empty list')
        if covered_caps != sorted(covered_caps):
            return fail(f'covered_budget_caps not sorted for root cap {root_cap}')
        if int(covered_caps[0]) != root_cap:
            return fail(f'covered_budget_caps must start with root cap {root_cap}')
        if core_start_step < root_start_step or core_end_step > root_end_step:
            return fail(f'shared core must be contained in root interval for root cap {root_cap}')

        i = caps.index(root_cap)
        expected_caps = [root_cap]
        running_start = root_start_step
        running_end = root_end_step
        for next_cap in caps[i + 1:]:
            same_code = [cand for cand in cap_to_rows[next_cap] if cand['topology_code'] == code]
            overlap = best_overlap(running_start, running_end, same_code)
            if overlap is None:
                break
            running_start = max(running_start, int(overlap['start_step']))
            running_end = min(running_end, int(overlap['end_step']))
            expected_caps.append(next_cap)

        if covered_caps != expected_caps:
            return fail(f'covered_budget_caps mismatch for root cap {root_cap}, code {code}')
        if core_start_step != running_start or core_end_step != running_end:
            return fail(f'shared core mismatch for root cap {root_cap}, code {code}')

        expected_width = width_from_steps(core_start_step, core_end_step)
        if not approx(float(row['shared_core_width']), expected_width):
            return fail(f'shared_core_width mismatch for root cap {root_cap}, code {code}')
        expected_points = core_end_step - core_start_step + 1
        if int(row['shared_core_gridpoint_count']) != expected_points:
            return fail(f'shared_core_gridpoint_count mismatch for root cap {root_cap}, code {code}')

        expected_anchor_step, expected_tie_count, expected_buffer_steps = discrete_center(core_start_step, core_end_step)
        if not approx(float(row['shared_core_anchor_delta']), from_step(expected_anchor_step)):
            return fail(f'shared_core_anchor_delta mismatch for root cap {root_cap}, code {code}')
        if int(row['shared_core_anchor_tie_count']) != expected_tie_count:
            return fail(f'shared_core_anchor_tie_count mismatch for root cap {root_cap}, code {code}')
        if not approx(float(row['shared_core_anchor_buffer_to_boundary']), round(expected_buffer_steps * DELTA_STEP, 5)):
            return fail(f'shared_core_anchor_buffer_to_boundary mismatch for root cap {root_cap}, code {code}')
        if bool(row['single_grid_point_shared_core']) != (expected_points == 1):
            return fail(f'single_grid_point_shared_core mismatch for root cap {root_cap}, code {code}')
        if bool(row['covers_all_larger_declared_caps']) != (int(covered_caps[-1]) == caps[-1]):
            return fail(f'covers_all_larger_declared_caps mismatch for root cap {root_cap}, code {code}')
        if int(row['covered_budget_cap_count']) != len(covered_caps):
            return fail(f'covered_budget_cap_count mismatch for root cap {root_cap}, code {code}')

        rooted_ladders += 1
        if len(covered_caps) >= 4:
            cover4 += 1
            if expected_points == 1:
                cover4_single += 1
            else:
                cover4_non_single += 1

        focal_lookup[(root_cap, code)] = max(
            focal_lookup.get((root_cap, code), row),
            row,
            key=lambda r: int(r['shared_core_gridpoint_count']),
        )

    if findings.get('rooted_ladder_count') != rooted_ladders:
        return fail('headline rooted_ladder_count mismatch')
    if findings.get('ladders_covering_at_least_four_caps_count') != cover4:
        return fail('headline ladders_covering_at_least_four_caps_count mismatch')
    if findings.get('non_single_point_ladders_covering_at_least_four_caps_count') != cover4_non_single:
        return fail('headline non_single_point_ladders_covering_at_least_four_caps_count mismatch')
    if findings.get('single_grid_point_ladders_covering_at_least_four_caps_count') != cover4_single:
        return fail('headline single_grid_point_ladders_covering_at_least_four_caps_count mismatch')

    for key, field in [
        ((10, 'TTTMMMMMU'), 'cap_10_low_delta_material_core'),
        ((10, 'TTTMMMMUU'), 'cap_10_low_delta_practical_tie_core'),
        ((10, 'TTTMMUMUU'), 'cap_10_single_grid_persistent_core'),
    ]:
        if findings.get(field) != focal_lookup.get(key):
            return fail(f'headline {field} mismatch')

    cap4_fragments = [
        row for row in ladder_rows
        if int(row['root_budget_cap_additional_paired_seeds']) == 4 and str(row['topology_code']) == 'TTTMMMMUU'
    ]
    expected_fragment_width = round(sum(float(row['shared_core_width']) for row in cap4_fragments), 5)
    if not approx(float(findings['cap_4_fragmented_practical_tie_code_total_shared_width']), expected_fragment_width):
        return fail('headline cap_4_fragmented_practical_tie_code_total_shared_width mismatch')

    cap10_tie = focal_lookup[(10, 'TTTMMMMUU')]
    if findings.get('cap_10_reconnected_practical_tie_core_width') != cap10_tie.get('shared_core_width'):
        return fail('headline cap_10_reconnected_practical_tie_core_width mismatch')
    expected_gain = round(float(cap10_tie['shared_core_width']) / expected_fragment_width, 3)
    if findings.get('cap_10_reconnected_width_gain_factor_vs_cap_4_fragments') != expected_gain:
        return fail('headline cap_10_reconnected_width_gain_factor_vs_cap_4_fragments mismatch')

    print(f'rematch-delta-persistence: ok ({rooted_ladders} ladders validated)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
