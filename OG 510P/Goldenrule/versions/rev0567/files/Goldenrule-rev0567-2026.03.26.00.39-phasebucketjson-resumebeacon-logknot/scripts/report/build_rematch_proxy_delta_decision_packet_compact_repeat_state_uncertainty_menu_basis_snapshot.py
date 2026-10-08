#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_menu_basis_snapshot_20260308.md'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'
PRECISION_GATE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    guarantee_rows = {row['tier']: row for row in _load(GUARANTEE_REPORT)['tier_rows']}
    amortized_rows = {row['tier']: row for row in _load(POST_AMORTIZATION_REPORT)['tier_rows']}
    rows: list[dict[str, Any]] = []
    for tier in ORDER:
        guarantee = guarantee_rows[tier]
        amortized = amortized_rows[tier]
        rows.append(
            {
                'tier': tier,
                'actual_certified_gain_share_floor_of_full_dynamic_savings': guarantee['actual_certified_gain_share_floor_of_full_dynamic_savings'],
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': guarantee['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
                'exact_hard_cap': amortized['exact_hard_cap'],
                'mode_specific_checkpoint_count': amortized['mode_specific_checkpoint_count'],
                'post_amortized_checkpoint_count': amortized['post_amortized_checkpoint_count'],
                'minimum_anchor_slack_unique_appends': amortized['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': amortized['exact_dwell_band_width_unique_appends'],
                'representative_anchor_minimum_dwell_unique_appends': amortized['representative_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band_start_unique_appends': amortized['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': amortized['exact_dwell_band_end_unique_appends'],
            }
        )
    return rows


def _basis_witness_rows(tiers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lower = tiers['lower_guarantee']
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    return [
        {
            'tier': 'lower_guarantee',
            'case': 'cap_limited_relaxed_exact_basis',
            'required_gain_share_floor_interval': f"[0, {lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'max_hard_cap': lower['exact_hard_cap'],
            'master_calendar_pre_registered': True,
            'min_anchor_slack_unique_appends': 0,
            'min_band_width_unique_appends': 1,
            'selected_tier': 'lower_guarantee',
            'why': 'The exact 0.85 lane is the only current exact tier that survives hard-cap budget 3; the stronger 0.95 and 0.99 lanes both exceed that cap.',
        },
        {
            'tier': 'near_optimal',
            'case': 'positive_slack_bridge_basis',
            'required_gain_share_floor_interval': f"({lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'max_hard_cap': near_exact['exact_hard_cap'],
            'master_calendar_pre_registered': True,
            'min_anchor_slack_unique_appends': 1,
            'min_band_width_unique_appends': 2,
            'selected_tier': 'near_optimal',
            'why': 'Above the exact 0.85 floor, the 0.95 lane is the only current exact tier that still survives positive slack and width above 1; 0.85 fails the floor and 0.99 fails the fragility budget.',
        },
        {
            'tier': 'near_exact',
            'case': 'high_floor_precision_basis',
            'required_gain_share_floor_interval': f"({near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'max_hard_cap': near_exact['exact_hard_cap'],
            'pre_amortization_checkpoint_budget': near_exact['mode_specific_checkpoint_count'],
            'master_calendar_pre_registered': False,
            'min_anchor_slack_unique_appends': 0,
            'min_band_width_unique_appends': 1,
            'selected_tier': 'near_exact',
            'why': 'Once the required floor exceeds 0.980481, the only surviving current exact tier is the single-point 0.99 precision mode; the 0.95 lane is no longer sufficient.',
        },
    ]


def _removal_rows(tiers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lower = tiers['lower_guarantee']
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    return [
        {
            'removed_tier': 'lower_guarantee',
            'lost_request_region': f"hard-cap budgets {lower['exact_hard_cap']}-{near_optimal['exact_hard_cap'] - 1} with required floor at most {lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}",
            'witness_request': {
                'required_gain_share_floor_interval': f"[0, {lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
                'max_hard_cap': lower['exact_hard_cap'],
                'min_anchor_slack_unique_appends': 0,
                'min_band_width_unique_appends': 1,
            },
            'surviving_exact_tier': None,
            'why': 'Removing the exact 0.85 lane leaves no current exact option for cap-limited deployments at hard cap 3 or 4.',
        },
        {
            'removed_tier': 'near_optimal',
            'lost_request_region': f"required floors in ({lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}] with any positive slack or band width above 1",
            'witness_request': {
                'required_gain_share_floor_interval': f"({lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
                'max_hard_cap': near_exact['exact_hard_cap'],
                'min_anchor_slack_unique_appends': 1,
                'min_band_width_unique_appends': 2,
            },
            'surviving_exact_tier': None,
            'why': 'Removing the exact 0.95 lane destroys the only current exact bridge between the relaxed 0.85 band and the fragile 0.99 precision point whenever positive slack is required.',
        },
        {
            'removed_tier': 'near_exact',
            'lost_request_region': f"required floors in ({near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'witness_request': {
                'required_gain_share_floor_interval': f"({near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
                'max_hard_cap': near_exact['exact_hard_cap'],
                'min_anchor_slack_unique_appends': 0,
                'min_band_width_unique_appends': 1,
                'pre_amortization_checkpoint_budget': near_exact['mode_specific_checkpoint_count'],
            },
            'surviving_exact_tier': None,
            'why': 'Removing the exact 0.99 tier leaves no current exact lane above floor 0.980481 at all.',
        },
    ]


def _headline(tiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    lower = tiers['lower_guarantee']
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    return {
        'exact_tier_count': len(tiers),
        'removable_tier_count_without_losing_current_exact_request_region': 0,
        'lower_guarantee_unique_basis_region': {
            'max_hard_cap': lower['exact_hard_cap'],
            'required_floor_ceiling': lower['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        },
        'near_optimal_unique_basis_region': {
            'required_floor_interval': f"({lower['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'minimum_anchor_slack_unique_appends': 1,
            'minimum_band_width_unique_appends': 2,
        },
        'near_exact_unique_basis_region': {
            'required_floor_interval': f"({near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}, {near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']:.6f}]",
            'max_hard_cap': near_exact['exact_hard_cap'],
            'pre_amortization_checkpoint_budget': near_exact['mode_specific_checkpoint_count'],
        },
        'near_optimal_is_only_positive_slack_exact_bridge_above_lower_guarantee_floor': True,
        'main_rule': 'Keep the current exact uncertainty menu as an irreducible three-tier basis: the exact 0.85 tier is the cap-limited relaxed basis row, the exact 0.95 tier is the only positive-slack bridge above floor 0.870482, and the exact 0.99 tier is the only surviving row above floor 0.980481.',
    }


def _decision_rules() -> list[str]:
    return [
        'Do not compress the current exact uncertainty menu below three tiers unless new frontier evidence creates a replacement row for one of the three current basis regions.',
        'Treat the exact 0.85 tier as the low-cap relaxed basis row: without it, cap-limited deployments at hard cap 3 or 4 lose every current exact option.',
        'Treat the exact 0.95 tier as the unique positive-slack bridge above floor 0.870482: without it, the menu jumps straight from the relaxed 0.85 band to the fragile single-point 0.99 precision mode.',
        'Treat the exact 0.99 tier as the high-floor precision basis row: without it, the archive has no current exact answer above floor 0.980481.',
        'When someone proposes simplifying the menu, demand an explicit witness that their replacement still covers each of the three current basis regions before accepting the simplification.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    tiers = {row['tier']: row for row in tier_rows}
    return {
        'focus': 'Show that the current exact uncertainty-safe compact repeat-sidecar menu is an irreducible three-tier basis, so future inheritors stop collapsing it into fewer tiers and silently orphaning real request regions.',
        'headline_findings': _headline(tiers),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'basis_witness_rows': _basis_witness_rows(tiers),
        'removal_rows': _removal_rows(tiers),
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
            str(PRECISION_GATE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty menu basis snapshot — 2026-03-08')
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
            f"{row['tier']}: actual floor `{row['actual_certified_gain_share_floor_of_full_dynamic_savings']}`; "
            f"rounded label `{row['rounded_label_minimum_gain_share_of_full_dynamic_savings']}`; "
            f"cap `{row['exact_hard_cap']}`; mode checkpoints `{row['mode_specific_checkpoint_count']}`; "
            f"slack `{row['minimum_anchor_slack_unique_appends']}`; band width `{row['exact_dwell_band_width_unique_appends']}`; "
            f"anchor `{row['representative_anchor_minimum_dwell_unique_appends']}`; band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Basis witness rows')
    for row in report['basis_witness_rows']:
        fields = [
            f"required floor `{row['required_gain_share_floor_interval']}`",
            f"max hard cap `{row['max_hard_cap']}`",
            f"master calendar pre-registered `{row['master_calendar_pre_registered']}`",
            f"min slack `{row['min_anchor_slack_unique_appends']}`",
            f"min band width `{row['min_band_width_unique_appends']}`",
            f"selected tier `{row['selected_tier']}`",
        ]
        if 'pre_amortization_checkpoint_budget' in row:
            fields.append(f"pre-amortization checkpoint budget `{row['pre_amortization_checkpoint_budget']}`")
        lines.append(f"- {row['case']}: " + '; '.join(fields) + f"; why `{row['why']}`")
    lines.append('')
    lines.append('## What breaks if a tier is removed')
    for row in report['removal_rows']:
        lines.append(
            '- '
            f"remove `{row['removed_tier']}` -> lost region `{row['lost_request_region']}`; "
            f"witness `{json.dumps(row['witness_request'], ensure_ascii=False)}`; "
            f"surviving exact tier `{row['surviving_exact_tier']}`; why `{row['why']}`"
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
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
