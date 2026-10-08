#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_OCC = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
SRC_XOVER = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delay_crossover_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_live_contenders_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_live_contenders_snapshot_20260306.md'

POLICIES = ('CCDDE', 'CCEEE', 'DCECC', 'always_c', 'courteous_firm')
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


def _predicted_overall(in_match_avg_payoff: float, avg_match_length: float, delay: float) -> float:
    return in_match_avg_payoff * avg_match_length / (avg_match_length + delay)


def _pairwise_crossover(in_match_a: float, length_a: float, in_match_b: float, length_b: float) -> float | None:
    numer = length_a * length_b * (in_match_b - in_match_a)
    denom = in_match_a * length_a - in_match_b * length_b
    if abs(denom) < 1e-12:
        return None
    return numer / denom


def _interval_repr(start: float, end: float | None) -> str:
    if end is None:
        return f'[{start:.6f}, inf)'
    return f'[{start:.6f}, {end:.6f})'


def main() -> int:
    occ = _read_json(SRC_OCC)
    xover = _read_json(SRC_XOVER)
    scenario_means = occ['scenario_means']
    predicted_rows = xover['scenario_prediction_rows']

    predicted_by_ext: dict[int, dict[str, dict[str, float]]] = {}
    for ext in EXTORTION_LEVELS:
        predicted_by_ext[ext] = {}
    for row in predicted_rows:
        ext = int(row['extortion'])
        predicted_by_ext[ext][str(row['policy'])] = {
            'in_match_avg_payoff': float(row['delay0_in_match_avg_payoff']),
            'avg_match_length': float(row['delay0_avg_match_length']),
        }

    extortion_rows: list[dict[str, object]] = []
    total_dominated_cells = 0
    total_live_contender_cells = 0
    total_pairwise_flips = 0
    total_top_flips = 0
    smallest_leader_gap = None
    smallest_leader_gap_panel = None
    tested_band_unique_leaders: set[str] = set()

    for ext in EXTORTION_LEVELS:
        base = predicted_by_ext[ext]

        dominated = []
        dominated_names = set()
        for policy in POLICIES:
            p = base[policy]
            dominators = []
            for other in POLICIES:
                if other == policy:
                    continue
                q = base[other]
                if (
                    q['in_match_avg_payoff'] >= p['in_match_avg_payoff']
                    and q['avg_match_length'] >= p['avg_match_length']
                    and (
                        q['in_match_avg_payoff'] > p['in_match_avg_payoff']
                        or q['avg_match_length'] > p['avg_match_length']
                    )
                ):
                    dominators.append(other)
            if dominators:
                dominated.append({'policy': policy, 'dominated_by': sorted(dominators)})
                dominated_names.add(policy)
        total_dominated_cells += len(dominated)

        tested_panels = []
        tested_leaders = []
        prev_leader = None
        actual_top_flips_ext = 0
        for delay in DELAY_LEVELS:
            ordered = sorted(
                (
                    (
                        policy,
                        float(scenario_means[policy][f'ext{ext}_delay{delay}']['overall_avg_payoff']),
                    )
                    for policy in POLICIES
                ),
                key=lambda kv: kv[1],
                reverse=True,
            )
            leader, leader_payoff = ordered[0]
            runner_up, runner_up_payoff = ordered[1]
            leader_gap = leader_payoff - runner_up_payoff
            tested_panels.append(
                {
                    'delay': delay,
                    'leader': leader,
                    'runner_up': runner_up,
                    'leader_gap': leader_gap,
                    'rank_order': [policy for policy, _ in ordered],
                }
            )
            tested_leaders.append(leader)
            tested_band_unique_leaders.add(leader)
            if prev_leader is not None and leader != prev_leader:
                actual_top_flips_ext += 1
            prev_leader = leader
            if smallest_leader_gap is None or leader_gap < smallest_leader_gap:
                smallest_leader_gap = leader_gap
                smallest_leader_gap_panel = {
                    'extortion': ext,
                    'delay': delay,
                    'leader': leader,
                    'runner_up': runner_up,
                    'leader_gap': leader_gap,
                }

        # pairwise flips in tested band between delay 0 and 2
        pairwise_flips_ext = 0
        for a, b in itertools.combinations(POLICIES, 2):
            gap0 = float(scenario_means[a][f'ext{ext}_delay0']['overall_avg_payoff']) - float(
                scenario_means[b][f'ext{ext}_delay0']['overall_avg_payoff']
            )
            gap2 = float(scenario_means[a][f'ext{ext}_delay2']['overall_avg_payoff']) - float(
                scenario_means[b][f'ext{ext}_delay2']['overall_avg_payoff']
            )
            if gap0 * gap2 < 0:
                pairwise_flips_ext += 1
        total_pairwise_flips += pairwise_flips_ext
        total_top_flips += actual_top_flips_ext

        # predicted upper envelope over nonnegative delays
        breakpoints = sorted(
            {
                cp
                for a, b in itertools.combinations(POLICIES, 2)
                for cp in [
                    _pairwise_crossover(
                        base[a]['in_match_avg_payoff'],
                        base[a]['avg_match_length'],
                        base[b]['in_match_avg_payoff'],
                        base[b]['avg_match_length'],
                    )
                ]
                if cp is not None and cp > 0
            }
        )
        sample_points = [0.0]
        for i, cp in enumerate(breakpoints):
            if i == 0:
                sample_points.append(cp / 2.0)
            else:
                sample_points.append((breakpoints[i - 1] + cp) / 2.0)
        if breakpoints:
            sample_points.append(breakpoints[-1] + 1.0)
        else:
            sample_points.append(1.0)

        def winner_at(delay: float) -> tuple[str, float]:
            scores = [
                (
                    policy,
                    _predicted_overall(base[policy]['in_match_avg_payoff'], base[policy]['avg_match_length'], delay),
                )
                for policy in POLICIES
            ]
            return max(scores, key=lambda kv: kv[1])

        intervals = []
        starts = [0.0] + breakpoints
        ends = breakpoints + [None]
        current_winner = None
        current_start = None
        for start, end, probe in zip(starts, ends, sample_points):
            winner, _ = winner_at(probe)
            if current_winner is None:
                current_winner = winner
                current_start = start
                continue
            if winner != current_winner:
                intervals.append({'winner': current_winner, 'start_delay': current_start, 'end_delay': start})
                current_winner = winner
                current_start = start
        if current_winner is None:
            current_winner = winner_at(0.0)[0]
            current_start = 0.0
        intervals.append({'winner': current_winner, 'start_delay': current_start, 'end_delay': None})

        live_contenders = []
        for winner in [] if not intervals else [interval['winner'] for interval in intervals]:
            if winner not in live_contenders:
                live_contenders.append(winner)
        total_live_contender_cells += len(live_contenders)

        extortion_rows.append(
            {
                'extortion': ext,
                'strictly_dominated_policies': dominated,
                'tested_band_panel_rows': tested_panels,
                'tested_band_unique_leaders': tested_leaders,
                'tested_band_leader_set': sorted(set(tested_leaders)),
                'tested_band_pairwise_flips_between_delay0_and_delay2': pairwise_flips_ext,
                'tested_band_leader_flips': actual_top_flips_ext,
                'predicted_nonnegative_delay_live_contender_set': live_contenders,
                'predicted_nonnegative_delay_winner_intervals': [
                    {
                        **interval,
                        'interval': _interval_repr(float(interval['start_delay']), None if interval['end_delay'] is None else float(interval['end_delay'])),
                    }
                    for interval in intervals
                ],
            }
        )

    summary = {
        'focus': 'Shrink rematch delay reporting to the decision-relevant policies by separating dead contenders, live contenders, and actual top-winner fragility in the current proxy.',
        'source_reports': [str(SRC_OCC.relative_to(ROOT)), str(SRC_XOVER.relative_to(ROOT))],
        'headline_findings': {
            'policy_extortion_cells_checked': len(POLICIES) * len(EXTORTION_LEVELS),
            'strictly_dominated_policy_extortion_cells': total_dominated_cells,
            'predicted_nonnegative_delay_live_contender_cells': total_live_contender_cells,
            'predicted_nonnegative_delay_never_top_cells': len(POLICIES) * len(EXTORTION_LEVELS) - total_live_contender_cells,
            'tested_panels_checked': len(EXTORTION_LEVELS) * len(DELAY_LEVELS),
            'tested_pairwise_flips_between_delay0_and_delay2': total_pairwise_flips,
            'tested_leader_flips_across_adjacent_delays': total_top_flips,
            'smallest_tested_leader_gap': smallest_leader_gap,
            'smallest_tested_leader_gap_panel': smallest_leader_gap_panel,
            'leaders_observed_anywhere_in_tested_band': sorted(tested_band_unique_leaders),
            'interpretation': 'In the current proxy, most delay fragility is below the top slot. A compact live-contender / leader-margin artifact would preserve decision-relevant uncertainty while pruning dead policies from bulky delay sweeps.',
        },
        'extortion_rows': _round(extortion_rows),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Live Contenders Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the occupancy-accounting and delay-crossover snapshots for the current exogenous-pool leave/rematch proxy',
        '- marked a policy as strictly dominated when another policy had at least as much delay-0 `in_match_avg_payoff` and at least as much delay-0 `avg_match_length`, with one strict improvement',
        '- used the delay-0 quality/tempo proxy `m * L / (L + d)` to extract the predicted top-winner envelope over all nonnegative delays',
        '- compared that with the actual top winner and winner margin on the tested delay band `d in {0,1,2}`',
        '',
        'Main finding:',
        f'- `{total_dominated_cells}` of `{len(POLICIES) * len(EXTORTION_LEVELS)}` policy/extortion cells are strictly dominated in delay-0 quality/tempo space and can never be top under the current proxy while world semantics stay fixed.',
        f'- Across the tested panels there are `{total_pairwise_flips}` pairwise flips between delay `0` and delay `2`, but only `{total_top_flips}` actual leader flip across adjacent tested delays.',
        f'- The tightest tested leader race is `{smallest_leader_gap_panel["leader"]}` over `{smallest_leader_gap_panel["runner_up"]}` at extortion `{smallest_leader_gap_panel["extortion"]}`, delay `{smallest_leader_gap_panel["delay"]}`, with gap `{smallest_leader_gap:.6f}`.',
        '- So the archive can stay smaller and more decision-facing by publishing dead-contender pruning plus leader margins, instead of treating every below-top pairwise crossover as equally important.',
        '',
        'Per-extortion contender summary:',
        '| extortion | dominated policies | tested-band leader set | predicted live contender set over d >= 0 |',
        '|---:|---|---|---|',
    ]
    for row in extortion_rows:
        dominated_text = ', '.join(item['policy'] for item in row['strictly_dominated_policies']) or '_none_'
        lines.append(
            '| `{}` | `{}` | `{}` | `{}` |'.format(
                row['extortion'],
                dominated_text,
                ', '.join(row['tested_band_leader_set']),
                ', '.join(row['predicted_nonnegative_delay_live_contender_set']),
            )
        )
    lines.extend(
        [
            '',
            'Implementor consequence:',
            '- Publish a compact live-contender artifact for each rematch world: dominated policies, tested-band leader set, winner margins, and the live contender set over the deployed delay band.',
            '- Keep full pairwise crossover matrices as scratch or secondary evidence; they are not the smallest decision-facing handoff artifact once dead contenders are identified.',
            '- Recompute the live contender set whenever world semantics change (noise semantics, entrant pool, role policy, persistence, or matching/search rules).',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
