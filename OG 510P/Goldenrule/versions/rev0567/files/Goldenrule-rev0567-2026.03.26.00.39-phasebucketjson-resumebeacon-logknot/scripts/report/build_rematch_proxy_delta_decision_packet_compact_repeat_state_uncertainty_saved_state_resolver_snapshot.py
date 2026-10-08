#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    decide_saved_state_resolution,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.md'
ORACLE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.json'
BOUNDARY_PROTOCOL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.json'
ANCHOR_CONTROL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.json'
ROUTE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.json'

CURRENT_STATES = [2, 8, 13, 18, 19, 25]
FLOOR_INTERVALS = [
    ('up_to_lower_guarantee_floor', '0.84', 'floor ≤ 0.870482'),
    ('middle_band', '0.95', '0.870482 < floor ≤ 0.980481'),
    ('precision_band', '0.99', '0.980481 < floor ≤ 0.999822'),
]


def _default_resolution_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for current_state in CURRENT_STATES:
        for interval_label, floor_value, floor_notation in FLOOR_INTERVALS:
            decision = decide_saved_state_resolution(
                current_dwell_unique_appends=current_state,
                required_gain_share_floor=floor_value,
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            )
            route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
            deltas = decision['selected_minus_current_band_deltas']
            rows.append(
                {
                    'current_state_unique_appends': current_state,
                    'current_state_label': decision['current_state']['state_label'],
                    'current_state_kind': decision['current_state']['state_kind'],
                    'current_band_tier': decision['current_state']['current_tier'],
                    'floor_interval_label': interval_label,
                    'floor_interval_notation': floor_notation,
                    'selected_steady_tier': decision['selected_steady_tier'],
                    'action_family': decision['action_family'],
                    'status': decision['status'],
                    'route_unique_appends': route,
                    'exact_hard_cap_change_selected_minus_current_band': None if deltas is None else deltas['exact_hard_cap_change_selected_minus_current_band'],
                    'mode_specific_checkpoint_change_selected_minus_current_band': None if deltas is None else deltas['mode_specific_checkpoint_change_selected_minus_current_band'],
                    'minimum_anchor_slack_change_selected_minus_current_band': None if deltas is None else deltas['minimum_anchor_slack_change_selected_minus_current_band'],
                    'exact_dwell_band_width_change_selected_minus_current_band': None if deltas is None else deltas['exact_dwell_band_width_change_selected_minus_current_band'],
                    'total_absolute_dwell_shift_unique_appends': 0 if decision['route_plan'] is None else decision['route_plan']['total_absolute_dwell_shift_unique_appends'],
                }
            )
    return rows


