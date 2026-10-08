#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    classify_saved_state,
    saved_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_STATES = saved_states()
DEFAULT_FLOORS = ['0.84', '0.95', '0.99']
REFERENCE_THRESHOLDS = [7, 11, 12, 17, 23]
THRESHOLD_BANDS = [
    {'label': '0–6', 'representative_threshold': 0},
    {'label': '7–10', 'representative_threshold': 7},
    {'label': '11–11', 'representative_threshold': 11},
    {'label': '12–16', 'representative_threshold': 12},
    {'label': '17–22', 'representative_threshold': 17},
    {'label': '23–∞', 'representative_threshold': 23},
]


class WeakeningHysteresisClosureError(RuntimeError):
    pass


def simulate_persistent_request_under_fixed_weakening_threshold(
    *,
    current_dwell_unique_appends: int,
    required_gain_share_floor: str | float,
    max_hard_cap_budget_inclusive: int,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = None,
    max_forced_weakening_shift_unique_appends: int,
    max_cycles: int = 8,
) -> dict[str, Any]:
    if max_cycles <= 0:
        raise WeakeningHysteresisClosureError('max_cycles must be positive')

    current_state = current_dwell_unique_appends
    sequence: list[dict[str, Any]] = []
    seen: set[tuple[int, str, str, tuple[int, ...] | None]] = set()

    for cycle_index in range(1, max_cycles + 1):
        decision = decide_saved_state_with_weakening_hysteresis(
            current_dwell_unique_appends=current_state,
            required_gain_share_floor=required_gain_share_floor,
            max_hard_cap_budget_inclusive=max_hard_cap_budget_inclusive,
            minimum_anchor_slack_unique_appends=minimum_anchor_slack_unique_appends,
            minimum_band_width_unique_appends=minimum_band_width_unique_appends,
            master_calendar_pre_registered=master_calendar_pre_registered,
            max_pre_amortization_checkpoint_budget_inclusive=max_pre_amortization_checkpoint_budget_inclusive,
            max_forced_weakening_shift_unique_appends=max_forced_weakening_shift_unique_appends,
        )
        route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
        to_state = current_state if route is None else route[-1]
        step = {
            'cycle_index': cycle_index,
            'from_state_unique_appends': current_state,
            'from_state_label': classify_saved_state(current_state)['state_label'],
            'status': decision['status'],
            'action_family': decision['action_family'],
            'selected_steady_tier': decision['selected_steady_tier'],
            'route_unique_appends': route,
            'to_state_unique_appends': to_state,
            'deferred_weaken': decision['deferred_weaken'],
        }
        sequence.append(step)

        if decision['action_family'] in {'hold', 'infeasible'} and route is None:
            final_state = classify_saved_state(current_state)
            return {
                'tool': str(Path(__file__).resolve()),
                'required_gain_share_floor': str(required_gain_share_floor),
                'max_forced_weakening_shift_unique_appends': max_forced_weakening_shift_unique_appends,
                'sequence': sequence,
                'settled': True,
                'settled_after_cycles': cycle_index,
                'final_state_unique_appends': current_state,
                'final_state': final_state,
                'termination_reason': 'fixed_point_hold' if decision['action_family'] == 'hold' else 'infeasible_request',
            }

        loop_key = (current_state, decision['action_family'], decision['status'], tuple(route) if route else None)
        if loop_key in seen:
            raise WeakeningHysteresisClosureError(
                f'non-terminating loop detected for state {current_state}, floor {required_gain_share_floor}, threshold {max_forced_weakening_shift_unique_appends}'
            )
        seen.add(loop_key)
        current_state = to_state

    raise WeakeningHysteresisClosureError(
        f'closure did not settle within {max_cycles} cycles for floor {required_gain_share_floor} and threshold {max_forced_weakening_shift_unique_appends}'
    )



