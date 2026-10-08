#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.md'
TOLERANCE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
CANONICAL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'

ORDER = ['near_exact', 'near_optimal', 'lower_guarantee']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    tolerance_rows = {row['tier']: row for row in _load(TOLERANCE_REPORT)['tier_rows']}
    guarantee_rows = {row['tier']: row for row in _load(GUARANTEE_REPORT)['tier_rows']}
    canonical_rows = {row['tier']: row for row in _load(CANONICAL_REPORT)['tier_rows']}

    rows: list[dict[str, Any]] = []
    for tier in ORDER:
        tolerance = tolerance_rows[tier]
        guarantee = guarantee_rows[tier]
        canonical = canonical_rows[tier]
        rows.append(
            {
                'tier': tier,
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': guarantee['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
                'actual_certified_gain_share_floor_of_full_dynamic_savings': guarantee['actual_certified_gain_share_floor_of_full_dynamic_savings'],
                'exact_hard_cap': tolerance['exact_hard_cap'],
                'canonical_anchor_minimum_dwell_unique_appends': canonical['canonical_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band_start_unique_appends': tolerance['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': tolerance['exact_dwell_band_end_unique_appends'],
                'exact_dwell_band_width_unique_appends': tolerance['exact_dwell_band_width_unique_appends'],
                'minimum_anchor_slack_unique_appends': tolerance['minimum_anchor_slack_unique_appends'],
                'union_transition_checkpoint_count': tolerance['union_transition_checkpoint_count'],
            }
        )
    return rows


def _coverage_rows(tier_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous_end: int | None = None
    for row in tier_rows:
        start = int(row['exact_dwell_band_start_unique_appends'])
        end = int(row['exact_dwell_band_end_unique_appends'])
        if previous_end is None:
            relation = 'first_exact_band'
            gap_from_previous = None
            intervening_uncovered_dwell_values: list[int] = []
        else:
            if start <= previous_end + 1:
                relation = 'adjacent_or_overlapping_with_previous_exact_band'
                gap_from_previous = 0
                intervening_uncovered_dwell_values = []
            else:
                relation = 'separated_from_previous_exact_band_by_internal_gap'
                gap_from_previous = start - previous_end - 1
                intervening_uncovered_dwell_values = list(range(previous_end + 1, start))
        rows.append(
            {
                'tier': row['tier'],
                'exact_dwell_band': [start, end],
                'relation_to_previous_exact_band': relation,
                'internal_gap_from_previous_exact_band_unique_appends': gap_from_previous,
                'intervening_uncovered_dwell_values_unique_appends': intervening_uncovered_dwell_values,
            }
        )
        previous_end = end
    return rows


def _headline_findings(tier_rows: list[dict[str, Any]], coverage_rows: list[dict[str, Any]]) -> dict[str, Any]:
    indexed = {row['tier']: row for row in tier_rows}
    near_exact = indexed['near_exact']
    near_optimal = indexed['near_optimal']
    lower = indexed['lower_guarantee']
    internal_gap = coverage_rows[1]['intervening_uncovered_dwell_values_unique_appends']
    return {
        'exact_covered_dwell_intervals_unique_appends': [
            [near_exact['exact_dwell_band_start_unique_appends'], near_exact['exact_dwell_band_end_unique_appends']],
            [near_optimal['exact_dwell_band_start_unique_appends'], lower['exact_dwell_band_end_unique_appends']],
        ],
        'largest_internal_exact_dwell_gap_unique_appends': internal_gap,
        'largest_internal_exact_dwell_gap_width_unique_appends': len(internal_gap),
        'exact_precision_band_is_isolated': near_exact['exact_dwell_band_width_unique_appends'] == 1 and bool(internal_gap),
        'next_exact_non_precision_band_starts_at_unique_appends': near_optimal['exact_dwell_band_start_unique_appends'],
        'near_optimal_and_lower_guarantee_bands_are_contiguous': near_optimal['exact_dwell_band_end_unique_appends'] + 1 == lower['exact_dwell_band_start_unique_appends'],
        'no_current_exact_positive_slack_band_below_unique_appends': near_optimal['exact_dwell_band_start_unique_appends'],
        'main_rule': 'Treat dwell values 3 through 7 as an exact uncertainty-certification gap, not as a live retuning region: the current exact menu covers dwell 2 as an isolated precision point and then resumes only at dwell 8, while the 0.95 and 0.85 bands join contiguously at 18/19.',
    }


def _decision_rules() -> list[str]:
    return [
        'Do not spend implementor time sweeping dwell 3 through 7 when the goal is to stay inside the current exact uncertainty-certified menu: that five-step region is not covered by any saved exact tier.',
        'Treat dwell 2 as a special isolated precision point tied to the exact 0.99 lane, not as the left edge of a broader small-dwell family.',
        'When a deployment needs any positive anchor slack or any dwell-band width above 1, jump directly to the exact 0.95 band beginning at dwell 8 instead of trying intermediate small dwells.',
        'Treat the boundary between the exact 0.95 and 0.85 lanes as continuous in dwell space: the certified menu stays live from dwell 8 through 32 with no internal gap once the 0.95 band begins.',
        'Treat dwell values below 2, between 3 and 7, and above 32 as outside the current exact uncertainty-certified dwell menu unless new frontier evidence is generated.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    coverage_rows = _coverage_rows(tier_rows)
    return {
        'focus': 'Expose the topology of the current exact uncertainty-certified dwell menu so inheritors can skip dead retuning regions and jump directly to the next live exact band.',
        'headline_findings': _headline_findings(tier_rows, coverage_rows),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'coverage_rows': coverage_rows,
        'source_reports': [
            str(TOLERANCE_REPORT.relative_to(ROOT)),
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(CANONICAL_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty dwell-coverage topology snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Tier rows')
    for row in report['tier_rows']:
        lines.append(
            '- '
            f"{row['tier']}: rounded label `{row['rounded_label_minimum_gain_share_of_full_dynamic_savings']}`; "
            f"actual floor `{row['actual_certified_gain_share_floor_of_full_dynamic_savings']}`; "
            f"cap `{row['exact_hard_cap']}`; canonical anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}`; "
            f"band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`; "
            f"width `{row['exact_dwell_band_width_unique_appends']}`; slack `{row['minimum_anchor_slack_unique_appends']}`; "
            f"checkpoints `{row['union_transition_checkpoint_count']}`"
        )
    lines.append('')
    lines.append('## Coverage rows')
    for row in report['coverage_rows']:
        lines.append(
            '- '
            f"{row['tier']}: band `{row['exact_dwell_band'][0]}-{row['exact_dwell_band'][1]}`; "
            f"relation `{row['relation_to_previous_exact_band']}`; "
            f"gap from previous `{row['internal_gap_from_previous_exact_band_unique_appends']}`; "
            f"uncovered dwells `{row['intervening_uncovered_dwell_values_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Source reports')
    for item in report['source_reports']:
        lines.append(f'- `{item}`')
    lines.append('')
    lines.append(f"Source script: `{report['source_script']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n')
    OUT_MD.write_text(_render_md(report))


if __name__ == '__main__':
    main()