def _example_rows() -> list[dict[str, Any]]:
    examples = [
        {
            'example_label': 'stabilize_neutral_entry_boundary_when_middle_lane_is_still_cheapest',
            'input': {
                'current_dwell_unique_appends': 8,
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 4,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'expected_status': 'stabilize_current_band',
            'expected_action': 'stabilize',
            'expected_selected_tier': 'near_optimal',
            'expected_route': [8, 13],
        },
        {
            'example_label': 'stabilize_relaxed_entry_boundary_when_low_floor_persists',
            'input': {
                'current_dwell_unique_appends': 19,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 3,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 5,
            },
            'expected_status': 'stabilize_current_band',
            'expected_action': 'stabilize',
            'expected_selected_tier': 'lower_guarantee',
            'expected_route': [19, 25],
        },
        {
            'example_label': 'weaken_neutral_exit_boundary_after_floor_relaxation',
            'input': {
                'current_dwell_unique_appends': 18,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'weaken',
            'expected_selected_tier': 'lower_guarantee',
            'expected_route': [18, 19, 25],
        },
        {
            'example_label': 'strengthen_relaxed_entry_boundary_to_middle_anchor',
            'input': {
                'current_dwell_unique_appends': 19,
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 4,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'strengthen',
            'expected_selected_tier': 'near_optimal',
            'expected_route': [19, 18, 13],
        },
        {
            'example_label': 'collapse_neutral_entry_boundary_to_precision_when_high_floor_arrives',
            'input': {
                'current_dwell_unique_appends': 8,
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'strengthen',
            'expected_selected_tier': 'near_exact',
            'expected_route': [8, 2],
        },
        {
            'example_label': 'positive_slack_can_still_block_saved_state_resolution',
            'input': {
                'current_dwell_unique_appends': 18,
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': True,
            },
            'expected_status': 'no_saved_state_resolution',
            'expected_action': 'infeasible',
            'expected_selected_tier': None,
            'expected_route': None,
        },
    ]

    resolved: list[dict[str, Any]] = []
    for row in examples:
        decision = decide_saved_state_resolution(**row['input'])
        if decision['status'] != row['expected_status']:
            raise SystemExit(f"unexpected status for {row['example_label']}: {decision['status']}")
        if decision['action_family'] != row['expected_action']:
            raise SystemExit(f"unexpected action for {row['example_label']}: {decision['action_family']}")
        if decision['selected_steady_tier'] != row['expected_selected_tier']:
            raise SystemExit(f"unexpected selected tier for {row['example_label']}: {decision['selected_steady_tier']}")
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        if route != row['expected_route']:
            raise SystemExit(f"unexpected route for {row['example_label']}: {route}")
        resolved.append({**row, 'decision': decision})
    return resolved


def _headline(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts = {
        action: sum(1 for row in matrix if row['action_family'] == action)
        for action in ['hold', 'stabilize', 'weaken', 'strengthen']
    }
    stabilize_rows = [row for row in matrix if row['action_family'] == 'stabilize']
    strengthening_rows = [row for row in matrix if row['action_family'] == 'strengthen']
    return {
        'resolver_selection_policy': 'choose the cheapest feasible exact tier for the declared request, then resolve any saved control state directly to that tier\'s canonical anchor',
        'control_matrix_shape': {'current_saved_states': 6, 'floor_intervals': 3, 'ordered_states': 18},
        'default_matrix_action_counts': action_counts,
        'transient_boundaries_supported_directly': [8, 18, 19],
        'boundary_states_that_only_need_stabilization_when_their_band_remains_selected': [8, 18, 19],
        'maximum_stabilization_only_shift_unique_appends': max(row['total_absolute_dwell_shift_unique_appends'] for row in stabilize_rows),
        'minimum_direct_precision_collapse_from_transient_boundary_unique_appends': min(
            row['total_absolute_dwell_shift_unique_appends']
            for row in strengthening_rows
            if row['selected_steady_tier'] == 'near_exact'
        ),
        'main_rule': 'Do not make inheritors compose a boundary protocol and an anchor controller by hand: once the cheapest feasible exact tier is known, resolve directly from the current saved state `{2, 8, 13, 18, 19, 25}` to the destination canonical anchor, treating same-band boundaries as cheap stabilization rather than as a fresh search problem.',
    }


def _decision_rules() -> list[str]:
    return [
        'Use this resolver when the live control state is one of the saved anchors or transient support boundaries `{2, 8, 13, 18, 19, 25}`.',
        'Run the request oracle first and still fail fast on infeasible floor, budget, slack, or width bundles; saved-state routing does not override those blockers.',
        'If the cheapest feasible tier matches the current band and the current state is a transient boundary, treat the move as stabilization, not as hold and not as a new dwell search.',
        'If the cheapest feasible tier differs from the current band, resolve directly from the current saved state to the destination canonical anchor using the exact saved route instead of first recentering to the old anchor and then rerunning a second controller.',
        'The only saved states that are not steady-ready are `8`, `18`, and `19`; their stabilization tax is at most 6 unique appends.',
    ]


def _build_report() -> dict[str, Any]:
    matrix = _default_resolution_matrix()
    return {
        'focus': 'Extend exact-uncertainty control from canonical anchors to the full saved control-state menu, so inheritors can resolve directly from transient boundaries as well as anchors without manually composing two separate cards.',
        'headline_findings': _headline(matrix),
        'decision_rules': _decision_rules(),
        'default_nonbinding_budget_resolution_matrix': matrix,
        'examples': _example_rows(),
        'source_reports': [
            str(ORACLE_REPORT.relative_to(ROOT)),
            str(BOUNDARY_PROTOCOL_REPORT.relative_to(ROOT)),
            str(ANCHOR_CONTROL_REPORT.relative_to(ROOT)),
            str(ROUTE_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver.py',
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty saved-state resolver snapshot — 2026-03-08')
    lines.append('')
    lines.append(f"Focus: {report['focus']}")
    lines.append('')
    lines.append('## Headline findings')
    for key, value in report['headline_findings'].items():
        lines.append(f'- **{key}**: `{json.dumps(value, ensure_ascii=False)}`')
    lines.append('')
    lines.append('## Decision rules')
    for rule in report['decision_rules']:
        lines.append(f'- {rule}')
    lines.append('')
    lines.append('## Default nonbinding-budget resolution matrix')
    lines.append('| current state | kind | current band | floor interval | selected steady tier | action | route | cap Δ vs band | checkpoints Δ vs band | shift |')
    lines.append('|---:|---|---|---|---|---|---|---:|---:|---:|')
    for row in report['default_nonbinding_budget_resolution_matrix']:
        route = 'hold' if row['route_unique_appends'] is None else '→'.join(str(x) for x in row['route_unique_appends'])
        lines.append(
            f"| `{row['current_state_unique_appends']}` | `{row['current_state_kind']}` | `{row['current_band_tier']}` | `{row['floor_interval_notation']}` | `{row['selected_steady_tier']}` | `{row['action_family']}` | `{route}` | `{row['exact_hard_cap_change_selected_minus_current_band']}` | `{row['mode_specific_checkpoint_change_selected_minus_current_band']}` | `{row['total_absolute_dwell_shift_unique_appends']}` |"
        )
    lines.append('')
    lines.append('## Checked examples')
    for row in report['examples']:
        decision = row['decision']
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        lines.append(
            f"- `{row['example_label']}`: status `{decision['status']}`, action `{decision['action_family']}`, selected tier `{decision['selected_steady_tier']}`, route `{route}`, blocker `{decision['blocking_summary']}`."
        )
    lines.append('')
    lines.append('## Source reports')
    for src in report['source_reports']:
        lines.append(f'- `{src}`')
    lines.append(f"- `{report['analysis_script']}`")
    lines.append(f"- `{report['source_script']}`")
    return '\n'.join(lines) + '\n'


def main() -> None:
    report = _build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)}')
    print(f'wrote {OUT_MD.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
