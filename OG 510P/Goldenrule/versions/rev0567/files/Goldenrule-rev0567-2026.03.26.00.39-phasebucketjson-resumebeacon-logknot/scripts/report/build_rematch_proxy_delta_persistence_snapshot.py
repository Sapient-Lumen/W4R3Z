#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_persistence_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_persistence_snapshot_20260306.md'
DELTA_STEP = 0.00001


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _to_step(delta: float) -> int:
    return int(round(delta / DELTA_STEP))


def _from_step(step: int) -> float:
    return round(step * DELTA_STEP, 5)


def _width_from_steps(start_step: int, end_step: int) -> float:
    return round((end_step - start_step + 1) * DELTA_STEP, 5)


def _max_buffer_steps(anchor_step: int, start_step: int, end_step: int) -> int:
    return min(anchor_step - start_step, end_step - anchor_step)


def _discrete_center(start_step: int, end_step: int) -> tuple[int, int, int]:
    point_count = end_step - start_step + 1
    if point_count % 2 == 1:
        anchor = (start_step + end_step) // 2
        tie_count = 1
    else:
        anchor = (start_step + end_step) // 2
        tie_count = 2
    return anchor, tie_count, _max_buffer_steps(anchor, start_step, end_step)


def _load_topology_rows() -> tuple[list[int], dict[int, list[dict[str, object]]]]:
    data = json.loads(TOPOLOGY_PATH.read_text(encoding='utf-8'))
    cap_to_rows: dict[int, list[dict[str, object]]] = {}
    for parent_row in data['band_rows']:
        cap = int(parent_row['budget_cap_additional_paired_seeds'])
        bucket = cap_to_rows.setdefault(cap, [])
        for subband in parent_row['topology_subbands']:
            bucket.append(
                {
                    'budget_cap_additional_paired_seeds': cap,
                    'parent_band_start_delta': float(parent_row['parent_band_start_delta']),
                    'parent_band_end_delta': float(parent_row['parent_band_end_delta']),
                    'root_topology_subband_start_delta': float(subband['start_delta']),
                    'root_topology_subband_end_delta': float(subband['end_delta']),
                    'root_topology_subband_width': float(subband['width']),
                    'topology_code': str(subband['topology_code']),
                    'counts': subband['counts'],
                    'root_start_step': _to_step(float(subband['start_delta'])),
                    'root_end_step': _to_step(float(subband['end_delta'])),
                }
            )
    return sorted(cap_to_rows), cap_to_rows


def _best_overlap(core_start_step: int, core_end_step: int, candidates: list[dict[str, object]]) -> dict[str, object] | None:
    overlaps = [
        cand for cand in candidates
        if int(cand['root_start_step']) <= core_end_step and int(cand['root_end_step']) >= core_start_step
    ]
    if not overlaps:
        return None
    return max(
        overlaps,
        key=lambda cand: (
            min(core_end_step, int(cand['root_end_step'])) - max(core_start_step, int(cand['root_start_step'])) + 1,
            -int(cand['root_start_step']),
        ),
    )


