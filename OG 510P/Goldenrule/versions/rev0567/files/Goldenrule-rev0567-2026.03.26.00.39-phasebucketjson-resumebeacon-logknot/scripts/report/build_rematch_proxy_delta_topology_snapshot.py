#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_WINNER = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
SRC_ADMISS = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_admissibility_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_topology_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
DELTA_STEP = 0.00001


PANEL_ORDER = [
    (20, 0),
    (20, 1),
    (20, 2),
    (50, 0),
    (50, 1),
    (50, 2),
    (80, 0),
    (80, 1),
    (80, 2),
]


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _panel_bounds(row: dict[str, object]) -> tuple[float, float]:
    mean_gap = float(row['leader_margin'])
    se_gap = float(row['paired_margin_se'])
    return mean_gap - T_CRIT_90_DF5 * se_gap, mean_gap + T_CRIT_90_DF5 * se_gap


def _class(row: dict[str, object], delta: float) -> str:
    ci_low_90, ci_high_90 = _panel_bounds(row)
    if ci_low_90 > delta:
        return 'material_leader'
    if ci_low_90 > -delta and ci_high_90 < delta:
        return 'practical_tie'
    return 'undecided'


def _required_total_paired_seeds_to_close(row: dict[str, object], delta: float) -> float:
    if _class(row, delta) != 'undecided':
        return 0.0
    mean_gap = float(row['leader_margin'])
    sd_gap = float(row['paired_margin_sd'])
    if abs(mean_gap - delta) < 5e-12:
        return math.inf
    required_total = max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / abs(mean_gap - delta)) ** 2))
    return float(required_total - int(row['paired_seed_count']))


def _total_additional(rows: list[dict[str, object]], delta: float) -> int | None:
    total = 0.0
    for row in rows:
        need = _required_total_paired_seeds_to_close(row, delta)
        if math.isinf(need):
            return None
        total += need
    return int(total)


def _fingerprint(rows: list[dict[str, object]], delta: float) -> tuple[str, dict[str, int], list[dict[str, object]]]:
    states = []
    counts = {'material_leader': 0, 'practical_tie': 0, 'undecided': 0}
    panel_states = []
    lookup = {(int(r['extortion']), int(r['delay'])): r for r in rows}
    short = {'material_leader': 'M', 'practical_tie': 'T', 'undecided': 'U'}
    for ext, delay in PANEL_ORDER:
        row = lookup[(ext, delay)]
        cls = _class(row, delta)
        counts[cls] += 1
        states.append(short[cls])
        panel_states.append({'extortion': ext, 'delay': delay, 'state': cls})
    return ''.join(states), counts, panel_states


def _buffer(anchor: float, start: float, end: float) -> float:
    return min(anchor - start, end - anchor)


def _topology_rows_for_band(rows: list[dict[str, object]], band: dict[str, object]) -> list[dict[str, object]]:
    start = float(band['start_delta'])
    end = float(band['end_delta'])
    steps = int(round((end - start) / DELTA_STEP))
    deltas = [round(start + i * DELTA_STEP, 5) for i in range(steps + 1)]
    segments: list[dict[str, object]] = []
    cur_fp = None
    cur_counts = None
    cur_states = None
    seg_start = None
    prev = None
    for delta in deltas:
        fp, counts, panel_states = _fingerprint(rows, delta)
        if cur_fp is None:
            cur_fp = fp
            cur_counts = counts
            cur_states = panel_states
            seg_start = delta
            prev = delta
            continue
        if fp != cur_fp:
            assert seg_start is not None and prev is not None and cur_counts is not None and cur_states is not None
            width = prev - seg_start + DELTA_STEP
            midpoint = round((seg_start + prev) / 2.0, 5)
            segments.append(
                {
                    'start_delta': seg_start,
                    'end_delta': prev,
                    'width': width,
                    'topology_code': cur_fp,
                    'counts': cur_counts,
                    'panel_states': cur_states,
                    'stability_anchor_delta': midpoint,
                    'stability_anchor_total_additional_paired_seeds': _total_additional(rows, midpoint),
                    'stability_anchor_buffer_to_nearest_topology_boundary': _buffer(midpoint, seg_start, prev),
                    'is_single_grid_point': seg_start == prev,
                }
            )
            cur_fp = fp
            cur_counts = counts
            cur_states = panel_states
            seg_start = delta
        prev = delta
    assert seg_start is not None and prev is not None and cur_counts is not None and cur_states is not None and cur_fp is not None
    width = prev - seg_start + DELTA_STEP
    midpoint = round((seg_start + prev) / 2.0, 5)
    segments.append(
        {
            'start_delta': seg_start,
            'end_delta': prev,
            'width': width,
            'topology_code': cur_fp,
            'counts': cur_counts,
            'panel_states': cur_states,
            'stability_anchor_delta': midpoint,
            'stability_anchor_total_additional_paired_seeds': _total_additional(rows, midpoint),
            'stability_anchor_buffer_to_nearest_topology_boundary': _buffer(midpoint, seg_start, prev),
            'is_single_grid_point': seg_start == prev,
        }
    )
    return segments


