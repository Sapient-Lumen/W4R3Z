#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control import (
    decide_canonical_anchor_control,
)

REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.json'
OUT_MD = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.md'
GUARANTEE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'
ORACLE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_request_oracle_snapshot_20260308.json'
ROUTE_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.json'
BOUNDARY_PROTOCOL_REPORT = REPORTS / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.json'

CURRENT_TIERS = ['near_exact', 'near_optimal', 'lower_guarantee']
FLOOR_INTERVALS = [
    ('up_to_lower_guarantee_floor', '0.84', 'floor ≤ 0.870482'),
    ('middle_band', '0.95', '0.870482 < floor ≤ 0.980481'),
    ('precision_band', '0.99', '0.980481 < floor ≤ 0.999822'),
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _default_control_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for current_tier in CURRENT_TIERS:
        for interval_label, floor_value, floor_notation in FLOOR_INTERVALS:
            decision = decide_canonical_anchor_control(
                current_tier=current_tier,
                required_gain_share_floor=floor_value,
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                master_calendar_pre_registered=False,
                max_pre_amortization_checkpoint_budget_inclusive=14,
            )
            rows.append(
                {
                    'current_tier': current_tier,
                    'floor_interval_label': interval_label,
                    'floor_interval_notation': floor_notation,
                    'selected_steady_tier': decision['selected_steady_tier'],
                    'action_family': decision['action_family'],
                    'status': decision['status'],
                    'route_unique_appends': None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends'],
                    'exact_hard_cap_change_selected_minus_current': None if decision['selected_minus_current_deltas'] is None else decision['selected_minus_current_deltas']['exact_hard_cap_change_selected_minus_current'],
                    'mode_specific_checkpoint_change_selected_minus_current': None if decision['selected_minus_current_deltas'] is None else decision['selected_minus_current_deltas']['mode_specific_checkpoint_change_selected_minus_current'],
                    'minimum_anchor_slack_change_selected_minus_current': None if decision['selected_minus_current_deltas'] is None else decision['selected_minus_current_deltas']['minimum_anchor_slack_change_selected_minus_current'],
                    'exact_dwell_band_width_change_selected_minus_current': None if decision['selected_minus_current_deltas'] is None else decision['selected_minus_current_deltas']['exact_dwell_band_width_change_selected_minus_current'],
                }
            )
    return rows


def _example_rows() -> list[dict[str, Any]]:
    examples = [
        {
            'example_label': 'release_precision_premium_when_floor_drops',
            'input': {
                'current_tier': 'near_exact',
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_selected_tier': 'lower_guarantee',
            'expected_route': [2, 8, 19, 25],
        },
        {
            'example_label': 'upgrade_relaxed_anchor_to_middle_lane',
            'input': {
                'current_tier': 'lower_guarantee',
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 4,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'expected_status': 'retune_to_new_anchor',
            'expected_selected_tier': 'near_optimal',
            'expected_route': [25, 18, 13],
        },
        {
            'example_label': 'hold_middle_anchor_when_already_minimal',
            'input': {
                'current_tier': 'near_optimal',
                'required_gain_share_floor': '0.95',
                'max_hard_cap_budget_inclusive': 5,
                'minimum_anchor_slack_unique_appends': 2,
                'minimum_band_width_unique_appends': 4,
                'master_calendar_pre_registered': False,
                'max_pre_amortization_checkpoint_budget_inclusive': 8,
            },
            'expected_status': 'hold_current_anchor',
            'expected_selected_tier': 'near_optimal',
            'expected_route': None,
        },
        {
            'example_label': 'precision_request_with_positive_slack_is_infeasible',
            'input': {
                'current_tier': 'near_optimal',
                'required_gain_share_floor': '0.99',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 1,
                'minimum_band_width_unique_appends': 1,
                'master_calendar_pre_registered': True,
            },
            'expected_status': 'no_canonical_exact_tier',
            'expected_selected_tier': None,
            'expected_route': None,
        },
    ]

    resolved = []
    for row in examples:
        decision = decide_canonical_anchor_control(**row['input'])
        if decision['status'] != row['expected_status']:
            raise SystemExit(f"unexpected status for {row['example_label']}: {decision['status']}")
        if decision['selected_steady_tier'] != row['expected_selected_tier']:
            raise SystemExit(f"unexpected selected tier for {row['example_label']}: {decision['selected_steady_tier']}")
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        if route != row['expected_route']:
            raise SystemExit(f"unexpected route for {row['example_label']}: {route}")
        resolved.append({**row, 'decision': decision})
    return resolved


def _headline(control_rows: list[dict[str, Any]]) -> dict[str, Any]:
    route_rows = [row for row in control_rows if row['route_unique_appends'] is not None]
    holds = [row for row in control_rows if row['status'] == 'hold_current_anchor']
    weakens = [row for row in control_rows if row['action_family'] == 'weaken']
    strengthens = [row for row in control_rows if row['action_family'] == 'strengthen']
    return {
        'tier_selection_policy': 'choose the cheapest feasible exact tier for the declared steady-state request, then route from the current canonical anchor to that tier only if it differs',
        'control_matrix_shape': {'current_tiers': 3, 'floor_intervals': 3, 'ordered_states': 9},
        'holds_in_default_matrix': len(holds),
        'weakens_in_default_matrix': len(weakens),
        'strengthens_in_default_matrix': len(strengthens),
        'default_floor_only_matrix_reuses_existing_route_atlas': all(row['route_unique_appends'] is None or len(row['route_unique_appends']) >= 2 for row in route_rows),
        'largest_cap_release_in_default_matrix': min(row['exact_hard_cap_change_selected_minus_current'] for row in control_rows),
        'largest_checkpoint_release_in_default_matrix': min(row['mode_specific_checkpoint_change_selected_minus_current'] for row in control_rows),
        'largest_cap_increase_in_default_matrix': max(row['exact_hard_cap_change_selected_minus_current'] for row in control_rows),
        'largest_checkpoint_increase_in_default_matrix': max(row['mode_specific_checkpoint_change_selected_minus_current'] for row in control_rows),
        'main_rule': 'For canonical steady-state operation, do not keep a stronger anchor just because it is feasible: pick the cheapest exact tier that satisfies the current request, hold only if you are already there, weaken to release avoidable burden, strengthen only when the cheaper lanes no longer satisfy the request, and surface oracle blockers when no tier works.',
    }


def _decision_rules() -> list[str]:
    return [
        'This controller is for canonical steady-state deployments that are allowed to recenter to anchors `{2, 13, 25}`; it is not a fixed-dwell controller.',
        'Run the request oracle first to detect infeasible floor, budget, slack, or width bundles before discussing routes.',
        'Among feasible exact tiers, choose the cheapest one rather than the strongest one; otherwise the archive needlessly stays over-provisioned after floor relaxations.',
        'If the selected tier differs from the current tier, reuse the canonical-anchor path atlas instead of reopening dwell search.',
        'If a deployment is sitting on transient boundary `{8, 18, 19}` rather than a canonical anchor, repair and recenter with the boundary-stabilization protocol before using this steady-state controller.',
    ]


def _build_report() -> dict[str, Any]:
    control_rows = _default_control_matrix()
    return {
        'focus': 'Turn the exact uncertainty selector cards into a tiny steady-state canonical-anchor control law so inheritors can decide hold/strengthen/weaken/infeasible directly from the current anchor and a declared request bundle.',
        'headline_findings': _headline(control_rows),
        'decision_rules': _decision_rules(),
        'default_nonbinding_budget_control_matrix': control_rows,
        'examples': _example_rows(),
        'source_reports': [
            str(GUARANTEE_REPORT.relative_to(ROOT)),
            str(ORACLE_REPORT.relative_to(ROOT)),
            str(ROUTE_REPORT.relative_to(ROOT)),
            str(BOUNDARY_PROTOCOL_REPORT.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control.py',
    }


def _render_md(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append('# Compact repeat-state uncertainty canonical-anchor control snapshot — 2026-03-08')
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
    lines.append('## Default nonbinding-budget control matrix')
    lines.append('| current tier | floor interval | selected steady tier | action | route | cap Δ | checkpoints Δ | slack Δ | width Δ |')
    lines.append('|---|---|---|---|---|---:|---:|---:|---:|')
    for row in report['default_nonbinding_budget_control_matrix']:
        route = 'hold' if row['route_unique_appends'] is None else '→'.join(str(x) for x in row['route_unique_appends'])
        lines.append(
            f"| `{row['current_tier']}` | `{row['floor_interval_notation']}` | `{row['selected_steady_tier']}` | `{row['action_family']}` | `{route}` | `{row['exact_hard_cap_change_selected_minus_current']}` | `{row['mode_specific_checkpoint_change_selected_minus_current']}` | `{row['minimum_anchor_slack_change_selected_minus_current']}` | `{row['exact_dwell_band_width_change_selected_minus_current']}` |"
        )
    lines.append('')
    lines.append('## Checked examples')
    for row in report['examples']:
        decision = row['decision']
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        lines.append(
            f"- `{row['example_label']}`: status `{decision['status']}`, selected tier `{decision['selected_steady_tier']}`, action `{decision['action_family']}`, route `{route}`, blocker `{decision['blocking_summary']}`."
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
