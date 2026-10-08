#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control import (
    CHEAP_TO_EXPENSIVE_TIERS,
    TIER_INFO,
    cheapest_feasible_tier,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle import (
    MASTER_CALENDAR_CHECKPOINTS,
    classify_request,
)

ROOT = Path(__file__).resolve().parents[2]

SAVED_STATES: dict[int, dict[str, Any]] = {
    2: {
        'state_label': 'precision_anchor',
        'state_kind': 'canonical_anchor',
        'current_tier': 'near_exact',
        'region_label': '{2}',
        'canonical_anchor_unique_appends': 2,
        'is_canonical_anchor': True,
    },
    8: {
        'state_label': 'neutral_entry_boundary',
        'state_kind': 'transient_boundary',
        'current_tier': 'near_optimal',
        'region_label': '[8, 18]',
        'canonical_anchor_unique_appends': 13,
        'is_canonical_anchor': False,
    },
    13: {
        'state_label': 'neutral_anchor',
        'state_kind': 'canonical_anchor',
        'current_tier': 'near_optimal',
        'region_label': '[8, 18]',
        'canonical_anchor_unique_appends': 13,
        'is_canonical_anchor': True,
    },
    18: {
        'state_label': 'neutral_exit_boundary',
        'state_kind': 'transient_boundary',
        'current_tier': 'near_optimal',
        'region_label': '[8, 18]',
        'canonical_anchor_unique_appends': 13,
        'is_canonical_anchor': False,
    },
    19: {
        'state_label': 'relaxed_entry_boundary',
        'state_kind': 'transient_boundary',
        'current_tier': 'lower_guarantee',
        'region_label': '[19, 32]',
        'canonical_anchor_unique_appends': 25,
        'is_canonical_anchor': False,
    },
    25: {
        'state_label': 'relaxed_anchor',
        'state_kind': 'canonical_anchor',
        'current_tier': 'lower_guarantee',
        'region_label': '[19, 32]',
        'canonical_anchor_unique_appends': 25,
        'is_canonical_anchor': True,
    },
}

TIER_STRENGTH_ORDER = {
    'lower_guarantee': 0,
    'near_optimal': 1,
    'near_exact': 2,
}

