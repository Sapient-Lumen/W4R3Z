#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_repair_guide_snapshot_20260308.md'
INFEASIBILITY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_infeasibility_screen_snapshot_20260308.json'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
POST_AMORTIZATION_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_post_amortization_selector_snapshot_20260308.json'
TOPOLOGY_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'
MASTER_CALENDAR_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_calendar_amortization_snapshot_20260308.json'

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
                'mode_specific_checkpoint_count': post['mode_specific_checkpoint_count'],
                'post_amortized_checkpoint_count': post['post_amortized_checkpoint_count'],
                'minimum_anchor_slack_unique_appends': post['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': post['exact_dwell_band_width_unique_appends'],
                'representative_anchor_minimum_dwell_unique_appends': post['representative_anchor_minimum_dwell_unique_appends'],
                'exact_dwell_band_start_unique_appends': post['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': post['exact_dwell_band_end_unique_appends'],
            }
        )
    return rows


def _headline_findings(tiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    lower = tiers['lower_guarantee']
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    return {
        'single_notch_local_repairs': {
            'hard_cap_underflow': '+1 hard-cap step restores the exact 0.85 lane',
            'pre_amortization_checkpoint_underflow': '+1 checkpoint restores the exact 0.85 lane',
            'slack_overflow': '-1 slack demand restores the exact 0.85 lane',
            'bandwidth_overflow': '-1 dwell-band-width demand restores the exact 0.85 lane',
        },
        'dual_path_repairs': {
            'high_floor_positive_slack_conflict': {
                'non_fragile_repair': f'clip required floor down to {near_optimal["actual_certified_gain_share_floor_of_full_dynamic_savings"]:.6f}',
                'high_floor_repair': 'relax minimum anchor slack to 0',
            },
            'high_floor_bandwidth_conflict': {
                'non_fragile_repair': f'clip required floor down to {near_optimal["actual_certified_gain_share_floor_of_full_dynamic_savings"]:.6f}',
                'high_floor_repair': 'relax minimum band width to 1',
            },
        },
        'dwell_gap_repair_choices': {'precision_point': 2, 'non_fragile_band_start': 8},
        'largest_no_local_structural_repair_case': f'required floor > {near_exact["actual_certified_gain_share_floor_of_full_dynamic_savings"]:.6f}',
        'global_checkpoint_repair_available_before_amortization': True,
        'master_calendar_repairs_pre_amortization_checkpoint_underflow_without_raising_mode_budget': True,
        'maximum_live_floor_after_local_requirement_clip': near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings'],
        'main_rule': 'When a current exact uncertainty-safe request bundle is impossible, first try the smallest single-constraint repair: add one cap/checkpoint step, shave one slack/width step, or jump requested dwell directly onto the live support {2} union [8, 32]. Only floor overflow above 0.999822 lacks a menu-internal structural repair and therefore forces either a weaker requirement or new frontier evidence.',
    }


def _repair_rows(tiers: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lower = tiers['lower_guarantee']
    near_optimal = tiers['near_optimal']
    near_exact = tiers['near_exact']
    lower_floor = lower['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_optimal_floor = near_optimal['actual_certified_gain_share_floor_of_full_dynamic_savings']
    near_exact_floor = near_exact['actual_certified_gain_share_floor_of_full_dynamic_savings']
    return [
        {
            'case': 'hard_cap_underflow',
            'blocking_boundary': 'max_hard_cap_budget_inclusive < 3',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'max_hard_cap_budget_inclusive': 2,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'primary_repair': {
                'relaxation_type': 'raise_budget',
                'constraint': 'max_hard_cap_budget_inclusive',
                'old_value': 2,
                'new_value': 3,
                'delta': 1,
                'recovered_exact_tier': 'lower_guarantee',
            },
            'why': 'The exact 0.85 lane is the first live cap row, so hard-cap underflow is repaired by a single added cap step.',
        },
        {
            'case': 'pre_amortization_checkpoint_underflow',
            'blocking_boundary': 'pre-amortization checkpoint budget < 5',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {lower_floor:.6f}]',
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 4,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'primary_repair': {
                'relaxation_type': 'raise_budget',
                'constraint': 'max_pre_amortization_checkpoint_budget_inclusive',
                'old_value': 4,
                'new_value': 5,
                'delta': 1,
                'recovered_exact_tier': 'lower_guarantee',
            },
            'alternative_repair': {
                'relaxation_type': 'global_switch',
                'constraint': 'master_calendar_pre_registered',
                'old_value': False,
                'new_value': True,
                'delta': 'checkpoint bottleneck removed',
                'recovered_exact_tier': 'lower_guarantee',
            },
            'why': 'Before amortization, the relaxed exact lane needs five checkpoints. A one-checkpoint increase fixes the local budget; pre-registering the master calendar removes this bottleneck globally.',
        },
        {
            'case': 'certified_floor_overflow',
            'blocking_boundary': f'required floor > {near_exact_floor:.6f}',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_exact_floor:.6f}, 1.000000]',
                'max_hard_cap_budget_inclusive': near_exact['exact_hard_cap'],
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
            },
            'primary_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'required_gain_share_floor',
                'old_interval': f'({near_exact_floor:.6f}, 1.000000]',
                'new_ceiling': near_exact_floor,
                'recovered_exact_tier': 'near_exact',
            },
            'alternative_repair': {
                'relaxation_type': 'new_evidence',
                'constraint': 'saved_exact_frontier',
                'old_value': 'tops out at 0.999822',
                'new_value': 'extend frontier beyond 0.999822',
                'delta': 'new computation required',
                'recovered_exact_tier': None,
            },
            'why': 'Nothing inside the current exact menu exceeds floor 0.999822, so the only menu-internal repair is to weaken the floor request. Otherwise the frontier itself must grow.',
        },
        {
            'case': 'high_floor_positive_slack_conflict',
            'blocking_boundary': f'required floor > {near_optimal_floor:.6f} together with positive slack',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': near_exact['exact_hard_cap'],
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
            },
            'primary_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'required_gain_share_floor',
                'old_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'new_ceiling': near_optimal_floor,
                'recovered_exact_tier': 'near_optimal',
            },
            'alternative_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'minimum_anchor_slack_unique_appends',
                'old_value': 1,
                'new_value': 0,
                'delta': -1,
                'recovered_exact_tier': 'near_exact',
            },
            'why': 'Preserving positive slack forces the request back down into the exact 0.95 band; preserving the high floor forces the request all the way into the zero-slack precision point.',
        },
        {
            'case': 'high_floor_bandwidth_conflict',
            'blocking_boundary': f'required floor > {near_optimal_floor:.6f} together with minimum band width >= 2',
            'request_bundle': {
                'required_gain_share_floor_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': near_exact['exact_hard_cap'],
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 2,
            },
            'primary_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'required_gain_share_floor',
                'old_interval': f'({near_optimal_floor:.6f}, {near_exact_floor:.6f}]',
                'new_ceiling': near_optimal_floor,
                'recovered_exact_tier': 'near_optimal',
            },
            'alternative_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'minimum_band_width_unique_appends',
                'old_value': 2,
                'new_value': 1,
                'delta': -1,
                'recovered_exact_tier': 'near_exact',
            },
            'why': 'Preserving band width at 2 or more forces the request back into the exact 0.95 band; preserving the high floor collapses the request to the single-point width-1 precision tier.',
        },
        {
            'case': 'slack_overflow',
            'blocking_boundary': 'minimum anchor slack >= 7',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': near_exact['exact_hard_cap'],
                'minimum_anchor_slack_unique_appends': 7,
                'minimum_band_width_unique_appends': 1,
            },
            'primary_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'minimum_anchor_slack_unique_appends',
                'old_value': 7,
                'new_value': 6,
                'delta': -1,
                'recovered_exact_tier': 'lower_guarantee',
            },
            'why': 'Slack overflow repairs in one step because the relaxed exact 0.85 band certifies maximum slack 6.',
        },
        {
            'case': 'bandwidth_overflow',
            'blocking_boundary': 'minimum band width >= 15',
            'request_bundle': {
                'required_gain_share_floor_interval': f'[0, {near_exact_floor:.6f}]',
                'max_hard_cap_budget_inclusive': near_exact['exact_hard_cap'],
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 15,
            },
            'primary_repair': {
                'relaxation_type': 'lower_requirement',
                'constraint': 'minimum_band_width_unique_appends',
                'old_value': 15,
                'new_value': 14,
                'delta': -1,
                'recovered_exact_tier': 'lower_guarantee',
            },
            'why': 'Width overflow repairs in one step because the relaxed exact 0.85 band certifies maximum width 14.',
        },
        {
            'case': 'internal_dwell_gap_request',
            'blocking_boundary': 'requested dwell inside internal exact gap 3-7',
            'request_bundle': {
                'requested_exact_dwell_unique_appends_interval': '[3, 7]',
                'required_gain_share_floor_interval': f'[0, {near_exact_floor:.6f}]',
            },
            'primary_repair': {
                'relaxation_type': 'move_dwell',
                'constraint': 'requested_exact_dwell_unique_appends',
                'old_interval': '[3, 7]',
                'new_live_support': 8,
                'delta': 'jump to first non-fragile live dwell',
                'recovered_exact_tier': 'near_optimal',
            },
            'alternative_repair': {
                'relaxation_type': 'move_dwell',
                'constraint': 'requested_exact_dwell_unique_appends',
                'old_interval': '[3, 7]',
                'new_live_support': 2,
                'delta': 'jump to precision point',
                'recovered_exact_tier': 'near_exact',
            },
            'why': 'The gap 3–7 is not a tuning corridor. Non-fragile repairs jump forward to 8; precision repairs jump back to the isolated exact point at 2.',
        },
        {
            'case': 'below_current_exact_dwell_menu',
            'blocking_boundary': 'requested dwell below 2',
            'request_bundle': {
                'requested_exact_dwell_unique_appends_interval': '(-inf, 1]',
                'required_gain_share_floor_interval': f'[0, {near_exact_floor:.6f}]',
            },
            'primary_repair': {
                'relaxation_type': 'move_dwell',
                'constraint': 'requested_exact_dwell_unique_appends',
                'old_interval': '(-inf, 1]',
                'new_live_support': 2,
                'delta': 'clamp up to precision point',
                'recovered_exact_tier': 'near_exact',
            },
            'alternative_repair': {
                'relaxation_type': 'move_dwell',
                'constraint': 'requested_exact_dwell_unique_appends',
                'old_interval': '(-inf, 1]',
                'new_live_support': 8,
                'delta': 'jump to first non-fragile live dwell',
                'recovered_exact_tier': 'near_optimal',
            },
            'why': 'Below the menu, the nearest exact support is the isolated dwell-2 precision point; if fragility is unacceptable, the first non-fragile repair is dwell 8.',
        },
        {
            'case': 'above_current_exact_dwell_menu',
            'blocking_boundary': 'requested dwell above 32',
            'request_bundle': {
                'requested_exact_dwell_unique_appends_interval': '[33, +inf)',
                'required_gain_share_floor_interval': f'[0, {near_exact_floor:.6f}]',
            },
            'primary_repair': {
                'relaxation_type': 'move_dwell',
                'constraint': 'requested_exact_dwell_unique_appends',
                'old_interval': '[33, +inf)',
                'new_live_support': 32,
                'delta': 'clamp down to band edge',
                'recovered_exact_tier': 'lower_guarantee',
            },
            'why': 'Above the menu, the nearest current exact support is the top of the relaxed 0.85 band at dwell 32.',
        },
    ]