def build_threshold_closure_matrix(
    *,
    current_states: list[int] | None = None,
    floors: list[str] | None = None,
    max_hard_cap_budget_inclusive: int = 11,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = 14,
) -> list[dict[str, Any]]:
    current_states = DEFAULT_CURRENT_STATES if current_states is None else current_states
    floors = DEFAULT_FLOORS if floors is None else floors
    rows: list[dict[str, Any]] = []
    for band in THRESHOLD_BANDS:
        threshold = band['representative_threshold']
        final_counts: Counter[int] = Counter()
        max_cycles = 0
        for current_state in current_states:
            for floor in floors:
                closure = simulate_persistent_request_under_fixed_weakening_threshold(
                    current_dwell_unique_appends=current_state,
                    required_gain_share_floor=floor,
                    max_hard_cap_budget_inclusive=max_hard_cap_budget_inclusive,
                    minimum_anchor_slack_unique_appends=minimum_anchor_slack_unique_appends,
                    minimum_band_width_unique_appends=minimum_band_width_unique_appends,
                    master_calendar_pre_registered=master_calendar_pre_registered,
                    max_pre_amortization_checkpoint_budget_inclusive=max_pre_amortization_checkpoint_budget_inclusive,
                    max_forced_weakening_shift_unique_appends=threshold,
                )
                final_counts[closure['final_state_unique_appends']] += 1
                max_cycles = max(max_cycles, closure['settled_after_cycles'])
        rows.append(
            {
                'threshold_band_label': band['label'],
                'representative_threshold_unique_appends': threshold,
                'final_anchor_counts': {str(anchor): final_counts.get(anchor, 0) for anchor in [2, 13, 25]},
                'max_cycles_to_settle': max_cycles,
            }
        )
    return rows



def _compress_consecutive_states(states: list[int]) -> list[int]:
    compressed: list[int] = []
    for state in states:
        if not compressed or compressed[-1] != state:
            compressed.append(state)
    return compressed


def build_floor_relaxation_release_table() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for current_state in DEFAULT_CURRENT_STATES:
        eventual_threshold = None
        direct_threshold = None
        eventual_cycles = None
        eventual_route = None
        for threshold in range(0, 24):
            closure = simulate_persistent_request_under_fixed_weakening_threshold(
                current_dwell_unique_appends=current_state,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=threshold,
            )
            if closure['final_state_unique_appends'] == 25:
                eventual_threshold = threshold
                eventual_cycles = closure['settled_after_cycles']
                eventual_route = _compress_consecutive_states([step['to_state_unique_appends'] for step in closure['sequence']])
                break
        for threshold in range(0, 24):
            first = decide_saved_state_with_weakening_hysteresis(
                current_dwell_unique_appends=current_state,
                required_gain_share_floor='0.84',
                max_hard_cap_budget_inclusive=11,
                minimum_anchor_slack_unique_appends=0,
                minimum_band_width_unique_appends=1,
                max_pre_amortization_checkpoint_budget_inclusive=14,
                max_forced_weakening_shift_unique_appends=threshold,
            )
            route = None if first['route_plan'] is None else first['route_plan']['route_unique_appends']
            if current_state == 25:
                direct_threshold = 0
                break
            if route is not None and route[-1] == 25:
                direct_threshold = threshold
                break
        state = classify_saved_state(current_state)
        rows.append(
            {
                'current_state_unique_appends': current_state,
                'current_state_label': state['state_label'],
                'current_tier': state['current_tier'],
                'minimum_threshold_for_eventual_relaxed_anchor': eventual_threshold,
                'minimum_threshold_for_direct_relaxed_anchor': direct_threshold,
                'cycles_to_relaxed_anchor_at_eventual_threshold': eventual_cycles,
                'eventual_route_state_suffix_at_threshold': eventual_route,
            }
        )
    return rows



def build_reference_examples() -> list[dict[str, Any]]:
    examples = [
        {
            'example_label': 'threshold_twelve_stages_entry_boundary_to_relaxed_anchor',
            'input': {
                'current_dwell_unique_appends': 8,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 12,
            },
            'expected_final_state': 25,
            'expected_cycles': 3,
            'expected_actions': ['stabilize', 'weaken', 'hold'],
        },
        {
            'example_label': 'threshold_eleven_keeps_precision_sticky_under_relaxed_floor',
            'input': {
                'current_dwell_unique_appends': 2,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 11,
            },
            'expected_final_state': 2,
            'expected_cycles': 1,
            'expected_actions': ['hold'],
        },
        {
            'example_label': 'threshold_seventeen_shortens_but_does_not_change_entry_boundary_destination',
            'input': {
                'current_dwell_unique_appends': 8,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 17,
            },
            'expected_final_state': 25,
            'expected_cycles': 2,
            'expected_actions': ['weaken', 'hold'],
        },
        {
            'example_label': 'threshold_twenty_three_recovers_direct_precision_release',
            'input': {
                'current_dwell_unique_appends': 2,
                'required_gain_share_floor': '0.84',
                'max_hard_cap_budget_inclusive': 11,
                'minimum_anchor_slack_unique_appends': 0,
                'minimum_band_width_unique_appends': 1,
                'max_pre_amortization_checkpoint_budget_inclusive': 14,
                'max_forced_weakening_shift_unique_appends': 23,
            },
            'expected_final_state': 25,
            'expected_cycles': 2,
            'expected_actions': ['weaken', 'hold'],
        },
    ]

    resolved = []
    for example in examples:
        closure = simulate_persistent_request_under_fixed_weakening_threshold(**example['input'])
        actions = [step['action_family'] for step in closure['sequence']]
        if closure['final_state_unique_appends'] != example['expected_final_state']:
            raise WeakeningHysteresisClosureError(
                f"unexpected final state for {example['example_label']}: {closure['final_state_unique_appends']}"
            )
        if closure['settled_after_cycles'] != example['expected_cycles']:
            raise WeakeningHysteresisClosureError(
                f"unexpected cycle count for {example['example_label']}: {closure['settled_after_cycles']}"
            )
        if actions != example['expected_actions']:
            raise WeakeningHysteresisClosureError(
                f"unexpected action chain for {example['example_label']}: {actions}"
            )
        resolved.append({**example, 'closure': closure})
    return resolved



