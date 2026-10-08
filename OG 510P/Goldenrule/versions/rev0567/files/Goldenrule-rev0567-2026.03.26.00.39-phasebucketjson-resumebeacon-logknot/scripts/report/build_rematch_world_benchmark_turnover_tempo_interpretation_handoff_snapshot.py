#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_turnover_tempo_interpretation_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    high = report['highest_churn_delay2_cell']
    low = report['lowest_churn_delay2_cell']
    return '\n'.join([
        '# Rematch-world benchmark turnover-tempo interpretation handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact turnover-tempo interpretation handoff copied from the proxy turnover report instead of forcing inheritors to reopen the full scenario table.',
        f"- Across `{report['scenario_means_checked']}` scenario means, tempo predicts matched-round share with mean absolute error `{report['mean_abs_prediction_error']}` and max absolute error `{report['max_abs_prediction_error']}`.",
        f"- The highest-churn delay-2 anchor is `{high['policy']}` at extortion `{high['extortion']}` with avg match length `{high['avg_match_length']}` and matched-share loss `{high['matched_share_loss']}`.",
        f"- The lowest-churn delay-2 anchor is `{low['policy']}` at extortion `{low['extortion']}` with avg match length `{low['avg_match_length']}` and matched-share loss `{low['matched_share_loss']}`.",
        f"- The same nominal delay therefore induces a `{report['highest_vs_lowest_churn_delay2_matched_share_loss_ratio']}`x larger occupancy penalty in the highest-churn anchor than in the lowest-churn anchor.",
        '',
        '## Implementor guidance',
        '',
        '- Publish one turnover or persistence metric beside every delay field so fixed-delay comparisons remain comparable across worlds.',
        '- Keep persistence and search dead-time as separate world fields rather than folding them into one friction scalar.',
        '- Keep the copied handoff frozen until endogenous rematch runs can emit native tempo-aware turnover sections directly.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact turnover-tempo interpretation handoff directly into the rematch-world benchmark seed so future implementors can cite one frozen packet for tempo-scaled delay tax',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_turnover_tempo_interpretation_handoff_snapshot.py',
        'turnover_tempo_report_path': handoff['turnover_tempo_report_path'],
        'turnover_tempo_report_sha256': handoff['turnover_tempo_report_sha256'],
        'scenario_means_checked': handoff['tempo_scaling_summary']['scenario_means_checked'],
        'mean_abs_prediction_error': handoff['tempo_scaling_summary']['mean_abs_prediction_error'],
        'max_abs_prediction_error': handoff['tempo_scaling_summary']['max_abs_prediction_error'],
        'rms_prediction_error': handoff['tempo_scaling_summary']['rms_prediction_error'],
        'highest_churn_delay2_cell': handoff['tempo_scaling_summary']['highest_churn_delay2_cell'],
        'lowest_churn_delay2_cell': handoff['tempo_scaling_summary']['lowest_churn_delay2_cell'],
        'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
        'recommended_next_move': 'Keep the copied turnover-tempo interpretation handoff frozen in the benchmark seed and use it to interpret fixed-delay comparisons until endogenous rematch runs can emit native persistence-normalized turnover sections.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-turnover-tempo-interpretation-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-turnover-tempo-interpretation-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
