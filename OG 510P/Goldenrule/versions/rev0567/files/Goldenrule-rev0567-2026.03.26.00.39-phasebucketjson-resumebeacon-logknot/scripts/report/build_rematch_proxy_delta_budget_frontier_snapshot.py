#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_budget_frontier_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_budget_frontier_snapshot_20260306.md'
REFERENCE_DELTAS = [0.0, 0.005, 0.01]
DELTA_GRID_STEP = 0.0001
DELTA_GRID_MAX_LOCAL = 0.01
DELTA_GRID_MAX_GLOBAL = 0.02
T_CRIT_90_DF5 = 2.015048


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _current_class(mean_gap: float, se_gap: float, delta: float) -> str:
    ci_low_90 = mean_gap - T_CRIT_90_DF5 * se_gap
    ci_high_90 = mean_gap + T_CRIT_90_DF5 * se_gap
    if ci_low_90 > delta:
        return 'material_leader'
    if ci_low_90 > -delta and ci_high_90 < delta:
        return 'practical_tie'
    return 'undecided'


def _required_total_paired_seeds_to_close(mean_gap: float, sd_gap: float, delta: float) -> tuple[float, str]:
    if delta < mean_gap:
        denom = mean_gap - delta
        return max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / denom) ** 2)), 'material_leader'
    if delta > mean_gap:
        denom = delta - mean_gap
        return max(2, math.ceil((T_CRIT_90_DF5 * sd_gap / denom) ** 2)), 'practical_tie'
    return math.inf, 'knife_edge'


def _reference_profile(rows: list[dict[str, object]], delta: float) -> dict[str, object]:
    unresolved_rows: list[dict[str, object]] = []
    total_additional = 0
    closed_now = 0
    for row in rows:
        mean_gap = float(row['leader_margin'])
        sd_gap = float(row['paired_margin_sd'])
        se_gap = float(row['paired_margin_se'])
        current_n = int(row['paired_seed_count'])
        current_state = _current_class(mean_gap, se_gap, delta)
        if current_state != 'undecided':
            closed_now += 1
            continue
        required_total, closure_route = _required_total_paired_seeds_to_close(mean_gap, sd_gap, delta)
        additional_needed = required_total - current_n if math.isfinite(required_total) else math.inf
        total_additional += additional_needed if math.isfinite(additional_needed) else 0
        unresolved_rows.append(
            {
                'extortion': int(row['extortion']),
                'delay': int(row['delay']),
                'leader': row['leader'],
                'runner_up': row['runner_up'],
                'leader_margin': mean_gap,
                'current_state_at_delta': current_state,
                'closure_route_if_more_budget_is_spent': closure_route,
                'current_paired_seeds': current_n,
                'approx_total_paired_seeds_needed_to_close_90': required_total,
                'approx_additional_paired_seeds_needed_to_close_90': additional_needed,
            }
        )
    return {
        'delta': delta,
        'closed_now': closed_now,
        'undecided_now': len(unresolved_rows),
        'approx_total_additional_paired_seeds_to_close_all_90': total_additional,
        'unresolved_rows': unresolved_rows,
    }


def _min_bands(rows: list[dict[str, object]], max_delta: float) -> tuple[int, list[dict[str, float]]]:
    grid_count = int(round(max_delta / DELTA_GRID_STEP))
    deltas = [i * DELTA_GRID_STEP for i in range(grid_count + 1)]
    totals = [int(_reference_profile(rows, delta)['approx_total_additional_paired_seeds_to_close_all_90']) for delta in deltas]
    min_total = min(totals)
    bands: list[dict[str, float]] = []
    i = 0
    while i < len(deltas):
        if totals[i] != min_total:
            i += 1
            continue
        start = deltas[i]
        j = i
        while j + 1 < len(deltas) and totals[j + 1] == min_total:
            j += 1
        bands.append({'start_delta': start, 'end_delta': deltas[j]})
        i = j + 1
    return min_total, bands


