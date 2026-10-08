#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_anchor_routes import (
    ANCHOR_DWELLS,
    plan_anchor_route,
    tiers as anchor_tiers,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_oracle import (
    MASTER_CALENDAR_CHECKPOINTS,
    TIERS,
    classify_request,
)

ROOT = Path(__file__).resolve().parents[2]
CHEAP_TO_EXPENSIVE_TIERS = ['lower_guarantee', 'near_optimal', 'near_exact']
TIER_INFO = {row['tier']: row for row in TIERS}


class CanonicalControlError(ValueError):
    pass


def cheapest_feasible_tier(oracle_result: dict[str, Any]) -> str | None:
    feasible = {
        row['tier']
        for row in oracle_result['tier_evaluations']
        if row['feasible']
    }
    for tier in CHEAP_TO_EXPENSIVE_TIERS:
        if tier in feasible:
            return tier
    return None


def _delta_summary(current_tier: str, selected_tier: str) -> dict[str, Any]:
    current = TIER_INFO[current_tier]
    selected = TIER_INFO[selected_tier]
    return {
        'exact_hard_cap_change_selected_minus_current': selected['exact_hard_cap'] - current['exact_hard_cap'],
        'mode_specific_checkpoint_change_selected_minus_current': selected['mode_specific_checkpoint_count'] - current['mode_specific_checkpoint_count'],
        'post_amortized_checkpoint_change_selected_minus_current': 0,
        'minimum_anchor_slack_change_selected_minus_current': selected['minimum_anchor_slack_unique_appends'] - current['minimum_anchor_slack_unique_appends'],
        'exact_dwell_band_width_change_selected_minus_current': selected['exact_dwell_band_width_unique_appends'] - current['exact_dwell_band_width_unique_appends'],
        'anchor_shift_selected_minus_current': selected['canonical_anchor_minimum_dwell_unique_appends'] - current['canonical_anchor_minimum_dwell_unique_appends'],
    }


def decide_canonical_anchor_control(
    *,
    current_tier: str,
    required_gain_share_floor: str | float,
    max_hard_cap_budget_inclusive: int,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = None,
) -> dict[str, Any]:
    if current_tier not in TIER_INFO:
        raise CanonicalControlError(f'unknown current tier: {current_tier}')

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
    current = TIER_INFO[current_tier]

    result: dict[str, Any] = {
        'tool': str(Path(__file__).resolve()),
        'tier_selection_policy': 'cheapest_feasible_exact_tier_for_canonical_steady_state',
        'current_tier': current_tier,
        'current_anchor_unique_appends': current['canonical_anchor_minimum_dwell_unique_appends'],
        'request': {
            'required_gain_share_floor': oracle_result['input']['required_gain_share_floor'],
            'max_hard_cap_budget_inclusive': max_hard_cap_budget_inclusive,
            'minimum_anchor_slack_unique_appends': minimum_anchor_slack_unique_appends,
            'minimum_band_width_unique_appends': minimum_band_width_unique_appends,
            'master_calendar_pre_registered': master_calendar_pre_registered,
            'max_pre_amortization_checkpoint_budget_inclusive': max_pre_amortization_checkpoint_budget_inclusive,
        },
        'checkpoint_mode': 'post_amortized_master_calendar' if master_calendar_pre_registered else 'mode_specific',
        'current_tier_metrics': {
            'actual_certified_gain_share_floor_of_full_dynamic_savings': float(current['actual_floor']),
            'rounded_label_minimum_gain_share_of_full_dynamic_savings': float(current['rounded_label']),
            'exact_hard_cap': current['exact_hard_cap'],
            'mode_specific_checkpoint_count': current['mode_specific_checkpoint_count'],
            'post_amortized_checkpoint_count': MASTER_CALENDAR_CHECKPOINTS,
            'minimum_anchor_slack_unique_appends': current['minimum_anchor_slack_unique_appends'],
            'exact_dwell_band_width_unique_appends': current['exact_dwell_band_width_unique_appends'],
            'canonical_anchor_minimum_dwell_unique_appends': current['canonical_anchor_minimum_dwell_unique_appends'],
        },
        'current_anchor_already_satisfies_request': any(
            row['tier'] == current_tier and row['feasible'] for row in oracle_result['tier_evaluations']
        ),
        'oracle_status': oracle_result['status'],
        'blocking_summary': oracle_result['blocking_summary'],
        'recommended_repair_family': oracle_result['recommended_repair_family'],
        'floor_conditioned_live_support_components': oracle_result['floor_conditioned_live_support_components'],
        'eligible_tiers_by_floor': oracle_result['eligible_tiers_by_floor'],
        'feasible_tiers_sorted_cheap_to_expensive': [
            tier for tier in CHEAP_TO_EXPENSIVE_TIERS
            if any(row['tier'] == tier and row['feasible'] for row in oracle_result['tier_evaluations'])
        ],
        'tier_evaluations': oracle_result['tier_evaluations'],
        'selected_steady_tier': selected_tier,
    }

    if selected_tier is None:
        result.update(
            {
                'status': 'no_canonical_exact_tier',
                'action_family': 'infeasible',
                'selected_anchor_unique_appends': None,
                'route_plan': None,
                'selected_tier_metrics': None,
                'selected_minus_current_deltas': None,
                'action_reason': 'no exact tier simultaneously satisfies the declared floor, budget, slack, and width constraints',
            }
        )
        return result

    selected = TIER_INFO[selected_tier]
    delta_summary = _delta_summary(current_tier, selected_tier)
    route_plan = None if selected_tier == current_tier else plan_anchor_route(current_tier, selected_tier)

    if selected_tier == current_tier:
        status = 'hold_current_anchor'
        action_family = 'hold'
        action_reason = 'current anchor already sits at the cheapest feasible exact tier for the declared steady-state request'
    elif selected['exact_hard_cap'] < current['exact_hard_cap']:
        status = 'retune_to_new_anchor'
        action_family = 'weaken'
        action_reason = 'current anchor over-provisions the declared request, so the cheapest feasible steady-state tier releases avoidable cap/checkpoint burden'
    else:
        status = 'retune_to_new_anchor'
        action_family = 'strengthen'
        action_reason = 'current anchor is too weak for the declared request, so the controller strengthens to the cheapest exact tier that still satisfies the request'

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
            'selected_minus_current_deltas': delta_summary,
            'route_plan': route_plan,
            'action_reason': action_reason,
        }
    )
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Canonical exact-uncertainty steady-state control law.')
    parser.add_argument('--current-tier', required=True, choices=anchor_tiers())
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
            decide_canonical_anchor_control(
                current_tier=args.current_tier,
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
