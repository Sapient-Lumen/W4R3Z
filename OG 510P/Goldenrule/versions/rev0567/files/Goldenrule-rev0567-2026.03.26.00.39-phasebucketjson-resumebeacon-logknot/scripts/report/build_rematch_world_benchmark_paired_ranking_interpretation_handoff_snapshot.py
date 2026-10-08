#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff_snapshot_20260317.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff_snapshot_20260317.md'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def render_md(report: dict[str, Any]) -> str:
    canonical = ', '.join(f'`{policy}`' for policy in report['canonical_occupancy_normalized_rank_order'])
    extortions = ', '.join(f'`{ext}`' for ext in report['extortions_sharing_canonical_order'])
    panel = report['largest_disagreement_panel']
    return '\n'.join([
        '# Rematch-world benchmark paired-ranking interpretation handoff snapshot — 2026-03-17',
        '',
        f"Focus: {report['focus']}",
        '',
        '## Local result',
        '',
        '- The benchmark seed now carries one compact paired-ranking interpretation handoff copied from the proxy occupancy, tempo, and rank-decomposition reports instead of forcing inheritors to reopen those sources separately.',
        f"- The copied handoff says the occupancy-normalized leaderboard stays canonical across extortion shares {extortions}: {canonical}.",
        f"- Raw-vs-normalized disagreement appears in `{report['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement']}` of `{report['nonzero_delay_panels_checked']}` nonzero-delay panels, with `{report['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels']}` total pairwise inversions.",
        f"- The sharpest disagreement is extortion `{panel['extortion']}`, delay `{panel['delay']}`, where Kendall tau drops to `{panel['kendall_tau_overall_vs_occupancy_normalized']}` and `{panel['pairwise_inversion_count']}` pairwise inversions appear.",
        '',
        '## Implementor guidance',
        '',
        '- Treat paired leaderboards as part of the retained world contract, not as optional report polish.',
        '- Default raw-only leaderboard movement to an occupancy or tempo artifact until the occupancy-normalized leaderboard moves too.',
        '- Keep the copied handoff frozen until endogenous rematch runs can emit world-native occupancy-flow, turnover, and paired-ranking interpretation surfaces directly.',
        '',
    ])


def main() -> int:
    handoff = load_json(EXAMPLE)
    report = {
        'snapshot_date': '2026-03-17',
        'focus': 'wire a compact paired-ranking interpretation handoff directly into the rematch-world benchmark seed so future implementors can read raw-vs-normalized leaderboard movement from one frozen packet',
        'analysis_script': 'scripts/report/build_rematch_world_benchmark_paired_ranking_interpretation_handoff_snapshot.py',
        'occupancy_accounting_report_path': handoff['occupancy_accounting_report_path'],
        'occupancy_accounting_report_sha256': handoff['occupancy_accounting_report_sha256'],
        'turnover_tempo_report_path': handoff['turnover_tempo_report_path'],
        'turnover_tempo_report_sha256': handoff['turnover_tempo_report_sha256'],
        'rank_decomposition_report_path': handoff['rank_decomposition_report_path'],
        'rank_decomposition_report_sha256': handoff['rank_decomposition_report_sha256'],
        'canonical_occupancy_normalized_rank_order': handoff['canonical_occupancy_normalized_rank_order'],
        'extortions_sharing_canonical_order': handoff['extortions_sharing_canonical_order'],
        'nonzero_delay_panels_checked': handoff['rank_disagreement_summary']['nonzero_delay_panels_checked'],
        'nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement': handoff['rank_disagreement_summary']['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement'],
        'total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels': handoff['rank_disagreement_summary']['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels'],
        'mean_share_component_fraction_of_delay_loss': handoff['occupancy_loss_summary']['mean_share_component_fraction_of_delay_loss'],
        'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
        'largest_disagreement_panel': handoff['rank_disagreement_summary']['largest_disagreement_panel'],
        'recommended_next_move': 'Keep the copied paired-ranking interpretation handoff frozen in the benchmark seed and use it to interpret raw-vs-normalized leaderboard changes until endogenous rematch runs can emit world-native ranking explanation surfaces.',
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_md(report) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-paired-ranking-interpretation-handoff-snapshot: wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'rematch-world-benchmark-paired-ranking-interpretation-handoff-snapshot: wrote {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