ROUTE_STEPS: dict[tuple[int, str], list[dict[str, Any]]] = {
    (2, 'near_exact'): [],
    (2, 'near_optimal'): [
        {
            'phase_label': 'boundary_widen_to_neutral_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 2,
            'to_dwell_unique_appends': 8,
            'why': 'Weakening from precision first lands on neutral entry boundary 8.',
        },
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 13,
            'why': 'Steady neutral-band operation recenters from 8 to canonical anchor 13.',
        },
    ],
    (2, 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_neutral_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 2,
            'to_dwell_unique_appends': 8,
            'why': 'Full relaxation from precision still starts at boundary 8.',
        },
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 19,
            'why': 'The next weaker support entry is relaxed-boundary dwell 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady relaxed-suffix operation recenters from 19 to canonical anchor 25.',
        },
    ],
    (8, 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 2,
            'why': 'Once the stronger floor requires precision, neutral entry boundary 8 collapses directly to dwell 2.',
        },
    ],
    (8, 'near_optimal'): [
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 13,
            'why': 'Boundary 8 is transient; steady neutral-band operation recenters to anchor 13.',
        },
    ],
    (8, 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 8,
            'to_dwell_unique_appends': 19,
            'why': 'Weakening below the neutral band next lands on relaxed entry boundary 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady relaxed-suffix operation recenters from 19 to anchor 25.',
        },
    ],
    (13, 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 13,
            'to_dwell_unique_appends': 2,
            'why': 'Strengthening beyond the middle cliff collapses directly to dwell 2.',
        },
    ],
    (13, 'near_optimal'): [],
    (13, 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 13,
            'to_dwell_unique_appends': 19,
            'why': 'Weakening from the neutral anchor first enters the relaxed suffix at boundary 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady relaxed-suffix operation recenters from 19 to anchor 25.',
        },
    ],
    (18, 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 2,
            'why': 'Once the stronger floor requires precision, neutral exit boundary 18 collapses directly to dwell 2.',
        },
    ],
    (18, 'near_optimal'): [
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 13,
            'why': 'Boundary 18 is transient; steady neutral-band operation recenters to anchor 13.',
        },
    ],
    (18, 'lower_guarantee'): [
        {
            'phase_label': 'boundary_widen_to_relaxed_entry',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 19,
            'why': 'Weakening below the neutral band next lands on relaxed entry boundary 19.',
        },
        {
            'phase_label': 'steady_recenter_to_lower_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Steady relaxed-suffix operation recenters from 19 to anchor 25.',
        },
    ],
    (19, 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 2,
            'why': 'High-floor strengthening from relaxed entry boundary 19 collapses directly to dwell 2.',
        },
    ],
    (19, 'near_optimal'): [
        {
            'phase_label': 'boundary_repair_to_neutral_exit',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 18,
            'why': 'Strengthening from the relaxed suffix first exits at neutral boundary 18.',
        },
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 13,
            'why': 'Steady neutral-band operation recenters from 18 to anchor 13.',
        },
    ],
    (19, 'lower_guarantee'): [
        {
            'phase_label': 'steady_recenter_to_lower_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 19,
            'to_dwell_unique_appends': 25,
            'why': 'Boundary 19 is transient; steady relaxed-suffix operation recenters to anchor 25.',
        },
    ],
    (25, 'near_exact'): [
        {
            'phase_label': 'direct_collapse_to_precision_anchor',
            'phase_type': 'boundary_and_anchor',
            'from_dwell_unique_appends': 25,
            'to_dwell_unique_appends': 2,
            'why': 'High-floor strengthening from the relaxed anchor bypasses the middle band and collapses to 2.',
        },
    ],
    (25, 'near_optimal'): [
        {
            'phase_label': 'boundary_repair_to_neutral_exit',
            'phase_type': 'boundary_repair',
            'from_dwell_unique_appends': 25,
            'to_dwell_unique_appends': 18,
            'why': 'Strengthening from the relaxed anchor first exits at neutral boundary 18.',
        },
        {
            'phase_label': 'steady_recenter_to_neutral_anchor',
            'phase_type': 'anchor_recentering',
            'from_dwell_unique_appends': 18,
            'to_dwell_unique_appends': 13,
            'why': 'Steady neutral-band operation recenters from 18 to anchor 13.',
        },
    ],
    (25, 'lower_guarantee'): [],
}


class SavedStateResolverError(ValueError):
    pass


def saved_states() -> list[int]:
    return list(SAVED_STATES)


def classify_saved_state(current_dwell_unique_appends: int) -> dict[str, Any]:
    if current_dwell_unique_appends not in SAVED_STATES:
        raise SavedStateResolverError(f'unknown saved control state: {current_dwell_unique_appends}')
    row = dict(SAVED_STATES[current_dwell_unique_appends])
    row['current_dwell_unique_appends'] = current_dwell_unique_appends
    row['steady_ready'] = row['is_canonical_anchor']
    return row


def _delta_summary(current_tier: str, selected_tier: str) -> dict[str, Any]:
    current = TIER_INFO[current_tier]
    selected = TIER_INFO[selected_tier]
    return {
        'exact_hard_cap_change_selected_minus_current_band': selected['exact_hard_cap'] - current['exact_hard_cap'],
        'mode_specific_checkpoint_change_selected_minus_current_band': selected['mode_specific_checkpoint_count'] - current['mode_specific_checkpoint_count'],
        'post_amortized_checkpoint_change_selected_minus_current_band': 0,
        'minimum_anchor_slack_change_selected_minus_current_band': selected['minimum_anchor_slack_unique_appends'] - current['minimum_anchor_slack_unique_appends'],
        'exact_dwell_band_width_change_selected_minus_current_band': selected['exact_dwell_band_width_unique_appends'] - current['exact_dwell_band_width_unique_appends'],
        'anchor_shift_selected_minus_current_band_anchor': selected['canonical_anchor_minimum_dwell_unique_appends'] - current['canonical_anchor_minimum_dwell_unique_appends'],
    }


