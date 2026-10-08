#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.md'

DELAY_LEVELS = (0, 1, 2)
EXTORTION_LEVELS = (20, 50, 80)
POLICY_ORDER = ('CCEEE', 'CCDDE', 'always_c', 'courteous_firm', 'DCECC')


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


def _scenario_row(policy_name: str, scenario_key: str, metrics: dict[str, float]) -> dict[str, object]:
    delay = int(scenario_key.split('delay')[1])
    extortion = int(scenario_key.split('_')[0].removeprefix('ext'))
    avg_match_length = float(metrics['avg_match_length'])
    matched_round_share = float(metrics['matched_round_share'])
    predicted = avg_match_length / (avg_match_length + delay) if delay else 1.0
    return {
        'policy': policy_name,
        'extortion': extortion,
        'delay': delay,
        'avg_match_length': avg_match_length,
        'matched_round_share': matched_round_share,
        'dead_round_share': float(metrics['dead_round_share']),
        'in_match_avg_payoff': float(metrics['in_match_avg_payoff']),
        'overall_avg_payoff': float(metrics['overall_avg_payoff']),
        'exit_rate': float(metrics['exit_rate']),
        'predicted_matched_round_share_from_tempo': predicted,
        'abs_prediction_error': abs(matched_round_share - predicted),
    }


