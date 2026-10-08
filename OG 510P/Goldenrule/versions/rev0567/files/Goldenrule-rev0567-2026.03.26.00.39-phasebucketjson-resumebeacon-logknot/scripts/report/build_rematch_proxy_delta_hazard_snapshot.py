#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_hazard_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
DELTA_MAX = 0.02
DELTA_STEP = 0.00001
ADDITIONAL_THRESHOLDS = [100, 500, 1000, 10000]


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
    ci_low_90 = mean_gap - T_CRIT_90_DF5 * se_gap
    ci_high_90 = mean_gap + T_CRIT_90_DF5 * se_gap
    return ci_low_90, ci_high_90


def _current_class(row: dict[str, object], delta: float) -> str:
    ci_low_90, ci_high_90 = _panel_bounds(row)
    if ci_low_90 > delta:
        return 'material_leader'
    if ci_low_90 > -delta and ci_high_90 < delta:
        return 'practical_tie'
    return 'undecided'


def _required_total_paired_seeds_to_close(row: dict[str, object], delta: float) -> tuple[float, str]:
    mean_gap = float(row['leader_margin'])
    sd_gap = float(row['paired_margin_sd'])
    if delta < mean_gap:
        denom = mean_gap - delta
        return max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / denom) ** 2)), 'material_leader'
    if delta > mean_gap:
        denom = delta - mean_gap
        return max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / denom) ** 2)), 'practical_tie'
    return math.inf, 'knife_edge'


def _total_additional_budget(rows: list[dict[str, object]], delta: float) -> float:
    total_additional = 0.0
    for row in rows:
        if _current_class(row, delta) != 'undecided':
            continue
        required_total, _ = _required_total_paired_seeds_to_close(row, delta)
        current_n = int(row['paired_seed_count'])
        if not math.isfinite(required_total):
            return math.inf
        total_additional += required_total - current_n
    return total_additional


