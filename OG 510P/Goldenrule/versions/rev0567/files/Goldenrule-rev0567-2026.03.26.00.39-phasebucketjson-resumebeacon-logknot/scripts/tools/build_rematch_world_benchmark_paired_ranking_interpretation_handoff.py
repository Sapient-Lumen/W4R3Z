#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
OCCUPANCY_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_occupancy_accounting_snapshot_20260306.json'
TURNOVER_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_turnover_tempo_snapshot_20260306.json'
RANK_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_rank_decomposition_snapshot_20260306.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_paired_ranking_interpretation_handoff.schema.json'
LINKED_QUESTION_IDS = ['SQ-014', 'SQ-015', 'SQ-016']


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_json(node: Any) -> str:
    blob = json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _extortion_levels(rank_report: dict[str, Any]) -> list[int]:
    return sorted(int(key.replace('ext', '')) for key in rank_report['canonical_occupancy_normalized_rank_order_by_extortion'])


def _canonical_rank_payload(rank_report: dict[str, Any]) -> tuple[list[str], list[int]]:
    rows = rank_report['canonical_occupancy_normalized_rank_order_by_extortion']
    canonical_order: list[str] | None = None
    matched_extortions: list[int] = []
    for key, order in sorted(rows.items()):
        extortion = int(key.replace('ext', ''))
        if canonical_order is None:
            canonical_order = list(order)
            matched_extortions.append(extortion)
            continue
        if list(order) == canonical_order:
            matched_extortions.append(extortion)
    if canonical_order is None:
        raise ValueError('rank report did not contain any canonical occupancy-normalized rank order rows')
    return canonical_order, matched_extortions


def _largest_disagreement_panel(rank_report: dict[str, Any]) -> dict[str, Any]:
    best_row: dict[str, Any] | None = None
    best_key: tuple[int, float] | None = None
    for row in rank_report['panel_rows']:
        key = (
            int(row['pairwise_inversions_overall_vs_occupancy_normalized']),
            float(1 - row['kendall_tau_overall_vs_occupancy_normalized']),
        )
        if best_key is None or key > best_key:
            best_key = key
            best_row = row
    if best_row is None:
        raise ValueError('rank report did not contain any panel rows')
    return {
        'extortion': best_row['extortion'],
        'delay': best_row['delay'],
        'kendall_tau_overall_vs_occupancy_normalized': best_row['kendall_tau_overall_vs_occupancy_normalized'],
        'pairwise_inversion_count': best_row['pairwise_inversions_overall_vs_occupancy_normalized'],
        'overall_rank_order': list(best_row['overall_rank_order']),
        'occupancy_normalized_rank_order': list(best_row['occupancy_normalized_rank_order']),
        'example_inversions': list(best_row['example_inversions']),
    }


