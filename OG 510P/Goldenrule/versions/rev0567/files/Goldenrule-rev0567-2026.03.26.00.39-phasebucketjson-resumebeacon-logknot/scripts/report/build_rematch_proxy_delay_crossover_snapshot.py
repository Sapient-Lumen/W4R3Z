#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delay_crossover_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delay_crossover_snapshot_20260306.md'

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


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _predicted_overall(in_match_avg_payoff: float, avg_match_length: float, delay: int) -> float:
    return in_match_avg_payoff * avg_match_length / (avg_match_length + delay)


def _crossover_delay(in_match_a: float, length_a: float, in_match_b: float, length_b: float) -> float | None:
    # Solve m_a * L_a / (L_a + d) = m_b * L_b / (L_b + d)
    numer = length_a * length_b * (in_match_b - in_match_a)
    denom = in_match_a * length_a - in_match_b * length_b
    if abs(denom) < 1e-12:
        return None
    return numer / denom


def main() -> int:
    src = _read_json(SRC)
    scenario_means = src['scenario_means']

    scenario_prediction_rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    prediction_errors: list[float] = []
    pairwise_total = 0
    pairwise_correct = 0
    actual_flips_delay0_to_delay2 = 0
    predicted_thresholds_in_tested_range = 0
    predicted_positive_thresholds = 0
    near_thresholds_2_to_3 = 0

    for ext in EXTORTION_LEVELS:
        base = {policy: scenario_means[policy][f'ext{ext}_delay0'] for policy in POLICIES}
        for policy in POLICIES:
            base_metrics = base[policy]
            in_match_avg = float(base_metrics['in_match_avg_payoff'])
            avg_match_length = float(base_metrics['avg_match_length'])
            row = {
                'policy': policy,
                'extortion': ext,
                'delay0_in_match_avg_payoff': in_match_avg,
                'delay0_avg_match_length': avg_match_length,
                'delay_rows': [],
            }
            for delay in DELAY_LEVELS:
                actual = float(scenario_means[policy][f'ext{ext}_delay{delay}']['overall_avg_payoff'])
                predicted = _predicted_overall(in_match_avg, avg_match_length, delay)
                error = predicted - actual
                prediction_errors.append(abs(error))
                row['delay_rows'].append(
                    {
                        'delay': delay,
                        'actual_overall_avg_payoff': actual,
                        'predicted_overall_avg_payoff_from_delay0_summary': predicted,
                        'prediction_error': error,
                    }
                )
            scenario_prediction_rows.append(row)

        for a, b in itertools.combinations(POLICIES, 2):
            a0 = base[a]
            b0 = base[b]
            crossover = _crossover_delay(
                float(a0['in_match_avg_payoff']),
                float(a0['avg_match_length']),
                float(b0['in_match_avg_payoff']),
                float(b0['avg_match_length']),
            )
            if crossover is not None and crossover > 0:
                predicted_positive_thresholds += 1
                if crossover <= 2.0:
                    predicted_thresholds_in_tested_range += 1
                elif crossover <= 3.0:
                    near_thresholds_2_to_3 += 1
            delay_signs = {}
            predicted_signs = {}
            actual_gaps = {}
            predicted_gaps = {}
            for delay in DELAY_LEVELS:
                actual_gap = float(scenario_means[a][f'ext{ext}_delay{delay}']['overall_avg_payoff']) - float(
                    scenario_means[b][f'ext{ext}_delay{delay}']['overall_avg_payoff']
                )
                predicted_gap = _predicted_overall(float(a0['in_match_avg_payoff']), float(a0['avg_match_length']), delay) - _predicted_overall(
                    float(b0['in_match_avg_payoff']), float(b0['avg_match_length']), delay
                )
                actual_sign = _sign(actual_gap)
                predicted_sign = _sign(predicted_gap)
                delay_signs[f'delay{delay}'] = actual_sign
                predicted_signs[f'delay{delay}'] = predicted_sign
                actual_gaps[f'delay{delay}'] = actual_gap
                predicted_gaps[f'delay{delay}'] = predicted_gap
                pairwise_total += 1
                pairwise_correct += int(actual_sign == predicted_sign)
            if delay_signs['delay0'] * delay_signs['delay2'] < 0:
                actual_flips_delay0_to_delay2 += 1
            pair_rows.append(
                {
                    'extortion': ext,
                    'policy_a': a,
                    'policy_b': b,
                    'predicted_crossover_delay': crossover,
                    'predicted_threshold_in_tested_delay_range_0_to_2': bool(crossover is not None and 0 < crossover <= 2.0),
                    'predicted_threshold_near_tested_range_2_to_3': bool(crossover is not None and 2.0 < crossover <= 3.0),
                    'actual_delay_signs_a_minus_b': delay_signs,
                    'predicted_delay_signs_a_minus_b': predicted_signs,
                    'actual_gaps_a_minus_b': actual_gaps,
                    'predicted_gaps_a_minus_b': predicted_gaps,
                    'actual_flip_between_delay0_and_delay2': bool(delay_signs['delay0'] * delay_signs['delay2'] < 0),
                    'model_classifies_all_tested_delay_orders_correctly': all(
                        delay_signs[f'delay{delay}'] == predicted_signs[f'delay{delay}'] for delay in DELAY_LEVELS
                    ),
                }
            )

    fragile_rows = [row for row in pair_rows if row['predicted_threshold_in_tested_delay_range_0_to_2']]
    near_rows = [row for row in pair_rows if row['predicted_threshold_near_tested_range_2_to_3']]
    worst_prediction = max(
        scenario_prediction_rows,
        key=lambda row: max(abs(float(dr['prediction_error'])) for dr in row['delay_rows']),
    )
    worst_delay_row = max(worst_prediction['delay_rows'], key=lambda dr: abs(float(dr['prediction_error'])))

    summary = {
        'focus': 'Treat single-delay rematch rankings as fragile unless they are accompanied by either a delay sweep or explicit crossover-threshold / robustness information.',
        'source_report': str(SRC.relative_to(ROOT)),
        'headline_findings': {
            'scenario_means_checked': len(POLICIES) * len(EXTORTION_LEVELS) * len(DELAY_LEVELS),
            'pairwise_orders_checked': pairwise_total,
            'pairwise_orders_classified_correctly_by_delay0_in_match_plus_tempo_proxy': pairwise_correct,
            'pairwise_order_classification_accuracy': pairwise_correct / pairwise_total,
            'mean_abs_overall_payoff_prediction_error': statistics.fmean(prediction_errors),
            'max_abs_overall_payoff_prediction_error': max(prediction_errors),
            'predicted_positive_crossover_thresholds': predicted_positive_thresholds,
            'predicted_crossover_thresholds_in_tested_delay_range_0_to_2': predicted_thresholds_in_tested_range,
            'predicted_crossover_thresholds_near_tested_range_2_to_3': near_thresholds_2_to_3,
            'actual_pairwise_flips_between_delay0_and_delay2': actual_flips_delay0_to_delay2,
            'interpretation': 'In the current proxy, most raw rematch ranking changes are already explained by a two-number summary from delay0: in-match quality and partnership tempo. So a single nominal delay point is not a robust ranking contract.',
        },
        'formula': {
            'predicted_overall_avg_payoff_at_delay_d': 'delay0_in_match_avg_payoff * delay0_avg_match_length / (delay0_avg_match_length + d)',
            'pairwise_crossover_delay_d_star': 'solve m_a * L_a / (L_a + d) = m_b * L_b / (L_b + d) for d, using delay0 in-match payoff m and delay0 avg match length L',
        },
        'fragile_pairs_in_tested_delay_range': _round(fragile_rows),
        'near_threshold_pairs_just_beyond_tested_range': _round(near_rows),
        'worst_prediction_cell': _round(
            {
                'policy': worst_prediction['policy'],
                'extortion': worst_prediction['extortion'],
                **worst_delay_row,
            }
        ),
        'scenario_prediction_rows': _round(scenario_prediction_rows),
        'pair_rows': _round(pair_rows),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Delay Crossover Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the occupancy-accounting snapshot for the current exogenous-pool leave/rematch proxy',
        '- used only two delay-0 summary statistics per policy/extortion cell: `in_match_avg_payoff` and `avg_match_length`',
        '- predicted aggregate welfare at delay `d` via `m * L / (L + d)` and solved pairwise crossover delays where two policies tie in predicted aggregate welfare',
        '',
        'Main finding:',
        f'- This two-number proxy classifies `{pairwise_correct}` of `{pairwise_total}` observed pairwise delay-specific orders correctly (`{pairwise_correct / pairwise_total:.3f}` accuracy).',
        f'- The mean absolute aggregate-payoff prediction error is `{statistics.fmean(prediction_errors):.6f}`; the max absolute error is `{max(prediction_errors):.6f}`.',
        f'- There are `{predicted_thresholds_in_tested_range}` predicted pairwise crossover thresholds inside the tested delay range `[0, 2]`, plus `{near_thresholds_2_to_3}` more just beyond it in `(2, 3]`.',
        f'- Actual data show `{actual_flips_delay0_to_delay2}` pairwise raw-rank flips between delay `0` and delay `2`.',
        '- So the current proxy already supports a stronger reporting rule: a single-delay rematch leaderboard is not a stable contract unless its delay robustness is shown too.',
        '',
        'Fragile predicted pairs on the tested delay sweep:',
        '| extortion | pair | predicted crossover delay | actual delay-0 sign | actual delay-2 sign |',
        '|---:|---|---:|---:|---:|',
    ]
    for row in fragile_rows:
        lines.append(
            '| `{}` | `{}` vs `{}` | `{:.3f}` | `{}` | `{}` |'.format(
                row['extortion'],
                row['policy_a'],
                row['policy_b'],
                float(row['predicted_crossover_delay']),
                row['actual_delay_signs_a_minus_b']['delay0'],
                row['actual_delay_signs_a_minus_b']['delay2'],
            )
        )
    if not fragile_rows:
        lines.append('| _none_ |  |  |  |  |')
    lines.extend(
        [
            '',
            'Near-threshold pairs just beyond the tested sweep:',
            '| extortion | pair | predicted crossover delay | actual delay-2 gap |',
            '|---:|---|---:|---:|',
        ]
    )
    for row in near_rows:
        lines.append(
            '| `{}` | `{}` vs `{}` | `{:.3f}` | `{:.6f}` |'.format(
                row['extortion'],
                row['policy_a'],
                row['policy_b'],
                float(row['predicted_crossover_delay']),
                float(row['actual_gaps_a_minus_b']['delay2']),
            )
        )
    if not near_rows:
        lines.append('| _none_ |  |  |  |')
    lines.extend(
        [
            '',
            'Implementor consequence:',
            '- Do not ship a rematch-world “winner” at one delay value without either a delay sweep or an explicit crossover/robustness report.',
            '- If a pair has a finite crossover threshold inside the deployed delay range, its raw aggregate ordering is institution-sensitive rather than universally stable.',
            '- Occupancy-normalized rankings still matter; this report only sharpens when the raw ranking itself should be treated as fragile.',
            '',
        ]
    )
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