def _build_rows() -> list[dict[str, object]]:
    caps, cap_to_rows = _load_topology_rows()
    ladder_rows: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()

    for i, root_cap in enumerate(caps):
        for root in cap_to_rows[root_cap]:
            topology_code = str(root['topology_code'])
            core_start_step = int(root['root_start_step'])
            core_end_step = int(root['root_end_step'])
            covered_caps = [root_cap]

            for next_cap in caps[i + 1:]:
                same_code_rows = [row for row in cap_to_rows[next_cap] if str(row['topology_code']) == topology_code]
                overlap = _best_overlap(core_start_step, core_end_step, same_code_rows)
                if overlap is None:
                    break
                core_start_step = max(core_start_step, int(overlap['root_start_step']))
                core_end_step = min(core_end_step, int(overlap['root_end_step']))
                covered_caps.append(next_cap)

            key = (root_cap, topology_code, core_start_step, core_end_step, tuple(covered_caps))
            if key in seen:
                continue
            seen.add(key)

            anchor_step, anchor_tie_count, anchor_buffer_steps = _discrete_center(core_start_step, core_end_step)
            point_count = core_end_step - core_start_step + 1
            ladder_rows.append(
                {
                    'root_budget_cap_additional_paired_seeds': root_cap,
                    'root_parent_band_start_delta': float(root['parent_band_start_delta']),
                    'root_parent_band_end_delta': float(root['parent_band_end_delta']),
                    'root_topology_subband_start_delta': float(root['root_topology_subband_start_delta']),
                    'root_topology_subband_end_delta': float(root['root_topology_subband_end_delta']),
                    'root_topology_subband_width': float(root['root_topology_subband_width']),
                    'topology_code': topology_code,
                    'counts': root['counts'],
                    'covered_budget_caps': covered_caps,
                    'covered_budget_cap_count': len(covered_caps),
                    'shared_core_start_delta': _from_step(core_start_step),
                    'shared_core_end_delta': _from_step(core_end_step),
                    'shared_core_width': _width_from_steps(core_start_step, core_end_step),
                    'shared_core_gridpoint_count': point_count,
                    'shared_core_anchor_delta': _from_step(anchor_step),
                    'shared_core_anchor_tie_count': anchor_tie_count,
                    'shared_core_anchor_buffer_to_boundary': round(anchor_buffer_steps * DELTA_STEP, 5),
                    'single_grid_point_shared_core': point_count == 1,
                    'covers_all_larger_declared_caps': covered_caps[-1] == caps[-1],
                }
            )

    ladder_rows.sort(
        key=lambda row: (
            -int(row['covered_budget_cap_count']),
            -int(row['shared_core_gridpoint_count']),
            int(row['root_budget_cap_additional_paired_seeds']),
            float(row['shared_core_start_delta']),
            str(row['topology_code']),
        )
    )
    return ladder_rows


def _pick_focal(rows: list[dict[str, object]], root_cap: int, code: str) -> dict[str, object]:
    matches = [
        row for row in rows
        if int(row['root_budget_cap_additional_paired_seeds']) == root_cap and str(row['topology_code']) == code
    ]
    if not matches:
        raise SystemExit(f'missing focal persistence row for cap={root_cap} code={code}')
    return max(matches, key=lambda row: int(row['shared_core_gridpoint_count']))


def _build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    cap10_low_material = _pick_focal(rows, 10, 'TTTMMMMMU')
    cap10_low_tie = _pick_focal(rows, 10, 'TTTMMMMUU')
    cap10_single = _pick_focal(rows, 10, 'TTTMMUMUU')
    cap4_fragments = [
        row for row in rows
        if int(row['root_budget_cap_additional_paired_seeds']) == 4 and str(row['topology_code']) == 'TTTMMMMUU'
    ]
    fragment_width = round(sum(float(row['shared_core_width']) for row in cap4_fragments), 5)

    return {
        'focus': 'Expose cross-cap persistent delta cores whose rematch label topology survives increasing extra-budget caps, so published anchors remain scientifically stable when the certification budget is revised.',
        'headline_findings': {
            'rooted_ladder_count': len(rows),
            'ladders_covering_at_least_four_caps_count': sum(1 for row in rows if int(row['covered_budget_cap_count']) >= 4),
            'non_single_point_ladders_covering_at_least_four_caps_count': sum(
                1 for row in rows
                if int(row['covered_budget_cap_count']) >= 4 and not bool(row['single_grid_point_shared_core'])
            ),
            'single_grid_point_ladders_covering_at_least_four_caps_count': sum(
                1 for row in rows
                if int(row['covered_budget_cap_count']) >= 4 and bool(row['single_grid_point_shared_core'])
            ),
            'cap_10_low_delta_material_core': cap10_low_material,
            'cap_10_low_delta_practical_tie_core': cap10_low_tie,
            'cap_10_single_grid_persistent_core': cap10_single,
            'cap_4_fragmented_practical_tie_code_total_shared_width': fragment_width,
            'cap_10_reconnected_practical_tie_core_width': float(cap10_low_tie['shared_core_width']),
            'cap_10_reconnected_width_gain_factor_vs_cap_4_fragments': round(float(cap10_low_tie['shared_core_width']) / fragment_width, 3),
            'interpretation': 'The right rematch delta anchor should survive a family of nearby extra-budget caps, not just one cap-specific band. But persistence alone is insufficient: at least one topology survives from cap 10 upward only as a single grid point, so reports also need a minimum shared-core width rule and an exact discrete-center anchor contract.',
        },
        'ladder_rows': rows,
        'method_note': 'Started from the topology-stable admissible subbands. Treated each subband as a root, then walked upward across larger declared budget caps while the same topology code still overlapped. The persistent core is the exact intersection of those overlapping intervals on the 0.00001 delta grid. To avoid midpoint-rounding artifacts, the published anchor is the lower discrete center gridpoint that maximizes shared-core boundary buffer, with an anchor tie count when the core has an even number of grid points.',
        'source_report': 'artifacts/reports/rematch_proxy_delta_topology_snapshot_20260306.json',
        'source_script': 'scripts/report/build_rematch_proxy_delta_persistence_snapshot.py',
    }