def _fine_grid(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grid: list[dict[str, object]] = []
    steps = int(round(DELTA_MAX / DELTA_STEP))
    for i in range(steps + 1):
        delta = round(i * DELTA_STEP, 5)
        total_additional = _total_additional_budget(rows, delta)
        if math.isfinite(total_additional):
            nearest_row = min(rows, key=lambda row: abs(delta - float(row['leader_margin'])))
            grid.append(
                {
                    'delta': delta,
                    'approx_total_additional_paired_seeds_to_close_all_90': int(total_additional),
                    'nearest_leader_gap_distance': abs(delta - float(nearest_row['leader_margin'])),
                    'nearest_panel': {
                        'extortion': int(nearest_row['extortion']),
                        'delay': int(nearest_row['delay']),
                        'leader': nearest_row['leader'],
                        'runner_up': nearest_row['runner_up'],
                        'leader_margin': float(nearest_row['leader_margin']),
                    },
                }
            )
        else:
            matching_rows = [row for row in rows if abs(delta - float(row['leader_margin'])) < 5e-7]
            grid.append(
                {
                    'delta': delta,
                    'approx_total_additional_paired_seeds_to_close_all_90': 'inf',
                    'nearest_leader_gap_distance': 0.0,
                    'knife_edge_panels': [
                        {
                            'extortion': int(row['extortion']),
                            'delay': int(row['delay']),
                            'leader': row['leader'],
                            'runner_up': row['runner_up'],
                            'leader_margin': float(row['leader_margin']),
                        }
                        for row in matching_rows
                    ],
                }
            )
    return grid


def _hazard_bands(grid: list[dict[str, object]], threshold: int) -> dict[str, object]:
    bands: list[dict[str, object]] = []
    total_width = 0.0
    i = 0
    while i < len(grid):
        value = grid[i]['approx_total_additional_paired_seeds_to_close_all_90']
        in_band = value == 'inf' or int(value) > threshold
        if not in_band:
            i += 1
            continue
        start_i = i
        peak_i = i
        peak_value: float = math.inf if value == 'inf' else int(value)
        contains_exact_knife_edge = value == 'inf'
        while i + 1 < len(grid):
            next_value = grid[i + 1]['approx_total_additional_paired_seeds_to_close_all_90']
            next_in_band = next_value == 'inf' or int(next_value) > threshold
            if not next_in_band:
                break
            i += 1
            contains_exact_knife_edge = contains_exact_knife_edge or next_value == 'inf'
            candidate = math.inf if next_value == 'inf' else int(next_value)
            if candidate > peak_value:
                peak_value = candidate
                peak_i = i
        start_delta = float(grid[start_i]['delta'])
        end_delta = float(grid[i]['delta'])
        total_width += end_delta - start_delta + DELTA_STEP
        peak_row = grid[peak_i]
        if peak_row['approx_total_additional_paired_seeds_to_close_all_90'] == 'inf':
            peak_value_out: object = 'inf'
            nearest_panel = peak_row['knife_edge_panels'][0]
        else:
            peak_value_out = int(peak_row['approx_total_additional_paired_seeds_to_close_all_90'])
            nearest_panel = peak_row['nearest_panel']
        bands.append(
            {
                'start_delta': start_delta,
                'end_delta': end_delta,
                'peak_delta': float(peak_row['delta']),
                'peak_total_additional_paired_seeds': peak_value_out,
                'contains_exact_knife_edge': contains_exact_knife_edge,
                'nearest_panel_at_peak': nearest_panel,
            }
        )
        i += 1
    share = total_width / DELTA_MAX if DELTA_MAX > 0 else 0.0
    widest_band = None
    if bands:
        widest_band = max(bands, key=lambda band: float(band['end_delta']) - float(band['start_delta']))
    return {
        'threshold_additional_paired_seeds': threshold,
        'band_count': len(bands),
        'total_band_width': total_width,
        'share_of_delta_band_le_0_02': share,
        'widest_band': widest_band,
        'bands': bands,
    }


def _panel_hazard_rows(rows: list[dict[str, object]], additional_budget_cap: int) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        current_n = int(row['paired_seed_count'])
        radius = T_CRIT_90_DF5 * sd_gap / math.sqrt(current_n + additional_budget_cap)
        start_delta = max(0.0, mean_gap - radius)
        end_delta = min(DELTA_MAX, mean_gap + radius)
        if start_delta >= end_delta:
            continue
        out.append(
            {
                'extortion': int(row['extortion']),
                'delay': int(row['delay']),
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_margin': mean_gap,
                'knife_edge_exclusion_radius_for_additional_budget_cap': radius,
                'hazard_interval_within_delta_le_0_02': {
                    'start_delta': start_delta,
                    'end_delta': end_delta,
                },
            }
        )
    out.sort(key=lambda r: (r['leader_margin'], r['extortion'], r['delay']))
    return out


def _format_band(band: dict[str, object] | None) -> str:
    if band is None:
        return 'n/a'
    return f"{float(band['start_delta']):.5f}..{float(band['end_delta']):.5f}"


def _write_markdown(summary: dict[str, object]) -> None:
    threshold_rows = summary['threshold_rows']
    knife_edges = summary['knife_edge_rows']
    hazard_rows_1000 = summary['panel_hazard_rows_for_additional_budget_cap_1000']
    top_bands_10000 = next(row for row in threshold_rows if int(row['threshold_additional_paired_seeds']) == 10000)['bands']
    lines = [
        '# Rematch-Proxy Delta-Hazard Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- loaded paired top-gap means, paired-gap uncertainty, and current paired-seed counts from `{summary['source_report']}`",
        f'- swept `delta` on a dense `{DELTA_STEP:.5f}` grid over `[0, {DELTA_MAX:.2f}]`',
        '- reused the same fixed-precision closure proxy as the earlier delta-budget frontier: for each still-undecided panel, estimated how many paired seeds would be needed to close it under the 90% interval rule',
        '- treated exact equality `delta == observed leader_margin` as a knife-edge where the simple fixed-precision closure proxy becomes undefined because the denominator of the required-sample formula vanishes',
        '',
        'Main finding:',
        f"- There are `{summary['headline_findings']['knife_edge_deltas_within_delta_le_0_02']}` exact knife-edge deltas inside `[0, 0.02]`, one for each observed top-gap mean that falls inside the band.",
        f"- On the dense grid, bands requiring more than `10000` extra paired seeds occupy only `{summary['headline_findings']['band_width_above_10000']:.6f}` delta width (`{summary['headline_findings']['band_share_above_10000']:.2%}` of the band) across `{summary['headline_findings']['band_count_above_10000']}` narrow neighborhoods once exact knife-edge points are merged into their surrounding hazard bands.",
        f"- The largest sub-`0.02` spike appears near `delta={summary['headline_findings']['largest_grid_spike']['delta']:.5f}` with about `{int(summary['headline_findings']['largest_grid_spike']['approx_total_additional_paired_seeds_to_close_all_90']):,}` extra paired seeds, nearest to `ext{int(summary['headline_findings']['largest_grid_spike']['nearest_panel']['extortion'])}, delay{int(summary['headline_findings']['largest_grid_spike']['nearest_panel']['delay'])}` (leader gap `{float(summary['headline_findings']['largest_grid_spike']['nearest_panel']['leader_margin']):.6f}`).",
        f"- The second-largest spike appears near `delta={summary['headline_findings']['second_largest_grid_spike']['delta']:.5f}` with about `{int(summary['headline_findings']['second_largest_grid_spike']['approx_total_additional_paired_seeds_to_close_all_90']):,}` extra paired seeds, nearest to `ext{int(summary['headline_findings']['second_largest_grid_spike']['nearest_panel']['extortion'])}, delay{int(summary['headline_findings']['second_largest_grid_spike']['nearest_panel']['delay'])}` (leader gap `{float(summary['headline_findings']['second_largest_grid_spike']['nearest_panel']['leader_margin']):.6f}`).",
        '',
        'Exact knife-edge deltas inside `[0, 0.02]`:',
        '',
        '| extortion | delay | leader | runner-up | observed leader gap delta |',
        '|---:|---:|---|---|---:|',
    ]
    for row in knife_edges:
        lines.append(
            f"| {int(row['extortion'])} | {int(row['delay'])} | `{row['leader']}` | `{row['runner_up']}` | {float(row['leader_margin']):.6f} |"
        )
    lines.extend(
        [
            '',
            'Hazard-band summary by extra-budget threshold:',
            '',
            '| threshold (extra paired seeds) | band count | total delta width | share of `[0,0.02]` | widest band |',
            '|---:|---:|---:|---:|---|',
        ]
    )
    for row in threshold_rows:
        lines.append(
            f"| {int(row['threshold_additional_paired_seeds'])} | {int(row['band_count'])} | {float(row['total_band_width']):.6f} | {float(row['share_of_delta_band_le_0_02']):.2%} | `{_format_band(row['widest_band'])}` |"
        )
    lines.extend(
        [
            '',
            'Bands where the dense-grid closure cost exceeds `10000` extra paired seeds:',
            '',
            '| start delta | end delta | peak delta | peak extra paired seeds | nearest panel at peak |',
            '|---:|---:|---:|---:|---|',
        ]
    )
    for row in top_bands_10000:
        peak_panel = row['nearest_panel_at_peak']
        peak_value = row['peak_total_additional_paired_seeds']
        peak_str = 'inf' if peak_value == 'inf' else f"{int(peak_value):,}"
        lines.append(
            f"| {float(row['start_delta']):.5f} | {float(row['end_delta']):.5f} | {float(row['peak_delta']):.5f} | {peak_str} | `ext{int(peak_panel['extortion'])}, delay{int(peak_panel['delay'])}` gap `{float(peak_panel['leader_margin']):.6f}` |"
        )
    lines.extend(
        [
            '',
            'Per-panel exclusion radii for keeping additional closure budget below `1000` paired seeds:',
            '',
            '| extortion | delay | leader gap delta | exclusion radius | hazard interval inside `[0,0.02]` |',
            '|---:|---:|---:|---:|---|',
        ]
    )
    for row in hazard_rows_1000:
        interval = row['hazard_interval_within_delta_le_0_02']
        lines.append(
            f"| {int(row['extortion'])} | {int(row['delay'])} | {float(row['leader_margin']):.6f} | {float(row['knife_edge_exclusion_radius_for_additional_budget_cap']):.6f} | `{float(interval['start_delta']):.6f}..{float(interval['end_delta']):.6f}` |"
        )
    lines.extend(
        [
            '',
            'Implementor implication:',
            '- Future rematch-world benchmark artifacts should publish leader-gap hazard bands or an equivalent no-knife-edge buffer, not just a coarse delta grid and one cheapest point.',
            '- The point is not to forbid exploratory delta sweeps. The point is to make it explicit when a declared SESOI is so close to an observed top-gap mean that closure cost becomes numerically and operationally ill-conditioned.',
            '- This keeps the archive compact: one exact list of leader-gap deltas plus a few hazard summaries is enough to warn future inheritors away from fragile threshold choices without storing bulky multi-delta rerun tables.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    src = json.loads(SRC_JSON.read_text(encoding='utf-8'))
    rows = sorted(src['panel_rows'], key=lambda r: (int(r['extortion']), int(r['delay'])))
    grid = _fine_grid(rows)

    finite_grid = [row for row in grid if row['approx_total_additional_paired_seeds_to_close_all_90'] != 'inf']
    largest_spikes = sorted(
        finite_grid,
        key=lambda row: int(row['approx_total_additional_paired_seeds_to_close_all_90']),
        reverse=True,
    )[:2]
    threshold_rows = [_hazard_bands(grid, threshold) for threshold in ADDITIONAL_THRESHOLDS]

    knife_edge_rows = []
    for row in rows:
        margin = float(row['leader_margin'])
        if margin <= DELTA_MAX:
            knife_edge_rows.append(
                {
                    'extortion': int(row['extortion']),
                    'delay': int(row['delay']),
                    'leader': row['leader'],
                    'runner_up': row['runner_up'],
                    'leader_margin': margin,
                }
            )
    knife_edge_rows.sort(key=lambda row: (row['leader_margin'], row['extortion'], row['delay']))

    threshold_10000 = next(row for row in threshold_rows if int(row['threshold_additional_paired_seeds']) == 10000)
    summary = {
        'focus': 'Expose knife-edge SESOI neighborhoods where rematch closure cost explodes because the declared practical margin sits too close to an observed top-gap mean.',
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'method_note': f"Swept delta on a dense {DELTA_STEP:.5f} grid over [0, {DELTA_MAX:.2f}] using the same fixed-precision closure proxy as the earlier delta-budget frontier. At each delta, summed the additional paired seeds needed to close every currently undecided panel under the 90% interval rule. Exact equality delta == observed leader_margin is a knife-edge for this proxy because the required-sample denominator vanishes.",
        'headline_findings': {
            'knife_edge_deltas_within_delta_le_0_02': len(knife_edge_rows),
            'band_count_above_10000': int(threshold_10000['band_count']),
            'band_width_above_10000': float(threshold_10000['total_band_width']),
            'band_share_above_10000': float(threshold_10000['share_of_delta_band_le_0_02']),
            'largest_grid_spike': largest_spikes[0],
            'second_largest_grid_spike': largest_spikes[1],
            'interpretation': 'The current rematch closure-cost surface is locally ill-conditioned near observed top-gap means. Tiny changes in delta around those knife-edge points can move required closure budget by orders of magnitude, so inheritors need explicit hazard-band metadata rather than only a coarse delta grid or a single cheapest threshold.',
        },
        'knife_edge_rows': knife_edge_rows,
        'threshold_rows': threshold_rows,
        'panel_hazard_rows_for_additional_budget_cap_1000': _panel_hazard_rows(rows, 1000),
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2) + '\n', encoding='utf-8')
    _write_markdown(_round(summary))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