def plan_saved_state_route(current_dwell_unique_appends: int, selected_tier: str) -> dict[str, Any] | None:
    state = classify_saved_state(current_dwell_unique_appends)
    if selected_tier not in TIER_INFO:
        raise SavedStateResolverError(f'unknown selected tier: {selected_tier}')

    raw_steps = ROUTE_STEPS[(current_dwell_unique_appends, selected_tier)]
    if not raw_steps:
        return None

    steps: list[dict[str, Any]] = []
    for raw_step in raw_steps:
        step = dict(raw_step)
        step['absolute_dwell_shift_unique_appends'] = abs(
            step['to_dwell_unique_appends'] - step['from_dwell_unique_appends']
        )
        steps.append(step)

    route = [current_dwell_unique_appends] + [step['to_dwell_unique_appends'] for step in steps]
    return {
        'tool': str(Path(__file__).resolve()),
        'start_state_label': state['state_label'],
        'start_state_kind': state['state_kind'],
        'start_current_tier': state['current_tier'],
        'selected_steady_tier': selected_tier,
        'route_unique_appends': route,
        'step_count': len(steps),
        'total_absolute_dwell_shift_unique_appends': sum(step['absolute_dwell_shift_unique_appends'] for step in steps),
        'touches_transient_boundaries_unique_appends': sorted({d for d in route if d in {8, 18, 19}}),
        'steps': steps,
    }


