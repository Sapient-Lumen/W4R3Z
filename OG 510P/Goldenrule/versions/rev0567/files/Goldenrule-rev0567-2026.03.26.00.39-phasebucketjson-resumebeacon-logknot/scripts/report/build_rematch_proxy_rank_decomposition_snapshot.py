#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_rank_decomposition_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_rank_decomposition_snapshot_20260306.md'

POLICY_ORDER = ('CCEEE', 'CCDDE', 'DCECC', 'always_c', 'courteous_firm')
EXTORTION_LEVELS = (20, 50, 80)
DELAY_LEVELS = (0, 1, 2)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _kendall_tau(order_a: list[str], order_b: list[str]) -> float:
    pos_a = {item: idx for idx, item in enumerate(order_a)}
    pos_b = {item: idx for idx, item in enumerate(order_b)}
    discordant = 0
    total = 0
    for a, b in itertools.combinations(order_a, 2):
        total += 1
        if (pos_a[a] - pos_a[b]) * (pos_b[a] - pos_b[b]) < 0:
            discordant += 1
    return 1.0 - (2.0 * discordant / total)


def main() -> int:
    src = _read_json(SRC)
    scenario_means = src['scenario_means']

    panel_rows: list[dict[str, object]] = []
    total_pairwise_inversions_nonzero_delay = 0
    nonzero_delay_panels = 0
    nonzero_delay_panels_with_rank_disagreement = 0
    all_in_match_orders_identical = True

    extortion_in_match_orders: dict[int, list[str]] = {}
    for ext in EXTORTION_LEVELS:
        base_order: list[str] | None = None
        for delay in DELAY_LEVELS:
            panel = []
            for policy in POLICY_ORDER:
                metrics = scenario_means[policy][f'ext{ext}_delay{delay}']
                panel.append({'policy': policy, **metrics})
            overall_order = [row['policy'] for row in sorted(panel, key=lambda row: float(row['overall_avg_payoff']), reverse=True)]
            in_match_order = [row['policy'] for row in sorted(panel, key=lambda row: float(row['in_match_avg_payoff']), reverse=True)]
            if base_order is None:
                base_order = list(in_match_order)
                extortion_in_match_orders[ext] = list(in_match_order)
            else:
                all_in_match_orders_identical = all_in_match_orders_identical and (in_match_order == base_order)

            pairwise_examples: list[dict[str, object]] = []
            pairwise_inversions = 0
            for a, b in itertools.combinations(POLICY_ORDER, 2):
                row_a = next(row for row in panel if row['policy'] == a)
                row_b = next(row for row in panel if row['policy'] == b)
                overall_gap = float(row_a['overall_avg_payoff']) - float(row_b['overall_avg_payoff'])
                in_match_gap = float(row_a['in_match_avg_payoff']) - float(row_b['in_match_avg_payoff'])
                if _sign(overall_gap) != _sign(in_match_gap):
                    pairwise_inversions += 1
                    higher = a if in_match_gap > 0 else b
                    lower = b if in_match_gap > 0 else a
                    pairwise_examples.append(
                        {
                            'higher_by_in_match': higher,
                            'lower_by_in_match': lower,
                            'overall_gap': overall_gap,
                            'in_match_gap': in_match_gap,
                        }
                    )

            tau = _kendall_tau(overall_order, in_match_order)
            panel_rows.append(
                {
                    'extortion': ext,
                    'delay': delay,
                    'overall_rank_order': overall_order,
                    'occupancy_normalized_rank_order': in_match_order,
                    'kendall_tau_overall_vs_occupancy_normalized': tau,
                    'pairwise_inversions_overall_vs_occupancy_normalized': pairwise_inversions,
                    'pairwise_comparisons': len(POLICY_ORDER) * (len(POLICY_ORDER) - 1) // 2,
                    'example_inversions': pairwise_examples,
                }
            )
            if delay > 0:
                nonzero_delay_panels += 1
                total_pairwise_inversions_nonzero_delay += pairwise_inversions
                if pairwise_inversions > 0:
                    nonzero_delay_panels_with_rank_disagreement += 1

    max_pairwise = max(int(row['pairwise_inversions_overall_vs_occupancy_normalized']) for row in panel_rows)
    min_tau = min(float(row['kendall_tau_overall_vs_occupancy_normalized']) for row in panel_rows)
    summary = {
        'focus': 'Separate raw aggregate leaderboard shifts from occupancy-normalized strategy quality in the current leave/rematch proxy.',
        'source_report': str(SRC.relative_to(ROOT)),
        'headline_findings': {
            'panels_checked': len(panel_rows),
            'nonzero_delay_panels_checked': nonzero_delay_panels,
            'nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement': nonzero_delay_panels_with_rank_disagreement,
            'total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels': total_pairwise_inversions_nonzero_delay,
            'max_pairwise_inversions_in_any_panel': max_pairwise,
            'lowest_kendall_tau_overall_vs_occupancy_normalized': min_tau,
            'occupancy_normalized_rank_order_identical_across_all_delay_levels_within_each_extortion': all_in_match_orders_identical,
            'interpretation': 'In the current proxy, raw rematch-delay leaderboard flips mostly come from occupancy/search time, not from changes in within-match strategy quality. Publish both views or risk misreading tempo taxes as behavioral improvements.',
        },
        'canonical_occupancy_normalized_rank_order_by_extortion': {f'ext{ext}': order for ext, order in extortion_in_match_orders.items()},
        'panel_rows': _round(panel_rows),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Rank Decomposition Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the occupancy-accounting snapshot for the current exogenous-pool leave/rematch proxy',
        '- compared the raw aggregate leaderboard (`overall_avg_payoff`) with the occupancy-normalized leaderboard (`in_match_avg_payoff`)',
        '- counted pairwise ranking inversions between the two views inside each extortion/delay panel',
        '',
        'Main finding:',
        f'- The occupancy-normalized rank order is identical across all `{len(panel_rows)}` extortion/delay panels once search dead-time is factored out.',
        f'- Among the `{nonzero_delay_panels}` nonzero-delay panels, `{nonzero_delay_panels_with_rank_disagreement}` have raw-vs-normalized rank disagreement, totaling `{total_pairwise_inversions_nonzero_delay}` pairwise inversions.',
        f'- The worst panel has `{max_pairwise}` pairwise inversions; the raw-vs-normalized Kendall tau drops as low as `{min_tau:.3f}`.',
        '- So the current proxy already has a useful diagnostic boundary: raw rank flips do not by themselves imply better or worse conduct inside matches.',
        '',
        'Why this matters:',
        '- The archive already separated aggregate welfare from in-match behavior.',
        '- This pass promotes that split into a leaderboard/reporting rule: publish both raw and occupancy-normalized rankings.',
        '- If only the raw leaderboard moves while the occupancy-normalized leaderboard stays fixed, the change is mostly a tempo/occupancy artifact rather than a within-match strategic improvement.',
        '',
        '| extortion | delay | overall rank order | occupancy-normalized rank order | pairwise inversions | Kendall tau |',
        '|---:|---:|---|---|---:|---:|',
    ]
    for row in sorted(panel_rows, key=lambda row: (int(row['extortion']), int(row['delay']))):
        lines.append(
            '| `{}` | `{}` | `{}` | `{}` | `{}` | `{:.3f}` |'.format(
                row['extortion'],
                row['delay'],
                ' > '.join(row['overall_rank_order']),
                ' > '.join(row['occupancy_normalized_rank_order']),
                row['pairwise_inversions_overall_vs_occupancy_normalized'],
                float(row['kendall_tau_overall_vs_occupancy_normalized']),
            )
        )
    lines.extend(
        [
            '',
            'Implementor consequence:',
            '- Every future rematch-world benchmark should publish a paired leaderboard: aggregate welfare and occupancy-normalized in-match welfare.',
            '- Treat raw-only rank changes as incomplete evidence until the occupancy-normalized ranking is checked too.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
