#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.md'
UNCERTAINTY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_repeat_uncertainty_snapshot_20260307.json'
MIN_DWELL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_min_dwell_snapshot_20260307.json'
CAP_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.json'
CAP_SAFE_CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.json'
LOWER_GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_lower_guarantee_three_cap_snapshot_20260308.json'

INTERVAL_RE = re.compile(r'(?P<kind>[a-z\-]+) (?P<start>\d+)–(?P<end>\d+)$')
REFERENCE_REPEATS = [0.15, 0.18, 0.25]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _parse_interval_summary(interval_summary: str) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for chunk in interval_summary.split('; '):
        match = INTERVAL_RE.fullmatch(chunk)
        if match is None:
            raise ValueError(f'unexpected interval chunk: {chunk!r}')
        rows.append(
            {
                'state_kind_label': match.group('kind'),
                'start_unique_appends': int(match.group('start')),
                'end_unique_appends': int(match.group('end')),
                'width_unique_appends': int(match.group('end')) - int(match.group('start')) + 1,
            }
        )
    return rows


def _transition_boundaries(interval_summary: str) -> list[int]:
    return [int(row['start_unique_appends']) for row in _parse_interval_summary(interval_summary)[1:]]


def _minimum_interval_width(interval_summary: str) -> int:
    return min(int(row['width_unique_appends']) for row in _parse_interval_summary(interval_summary))


def _uncertainty_row(report: dict[str, Any], gain_share: float) -> dict[str, Any]:
    return next(
        row for row in report['uncertainty_rows']
        if float(row['minimum_gain_share_of_full_dynamic_savings']) == gain_share
    )


def _focal_min_dwell_row(report: dict[str, Any], dwell: int) -> dict[str, Any]:
    return next(
        row for row in report['frontier_rows']
        if int(row['minimum_dwell_start_unique_appends']) <= dwell <= int(row['minimum_dwell_end_unique_appends'])
    )


