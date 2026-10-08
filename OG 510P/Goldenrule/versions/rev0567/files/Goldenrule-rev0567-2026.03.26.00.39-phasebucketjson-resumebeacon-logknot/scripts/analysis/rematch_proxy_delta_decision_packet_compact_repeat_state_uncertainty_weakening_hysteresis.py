#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    classify_saved_state,
    decide_saved_state_resolution,
    plan_saved_state_route,
    saved_states,
)

ROOT = Path(__file__).resolve().parents[2]


class WeakeningHysteresisError(ValueError):
    pass


def decide_saved_state_with_weakening_hysteresis(
    *,
    current_dwell_unique_appends: int,
    required_gain_share_floor: str | float,
    max_hard_cap_budget_inclusive: int,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = None,
    max_forced_weakening_shift_unique_appends: int = 23,
) -> dict[str, Any]:
    if max_forced_weakening_shift_unique_appends < 0:
        raise WeakeningHysteresisError('max_forced_weakening_shift_unique_appends must be non-negative')

    base = decide_saved_state_resolution(
        current_dwell_unique_appends=current_dwell_unique_appends,
        required_gain_share_floor=required_gain_share_floor,
        max_hard_cap_budget_inclusive=max_hard_cap_budget_inclusive,
        minimum_anchor_slack_unique_appends=minimum_anchor_slack_unique_appends,
        minimum_band_width_unique_appends=minimum_band_width_unique_appends,
        master_calendar_pre_registered=master_calendar_pre_registered,
        max_pre_amortization_checkpoint_budget_inclusive=max_pre_amortization_checkpoint_budget_inclusive,
    )
    state = classify_saved_state(current_dwell_unique_appends)

    route_shift = 0 if base['route_plan'] is None else base['route_plan']['total_absolute_dwell_shift_unique_appends']
    result: dict[str, Any] = {
        'tool': str(Path(__file__).resolve()),
        'overlay_policy': 'keep strengthening mandatory but allow weakening deferral when the current stronger tier already satisfies the request and the one-shot weakening shift exceeds the declared threshold',
        'max_forced_weakening_shift_unique_appends': max_forced_weakening_shift_unique_appends,
        'base_resolver_decision': base,
        'weakening_shift_unique_appends': route_shift if base['action_family'] == 'weaken' else None,
    }

    if base['action_family'] != 'weaken':
        result.update(
            {
                'threshold_triggered': False,
                'status': base['status'],
                'action_family': base['action_family'],
                'selected_steady_tier': base['selected_steady_tier'],
                'selected_anchor_unique_appends': base['selected_anchor_unique_appends'],
                'route_plan': base['route_plan'],
                'deferred_weaken': False,
                'avoided_one_shot_shift_unique_appends': 0,
                'forgone_steady_state_savings_vs_current_band': None,
                'action_reason': 'weakening hysteresis does not modify holds, stabilizations, strengthenings, or infeasible requests',
            }
        )
        return result

    if base['selected_steady_tier'] == state['current_tier']:
        raise WeakeningHysteresisError('base weakening decision unexpectedly selected the current tier')

    if route_shift <= max_forced_weakening_shift_unique_appends:
        result.update(
            {
                'threshold_triggered': False,
                'status': base['status'],
                'action_family': base['action_family'],
                'selected_steady_tier': base['selected_steady_tier'],
                'selected_anchor_unique_appends': base['selected_anchor_unique_appends'],
                'route_plan': base['route_plan'],
                'deferred_weaken': False,
                'avoided_one_shot_shift_unique_appends': 0,
                'forgone_steady_state_savings_vs_current_band': None,
                'action_reason': 'the cheapest feasible weakening is within the declared one-shot shift threshold, so follow the base resolver',
            }
        )
        return result

    deferred_route = None if state['is_canonical_anchor'] else plan_saved_state_route(current_dwell_unique_appends, state['current_tier'])
    if state['is_canonical_anchor']:
        status = 'defer_weakening_keep_current_anchor'
        action_family = 'hold'
        action_reason = 'the current stronger anchor already satisfies the request, and immediate weakening exceeds the allowed one-shot shift threshold'
    else:
        status = 'defer_weakening_stabilize_current_stronger_band'
        action_family = 'stabilize'
        action_reason = 'the current stronger band already satisfies the request, so defer the expensive weakening and first stabilize the transient boundary to its own canonical anchor'

    deltas = base['selected_minus_current_band_deltas']
    result.update(
        {
            'threshold_triggered': True,
            'status': status,
            'action_family': action_family,
            'selected_steady_tier': state['current_tier'],
            'selected_anchor_unique_appends': state['canonical_anchor_unique_appends'],
            'route_plan': deferred_route,
            'deferred_weaken': True,
            'avoided_one_shot_shift_unique_appends': route_shift,
            'forgone_steady_state_savings_vs_current_band': {
                'exact_hard_cap_units': abs(deltas['exact_hard_cap_change_selected_minus_current_band']),
                'mode_specific_checkpoint_units': abs(deltas['mode_specific_checkpoint_change_selected_minus_current_band']),
                'minimum_anchor_slack_units': abs(deltas['minimum_anchor_slack_change_selected_minus_current_band']),
                'exact_dwell_band_width_units': abs(deltas['exact_dwell_band_width_change_selected_minus_current_band']),
            },
            'action_reason': action_reason,
        }
    )
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Optional weakening-hysteresis overlay for exact-uncertainty saved-state control.')
    parser.add_argument('--current-dwell-unique-appends', required=True, type=int, choices=saved_states())
    parser.add_argument('--required-gain-share-floor', required=True)
    parser.add_argument('--max-hard-cap-budget-inclusive', required=True, type=int)
    parser.add_argument('--minimum-anchor-slack-unique-appends', type=int, default=0)
    parser.add_argument('--minimum-band-width-unique-appends', type=int, default=1)
    parser.add_argument('--master-calendar-pre-registered', action='store_true')
    parser.add_argument('--max-pre-amortization-checkpoint-budget-inclusive', type=int)
    parser.add_argument('--max-forced-weakening-shift-unique-appends', type=int, default=23)
    return parser


def main() -> None:
    args = _parser().parse_args()
    print(
        json.dumps(
            decide_saved_state_with_weakening_hysteresis(
                current_dwell_unique_appends=args.current_dwell_unique_appends,
                required_gain_share_floor=args.required_gain_share_floor,
                max_hard_cap_budget_inclusive=args.max_hard_cap_budget_inclusive,
                minimum_anchor_slack_unique_appends=args.minimum_anchor_slack_unique_appends,
                minimum_band_width_unique_appends=args.minimum_band_width_unique_appends,
                master_calendar_pre_registered=args.master_calendar_pre_registered,
                max_pre_amortization_checkpoint_budget_inclusive=args.max_pre_amortization_checkpoint_budget_inclusive,
                max_forced_weakening_shift_unique_appends=args.max_forced_weakening_shift_unique_appends,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == '__main__':
    main()