def build_handoff(occupancy_report: dict[str, Any], turnover_report: dict[str, Any], rank_report: dict[str, Any]) -> dict[str, Any]:
    canonical_order, shared_extortions = _canonical_rank_payload(rank_report)
    turnover_headline = turnover_report['headline_findings']
    occupancy_headline = occupancy_report['headline_findings']
    rank_headline = rank_report['headline_findings']
    return {
        'contract_kind': 'rematch_world_benchmark_paired_ranking_interpretation_handoff',
        'contract_version': '2026-03-17.rematch_world_benchmark_paired_ranking_interpretation_handoff.v1',
        'planner_origin': 'copy the current proxy-era occupancy, tempo, and rank-decomposition interpretation into the benchmark seed until native rematch worlds can emit world-owned paired leaderboard and occupancy-flow summaries directly',
        'occupancy_accounting_report_path': 'artifacts/reports/rematch_proxy_occupancy_accounting_snapshot_20260306.json',
        'occupancy_accounting_report_sha256': sha256_json(occupancy_report),
        'turnover_tempo_report_path': 'artifacts/reports/rematch_proxy_turnover_tempo_snapshot_20260306.json',
        'turnover_tempo_report_sha256': sha256_json(turnover_report),
        'rank_decomposition_report_path': 'artifacts/reports/rematch_proxy_rank_decomposition_snapshot_20260306.json',
        'rank_decomposition_report_sha256': sha256_json(rank_report),
        'linked_question_ids': list(LINKED_QUESTION_IDS),
        'tested_extortion_values': _extortion_levels(rank_report),
        'tested_delay_values': list(occupancy_report['delay_levels']),
        'canonical_occupancy_normalized_rank_order': canonical_order,
        'extortions_sharing_canonical_order': shared_extortions,
        'occupancy_loss_summary': {
            'tested_cells': occupancy_headline['tested_cells'],
            'matched_share_monotone_nonincreasing_in_all_tested_cells': occupancy_headline['matched_share_monotone_nonincreasing_in_all_tested_cells'],
            'mean_share_component_fraction_of_delay_loss': occupancy_headline['mean_share_component_fraction_of_delay_loss'],
            'min_share_component_fraction_of_delay_loss': occupancy_headline['min_share_component_fraction_of_delay_loss'],
            'max_abs_in_match_payoff_drift_delay0_to_delay2': occupancy_headline['max_abs_in_match_payoff_drift_delay0_to_delay2'],
        },
        'rank_disagreement_summary': {
            'panels_checked': rank_headline['panels_checked'],
            'nonzero_delay_panels_checked': rank_headline['nonzero_delay_panels_checked'],
            'nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement': rank_headline['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement'],
            'total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels': rank_headline['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels'],
            'max_pairwise_inversions_in_any_panel': rank_headline['max_pairwise_inversions_in_any_panel'],
            'lowest_kendall_tau_overall_vs_occupancy_normalized': rank_headline['lowest_kendall_tau_overall_vs_occupancy_normalized'],
            'largest_disagreement_panel': _largest_disagreement_panel(rank_report),
        },
        'tempo_scaling_summary': {
            'highest_churn_delay2_cell': dict(turnover_headline['highest_churn_delay2_cell']),
            'lowest_churn_delay2_cell': dict(turnover_headline['lowest_churn_delay2_cell']),
            'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': turnover_headline['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
            'mean_abs_prediction_error': turnover_headline['mean_abs_prediction_error'],
            'max_abs_prediction_error': turnover_headline['max_abs_prediction_error'],
        },
        'ranking_interpretation_rule': 'If the raw aggregate leaderboard moves but the occupancy-normalized leaderboard does not, treat the movement as an occupancy or tempo artifact until stronger evidence shows within-match strategic quality changed too.',
        'upgrade_requirement': 'Replace this copied ranking-interpretation handoff with world-native occupancy, tempo, and paired leaderboard outputs once endogenous rematch benchmarks can emit those sections directly from real runs.',
        'size_discipline_note': 'Carry only one canonical occupancy-normalized order, one largest-disagreement panel, and the headline occupancy/tempo counts inside the benchmark seed; keep wider per-panel ranking tables and scenario rows in cited reports instead of copying them forward.',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the compact paired-ranking interpretation handoff section to copy into the rematch-world benchmark seed.')
    parser.add_argument('--occupancy-report', default=str(OCCUPANCY_PATH), help='Path to the proxy occupancy-accounting snapshot JSON.')
    parser.add_argument('--turnover-report', default=str(TURNOVER_PATH), help='Path to the proxy turnover-tempo snapshot JSON.')
    parser.add_argument('--rank-report', default=str(RANK_PATH), help='Path to the proxy rank-decomposition snapshot JSON.')
    parser.add_argument('--output', help='Write the handoff JSON to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full handoff JSON.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        p = Path(raw)
        return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

    handoff = build_handoff(
        load_json(resolve(args.occupancy_report)),
        load_json(resolve(args.turnover_report)),
        load_json(resolve(args.rank_report)),
    )
    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(handoff, schema)

    if args.summary_json:
        summary = {
            'occupancy_accounting_report_sha256': handoff['occupancy_accounting_report_sha256'],
            'turnover_tempo_report_sha256': handoff['turnover_tempo_report_sha256'],
            'rank_decomposition_report_sha256': handoff['rank_decomposition_report_sha256'],
            'canonical_occupancy_normalized_rank_order': handoff['canonical_occupancy_normalized_rank_order'],
            'extortions_sharing_canonical_order': handoff['extortions_sharing_canonical_order'],
            'nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement': handoff['rank_disagreement_summary']['nonzero_delay_panels_with_raw_vs_occupancy_normalized_rank_disagreement'],
            'total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels': handoff['rank_disagreement_summary']['total_pairwise_inversions_overall_vs_occupancy_normalized_in_nonzero_delay_panels'],
            'mean_share_component_fraction_of_delay_loss': handoff['occupancy_loss_summary']['mean_share_component_fraction_of_delay_loss'],
            'highest_vs_lowest_churn_delay2_matched_share_loss_ratio': handoff['tempo_scaling_summary']['highest_vs_lowest_churn_delay2_matched_share_loss_ratio'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(handoff, indent=2, sort_keys=True) + '\n'
    if args.output:
        out = resolve(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding='utf-8')
        print(f'rematch-world-benchmark-paired-ranking-interpretation-handoff: wrote {out.relative_to(ROOT).as_posix()}')
        return 0
    print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