def main() -> int:
    src = _read_json(SRC)
    scenario_means = src['scenario_means']

    rows: list[dict[str, object]] = []
    for policy_name in POLICY_ORDER:
        block = scenario_means[policy_name]
        for ext in EXTORTION_LEVELS:
            for delay in DELAY_LEVELS:
                key = f'ext{ext}_delay{delay}'
                rows.append(_scenario_row(policy_name, key, block[key]))

    prediction_errors = [float(row['abs_prediction_error']) for row in rows]
    delay2_rows = [row for row in rows if int(row['delay']) == 2]
    delay2_rows_sorted = sorted(delay2_rows, key=lambda row: float(row['avg_match_length']))
    highest_churn = delay2_rows_sorted[0]
    lowest_churn = delay2_rows_sorted[-1]

    delay_loss_rows: list[dict[str, object]] = []
    for policy_name in POLICY_ORDER:
        block = scenario_means[policy_name]
        for ext in EXTORTION_LEVELS:
            d0 = block[f'ext{ext}_delay0']
            for delay in (1, 2):
                dx = block[f'ext{ext}_delay{delay}']
                matched_share_loss = float(d0['matched_round_share']) - float(dx['matched_round_share'])
                overall_payoff_loss = float(d0['overall_avg_payoff']) - float(dx['overall_avg_payoff'])
                delay_loss_rows.append(
                    {
                        'policy': policy_name,
                        'extortion': ext,
                        'delay': delay,
                        'avg_match_length': float(dx['avg_match_length']),
                        'matched_share_loss': matched_share_loss,
                        'overall_payoff_loss': overall_payoff_loss,
                        'exit_rate': float(dx['exit_rate']),
                    }
                )

    delay2_ratio = (
        float(highest_churn['matched_round_share'])
        if False
        else (
            float(delay_loss_rows[0]['matched_share_loss'])
        )
    )
    highest_churn_delay2 = min((row for row in delay_loss_rows if int(row['delay']) == 2), key=lambda row: float(row['avg_match_length']))
    lowest_churn_delay2 = max((row for row in delay_loss_rows if int(row['delay']) == 2), key=lambda row: float(row['avg_match_length']))
    churn_loss_ratio = float(highest_churn_delay2['matched_share_loss']) / float(lowest_churn_delay2['matched_share_loss'])

    summary = {
        'focus': 'Show that the current proxy\'s fixed rematch delay behaves like a turnover-scaled tax: shorter temporary partnerships pay the same delay more often.',
        'source_report': str(SRC.relative_to(ROOT)),
        'headline_findings': {
            'scenario_means_checked': len(rows),
            'max_abs_prediction_error': max(prediction_errors),
            'mean_abs_prediction_error': statistics.fmean(prediction_errors),
            'rms_prediction_error': statistics.fmean(error * error for error in prediction_errors) ** 0.5,
            'highest_churn_delay2_cell': {
                'policy': highest_churn_delay2['policy'],
                'extortion': highest_churn_delay2['extortion'],
                'avg_match_length': highest_churn_delay2['avg_match_length'],
                'matched_share_loss': highest_churn_delay2['matched_share_loss'],
            },
            'lowest_churn_delay2_cell': {
                'policy': lowest_churn_delay2['policy'],
                'extortion': lowest_churn_delay2['extortion'],
                'avg_match_length': lowest_churn_delay2['avg_match_length'],
                'matched_share_loss': lowest_churn_delay2['matched_share_loss'],
            },
            'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': churn_loss_ratio,
            'interpretation': 'In the current proxy, a fixed rematch delay is not one universal tax. It scales with partnership tempo: shorter matches pay the same dead-time more often, so persistence and search delay must stay separate in the world contract.',
        },
        'scenario_rows': _round(rows),
        'delay_loss_rows': _round(delay_loss_rows),
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Turnover Tempo Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the occupancy-accounting snapshot for the current exogenous-pool leave/rematch proxy',
        '- asked one narrow question: how much of the delay tax is explained by simple partnership tempo?',
        '- compared observed `matched_round_share` with the long-horizon tempo prediction `avg_match_length / (avg_match_length + rematch_delay)`',
        '',
        'Main finding:',
        f"- Across all `{len(rows)}` policy/extortion/delay scenario means, the tempo prediction has max absolute error `{max(prediction_errors):.6f}` and mean absolute error `{statistics.fmean(prediction_errors):.6f}`.",
        '- So in the current proxy, fixed rematch delay is almost entirely a tempo-scaled occupancy tax.',
        f"- At `delay=2`, the highest-churn tested cell (`{highest_churn_delay2['policy']}`, extortion `{highest_churn_delay2['extortion']}`) has `avg_match_length={highest_churn_delay2['avg_match_length']:.6f}` and loses `{highest_churn_delay2['matched_share_loss']:.6f}` matched-share points.",
        f"- The lowest-churn tested cells (`avg_match_length={lowest_churn_delay2['avg_match_length']:.6f}`) lose only `{lowest_churn_delay2['matched_share_loss']:.6f}` matched-share points, a `{churn_loss_ratio:.3f}x` smaller penalty.",
        '',
        'Why this matters:',
        '- The archive already separated occupancy from in-match behavior.',
        '- This pass shows why that is not enough by itself: the occupancy term is strongly governed by partnership tempo (`avg_match_length` / turnover), not only by the nominal delay value.',
        '- Therefore future rematch worlds should expose both a persistence / turnover field and a separate search-dead-time field.',
        '',
        'Selected delay-2 tempo rows:',
        '',
        '| policy | extortion | avg_match_length | matched_round_share | predicted_from_tempo | abs_error | matched_share_loss_vs_delay0 | exit_rate |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ]

    delay0_map = {
        (row['policy'], row['extortion']): row
        for row in rows
        if int(row['delay']) == 0
    }
    for row in delay2_rows_sorted:
        d0 = delay0_map[(str(row['policy']), int(row['extortion']))]
        matched_share_loss = float(d0['matched_round_share']) - float(row['matched_round_share'])
        lines.append(
            '| `{}` | `{}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` | `{:.6f}` |'.format(
                row['policy'],
                row['extortion'],
                float(row['avg_match_length']),
                float(row['matched_round_share']),
                float(row['predicted_matched_round_share_from_tempo']),
                float(row['abs_prediction_error']),
                matched_share_loss,
                float(row['exit_rate']),
            )
        )

    lines.extend(
        [
            '',
            'Implementor consequence:',
            '- Do not compare identical `rematch_delay` settings across worlds or policies without also publishing `avg_match_length` or an equivalent turnover-rate field.',
            '- Otherwise one world can look “more delay-sensitive” simply because it creates shorter temporary partnerships, not because the nominal delay knob changed.',
            '',
        ]
    )

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
