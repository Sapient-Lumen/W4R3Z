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
    classify_saved_state,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.md'
RESOLVER_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.json'

CURRENT_STATES = [2, 8, 13, 18, 19, 25]
FLOOR_INTERVALS = [
    ('up_to_lower_guarantee_floor', '0.84', 'floor ≤ 0.870482'),
    ('middle_band', '0.95', '0.870482 < floor ≤ 0.980481'),
    ('precision_band', '0.99', '0.980481 < floor ≤ 0.999822'),
]
REFERENCE_THRESHOLDS = [0, 7, 11, 12, 17, 23]


def _decision(current_state: int, floor_value: str, threshold: int) -> dict[str, Any]:
    return decide_saved_state_with_weakening_hysteresis(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor_value,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=threshold,
    )


def _label(current_state: int, floor_label: str, decision: dict[str, Any]) -> str:
    state = classify_saved_state(current_state)
    return f"{current_state}:{state['state_label']}@{floor_label}->{decision['base_resolver_decision']['selected_steady_tier']}"


def _base_weakening_cases() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for current_state in CURRENT_STATES:
        for floor_label, floor_value, floor_notation in FLOOR_INTERVALS:
            decision = _decision(current_state, floor_value, 23)
            base = decision['base_resolver_decision']
            if base['action_family'] != 'weaken':
                continue
            route_plan = base['route_plan']
            rows.append(
                {
                    'case_label': _label(current_state, floor_label, decision),
                    'current_state_unique_appends': current_state,
                    'current_state_label': base['current_state']['state_label'],
                    'current_state_kind': base['current_state']['state_kind'],
                    'floor_interval_label': floor_label,
                    'floor_interval_notation': floor_notation,
                    'current_tier': base['current_state']['current_tier'],
                    'selected_weaker_tier': base['selected_steady_tier'],
                    'route_unique_appends': route_plan['route_unique_appends'],
                    'weakening_shift_unique_appends': route_plan['total_absolute_dwell_shift_unique_appends'],
                    'steady_state_savings_vs_current_band': {
                        'exact_hard_cap_units': abs(base['selected_minus_current_band_deltas']['exact_hard_cap_change_selected_minus_current_band']),
                        'mode_specific_checkpoint_units': abs(base['selected_minus_current_band_deltas']['mode_specific_checkpoint_change_selected_minus_current_band']),
                    },
                }
            )
    rows.sort(key=lambda row: (row['weakening_shift_unique_appends'], row['current_state_unique_appends'], row['floor_interval_label']))
    return rows


def _threshold_row(threshold: int) -> dict[str, Any]:
    action_counts = {'hold': 0, 'stabilize': 0, 'weaken': 0, 'strengthen': 0}
    deferred_cases: list[str] = []
    forced_cases: list[str] = []
    for current_state in CURRENT_STATES:
        for floor_label, floor_value, _floor_notation in FLOOR_INTERVALS:
            decision = _decision(current_state, floor_value, threshold)
            action_counts[decision['action_family']] += 1
            if decision['base_resolver_decision']['action_family'] == 'weaken':
                case_label = _label(current_state, floor_label, decision)
                if decision['deferred_weaken']:
                    deferred_cases.append(case_label)
                else:
                    forced_cases.append(case_label)
    return {
        'max_forced_weakening_shift_unique_appends': threshold,
        'action_counts': action_counts,
        'forced_weakening_cases': forced_cases,
        'deferred_weakening_cases': deferred_cases,
    }


