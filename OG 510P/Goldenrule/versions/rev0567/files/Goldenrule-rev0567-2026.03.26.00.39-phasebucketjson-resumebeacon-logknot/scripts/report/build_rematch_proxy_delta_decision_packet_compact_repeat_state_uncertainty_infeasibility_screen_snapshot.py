#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.md'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
CONSTRAINT_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_constraint_selector_snapshot_20260308.json'
PRECISION_GATE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.json'
TOPOLOGY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'

ORDER = ['lower_guarantee', 'near_optimal', 'near_exact']


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _tier_rows() -> list[dict[str, Any]]:
    guarantee_rows = {row['tier']: row for row in _load(GUARANTEE_REPORT)['tier_rows']}
    post_rows = {row['tier']: row for row in _load(POST_AMORTIZATION_REPORT)['tier_rows']}
    rows: list[dict[str, Any]] = []
    for tier in ORDER:
        guarantee = guarantee_rows[tier]
        post = post_rows[tier]
        rows.append(
            {
                'tier': tier,
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': guarantee['rounded_label_minimum_gain_share_of_full_dynamic_savings'],
                'actual_certified_gain_share_floor_of_full_dynamic_savings': guarantee['actual_certified_gain_share_floor_of_full_dynamic_savings'],
                'exact_hard_cap': post['exact_hard_cap'],
                'pre_amortization_checkpoint_budget': post['mode_specific_checkpoint_count'],
                'minimum_anchor_slack_unique_appends': post['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': post['exact_dwell_band_width_unique_appends'],
                'representative_anchor_minimum_dwell_unique_appends': post['representative_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band_start_unique_appends': post['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': post['exact_dwell_band_end_unique_appends'],
            }
        )
    return rows


def _axis_map() -> dict[str, dict[int, str | None]]:
    axis_rows = _load(CONSTRAINT_REPORT)['axis_rows']
    return {
        axis: {int(row['budget_or_requirement']): row['strongest_feasible_tier'] for row in rows}
        for axis, rows in axis_rows.items()
    }


def _headline(axis_map: dict[str, dict[int, str | None]], topology: dict[str, Any], guarantee_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    near_optimal_floor = guarantee_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_exact_floor = guarantee_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    return {
        'no_current_exact_tier_if_max_hard_cap_below': 3,
        'no_current_exact_tier_if_pre_amortization_checkpoint_budget_below': 5,
        'no_current_exact_tier_if_required_floor_above': near_exact_floor,
        'no_current_exact_tier_if_minimum_anchor_slack_at_least': 7,
        'no_current_exact_tier_if_minimum_band_width_at_least': 15,
        'no_current_exact_positive_slack_tier_above_required_floor': near_optimal_floor,
        'exact_dwell_support_inside_current_menu_unique_appends': topology['headline_findings']['exact_covered_dwell_intervals_unique_appends'],
        'largest_internal_exact_dwell_gap_unique_appends': topology['headline_findings']['largest_internal_exact_dwell_gap_unique_appends'],
        'main_rule': 'Fail fast on request bundles that the current exact uncertainty-safe menu cannot satisfy: below hard cap 3, below checkpoint budget 5 before amortization, above floor 0.999822, at slack 7 or width 15, or anywhere inside the dwell gap 3–7, there is no current exact tier to find.',
    }


def _infeasibility_rows(guarantee_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lower_floor = guarantee_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_optimal_floor = guarantee_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_exact_floor = guarantee_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    return [
        {
            'case': 'hard_cap_underflow',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 2,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'blocking_boundary': 'max_hard_cap_budget_inclusive < 3',
            'surviving_exact_tier': None,
            'why': 'No current exact uncertainty-safe tier survives hard-cap budget 2 or below; the relaxed exact 0.85 lane already needs cap 3.',
        },
        {
            'case': 'pre_amortization_checkpoint_underflow',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 4,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'blocking_boundary': 'pre-amortization checkpoint budget < 5',
            'surviving_exact_tier': None,
            'why': 'Before master-calendar amortization, even the relaxed exact 0.85 lane needs five transition checkpoints, so checkpoint budget 4 or below leaves no current exact option.',
        },
        {
            'case': 'certified_floor_overflow',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_exact_floor:.6f}, 1.000000]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'blocking_boundary': f'required floor > {near_exact_floor:.6f}',
            'surviving_exact_tier': None,
            'why': 'The current exact menu tops out at certified floor 0.999822; any stricter requirement lies outside the saved exact frontier entirely.',
        },
        {
            'case': 'high_floor_positive_slack_conflict',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
            },
            'blocking_boundary': f'required floor > {near_optimal_floor:.6f} together with positive slack',
            'surviving_exact_tier': None,
            'why': 'Above floor 0.980481 the only surviving current exact tier is the single-point 0.99 precision mode, and it has zero slack.',
        },
        {
            'case': 'high_floor_bandwidth_conflict',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 2,
            },
            'blocking_boundary': f'required floor > {near_optimal_floor:.6f} together with minimum band width >= 2',
            'surviving_exact_tier': None,
            'why': 'The exact 0.99 tier is the only high-floor survivor and its certified dwell band width is exactly 1, so any wider requirement fails.',
        },
        {
            'case': 'slack_overflow',
            'request_bundle': {
                'required_gain_share_floor_interval': '[0, 0.999822]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 7,
                'minimum_band_width_unique_appends': 1,
            },
            'blocking_boundary': 'minimum anchor slack >= 7',
            'surviving_exact_tier': None,
            'why': 'The widest current exact lane is the relaxed 0.85 band and it only certifies minimum anchor slack 6, so slack 7 already empties the whole exact menu.',
        },
        {
            'case': 'bandwidth_overflow',
            'request_bundle': {
                'required_gain_share_floor_interval': '[0, 0.999822]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 15,
            },
            'blocking_boundary': 'minimum band width >= 15',
            'surviving_exact_tier': None,
            'why': 'The widest current exact lane has certified dwell-band width 14, so asking for width 15 or more leaves no current exact tier.',
        },
        {
            'case': 'internal_dwell_gap_request',
            'request_bundle': {
                'requested_exact_dwell_unique_appends_interval': '[3, 7]',
                'required_gain_share_floor_interval': '[0, 0.999822]',
            },
            'blocking_boundary': 'requested dwell inside internal exact gap 3-7',
            'surviving_exact_tier': None,
            'why': 'The saved exact uncertainty-safe dwell support is {2} union [8, 32]; dwell 3 through 7 is a real uncovered gap, not a live retuning corridor.',
        },
        {
            'case': 'outside_current_exact_dwell_menu',
            'request_bundle': {
                'requested_exact_dwell_unique_appends_sets': ['(-inf, 1]', '[33, +inf)'],
                'required_gain_share_floor_interval': '[0, 0.999822]',
            },
            'blocking_boundary': 'requested dwell outside {2} union [8, 32]',
            'surviving_exact_tier': None,
            'why': 'The current exact uncertainty-certified dwell menu has only one isolated precision point at 2 and then a continuous non-precision band from 8 through 32.',
        },
    ]


def _boundary_rows(guarantee_rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lower_floor = guarantee_rows['lower_guarantee']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_optimal_floor = guarantee_rows['near_optimal']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_exact_floor = guarantee_rows['near_exact']['actual_certified_gain_share_floor_of_full_dynamic_savings']
    return [
        {
            'boundary_case': 'minimum_live_hard_cap',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 3,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'selected_exact_tier': 'lower_guarantee',
            'why': 'Hard cap 3 is the first live cap that still leaves one exact tier alive: the relaxed 0.85 lane.',
        },
        {
            'boundary_case': 'minimum_live_pre_amortization_checkpoint_budget',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'selected_exact_tier': 'lower_guarantee',
            'why': 'Checkpoint budget 5 is the first live pre-amortization budget because it exactly matches the relaxed 0.85 union checkpoint count.',
        },
        {
            'boundary_case': 'maximum_live_minimum_anchor_slack',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 6,
                'minimum_band_width_unique_appends': 1,
            },
            'selected_exact_tier': 'lower_guarantee',
            'why': 'Minimum anchor slack 6 is the strongest slack demand the current exact menu can still satisfy, again only through the relaxed 0.85 lane.',
        },
        {
            'boundary_case': 'maximum_live_minimum_band_width',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 14,
            },
            'selected_exact_tier': 'lower_guarantee',
            'why': 'Minimum band width 14 is the widest dwell-band demand that the current exact menu can still satisfy, again only through the relaxed 0.85 lane.',
        },
        {
            'boundary_case': 'maximum_live_certified_floor',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[{near_exact_floor:.6f}, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'requested_exact_dwell_unique_appends_interval': '[2, 2]',
            },
            'selected_exact_tier': 'near_exact',
            'why': 'Certified floor 0.999822 is the strongest live exact guarantee, but only as the single-point near-exact precision mode at dwell 2.',
        },
        {
            'boundary_case': 'largest_non_fragile_floor',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({lower_floor:.6f}, {near_optimal_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 2,
            },
            'selected_exact_tier': 'near_optimal',
            'why': 'The exact 0.95 lane is the strongest current exact tier that survives any positive slack and any band width above 1.',
        },
    ]


def _decision_rules() -> list[str]:
    return [
        'Fail fast instead of retuning when a request bundle crosses a known exact impossibility boundary: cap below 3, checkpoint budget below 5 before amortization, floor above 0.999822, slack at least 7, or band width at least 15.',
        'Treat the exact 0.99 tier as precision-only even inside the live menu: any request above floor 0.980481 that also demands positive slack or band width above 1 has no current exact answer.',
        'Treat dwell 3 through 7 as an internal exact gap and dwell values below 2 or above 32 as outside the current exact menu unless new frontier evidence is generated.',
        'Use the relaxed exact 0.85 lane as the live boundary witness for minimum feasible cap, checkpoint budget, maximum slack, and maximum width; it is the row that keeps the menu open at those edges.',
        'Use the exact 0.95 lane as the largest live non-fragile guarantee and the exact 0.99 tier only as the live ceiling witness for absolute floor, not as a generic fallback when other constraints are violated.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    guarantee_rows = {row['tier']: row for row in _load(GUARANTEE_REPORT)['tier_rows']}
    axis_map = _axis_map()
    precision_gate = _load(PRECISION_GATE_REPORT)
    topology = _load(TOPOLOGY_REPORT)
    return {
        'focus': 'Turn the scattered exact uncertainty no-go boundaries into one fail-fast screen so inheritors can reject unsatisfiable request bundles immediately instead of wasting search or retuning effort inside the current menu gaps.',
        'headline_findings': _headline(axis_map, topology, guarantee_rows),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'boundary_rows': _boundary_rows(guarantee_rows),
        'infeasibility_rows': _infeasibility_rows(guarantee_rows),
        'supporting_constraints': {
            'positive_slack_rules_out_near_exact_above_required_floor': precision_gate['headline_findings']['precision_escalation_requires_zero_minimum_anchor_slack'],
            'minimum_live_hard_cap_tier': axis_map['max_hard_cap'][3],
            'minimum_live_pre_amortization_checkpoint_tier': axis_map['max_checkpoints'][5],
            'maximum_live_minimum_slack_tier': axis_map['min_anchor_slack'][6],
            'maximum_live_minimum_band_width_tier': axis_map['min_band_width'][14],
        },
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(CONSTRAINT_REPORT.relative_to(ROOT)),
            str(PRECISION_GATE_REPORT.relative_to(ROOT)),
            str(TOPOLOGY_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty infeasibility screen snapshot — 2026-03-08')
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
            f"{row['tier']}: floor `{row['actual_certified_gain_share_floor_of_full_dynamic_savings']}`; "
            f"cap `{row['exact_hard_cap']}`; pre-amortization checkpoints `{row['pre_amortization_checkpoint_budget']}`; "
            f"minimum slack `{row['minimum_anchor_slack_unique_appends']}`; width `{row['exact_dwell_band_width_unique_appends']}`; "
            f"anchor `{row['representative_anchor_minimum_dwell_unique_appends']}`; band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Live boundary rows')
    for row in report['boundary_rows']:
        lines.append(f"- **{row['boundary_case']}** -> `{row['selected_exact_tier']}`: `{json.dumps(row['request_bundle'], ensure_ascii=False)}`. {row['why']}")
    lines.append('')
    lines.append('## Infeasibility rows')
    for row in report['infeasibility_rows']:
        lines.append(f"- **{row['case']}** -> `{row['surviving_exact_tier']}`: blocker `{row['blocking_boundary']}` with `{json.dumps(row['request_bundle'], ensure_ascii=False)}`. {row['why']}")
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