def decide_saved_state_resolution(
    *,
    current_dwell_unique_appends: int,
    required_gain_share_floor: str | float,
    max_hard_cap_budget_inclusive: int,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = None,
) -> dict[str, Any]:
    state = classify_saved_state(current_dwell_unique_appends)
    oracle_result = classify_request(
        required_gain_share_floor=required_gain_share_floor,
        max_hard_cap_budget_inclusive=max_hard_cap_budget_inclusive,
        minimum_anchor_slack_unique_appends=minimum_anchor_slack_unique_appends,
        minimum_band_width_unique_appends=minimum_band_width_unique_appends,
        target_dwell_unique_appends=None,
        master_calendar_pre_registered=master_calendar_pre_registered,
        max_pre_amortization_checkpoint_budget_inclusive=max_pre_amortization_checkpoint_budget_inclusive,
    )
    selected_tier = cheapest_feasible_tier(oracle_result)
    current_tier = state['current_tier']
    current_metrics = TIER_INFO[current_tier]

    result: dict[str, Any] = {
        'tool': str(Path(__file__).resolve()),
        'resolver_policy': 'choose_the_cheapest_feasible_exact_tier_then_resolve_from_the_current_saved_state_to_its_canonical_anchor',
        'current_state': state,
        'request': {
            'required_gain_share_floor': oracle_result['input']['required_gain_share_floor'],
            'max_hard_cap_budget_inclusive': max_hard_cap_budget_inclusive,
            'minimum_anchor_slack_unique_appends': minimum_anchor_slack_unique_appends,
            'minimum_band_width_unique_appends': minimum_band_width_unique_appends,
            'master_calendar_pre_registered': master_calendar_pre_registered,
            'max_pre_amortization_checkpoint_budget_inclusive': max_pre_amortization_checkpoint_budget_inclusive,
        },
        'checkpoint_mode': 'post_amortized_master_calendar' if master_calendar_pre_registered else 'mode_specific',
        'current_band_metrics': {
            'actual_certified_gain_share_floor_of_full_dynamic_savings': float(current_metrics['actual_floor']),
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': float(current_metrics['rounded_label']),
            'exact_hard_cap': current_metrics['exact_hard_cap'],
            'mode_specific_checkpoint_count': current_metrics['mode_specific_checkpoint_count'],
            'post_amortized_checkpoint_count': MASTER_CALENDAR_CHECKPOINTS,
            'minimum_anchor_slack_unique_appends': current_metrics['minimum_anchor_slack_unique_appends'],
            'exact_dwell_band_width_unique_appends': current_metrics['exact_dwell_band_width_unique_appends'],
            'canonical_anchor_minimum_dwell_unique_appends': current_metrics['canonical_anchor_minimum_dwell_unique_appends'],
        },
        'oracle_status': oracle_result['status'],
        'blocking_summary': oracle_result['blocking_summary'],
        'recommended_repair_family': oracle_result['recommended_repair_family'],
        'eligible_tiers_by_floor': oracle_result['eligible_tiers_by_floor'],
        'feasible_tiers_sorted_cheap_to_expensive': [
            tier for tier in CHEAP_TO_EXPENSIVE_TIERS
            if any(row['tier'] == tier and row['feasible'] for row in oracle_result['tier_evaluations'])
        ],
        'selected_steady_tier': selected_tier,
        'floor_conditioned_live_support_components': oracle_result['floor_conditioned_live_support_components'],
        'tier_evaluations': oracle_result['tier_evaluations'],
    }

    if selected_tier is None:
        result.update(
            {
                'status': 'no_saved_state_resolution',
                'action_family': 'infeasible',
                'selected_anchor_unique_appends': None,
                'route_plan': None,
                'selected_tier_metrics': None,
                'selected_minus_current_band_deltas': None,
                'action_reason': 'no exact tier simultaneously satisfies the declared floor, budget, slack, and width constraints',
            }
        )
        return result

    selected = TIER_INFO[selected_tier]
    delta_summary = _delta_summary(current_tier, selected_tier)
    route_plan = plan_saved_state_route(current_dwell_unique_appends, selected_tier)

    if selected_tier == current_tier:
        if state['is_canonical_anchor']:
            status = 'hold_current_anchor'
            action_family = 'hold'
            action_reason = 'current saved state is already the canonical anchor of the cheapest feasible exact tier'
        else:
            status = 'stabilize_current_band'
            action_family = 'stabilize'
            action_reason = 'current saved state is a transient boundary inside the selected tier, so only recentering to the canonical anchor is needed'
    elif TIER_STRENGTH_ORDER[selected_tier] < TIER_STRENGTH_ORDER[current_tier]:
        status = 'retune_to_new_anchor'
        action_family = 'weaken'
        action_reason = 'current saved state belongs to a stronger band than the cheapest feasible request-satisfying tier, so the resolver weakens and recenters'
    else:
        status = 'retune_to_new_anchor'
        action_family = 'strengthen'
        action_reason = 'current saved state belongs to a weaker band than the cheapest feasible request-satisfying tier, so the resolver strengthens and recenters'

    result.update(
        {
            'status': status,
            'action_family': action_family,
            'selected_anchor_unique_appends': selected['canonical_anchor_minimum_dwell_unique_appends'],
            'selected_tier_metrics': {
                'actual_certified_gain_share_floor_of_full_dynamic_savings': float(selected['actual_floor']),
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': float(selected['rounded_label']),
                'exact_hard_cap': selected['exact_hard_cap'],
                'mode_specific_checkpoint_count': selected['mode_specific_checkpoint_count'],
                'post_amortized_checkpoint_count': MASTER_CALENDAR_CHECKPOINTS,
                'minimum_anchor_slack_unique_appends': selected['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': selected['exact_dwell_band_width_unique_appends'],
                'canonical_anchor_minimum_dwell_unique_appends': selected['canonical_anchor_minimum_dwell_unique_appends'],
            },
            'selected_minus_current_band_deltas': delta_summary,
            'route_plan': route_plan,
            'action_reason': action_reason,
        }
    )
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Unified exact-uncertainty resolver over saved anchors and transient boundaries.')
    parser.add_argument('--current-dwell-unique-appends', required=True, type=int, choices=saved_states())
    parser.add_argument('--required-gain-share-floor', required=True)
    parser.add_argument('--max-hard-cap-budget-inclusive', required=True, type=int)
    parser.add_argument('--minimum-anchor-slack-unique-appends', type=int, default=0)
    parser.add_argument('--minimum-band-width-unique-appends', type=int, default=1)
    parser.add_argument('--master-calendar-pre-registered', action='store_true')
    parser.add_argument('--max-pre-amortization-checkpoint-budget-inclusive', type=int)
    return parser


def main() -> None:
    args = _parser().parse_args()
    print(
        json.dumps(
            decide_saved_state_resolution(
                current_dwell_unique_appends=args.current_dwell_unique_appends,
                required_gain_share_floor=args.required_gain_share_floor,
                max_hard_cap_budget_inclusive=args.max_hard_cap_budget_inclusive,
                minimum_anchor_slack_unique_appends=args.minimum_anchor_slack_unique_appends,
                minimum_band_width_unique_appends=args.minimum_band_width_unique_appends,
                master_calendar_pre_registered=args.master_calendar_pre_registered,
                max_pre_amortization_checkpoint_budget_inclusive=args.max_pre_amortization_checkpoint_budget_inclusive,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == '__main__':
    main()
