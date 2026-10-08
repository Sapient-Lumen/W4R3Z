#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.md'
CHECKPOINT_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
TOLERANCE_STAIRCASE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_tolerance_staircase_snapshot_20260308.json'
CANONICAL_LABEL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    checkpoint_rows = {
        row['tier']: row
        for row in _load(CHECKPOINT_STAIRCASE_REPORT)['tier_rows']
    }
    tolerance_rows = {
        row['tier']: row
        for row in _load(TOLERANCE_STAIRCASE_REPORT)['tier_rows']
    }
    canonical_rows = {
        row['tier']: row
        for row in _load(CANONICAL_LABEL_REPORT)['tier_rows']
    }

    rows: list[dict[str, Any]] = []
    for tier in ORDER:
        checkpoint = checkpoint_rows[tier]
        tolerance = tolerance_rows[tier]
        canonical = canonical_rows[tier]
        rounded_label = float(checkpoint['minimum_gain_share_of_full_dynamic_savings'])
        actual_floor = float(checkpoint['worst_case_gain_share_of_full_dynamic_savings'])
        headroom = actual_floor - rounded_label
        rows.append(
            {
                'tier': tier,
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': rounded_label,
                'actual_certified_gain_share_floor_of_full_dynamic_savings': actual_floor,
                'certified_headroom_above_rounded_label': round(headroom, 6),
                'exact_hard_cap': int(checkpoint['exact_hard_cap']),
                'union_transition_checkpoint_count': int(checkpoint['union_transition_checkpoint_count']),
                'canonical_anchor_minimum_dwell_unique_appends': int(canonical['canonical_anchor_minimum_dwell_unique_appends']),
                'minimum_anchor_slack_unique_appends': int(tolerance['minimum_anchor_slack_unique_appends']),
                'exact_dwell_band_start_unique_appends': int(tolerance['exact_dwell_band_start_unique_appends']),
                'exact_dwell_band_end_unique_appends': int(tolerance['exact_dwell_band_end_unique_appends']),
            }
        )
    return rows


def _threshold_rows(tier_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous_upper: float | None = None
    for row in tier_rows:
        upper = float(row['actual_certified_gain_share_floor_of_full_dynamic_savings'])
        rows.append(
            {
                'required_gain_share_floor_interval': (
                    f'[0, {upper:.6f}]'
                    if previous_upper is None
                    else f'({previous_upper:.6f}, {upper:.6f}]'
                ),
                'minimum_required_gain_share_floor_exclusive': previous_upper,
                'maximum_required_gain_share_floor_inclusive': upper,
                'cheapest_exact_feasible_tier': row['tier'],
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': row['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
                'actual_certified_gain_share_floor_of_full_dynamic_savings': upper,
                'exact_hard_cap': row['exact_hard_cap'],
                'union_transition_checkpoint_count': row['union_transition_checkpoint_count'],
                'minimum_anchor_slack_unique_appends': row['minimum_anchor_slack_unique_appends'],
            }
        )
        previous_upper = upper
    rows.append(
        {
            'required_gain_share_floor_interval': f'({previous_upper:.6f}, 1.000000]',
            'minimum_required_gain_share_floor_exclusive': previous_upper,
            'maximum_required_gain_share_floor_inclusive': 1.0,
            'cheapest_exact_feasible_tier': 'none',
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': None,
            'actual_certified_gain_share_floor_of_full_dynamic_savings': None,
            'exact_hard_cap': None,
            'union_transition_checkpoint_count': None,
            'minimum_anchor_slack_unique_appends': None,
        }
    )
    return rows


def _headline(tier_rows: list[dict[str, Any]], threshold_rows: list[dict[str, Any]]) -> dict[str, Any]:
    indexed = {row['tier']: row for row in tier_rows}
    return {
        'rounded_labels_are_conservative_not_tight': True,
        'headroom_above_rounded_label_by_tier': {
            row['tier']: row['certified_headroom_above_rounded_label']
            for row in tier_rows
        },
        'largest_hidden_headroom_tier': max(
            tier_rows,
            key=lambda row: row['certified_headroom_above_rounded_label'],
        )['tier'],
        'strongest_exact_tier_not_needed_until_required_floor_exceeds': indexed['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'near_optimal_is_cheapest_exact_tier_for_required_floor_interval': threshold_rows[1]['required_gain_share_floor_interval'],
        'near_exact_required_floor_interval': threshold_rows[2]['required_gain_share_floor_interval'],
        'no_current_exact_tier_above_required_floor': threshold_rows[3]['required_gain_share_floor_interval'],
        'main_rule': 'Select exact uncertainty tiers by the actual certified worst-case gain-share floor, not by the rounded public label: the current 0.95 tier remains the cheapest exact choice for any requirement above 0.870482 and up to 0.980481, and the 0.99 precision tier is only necessary once the requirement exceeds 0.980481.',
    }


def _decision_rules() -> list[str]:
    return [
        'Treat the published 0.85, 0.95, and 0.99 labels as conservative bucket names rather than as the tight certified floors of the current exact lanes.',
        'When a stakeholder states a minimum guaranteed share requirement, compare it against the actual certified floors 0.870482, 0.980481, and 0.999822 before escalating to a more expensive tier.',
        'Choose the exact 0.85 lane only when the required worst-case gain-share floor is at most 0.870482 and the lower cap / wider dwell band matters more than stronger preservation.',
        'Choose the exact 0.95 lane for any requirement above 0.870482 and up to 0.980481; that is the cheapest current exact lane for the whole middle interval, so many requests phrased as “more than 0.95” still do not justify the 0.99 jump.',
        'Reserve the exact 0.99 precision lane for requirements above 0.980481, and treat requirements above 0.999822 as outside the current exact certified menu.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    threshold_rows = _threshold_rows(tier_rows)
    return {
        'focus': 'Turn the exact uncertainty tiers into a threshold selector keyed by the actual certified worst-case gain-share floor, so inheritors stop overpaying for stronger tiers just because the rounded public labels look tight.',
        'headline_findings': _headline(tier_rows, threshold_rows),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'threshold_rows': threshold_rows,
        'source_reports': [
            str(CHECKPOINT_STAIRCASE_REPORT.relative_to(ROOT)),
            str(TOLERANCE_STAIRCASE_REPORT.relative_to(ROOT)),
            str(CANONICAL_LABEL_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty guarantee-threshold selector snapshot — 2026-03-08')
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
            f"actual certified floor `{row['actual_certified_gain_share_floor_of_full_dynamic_savings']}`; "
            f"headroom `{row['certified_headroom_above_rounded_label']}`; "
            f"cap `{row['exact_hard_cap']}`; checkpoints `{row['union_transition_checkpoint_count']}`; "
            f"canonical anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}`; "
            f"slack `{row['minimum_anchor_slack_unique_appends']}`; "
            f"band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Threshold rows')
    for row in report['threshold_rows']:
        lines.append(
            '- '
            f"required floor `{row['required_gain_share_floor_interval']}` -> cheapest exact tier `{row['cheapest_exact_feasible_tier']}`; "
            f"cap `{row['exact_hard_cap']}`; checkpoints `{row['union_transition_checkpoint_count']}`; "
            f"minimum slack `{row['minimum_anchor_slack_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Sources')
    for source in report['source_reports']:
        lines.append(f'- `{source}`')
    lines.append(f"- `{report['source_script']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report))
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