def _threshold_frontier(base_weaken_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shifts = sorted({row['weakening_shift_unique_appends'] for row in base_weaken_rows})
    frontier: list[dict[str, Any]] = []
    lower = 0
    for index, shift in enumerate(shifts):
        row = _threshold_row(shift - 1)
        frontier.append(
            {
                'threshold_band_start_inclusive': lower,
                'threshold_band_end_inclusive': shift - 1,
                'forced_weakening_case_count': len(row['forced_weakening_cases']),
                'deferred_weakening_case_count': len(row['deferred_weakening_cases']),
                'action_counts': row['action_counts'],
                'newly_admitted_weakening_shift_at_next_breakpoint': shift,
            }
        )
        lower = shift
    row = _threshold_row(shifts[-1])
    frontier.append(
        {
            'threshold_band_start_inclusive': shifts[-1],
            'threshold_band_end_inclusive': None,
            'forced_weakening_case_count': len(row['forced_weakening_cases']),
            'deferred_weakening_case_count': len(row['deferred_weakening_cases']),
            'action_counts': row['action_counts'],
            'newly_admitted_weakening_shift_at_next_breakpoint': None,
        }
    )
    return frontier


def _headline(base_weaken_rows: list[dict[str, Any]], frontier: list[dict[str, Any]]) -> dict[str, Any]:
    weakest = frontier[0]
    strongest = frontier[-1]
    return {
        'main_rule': 'Strengthening remains mandatory, but weakening can be gated by a one-shot shift threshold because the current stronger tier already satisfies the request whenever a cheapest-tier weakening is proposed.',
        'default_base_matrix_weakening_case_count': len(base_weaken_rows),
        'exact_weakening_shift_breakpoints_unique_appends': [row['weakening_shift_unique_appends'] for row in base_weaken_rows],
        'lowest_threshold_band_action_counts': weakest['action_counts'],
        'full_base_policy_recovered_at_threshold_unique_appends': 23,
        'largest_deferrable_one_shot_weakening_shift_unique_appends': max(row['weakening_shift_unique_appends'] for row in base_weaken_rows),
        'smallest_forced_weakening_shift_unique_appends': min(row['weakening_shift_unique_appends'] for row in base_weaken_rows),
        'boundary_deferrals_recenter_before_waiting': [8, 18],
        'highest_threshold_band_action_counts': strongest['action_counts'],
    }


def _decision_rules() -> list[str]:
    return [
        'Apply this overlay only after the saved-state resolver has already identified a cheapest feasible exact tier.',
        'Never defer strengthenings: if the current tier is too weak for the declared request, move immediately.',
        'Only cheapest-tier weakenings are deferrable, because those are exactly the cases where the current stronger tier still satisfies the request.',
        'If a weakening is deferred from transient boundary `8` or `18`, stabilize to canonical anchor `13` instead of leaving the deployment stranded on a boundary.',
        'A threshold of `23` reproduces the base cheapest-tier resolver; smaller thresholds trade away future cap/checkpoint savings to avoid large one-shot retunes.',
    ]


def _examples() -> list[dict[str, Any]]:
    examples = [
        {
            'example_label': 'threshold_zero_turns_precision_to_middle_weaken_into_hold',
            'input': {
                'current_dwell_unique_appends': 2,
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 0,
            },
            'expected_status': 'defer_weakening_keep_current_anchor',
            'expected_action': 'hold',
            'expected_route': None,
        },
        {
            'example_label': 'threshold_zero_turns_neutral_entry_weaken_into_stabilize',
            'input': {
                'current_dwell_unique_appends': 8,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 0,
            },
            'expected_status': 'defer_weakening_stabilize_current_stronger_band',
            'expected_action': 'stabilize',
            'expected_route': [8, 13],
        },
        {
            'example_label': 'threshold_ten_allows_smallest_neutral_to_relaxed_weaken',
            'input': {
                'current_dwell_unique_appends': 18,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 10,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'weaken',
            'expected_route': [18, 19, 25],
        },
        {
            'example_label': 'strengthening_ignores_threshold',
            'input': {
                'current_dwell_unique_appends': 19,
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 0,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_action': 'strengthen',
            'expected_route': [19, 18, 13],
        },
        {
            'example_label': 'infeasibility_still_blocks',
            'input': {
                'current_dwell_unique_appends': 18,
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': True,
                'max_forced_weakening_shift_unique_appends': 0,
            },
            'expected_status': 'no_saved_state_resolution',
            'expected_action': 'infeasible',
            'expected_route': None,
        },
    ]
    resolved: list[dict[str, Any]] = []
    for row in examples:
        decision = decide_saved_state_with_weakening_hysteresis(**row['input'])
        if decision['status'] != row['expected_status']:
            raise SystemExit(f"unexpected status for {row['example_label']}: {decision['status']}")
        if decision['action_family'] != row['expected_action']:
            raise SystemExit(f"unexpected action for {row['example_label']}: {decision['action_family']}")
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        if route != row['expected_route']:
            raise SystemExit(f"unexpected route for {row['example_label']}: {route}")
        resolved.append({**row, 'decision': decision})
    return resolved


def _build_report() -> dict[str, Any]:
    base_weaken_rows = _base_weakening_cases()
    frontier = _threshold_frontier(base_weaken_rows)
    return {
        'focus': 'Add one small hysteresis overlay above the saved-state resolver so inheritors can defer large one-shot weakenings without ever deferring mandatory strengthenings or reopening dwell search.',
        'headline_findings': _headline(base_weaken_rows, frontier),
        'decision_rules': _decision_rules(),
        'base_policy_weakening_cases': base_weaken_rows,
        'weakening_shift_threshold_frontier': frontier,
        'reference_threshold_rows': [_threshold_row(threshold) for threshold in REFERENCE_THRESHOLDS],
        'examples': _examples(),
        'source_reports': [str(RESOLVER_REPORT.relative_to(ROOT))],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis.py',
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty weakening-hysteresis snapshot — 2026-03-08')
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
    lines.append('## Base-policy weakening cases')
    lines.append('| case | route | shift | cap saved | checkpoints saved |')
    lines.append('|---|---|---:|---:|---:|')
    for row in report['base_policy_weakening_cases']:
        savings = row['steady_state_savings_vs_current_band']
        lines.append(
            f"| `{row['case_label']}` | `{'→'.join(str(x) for x in row['route_unique_appends'])}` | `{row['weakening_shift_unique_appends']}` | `{savings['exact_hard_cap_units']}` | `{savings['mode_specific_checkpoint_units']}` |"
        )
    lines.append('')
    lines.append('## Weakening-shift threshold frontier')
    lines.append('| threshold band | forced weakenings | deferred weakenings | action counts | next breakpoint |')
    lines.append('|---|---:|---:|---|---:|')
    for row in report['weakening_shift_threshold_frontier']:
        band_end = '∞' if row['threshold_band_end_inclusive'] is None else row['threshold_band_end_inclusive']
        next_bp = '—' if row['newly_admitted_weakening_shift_at_next_breakpoint'] is None else row['newly_admitted_weakening_shift_at_next_breakpoint']
        lines.append(
            f"| `{row['threshold_band_start_inclusive']}–{band_end}` | `{row['forced_weakening_case_count']}` | `{row['deferred_weakening_case_count']}` | `{json.dumps(row['action_counts'], ensure_ascii=False)}` | `{next_bp}` |"
        )
    lines.append('')
    lines.append('## Reference threshold rows')
    lines.append('| threshold | action counts | forced weakenings | deferred weakenings |')
    lines.append('|---:|---|---|---|')
    for row in report['reference_threshold_rows']:
        lines.append(
            f"| `{row['max_forced_weakening_shift_unique_appends']}` | `{json.dumps(row['action_counts'], ensure_ascii=False)}` | `{json.dumps(row['forced_weakening_cases'], ensure_ascii=False)}` | `{json.dumps(row['deferred_weakening_cases'], ensure_ascii=False)}` |"
        )
    lines.append('')
    lines.append('## Checked examples')
    for row in report['examples']:
        decision = row['decision']
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        lines.append(
            f"- `{row['example_label']}`: status `{decision['status']}`, action `{decision['action_family']}`, selected tier `{decision['selected_steady_tier']}`, route `{route}`, deferred weaken `{decision['deferred_weaken']}`."
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