def _decision_rules() -> list[str]:
    return [
        'When a current exact request fails, look for a one-notch repair before you reopen the heavy frontier replay.',
        'Treat cap/checkpoint/slack/width underflow or overflow as local repair problems: adding or shaving a single unit already restores the relaxed exact 0.85 lane at the current boundary.',
        'Treat high-floor plus positive-slack or high-floor plus width-greater-than-1 conflicts as forked repairs: either lower the floor back into the exact 0.95 band or accept the fragile single-point exact 0.99 precision mode.',
        'Treat dwell 3 through 7 as a dead zone: repair by jumping directly to dwell 8 for non-fragile operation or to dwell 2 for precision, never by searching inside the gap.',
        'Treat floor demands above 0.999822 as frontier overflow: the current menu cannot repair them structurally, so either weaken the requirement or generate new frontier evidence.',
    ]


def _build_report() -> dict[str, Any]:
    tier_rows = _tier_rows()
    tiers = {row['tier']: row for row in tier_rows}
    return {
        'focus': 'Turn the exact uncertainty infeasibility screen into a smallest-relaxation repair guide so inheritors can fix impossible request bundles quickly instead of merely rejecting them.',
        'headline_findings': _headline_findings(tiers),
        'decision_rules': _decision_rules(),
        'tier_rows': tier_rows,
        'repair_rows': _repair_rows(tiers),
        'source_reports': [
            str(INFEASIBILITY_REPORT.relative_to(ROOT)),
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(POST_AMORTIZATION_REPORT.relative_to(ROOT)),
            str(TOPOLOGY_REPORT.relative_to(ROOT)),
            str(MASTER_CALENDAR_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty repair guide snapshot — 2026-03-08')
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
            f"cap `{row['exact_hard_cap']}`; mode checkpoints `{row['mode_specific_checkpoint_count']}`; "
            f"slack `{row['minimum_anchor_slack_unique_appends']}`; width `{row['exact_dwell_band_width_unique_appends']}`; "
            f"anchor `{row['representative_anchor_minimum_dwell_unique_appends']}`; band `{row['exact_dwell_band_start_unique_appends']}-{row['exact_dwell_band_end_unique_appends']}`"
        )
    lines.append('')
    lines.append('## Repair rows')
    for row in report['repair_rows']:
        lines.append(f"- **{row['case']}** — boundary `{row['blocking_boundary']}`")
        lines.append(f"  - request: `{json.dumps(row['request_bundle'], ensure_ascii=False)}`")
        lines.append(f"  - primary repair: `{json.dumps(row['primary_repair'], ensure_ascii=False)}`")
        if 'alternative_repair' in row:
            lines.append(f"  - alternative repair: `{json.dumps(row['alternative_repair'], ensure_ascii=False)}`")
        lines.append(f"  - why: {row['why']}")
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Source reports')
    for path in report['source_reports']:
        lines.append(f'- `{path}`')
    lines.append(f"- `source_script`: `{report['source_script']}`")
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    OUT_MD.write_text(_render_md(report) + '\n')
    print(OUT_JSON.relative_to(ROOT))
    print(OUT_MD.relative_to(ROOT))


if __name__ == '__main__':
    main()