def _band_rows(rows: list[dict[str, object]], admissibility: dict[str, object]) -> list[dict[str, object]]:
    out = []
    for cap_row in admissibility['budget_cap_rows']:
        cap = int(cap_row['budget_cap_additional_paired_seeds'])
        for band in cap_row['bands']:
            parent_anchor = float(band['anchor_delta'])
            parent_fp, parent_counts, _ = _fingerprint(rows, parent_anchor)
            topology_subbands = _topology_rows_for_band(rows, band)
            widest = max(topology_subbands, key=lambda r: (float(r['width']), -float(r['start_delta'])))
            out.append(
                {
                    'budget_cap_additional_paired_seeds': cap,
                    'parent_band_start_delta': float(band['start_delta']),
                    'parent_band_end_delta': float(band['end_delta']),
                    'parent_band_width': float(band['width']),
                    'parent_anchor_delta': parent_anchor,
                    'parent_anchor_total_additional_paired_seeds': int(band['anchor_total_additional_paired_seeds']),
                    'parent_anchor_topology_code': parent_fp,
                    'parent_anchor_counts': parent_counts,
                    'parent_anchor_buffer_to_nearest_topology_boundary': _buffer(parent_anchor, float(next(s['start_delta'] for s in topology_subbands if float(s['start_delta']) <= parent_anchor <= float(s['end_delta']))), float(next(s['end_delta'] for s in topology_subbands if float(s['start_delta']) <= parent_anchor <= float(s['end_delta'])))),
                    'topology_subband_count': len(topology_subbands),
                    'contains_single_point_knife_edge': any(bool(s['is_single_grid_point']) for s in topology_subbands),
                    'widest_topology_subband': widest,
                    'topology_subbands': topology_subbands,
                }
            )
    return out