def _build_near_exact_rows(uncertainty: dict[str, Any], min_dwell: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    uncertainty_99 = _uncertainty_row(uncertainty, 0.99)
    focal_row = _focal_min_dwell_row(min_dwell, 2)
    rows: list[dict[str, Any]] = []

    for repeat_value in REFERENCE_REPEATS:
        if repeat_value == 0.18:
            row = {
                'expected_repeat_lookups': repeat_value,
                'minimum_dwell_unique_appends': 2,
                'selected_transition_count': int(focal_row['selected_transition_count']),
                'gain_share_of_full_dynamic_savings': float(focal_row['gain_share_of_full_dynamic_savings']),
                'regret_vs_unbounded_dynamic': float(focal_row['regret_vs_unbounded_dynamic']),
                'interval_summary': str(focal_row['interval_summary']),
                'transition_boundaries_unique_appends': _transition_boundaries(str(focal_row['interval_summary'])),
                'minimum_interval_width_unique_appends': _minimum_interval_width(str(focal_row['interval_summary'])),
                'source_note': 'exact focal dwell-2 row from the saved 0.18 minimum-dwell frontier',
            }
        else:
            source_row = next(
                row for row in uncertainty_99['anchor_rows']
                if float(row['expected_repeat_lookups']) == repeat_value
            )
            interval_summary = str(source_row['interval_summary'])
            min_width = _minimum_interval_width(interval_summary)
            row = {
                'expected_repeat_lookups': repeat_value,
                'minimum_dwell_unique_appends': 2,
                'selected_transition_count': int(source_row['selected_transition_count']),
                'gain_share_of_full_dynamic_savings': float(source_row['gain_share_of_full_dynamic_savings']),
                'regret_vs_unbounded_dynamic': float(source_row['regret_vs_unbounded_dynamic']),
                'interval_summary': interval_summary,
                'transition_boundaries_unique_appends': _transition_boundaries(interval_summary),
                'minimum_interval_width_unique_appends': min_width,
                'source_note': 'copied from the saved 0.99 uncertainty anchor row because every interval already has width >= 2, so the same regret-0 schedule remains feasible at dwell 2',
            }
        rows.append(row)

    union = sorted({p for row in rows for p in row['transition_boundaries_unique_appends']})
    findings = {
        'exact_hard_cap': 11,
        'representative_anchor_minimum_dwell_unique_appends': 2,
        'union_transition_checkpoints_unique_appends': union,
        'union_transition_checkpoint_count': len(union),
        'maximum_selected_transition_count': max(row['selected_transition_count'] for row in rows),
        'minimum_selected_transition_count': min(row['selected_transition_count'] for row in rows),
        'worst_case_gain_share_of_full_dynamic_savings': min(row['gain_share_of_full_dynamic_savings'] for row in rows),
        'has_tail_checkpoint_255': 255 in union,
    }
    return rows, findings


def _build_report() -> dict[str, Any]:
    uncertainty = _load(UNCERTAINTY_REPORT)
    min_dwell = _load(MIN_DWELL_REPORT)
    cap_staircase = _load(CAP_STAIRCASE_REPORT)
    cap_safe_checkpoints = _load(CAP_SAFE_CHECKPOINT_REPORT)
    lower_guarantee = _load(LOWER_GUARANTEE_REPORT)

    tier_by_name = {row['tier']: row for row in cap_staircase['tier_rows']}
    near_exact_rows, near_exact_findings = _build_near_exact_rows(uncertainty, min_dwell)
    near_optimal_findings = cap_safe_checkpoints['headline_findings']
    lower_findings = lower_guarantee['headline_findings']

    tier_rows = [
        {
            'tier': 'near_exact',
            'minimum_gain_share_of_full_dynamic_savings': 0.99,
            'exact_hard_cap': int(tier_by_name['near_exact']['exact_hard_cap']),
            'representative_anchor_minimum_dwell_unique_appends': 2,
            'union_transition_checkpoints_unique_appends': near_exact_findings['union_transition_checkpoints_unique_appends'],
            'union_transition_checkpoint_count': near_exact_findings['union_transition_checkpoint_count'],
            'transition_range': {
                'minimum_selected_transition_count': near_exact_findings['minimum_selected_transition_count'],
                'maximum_selected_transition_count': near_exact_findings['maximum_selected_transition_count'],
            },
            'worst_case_gain_share_of_full_dynamic_savings': near_exact_findings['worst_case_gain_share_of_full_dynamic_savings'],
            'notable_checkpoint_delta_vs_next_tier': sorted(
                set(near_exact_findings['union_transition_checkpoints_unique_appends'])
                - set(near_optimal_findings['cap_safe_union_transition_checkpoints_unique_appends'])
            ),
            'notable_note': 'near-exact robustness adds six early/micro checkpoints plus the unique tail checkpoint 255 relative to the 0.95 tier.',
        },
        {
            'tier': 'near_optimal',
            'minimum_gain_share_of_full_dynamic_savings': 0.95,
            'exact_hard_cap': int(tier_by_name['near_optimal']['exact_hard_cap']),
            'representative_anchor_minimum_dwell_unique_appends': int(near_optimal_findings['near_optimal_cap_safe_anchor_minimum_dwell_unique_appends']),
            'union_transition_checkpoints_unique_appends': near_optimal_findings['cap_safe_union_transition_checkpoints_unique_appends'],
            'union_transition_checkpoint_count': near_optimal_findings['cap_safe_union_transition_checkpoint_count'],
            'transition_range': {'minimum_selected_transition_count': 2, 'maximum_selected_transition_count': 5},
            'worst_case_gain_share_of_full_dynamic_savings': 0.980481,
            'notable_checkpoint_delta_vs_next_tier': sorted(
                set(near_optimal_findings['cap_safe_union_transition_checkpoints_unique_appends'])
                - set(lower_findings['anchor_union_transition_checkpoints_unique_appends'])
            ),
            'notable_note': 'the checkpoint-neutral 0.95 tier keeps the late-tail checkpoints 230 and 239 and two mid-band checkpoints 24 and 63 that disappear once the guarantee relaxes to 0.85.',
        },
        {
            'tier': 'lower_guarantee',
            'minimum_gain_share_of_full_dynamic_savings': float(lower_findings['target_minimum_gain_share_of_full_dynamic_savings']),
            'exact_hard_cap': int(lower_findings['promoted_exact_band_wide_hard_cap']),
            'representative_anchor_minimum_dwell_unique_appends': int(lower_findings['promoted_exact_anchor_minimum_dwell_unique_appends']),
            'union_transition_checkpoints_unique_appends': lower_findings['anchor_union_transition_checkpoints_unique_appends'],
            'union_transition_checkpoint_count': lower_findings['anchor_union_transition_checkpoint_count'],
            'transition_range': lower_findings['anchor_transition_range'],
            'worst_case_gain_share_of_full_dynamic_savings': float(lower_findings['anchor_worst_case_gain_share_of_full_dynamic_savings']),
            'notable_checkpoint_delta_vs_next_tier': [],
            'notable_note': 'the relaxed 0.85 tier compresses the union to five checkpoints and removes both late-tail flips from the maintenance calendar.',
        },
    ]

    checkpoint_counts = [row['union_transition_checkpoint_count'] for row in tier_rows]
    report = {
        'focus': 'Turn the exact uncertainty-cap staircase into an exact uncertainty-checkpoint staircase so inheritors can see how much maintenance surface each guarantee tier really carries.',
        'headline_findings': {
            'checkpoint_union_counts_descending_by_guarantee': checkpoint_counts,
            'near_exact_union_transition_checkpoint_count': tier_rows[0]['union_transition_checkpoint_count'],
            'near_optimal_union_transition_checkpoint_count': tier_rows[1]['union_transition_checkpoint_count'],
            'lower_guarantee_union_transition_checkpoint_count': tier_rows[2]['union_transition_checkpoint_count'],
            'near_exact_extra_checkpoints_vs_near_optimal': tier_rows[0]['notable_checkpoint_delta_vs_next_tier'],
            'near_optimal_removed_checkpoints_when_relaxing_to_lower_guarantee': tier_rows[1]['notable_checkpoint_delta_vs_next_tier'],
            'lower_guarantee_adds_unique_checkpoint_56': 56 in tier_rows[2]['union_transition_checkpoints_unique_appends'],
            'main_rule': 'treat repeat-uncertainty operating modes as a checkpoint staircase as well as a cap staircase: the exact 0.99, 0.95, and 0.85 lanes currently require union checkpoint calendars of 14, 8, and 5 values respectively.',
        },
        'decision_rules': [
            'When maintenance scheduling is the bottleneck, compare exact union checkpoint counts together with hard caps instead of looking at cap counts alone.',
            'Use the 0.95 tier when the archive still wants near-optimal uncertainty safety: it stays checkpoint-neutral with the dwell-9 default and keeps the union to eight values.',
            'Relax to the 0.85 tier only when the guarantee can really be weakened: that cuts the union to five checkpoints and removes the late-tail 230/239 checks.',
            'Reserve the 0.99 tier for truly near-exact preservation goals: it expands the union to fourteen values and reintroduces the unique tail checkpoint 255.',
        ],
        'tier_rows': tier_rows,
        'near_exact_boundary_rows': near_exact_rows,
        'source_reports': [
            str(UNCERTAINTY_REPORT.relative_to(ROOT)),
            str(MIN_DWELL_REPORT.relative_to(ROOT)),
            str(CAP_STAIRCASE_REPORT.relative_to(ROOT)),
            str(CAP_SAFE_CHECKPOINT_REPORT.relative_to(ROOT)),
            str(LOWER_GUARANTEE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }
    return report


def _render_md(report: dict[str, Any]) -> str:
    findings = report['headline_findings']
    lines = [
        '# Rematch Proxy Delta Decision Packet Compact Repeat-State Uncertainty-Checkpoint Staircase Snapshot — 2026-03-08',
        '',
        '## Focus',
        f"- {report['focus']}",
        '',
        '## Headline findings',
        f"- the exact repeat-uncertainty tiers form a maintenance staircase as well as a cap staircase: union checkpoint counts are `{findings['checkpoint_union_counts_descending_by_guarantee']}` for guarantee floors `0.99`, `0.95`, and `0.85` respectively.",
        f"- near-exact `0.99` robustness adds checkpoints `{findings['near_exact_extra_checkpoints_vs_near_optimal']}` beyond the near-optimal `0.95` tier, including the unique tail checkpoint `255`.",
        f"- relaxing from `0.95` to `0.85` removes checkpoints `{findings['near_optimal_removed_checkpoints_when_relaxing_to_lower_guarantee']}` and leaves only one new relaxed-tier checkpoint marker `56`: `lower_guarantee_adds_unique_checkpoint_56 = {findings['lower_guarantee_adds_unique_checkpoint_56']}`.",
        f"- main rule: {findings['main_rule']}",
        '',
        '## Exact checkpoint staircase tiers',
        '| tier | min gain share | hard cap | anchor dwell | checkpoint count | checkpoint union | transition range | note |',
        '|---|---:|---:|---:|---:|---|---|---|',
    ]
    for row in report['tier_rows']:
        lines.append(
            f"| {row['tier']} | {row['minimum_gain_share_of_full_dynamic_savings']} | {row['exact_hard_cap']} | {row['representative_anchor_minimum_dwell_unique_appends']} | {row['union_transition_checkpoint_count']} | {row['union_transition_checkpoints_unique_appends']} | {row['transition_range']['minimum_selected_transition_count']}–{row['transition_range']['maximum_selected_transition_count']} | {row['notable_note']} |"
        )
    lines.extend([
        '',
        '## Near-exact dwell-2 boundary rows used to certify the 0.99 tier',
        '| repeat budget | transitions | gain share | regret vs full dynamic | min interval width | checkpoints | source note |',
        '|---:|---:|---:|---:|---:|---|---|',
    ])
    for row in report['near_exact_boundary_rows']:
        lines.append(
            f"| {row['expected_repeat_lookups']} | {row['selected_transition_count']} | {row['gain_share_of_full_dynamic_savings']} | {row['regret_vs_unbounded_dynamic']} | {row['minimum_interval_width_unique_appends']} | {row['transition_boundaries_unique_appends']} | {row['source_note']} |"
        )
    lines.extend([
        '',
        '## Decision rules',
    ])
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.extend([
        '',
        '## Source reports',
    ])
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