def _write_markdown(summary: dict[str, object]) -> None:
    findings = summary['headline_findings']
    material = findings['cap_10_low_delta_material_core']
    tie = findings['cap_10_low_delta_practical_tie_core']
    point = findings['cap_10_single_grid_persistent_core']

    lines = [
        '# Rematch-Proxy Delta Persistence Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded topology-stable admissible subbands from `artifacts/reports/rematch_proxy_delta_topology_snapshot_20260306.json`',
        '- treated each topology-stable subband as a root and walked upward through larger declared extra-budget caps while the same topology still overlapped',
        '- intersected those overlaps exactly on the `0.00001` delta grid to get a cap-persistent shared core',
        '- replaced rounded arithmetic midpoints with an exact discrete-center anchor rule (lower maximizing gridpoint, plus an anchor tie count for even-width cores)',
        '',
        'Headline findings:',
        f"- there are `{findings['rooted_ladder_count']}` rooted persistence ladders; `{findings['ladders_covering_at_least_four_caps_count']}` survive across at least four declared caps, but one of those survivors is only a single-grid-point knife-edge.",
        f"- the cap-10 low-delta material-core ladder (`{material['topology_code']}`) survives unchanged through caps `{', '.join(map(str, material['covered_budget_caps']))}` on shared core `{float(material['shared_core_start_delta']):.5f}..{float(material['shared_core_end_delta']):.5f}` with discrete-center anchor `{float(material['shared_core_anchor_delta']):.5f}`.",
        f"- the cap-10 low-delta practical-tie ladder (`{tie['topology_code']}`) likewise survives through caps `{', '.join(map(str, tie['covered_budget_caps']))}` on shared core `{float(tie['shared_core_start_delta']):.5f}..{float(tie['shared_core_end_delta']):.5f}` with two co-optimal center anchors and published lower anchor `{float(tie['shared_core_anchor_delta']):.5f}`.",
        f"- the same practical-tie code is fragmented into three cap-4 islands with total persistent width `{findings['cap_4_fragmented_practical_tie_code_total_shared_width']:.5f}`, but reconnects into one cap-10 persistent core of width `{findings['cap_10_reconnected_practical_tie_core_width']:.5f}` (`{findings['cap_10_reconnected_width_gain_factor_vs_cap_4_fragments']:.3f}x` wider).",
        f"- caution: the topology `{point['topology_code']}` persists from cap 10 upward only at `{float(point['shared_core_start_delta']):.5f}`, so raw persistence without a width floor would still publish a knife-edge anchor.",
        '',
        'Implementor consequence:',
        '- Choose rematch delta anchors from a declared budget family (for example, the cap range a benchmark owner is genuinely willing to fund), not from one isolated budget cap.',
        '- Require both cross-cap persistence and a minimum shared-core width before elevating a scalar delta anchor into a public benchmark constant.',
        '- When a persistent core has an even number of grid points, publish the discrete-center contract instead of a rounded arithmetic midpoint so later re-runs do not create fake off-grid or half-step anchors.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    rows = _build_rows()
    summary = _build_summary(rows)
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
