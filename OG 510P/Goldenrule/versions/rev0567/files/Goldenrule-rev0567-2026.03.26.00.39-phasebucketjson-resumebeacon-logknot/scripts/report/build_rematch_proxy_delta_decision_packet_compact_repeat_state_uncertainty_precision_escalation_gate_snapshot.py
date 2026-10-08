#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.md'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
CHECKPOINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'


ORDER = ['near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    guarantee_rows = {row['tier']: row for row in _load(GUARANTEE_REPORT)['tier_rows']}
    checkpoint_rows = {row['tier']: row for row in _load(CHECKPOINT_REPORT)['tier_rows']}
    amortized_rows = {row['tier']: row for row in _load(POST_AMORTIZATION_REPORT)['tier_rows']}
    rows: list[dict[str, Any]] = []
    for tier in ORDER:
        guarantee = guarantee_rows[tier]
        checkpoint = checkpoint_rows[tier]
        amortized = amortized_rows[tier]
        rows.append(
            {
                'tier': tier,
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': guarantee['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
                'actual_certified_gain_share_floor_of_full_dynamic_savings': guarantee['actual_certified_gain_share_floor_of_full_dynamic_savings'],
                'exact_hard_cap': checkpoint['exact_hard_cap'],
                'mode_specific_checkpoint_count': checkpoint['union_transition_checkpoint_count'],
                'post_amortized_checkpoint_count': amortized['post_amortized_checkpoint_count'],
                'minimum_anchor_slack_unique_appends': amortized['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': amortized['exact_dwell_band_width_unique_appends'],
                'representative_anchor_minimum_dwell_unique_appends': amortized['representative_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band_start_unique_appends': amortized['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': amortized['exact_dwell_band_end_unique_appends'],
            }
        )
    return rows


def _gate_rows(tiers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    near_optimal_floor = near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_exact_floor = near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']
    return [
        {
            'case': 'pre_amortization_precision_escalation_gate',
            'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
            'master_calendar_pre_registered': False,
            'minimum_required_max_hard_cap': near_exact['exact_hard_cap'],
            'minimum_required_checkpoint_budget': near_exact['mode_specific_checkpoint_count'],
            'maximum_allowed_minimum_anchor_slack_unique_appends': near_exact['minimum_anchor_slack_unique_appends'],
            'maximum_allowed_minimum_band_width_unique_appends': near_exact['exact_dwell_band_width_unique_appends'],
            'selected_tier': 'near_exact',
            'why': 'Before the master calendar is sunk cost, the exact 0.99 precision tier is only feasible when the requirement exceeds the exact 0.95 floor and the deployment can also afford the full 14-checkpoint precision surface, hard cap 11, zero slack, and width 1.',
        },
        {
            'case': 'post_amortization_precision_escalation_gate',
            'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
            'master_calendar_pre_registered': True,
            'minimum_required_max_hard_cap': near_exact['exact_hard_cap'],
            'minimum_required_checkpoint_budget': None,
            'maximum_allowed_minimum_anchor_slack_unique_appends': near_exact['minimum_anchor_slack_unique_appends'],
            'maximum_allowed_minimum_band_width_unique_appends': near_exact['exact_dwell_band_width_unique_appends'],
            'selected_tier': 'near_exact',
            'why': 'Once the 17-point master calendar is pre-registered, checkpoint budget no longer blocks the current exact menu, but the 0.99 precision tier still requires a requirement above 0.980481 together with hard cap 11, zero slack, and width 1.',
        },
        {
            'case': 'high_floor_but_positive_slack_leaves_no_current_exact_tier',
            'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
            'master_calendar_pre_registered': True,
            'minimum_required_max_hard_cap': near_exact['exact_hard_cap'],
            'minimum_required_checkpoint_budget': None,
            'minimum_anchor_slack_unique_appends': 1,
            'minimum_band_width_unique_appends': 2,
            'selected_tier': None,
            'why': 'Above the exact 0.95 floor, any positive minimum slack or any minimum band width above 1 rules out the current exact 0.99 tier, so no current exact lane survives.',
        },
        {
            'case': 'high_cap_precision_looking_but_no_floor_pressure_stays_near_optimal',
            'required_gain_share_floor_interval': f'[0, {near_optimal_floor:.6f}]',
            'master_calendar_pre_registered': False,
            'minimum_required_max_hard_cap': near_exact['exact_hard_cap'],
            'minimum_required_checkpoint_budget': near_exact['mode_specific_checkpoint_count'],
            'maximum_allowed_minimum_anchor_slack_unique_appends': near_exact['minimum_anchor_slack_unique_appends'],
            'maximum_allowed_minimum_band_width_unique_appends': near_exact['exact_dwell_band_width_unique_appends'],
            'selected_tier': 'near_optimal',
            'why': 'Even when cap, checkpoint, and fragility budgets could tolerate the 0.99 precision tier, a requirement at or below 0.980481 still does not justify escalating beyond the exact 0.95 lane.',
        },
    ]


def _headline(tiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    return {
        'near_exact_only_needed_when_required_floor_exceeds': near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'near_exact_exact_floor_ceiling': near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'precision_escalation_requires_hard_cap_at_least': near_exact['exact_hard_cap'],
        'precision_escalation_requires_pre_amortization_checkpoint_budget_at_least': near_exact['mode_specific_checkpoint_count'],
        'precision_escalation_requires_zero_minimum_anchor_slack': near_exact['minimum_anchor_slack_unique_appends'] == 0,
        'precision_escalation_requires_band_width_one': near_exact['exact_dwell_band_width_unique_appends'] == 1,
        'positive_minimum_slack_above_near_optimal_floor_leaves_no_current_exact_tier': True,
        'pre_registering_master_calendar_removes_only_the_checkpoint_blocker': True,
        'main_rule': 'Escalate from the exact 0.95 lane to the exact 0.99 precision tier only when the required worst-case gain-share floor exceeds 0.980481 and the deployment can accept a single-point zero-slack dwell mode with hard cap 11; before the master calendar is pre-registered that gate also requires checkpoint budget 14, and above 0.980481 any positive slack requirement leaves no current exact tier at all.',
    }


def _decision_rules() -> list[str]:
    return [
        'Do not pay the 0.99 precision premium merely because the deployment can afford it; pay it only when the required worst-case gain-share floor exceeds the exact 0.95 floor of 0.980481.',
        'Treat the 0.99 tier as a single-point precision mode: it is only compatible with zero minimum anchor slack and band width 1.',
        'Before the 17-point master calendar is pre-registered, include checkpoint budget 14 in the escalation gate; after amortization, drop only that checkpoint blocker and keep the floor, cap, and fragility gates unchanged.',
        'If the requirement exceeds 0.980481 and any positive slack or width above 1 is mandatory, do not pretend the current exact menu has a non-fragile near-exact option; it does not.',
        'When the requirement is at or below 0.980481, stay on the exact 0.95 lane even if hard cap, checkpoints, and fragility budgets could technically tolerate the 0.99 tier.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    tiers = {row['tier']: row for row in tier_rows}
    gate_rows = _gate_rows(tiers)
    return {
        'focus': 'Turn the upgrade from the exact 0.95 lane to the exact 0.99 precision tier into one explicit escalation gate, so future inheritors only pay for near-exact precision when the requirement and fragility budget both force it.',
        'headline_findings': _headline(tiers),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'gate_rows': gate_rows,
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(CHECKPOINT_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty precision-escalation gate snapshot — 2026-03-08')
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
            f"cap `{row['exact_hard_cap']}`; mode checkpoints `{row['mode_specific_checkpoint_count']}`; "
            f"post-amortized checkpoints `{row['post_amortized_checkpoint_count']}`; slack `{row['minimum_anchor_slack_unique_appends']}`; "
            f"band width `{row['exact_dwell_band_width_unique_appends']}`; anchor `{row['representative_anchor_minimum_dwell_unique_appends']}`; "
            f"band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Gate rows')
    for row in report['gate_rows']:
        fields = [
            f"required floor `{row['required_gain_share_floor_interval']}`",
            f"master calendar pre-registered `{row['master_calendar_pre_registered']}`",
            f"selected tier `{row['selected_tier']}`",
        ]
        for key in [
            'minimum_required_max_hard_cap',
            'minimum_required_checkpoint_budget',
            'maximum_allowed_minimum_anchor_slack_unique_appends',
            'maximum_allowed_minimum_band_width_unique_appends',
            'minimum_anchor_slack_unique_appends',
            'minimum_band_width_unique_appends',
        ]:
            if key in row:
                fields.append(f"{key.replace('_', ' ')} `{row[key]}`")
        lines.append(f"- {row['case']}: " + '; '.join(fields) + f"; why `{row['why']}`")
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