def _write_markdown(summary: dict[str, object]) -> None:
    focal = summary['headline_findings']['cap_10_lower_band']
    lines = [
        '# Rematch-Proxy Delta-Topology Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- loaded panel-level top-gap means/uncertainty from `{summary['source_reports'][0]}` and admissible delta bands from `{summary['source_reports'][1]}`",
        '- reused the same 90% material-leader / practical-tie / undecided rule as the earlier rematch materiality passes',
        '- intersected each admissible delta band with full 9-panel classification topology, yielding maximal contiguous subbands where every panel label stayed fixed',
        '- for each topology-stable subband, computed a stability anchor at the midpoint and its distance to the nearest topology boundary',
        '',
        'Headline findings:',
        f"- across the tested caps, `{summary['headline_findings']['fragmented_parent_band_count']}` of `{summary['headline_findings']['total_parent_bands']}` admissible parent bands fragment into more than one closure topology",
        f"- the cap-10 low-delta admissible band `{float(focal['parent_band_start_delta']):.5f}..{float(focal['parent_band_end_delta']):.5f}` splits into `{int(focal['topology_subband_count'])}` topology-stable subbands",
        f"- its widest stable core is `{float(focal['widest_topology_subband']['start_delta']):.5f}..{float(focal['widest_topology_subband']['end_delta']):.5f}` with stability anchor `{float(focal['widest_topology_subband']['stability_anchor_delta']):.5f}`",
        f"- the inherited min-cost anchor `{float(focal['parent_anchor_delta']):.5f}` sits only `{float(focal['parent_anchor_buffer_to_nearest_topology_boundary']):.5f}` from a topology boundary, while the stability anchor has `{float(focal['widest_topology_subband']['stability_anchor_buffer_to_nearest_topology_boundary']):.5f}` buffer",
        f"- that is a `{float(focal['buffer_gain_factor_vs_parent_anchor']):.3f}x` larger topology buffer with the same or lower closure cost status still inside the declared cap",
        '',
        'Implementor consequence:',
        '- budget-admissible delta bands are still too coarse when they contain multiple distinct closure topologies',
        '- rematch benchmark artifacts should therefore publish topology-stable subbands or a stability-first anchor, not only one min-cost anchor per admissible parent band',
        '- otherwise a future inheritor can stay inside the “same” admissible delta band while silently changing which panels are material leaders, practical ties, or still undecided',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    winner = json.loads(SRC_WINNER.read_text(encoding='utf-8'))
    admissibility = json.loads(SRC_ADMISS.read_text(encoding='utf-8'))
    rows = sorted(winner['panel_rows'], key=lambda r: (int(r['extortion']), int(r['delay'])))
    band_rows = _band_rows(rows, admissibility)
    total_parent_bands = len(band_rows)
    fragmented = [r for r in band_rows if int(r['topology_subband_count']) > 1]
    knife_edges = sum(1 for r in band_rows for s in r['topology_subbands'] if bool(s['is_single_grid_point']))
    cap10_lower = next(
        r
        for r in band_rows
        if int(r['budget_cap_additional_paired_seeds']) == 10 and float(r['parent_band_end_delta']) <= 0.01 + 1e-12
    )
    widest = cap10_lower['widest_topology_subband']
    summary = {
        'focus': 'Expose topology-stable delta subbands inside budget-admissible rematch margins so anchor choices do not sit on hidden panel-label boundaries.',
        'headline_findings': {
            'tested_panels': len(rows),
            'total_parent_bands': total_parent_bands,
            'fragmented_parent_band_count': len(fragmented),
            'single_grid_point_knife_edge_subband_count': knife_edges,
            'cap_10_lower_band': {
                'parent_band_start_delta': float(cap10_lower['parent_band_start_delta']),
                'parent_band_end_delta': float(cap10_lower['parent_band_end_delta']),
                'parent_band_width': float(cap10_lower['parent_band_width']),
                'parent_anchor_delta': float(cap10_lower['parent_anchor_delta']),
                'parent_anchor_total_additional_paired_seeds': int(cap10_lower['parent_anchor_total_additional_paired_seeds']),
                'parent_anchor_topology_code': cap10_lower['parent_anchor_topology_code'],
                'parent_anchor_counts': cap10_lower['parent_anchor_counts'],
                'parent_anchor_buffer_to_nearest_topology_boundary': float(cap10_lower['parent_anchor_buffer_to_nearest_topology_boundary']),
                'topology_subband_count': int(cap10_lower['topology_subband_count']),
                'contains_single_point_knife_edge': bool(cap10_lower['contains_single_point_knife_edge']),
                'widest_topology_subband': widest,
                'buffer_gain_factor_vs_parent_anchor': float(widest['stability_anchor_buffer_to_nearest_topology_boundary']) / float(cap10_lower['parent_anchor_buffer_to_nearest_topology_boundary']),
            },
            'interpretation': 'Budget-admissible bands can still hide multiple distinct panel-label topologies. Stability-first rematch reporting should therefore choose interior topology-safe anchors or publish the topology subbands directly.',
        },
        'method_note': 'Started from the paired 90% interval materiality rule and the previously derived budget-admissible delta bands. Within each admissible parent band, swept delta on the same 0.00001 grid and split the band whenever any of the 9 tested panels changed state among {material_leader, practical_tie, undecided}. This yields topology-stable subbands plus midpoint stability anchors with explicit buffer to the nearest state-change boundary.',
        'band_rows': band_rows,
        'source_reports': [
            'artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json',
            'artifacts/reports/rematch_proxy_delta_admissibility_snapshot_20260306.json',
        ],
        'source_script': 'scripts/report/build_rematch_proxy_delta_topology_snapshot.py',
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
