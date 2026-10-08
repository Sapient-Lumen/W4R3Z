#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot_20260308.md'
THRESHOLD_SELECTOR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
PRECISION_GATE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']
DISPLAY_NAMES = {
    'lower_guarantee': 'relaxed 0.85',
    'near_optimal': 'near-optimal 0.95',
    'near_exact': 'near-exact 0.99',
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    threshold = _load(THRESHOLD_SELECTOR_REPORT)
    tier_rows = {row['tier']: row for row in threshold['tier_rows']}
    precision = _load(PRECISION_GATE_REPORT)
    near_exact_gate = precision['headline_findings']['near_exact_only_needed_when_required_floor_exceeds']

    rows: list[dict[str, Any]] = []
    for index, tier in enumerate(ORDER):
        row = tier_rows[tier]
        rounded = float(row['rounded_label_minimum_gain_share_of_full_dynamic_savings'])
        actual = float(row['actual_certified_gain_share_floor_of_full_dynamic_savings'])
        headroom = round(actual - rounded, 6)
        relative = round(headroom / rounded, 6)

        next_trigger = actual
        next_kind = 'frontier_overflow' if tier == 'near_exact' else 'tier_escalation'

        rows.append(
            {
                'tier': tier,
                'display_name': DISPLAY_NAMES[tier],
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': rounded,
                'actual_certified_gain_share_floor_of_full_dynamic_savings': actual,
                'certified_requirement_creep_buffer_above_rounded_label': headroom,
                'relative_requirement_creep_buffer_vs_rounded_label': relative,
                'next_forced_change_trigger_floor': round(next_trigger, 6),
                'next_forced_change_kind': next_kind,
                'strongest_exact_tier_not_needed_until_required_floor_exceeds': round(actual, 6) if tier == 'near_optimal' else None,
                'exact_hard_cap': int(row['exact_hard_cap']),
                'union_transition_checkpoint_count': int(row['union_transition_checkpoint_count']),
                'canonical_anchor_minimum_dwell_unique_appends': int(row['canonical_anchor_minimum_dwell_unique_appends']),
                'minimum_anchor_slack_unique_appends': int(row['minimum_anchor_slack_unique_appends']),
                'exact_dwell_band_start_unique_appends': int(row['exact_dwell_band_start_unique_appends']),
                'exact_dwell_band_end_unique_appends': int(row['exact_dwell_band_end_unique_appends']),
                'exact_high_floor_escalation_gate_from_near_optimal': round(near_exact_gate, 6),
            }
        )
    return rows


def _headline(tier_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_tier = {row['tier']: row for row in tier_rows}
    largest_absolute = max(tier_rows, key=lambda row: row['certified_requirement_creep_buffer_above_rounded_label'])
    largest_relative = max(tier_rows, key=lambda row: row['relative_requirement_creep_buffer_vs_rounded_label'])
    near_optimal = by_tier['near_optimal']
    lower = by_tier['lower_guarantee']
    near_exact = by_tier['near_exact']
    return {
        'main_rule': 'Treat the exact 0.95 lane as the best current buffer against silent requirement creep: it absorbs the largest exact floor increase above its rounded public label before any tier escalation is truly forced.',
        'largest_absolute_requirement_creep_buffer_tier': largest_absolute['tier'],
        'largest_relative_requirement_creep_buffer_tier': largest_relative['tier'],
        'exact_requirement_creep_buffer_above_rounded_label': {
            row['tier']: row['certified_requirement_creep_buffer_above_rounded_label']
            for row in tier_rows
        },
        'near_optimal_buffer_advantage_vs_lower_guarantee': round(
            near_optimal['certified_requirement_creep_buffer_above_rounded_label'] - lower['certified_requirement_creep_buffer_above_rounded_label'],
            6,
        ),
        'near_optimal_buffer_advantage_vs_near_exact': round(
            near_optimal['certified_requirement_creep_buffer_above_rounded_label'] - near_exact['certified_requirement_creep_buffer_above_rounded_label'],
            6,
        ),
        'near_optimal_buffer_multiple_vs_near_exact': round(
            near_optimal['certified_requirement_creep_buffer_above_rounded_label'] / near_exact['certified_requirement_creep_buffer_above_rounded_label'],
            6,
        ),
        'do_not_pay_near_exact_until_required_floor_exceeds': near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'near_exact_frontier_overflow_margin_below_1_0': round(
            1.0 - near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings'],
            6,
        ),
    }


def _decision_rules() -> list[str]:
    return [
        'When public contracts or stakeholder asks are written as rounded labels, budget against the hidden certified buffer above that label rather than escalating immediately on small requirement creep.',
        'Treat the exact 0.95 lane as the best current requirement-creep absorber: it clears its rounded label by 0.030481, which is larger than the 0.020482 buffer of the relaxed 0.85 lane and the 0.009822 buffer of the fragile 0.99 precision lane.',
        'Do not pre-pay the 0.99 precision premium just because a requirement is drifting above 0.95; stay in the exact 0.95 lane until the required floor truly exceeds 0.980481.',
        'Treat the 0.99 lane as having the smallest creep tolerance: once its rounded label starts drifting upward, the current exact menu is only 0.009822 away from frontier overflow and there is no stronger saved exact tier to escalate into.',
        'Use the relaxed 0.85 lane as the cheapest low-cap buffer when the requested floor is comfortably below 0.870482, not as the best hedge against upward requirement drift.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    return {
        'focus': 'Turn the saved exact uncertainty floors into a requirement-creep buffer card so inheritors can see how much upward floor drift each rounded public label can absorb before a tier change is truly forced.',
        'headline_findings': _headline(tier_rows),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'source_reports': [
            str(THRESHOLD_SELECTOR_REPORT.relative_to(ROOT)),
            str(PRECISION_GATE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty requirement-creep buffer snapshot — 2026-03-08')
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
            f"requirement-creep buffer `{row['certified_requirement_creep_buffer_above_rounded_label']}`; "
            f"relative buffer `{row['relative_requirement_creep_buffer_vs_rounded_label']}`; "
            f"next forced change `{row['next_forced_change_kind']}` at floor `{row['next_forced_change_trigger_floor']}`; "
            f"cap `{row['exact_hard_cap']}`; checkpoints `{row['union_transition_checkpoint_count']}`; "
            f"anchor `{row['canonical_anchor_minimum_dwell_unique_appends']}`; "
            f"slack `{row['minimum_anchor_slack_unique_appends']}`; band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
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