def main() -> int:
    src = json.loads(SRC_JSON.read_text(encoding='utf-8'))
    base_rows = src['panel_rows']

    reference_rows = [_reference_profile(base_rows, delta) for delta in REFERENCE_DELTAS]
    by_delta = {str(row['delta']): row for row in reference_rows}

    local_min_total, local_min_bands = _min_bands(base_rows, DELTA_GRID_MAX_LOCAL)
    global_min_total, global_min_bands = _min_bands(base_rows, DELTA_GRID_MAX_GLOBAL)

    summary = {
        'focus': 'Expose how the declared smallest effect of interest changes the extra simulation budget needed to close unresolved rematch top-gap panels, so SESOI choice and closure cost stay explicit instead of being mixed implicitly.',
        'source_report': str(SRC_JSON.relative_to(ROOT)),
        'method_note': 'For each candidate delta, first classify every panel using the current 90% interval rule from the materiality-gate pass. For panels still undecided at that delta, estimate the additional paired seeds needed to close them with the same 90% interval proxy and stable paired-gap variance assumption. If delta is below the observed mean gap, the cheapest closure route is to certify a materially better leader; if delta is above the observed mean gap, the cheapest closure route is to certify a practical tie.',
        'headline_findings': {
            'tested_panels': len(base_rows),
            'reference_delta_total_additional_budgets': {
                '0.0': by_delta['0.0']['approx_total_additional_paired_seeds_to_close_all_90'],
                '0.005': by_delta['0.005']['approx_total_additional_paired_seeds_to_close_all_90'],
                '0.01': by_delta['0.01']['approx_total_additional_paired_seeds_to_close_all_90'],
            },
            'cheapest_total_additional_budget_within_delta_le_0_01': local_min_total,
            'first_cheapest_delta_band_within_delta_le_0_01': local_min_bands[0],
            'global_cheapest_total_additional_budget_within_delta_le_0_02': global_min_total,
            'first_global_cheapest_delta_band_within_delta_le_0_02': global_min_bands[0],
            'interpretation': 'Closure cost is a real function of the declared indifference zone, and it is locally non-monotone in the current proxy. That means inheritors should publish the delta-vs-budget frontier rather than silently fixing delta at one threshold or quietly choosing the cheapest threshold after looking at the data.',
        },
        'reference_rows': reference_rows,
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    delta0 = by_delta['0.0']
    delta005 = by_delta['0.005']
    delta001 = by_delta['0.01']

    lines = [
        '# Rematch-Proxy Delta-Budget Frontier Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded paired top-gap means, paired-gap uncertainty, and current paired-seed counts from `artifacts/reports/rematch_proxy_winner_certification_snapshot_20260306.json`',
        '- for each declared practical margin `delta`, first asked which panels already close under the current 90% materiality rule',
        '- for panels still undecided, estimated the total paired seeds needed to close them with the same 90% interval proxy, assuming stable paired-gap variance',
        '- treated `delta < observed mean gap` as a material-leader closure route and `delta > observed mean gap` as a practical-tie closure route',
        '',
        'Main finding:',
        f"- The current proxy turns `delta` into a real closure-cost frontier: fully closing all nine panels would need about `{int(delta0['approx_total_additional_paired_seeds_to_close_all_90'])}` extra paired seeds at `delta=0`, only `{int(delta005['approx_total_additional_paired_seeds_to_close_all_90'])}` at `delta=0.005`, and `{int(delta001['approx_total_additional_paired_seeds_to_close_all_90'])}` at `delta=0.01`.",
        f"- So the closure-cost surface is locally non-monotone: moving from `delta=0.005` to `delta=0.01` makes full closure about `{(float(delta001['approx_total_additional_paired_seeds_to_close_all_90']) / float(delta005['approx_total_additional_paired_seeds_to_close_all_90'])):.1f}x` more expensive in the current proxy because a different pair of panels becomes the unresolved residue.",
        f"- Within the moderate band `delta <= 0.01`, the cheapest total closure cost on a dense `0.0001` grid is `{local_min_total}` extra paired seeds, first reached around `delta={float(local_min_bands[0]['start_delta']):.4f}` to `{float(local_min_bands[0]['end_delta']):.4f}`.",
        f"- On the broader sweep `delta <= 0.02`, the cheapest total closure cost falls to `{global_min_total}` extra paired seeds, first reached around `delta={float(global_min_bands[0]['start_delta']):.4f}` to `{float(global_min_bands[0]['end_delta']):.4f}`.",
        '',
        'Reference-delta summary:',
        '',
        '| delta | panels already closed | panels still undecided | approx extra paired seeds to close all |',
        '|---:|---:|---:|---:|',
    ]
    for row in reference_rows:
        lines.append(
            f"| {float(row['delta']):.3f} | {int(row['closed_now'])} | {int(row['undecided_now'])} | {int(row['approx_total_additional_paired_seeds_to_close_all_90'])} |"
        )

    for row in reference_rows:
        if not row['unresolved_rows']:
            continue
        lines += [
            '',
            f"Unresolved panels at delta={float(row['delta']):.3f}:",
            '',
            '| extortion | delay | leader | runner-up | closure route with more budget | approx total paired seeds needed | approx additional paired seeds |',
            '|---:|---:|---|---|---|---:|---:|',
        ]
        for unresolved in row['unresolved_rows']:
            lines.append(
                f"| {unresolved['extortion']} | {unresolved['delay']} | `{unresolved['leader']}` | `{unresolved['runner_up']}` | {unresolved['closure_route_if_more_budget_is_spent']} | {int(unresolved['approx_total_paired_seeds_needed_to_close_90'])} | {int(unresolved['approx_additional_paired_seeds_needed_to_close_90'])} |"
            )

    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world benchmark artifacts should publish a compact delta-budget frontier over the plausible SESOI band, not just a single budget number at one arbitrary delta.',
        '- This frontier should make two things explicit at once: how many panels remain undecided and what extra paired-seed budget would be needed to close them.',
        '- The point is not to let budget secretly choose delta. The point is to surface the tradeoff openly so inheritors can keep scientific materiality and simulation cost separate while still keeping the archive compact.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