def build_weakening_hysteresis_closure_snapshot() -> dict[str, Any]:
    closure_bands = build_threshold_closure_matrix()
    release_table = build_floor_relaxation_release_table()
    threshold12_entry_boundary = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=8,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=12,
    )
    threshold17_entry_boundary = simulate_persistent_request_under_fixed_weakening_threshold(
        current_dwell_unique_appends=8,
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=17,
    )
    precision_relaxed_threshold = next(
        row['minimum_threshold_for_eventual_relaxed_anchor']
        for row in release_table
        if row['current_state_unique_appends'] == 2
    )

    return {
        'focus': 'Trace the weakening-hysteresis overlay to its eventual canonical anchor under persistent requests, so inheritors can tell which thresholds merely delay weakening and which thresholds permanently keep a stronger exact tier parked.',
        'headline_findings': {
            'main_rule': 'A fixed weakening threshold creates exact eventual anchor basins under persistent requests: some deferred weakenings are only delayed, while others remain permanently blocked until a larger threshold band is admitted.',
            'one_shot_weakening_breakpoints_unique_appends': REFERENCE_THRESHOLDS,
            'closure_threshold_bands': [band['label'] for band in THRESHOLD_BANDS],
            'lowest_threshold_final_anchor_counts': closure_bands[0]['final_anchor_counts'],
            'threshold_twelve_is_smallest_eventual_relaxed_release_for_entry_boundary_eight': 12,
            'threshold_seventeen_is_smallest_direct_relaxed_release_for_entry_boundary_eight': 17,
            'precision_anchor_two_needs_full_threshold_for_relaxed_release': precision_relaxed_threshold,
            'highest_threshold_final_anchor_counts': closure_bands[-1]['final_anchor_counts'],
        },
        'decision_rules': [
            'Use this closure view only after the one-shot weakening hysteresis overlay has been chosen; it explains the long-run effect of holding that threshold fixed under repeated identical requests.',
            'Differentiate direct release from eventual release: a threshold may be too small for the first weakening move but still large enough to permit a later weakening after a cheap stabilization to a nearer canonical anchor.',
            'For persistent relaxed-floor requests, boundary entry state `8` is the key staged case: threshold `12` eventually reaches relaxed anchor `25`, but threshold `17` is required for the direct one-cycle jump.',
            'Precision anchor `2` is uniquely sticky under relaxed floors because the cheapest-tier policy targets `25` directly; there is no staged release path unless the threshold reaches the full `23`-append outer-anchor move.',
            'Strengthenings and same-band stabilizations remain non-optional, so threshold tuning only changes which weakenings happen now, later, or never.',
        ],
        'persistent_floor_relaxation_release_table': release_table,
        'threshold_closure_bands': closure_bands,
        'reference_entry_boundary_threshold_twelve_closure': threshold12_entry_boundary,
        'reference_entry_boundary_threshold_seventeen_closure': threshold17_entry_boundary,
        'examples': build_reference_examples(),
        'source_script': str(Path(__file__).relative_to(ROOT)),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Trace weakening-hysteresis closure to eventual canonical anchors under persistent requests.')
    parser.add_argument('--pretty', action='store_true')
    return parser



def main() -> None:
    args = _parser().parse_args()
    report = build_weakening_hysteresis_closure_snapshot()
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
