#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_admissibility_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_admissibility_snapshot_20260306.md'
T_CRIT_90_DF5 = 2.015048
DELTA_MAX = 0.02
DELTA_STEP = 0.00001
BUDGET_CAPS = [2, 4, 10, 20, 50, 100]


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


def _current_class(row: dict[str, object], delta: float) -> str:
    ci_low_90, ci_high_90 = _panel_bounds(row)
    if ci_low_90 > delta:
        return 'material_leader'
    if ci_low_90 > -delta and ci_high_90 < delta:
        return 'practical_tie'
    return 'undecided'


def _required_total_paired_seeds_to_close(row: dict[str, object], delta: float) -> float:
    if _current_class(row, delta) != 'undecided':
        return 0.0
    mean_gap = float(row['leader_margin'])
    sd_gap = float(row['paired_margin_sd'])
    if abs(mean_gap - delta) < 5e-12:
        return math.inf
    required_total = max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / abs(mean_gap - delta)) ** 2))
    return float(required_total - int(row['paired_seed_count']))


def _grid(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    steps = int(round(DELTA_MAX / DELTA_STEP))
    for i in range(steps + 1):
        delta = round(i * DELTA_STEP, 5)
        counts = {'material_leader': 0, 'practical_tie': 0, 'undecided': 0}
        total_additional = 0.0
        inf = False
        nearest = min(rows, key=lambda row: abs(delta - float(row['leader_margin'])))
        for row in rows:
            cls = _current_class(row, delta)
            counts[cls] += 1
            need = _required_total_paired_seeds_to_close(row, delta)
            if math.isinf(need):
                inf = True
                break
            total_additional += need
        out.append(
            {
                'delta': delta,
                'approx_total_additional_paired_seeds_to_close_all_90': None if inf else int(total_additional),
                'counts': counts,
                'nearest_leader_gap_distance': abs(delta - float(nearest['leader_margin'])),
                'nearest_panel': {
                    'extortion': int(nearest['extortion']),
                    'delay': int(nearest['delay']),
                    'leader': nearest['leader'],
                    'runner_up': nearest['runner_up'],
                    'leader_margin': float(nearest['leader_margin']),
                },
            }
        )
    return out


def _bands_for_cap(grid: list[dict[str, object]], cap: int) -> dict[str, object]:
    bands: list[dict[str, object]] = []
    i = 0
    while i < len(grid):
        row = grid[i]
        value = row['approx_total_additional_paired_seeds_to_close_all_90']
        in_band = value is not None and int(value) <= cap
        if not in_band:
            i += 1
            continue
        start_i = i
        best_i = i
        min_total = int(value)
        max_total = int(value)
        while i + 1 < len(grid):
            next_value = grid[i + 1]['approx_total_additional_paired_seeds_to_close_all_90']
            if next_value is None or int(next_value) > cap:
                break
            i += 1
            candidate = int(grid[i]['approx_total_additional_paired_seeds_to_close_all_90'])
            if candidate < min_total:
                min_total = candidate
                best_i = i
            max_total = max(max_total, candidate)
        start_delta = float(grid[start_i]['delta'])
        end_delta = float(grid[i]['delta'])
        width = end_delta - start_delta + DELTA_STEP
        anchor_row = grid[best_i]
        bands.append(
            {
                'start_delta': start_delta,
                'end_delta': end_delta,
                'width': width,
                'anchor_delta': float(anchor_row['delta']),
                'anchor_total_additional_paired_seeds': int(anchor_row['approx_total_additional_paired_seeds_to_close_all_90']),
                'anchor_counts': anchor_row['counts'],
                'min_total_additional_paired_seeds_within_band': min_total,
                'max_total_additional_paired_seeds_within_band': max_total,
                'nearest_panel_to_anchor': anchor_row['nearest_panel'],
            }
        )
        i += 1
    total_width = sum(float(b['width']) for b in bands)
    widest_band = max(bands, key=lambda b: (float(b['width']), -float(b['start_delta']))) if bands else None
    return {
        'budget_cap_additional_paired_seeds': cap,
        'band_count': len(bands),
        'total_admissible_width': total_width,
        'share_of_delta_band_le_0_02': total_width / DELTA_MAX if DELTA_MAX > 0 else 0.0,
        'widest_band': widest_band,
        'bands': bands,
    }


def _write_markdown(summary: dict[str, object]) -> None:
    cap_rows = summary['budget_cap_rows']
    cap10 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 10)
    cap4 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 4)
    cap20 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 20)
    low_cap10 = [b for b in cap10['bands'] if float(b['end_delta']) <= 0.01 + 1e-12]
    lines = [
        '# Rematch-Proxy Delta-Admissibility Snapshot (2026-03-06)',
        '',
        'Method:',
        f"- loaded paired top-gap means, paired-gap uncertainty, and current paired-seed counts from `{summary['source_report']}`",
        f'- swept `delta` on a dense `{DELTA_STEP:.5f}` grid over `[0, {DELTA_MAX:.2f}]`',
        '- at each delta, reused the same 90% fixed-precision closure proxy as the delta-budget and delta-hazard passes',
        '- for each additional-budget cap, extracted maximal contiguous delta bands where all currently unresolved panels could be closed within that cap',
        '',
        'Headline findings:',
        f"- under a `+10` paired-seed cap, admissible deltas collapse to `{cap10['band_count']}` bands covering `{float(cap10['share_of_delta_band_le_0_02'])*100:.2f}%` of `[0, 0.02]`",
        f"- the only admissible sub-`0.01` band at cap `10` is `{float(low_cap10[0]['start_delta']):.5f}..{float(low_cap10[0]['end_delta']):.5f}` (width `{float(low_cap10[0]['width']):.5f}`)",
        f"- tightening the cap to `4` fragments the lower admissible region into `{sum(1 for b in cap4['bands'] if float(b['end_delta']) <= 0.01 + 1e-12)}` micro-bands totaling `{sum(float(b['width']) for b in cap4['bands'] if float(b['end_delta']) <= 0.01 + 1e-12):.5f}` width",
        f"- relaxing the cap from `10` to `20` widens the lower admissible band to `{float(next(b for b in cap20['bands'] if float(b['end_delta']) <= 0.01 + 1e-12)['start_delta']):.5f}..{float(next(b for b in cap20['bands'] if float(b['end_delta']) <= 0.01 + 1e-12)['end_delta']):.5f}`",
        '',
        'Budget-cap rows:',
    ]
    for row in cap_rows:
        widest = row['widest_band']
        if widest is None:
            lines.append(f"- cap `{int(row['budget_cap_additional_paired_seeds'])}`: no admissible delta band")
            continue
        lines.append(
            f"- cap `{int(row['budget_cap_additional_paired_seeds'])}`: `{int(row['band_count'])}` bands, total width `{float(row['total_admissible_width']):.5f}`, widest `{float(widest['start_delta']):.5f}..{float(widest['end_delta']):.5f}` anchored at `{float(widest['anchor_delta']):.5f}`"
        )
    lines += [
        '',
        'Interpretation:',
        '- a declared rematch SESOI should be treated as an interval-choice problem, not just a point-choice problem',
        '- once a practical margin is chosen, the archive should also say which contiguous budget-admissible bands support that choice under the current paired-seed budget rule',
        '- that lets future inheritors choose from stable intervals and avoid post hoc knife-edge deltas that are nearly identical substantively but wildly different operationally',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


def main() -> int:
    source = json.loads(SRC_JSON.read_text(encoding='utf-8'))
    rows = source['panel_rows']
    grid = _grid(rows)
    cap_rows = [_bands_for_cap(grid, cap) for cap in BUDGET_CAPS]
    cap10 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 10)
    cap4 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 4)
    cap20 = next(row for row in cap_rows if int(row['budget_cap_additional_paired_seeds']) == 20)
    low10 = next(b for b in cap10['bands'] if float(b['end_delta']) <= 0.01 + 1e-12)
    low20 = next(b for b in cap20['bands'] if float(b['end_delta']) <= 0.01 + 1e-12)
    summary = {
        'focus': 'Expose budget-admissible SESOI bands so rematch practical margins can be chosen from stable intervals rather than knife-edge points with explosive closure cost.',
        'headline_findings': {
            'tested_panels': len(rows),
            'cap_10_band_count': int(cap10['band_count']),
            'cap_10_total_admissible_width': float(cap10['total_admissible_width']),
            'cap_10_share_of_delta_band_le_0_02': float(cap10['share_of_delta_band_le_0_02']),
            'cap_10_only_sub_0_01_band': {
                'start_delta': float(low10['start_delta']),
                'end_delta': float(low10['end_delta']),
                'width': float(low10['width']),
                'anchor_delta': float(low10['anchor_delta']),
                'anchor_total_additional_paired_seeds': int(low10['anchor_total_additional_paired_seeds']),
                'anchor_counts': low10['anchor_counts'],
            },
            'cap_4_lower_region_fragment_count': sum(1 for b in cap4['bands'] if float(b['end_delta']) <= 0.01 + 1e-12),
            'cap_4_lower_region_total_width': sum(float(b['width']) for b in cap4['bands'] if float(b['end_delta']) <= 0.01 + 1e-12),
            'cap_20_lower_region_band': {
                'start_delta': float(low20['start_delta']),
                'end_delta': float(low20['end_delta']),
                'width': float(low20['width']),
            },
            'interpretation': 'Budget admissibility is interval-structured: substantively similar delta choices can differ sharply in closure cost, so inheritors should publish admissible bands plus anchors rather than one naked threshold point.',
        },
        'method_note': 'Swept delta on a dense 0.00001 grid over [0, 0.02]. At each delta, reused the same 90% fixed-precision closure proxy from the delta-budget/delta-hazard passes and then extracted maximal contiguous bands where total additional paired seeds needed to close all currently undecided panels stayed below each declared budget cap.',
        'budget_cap_rows': cap_rows,
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_markdown(summary)
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
