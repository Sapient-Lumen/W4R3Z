#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

LOWER_FLOOR = Decimal('0.870482')
NEAR_OPTIMAL_FLOOR = Decimal('0.980481')
NEAR_EXACT_FLOOR = Decimal('0.999822')
MASTER_CALENDAR_CHECKPOINTS = 17


class OracleInputError(ValueError):
    pass


TIERS = [
    {
        'tier': 'near_exact',
        'actual_floor': NEAR_EXACT_FLOOR,
        'rounded_label': Decimal('0.99'),
        'exact_hard_cap': 11,
        'mode_specific_checkpoint_count': 14,
        'minimum_anchor_slack_unique_appends': 0,
        'exact_dwell_band_width_unique_appends': 1,
        'exact_dwell_band_start_unique_appends': 2,
        'exact_dwell_band_end_unique_appends': 2,
        'canonical_anchor_minimum_dwell_unique_appends': 2,
    },
    {
        'tier': 'near_optimal',
        'actual_floor': NEAR_OPTIMAL_FLOOR,
        'rounded_label': Decimal('0.95'),
        'exact_hard_cap': 5,
        'mode_specific_checkpoint_count': 8,
        'minimum_anchor_slack_unique_appends': 5,
        'exact_dwell_band_width_unique_appends': 11,
        'exact_dwell_band_start_unique_appends': 8,
        'exact_dwell_band_end_unique_appends': 18,
        'canonical_anchor_minimum_dwell_unique_appends': 13,
    },
    {
        'tier': 'lower_guarantee',
        'actual_floor': LOWER_FLOOR,
        'rounded_label': Decimal('0.85'),
        'exact_hard_cap': 3,
        'mode_specific_checkpoint_count': 5,
        'minimum_anchor_slack_unique_appends': 6,
        'exact_dwell_band_width_unique_appends': 14,
        'exact_dwell_band_start_unique_appends': 19,
        'exact_dwell_band_end_unique_appends': 32,
        'canonical_anchor_minimum_dwell_unique_appends': 25,
    },
]


def _to_decimal(value: str | float | Decimal | None, name: str) -> Decimal:
    if value is None:
        raise OracleInputError(f'missing required value: {name}')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise OracleInputError(f'invalid decimal for {name}: {value}') from exc


def floor_conditioned_live_support(required_gain_share_floor: str | float | Decimal) -> list[tuple[int, int]]:
    floor = _to_decimal(required_gain_share_floor, 'required_gain_share_floor')
    if floor > NEAR_EXACT_FLOOR:
        return []
    if floor > NEAR_OPTIMAL_FLOOR:
        return [(2, 2)]
    if floor > LOWER_FLOOR:
        return [(2, 2), (8, 18)]
    return [(2, 2), (8, 32)]


def _contains(components: list[tuple[int, int]], dwell: int) -> bool:
    return any(start <= dwell <= end for start, end in components)


def _nearest_live_dwell(components: list[tuple[int, int]], dwell: int) -> int | None:
    if not components:
        return None
    candidates: list[int] = []
    for start, end in components:
        if dwell < start:
            candidates.append(start)
        elif dwell > end:
            candidates.append(end)
        else:
            candidates.append(dwell)
    best = min(candidates, key=lambda candidate: (abs(candidate - dwell), candidate))
    return best


def classify_request(
    *,
    required_gain_share_floor: str | float | Decimal,
    max_hard_cap_budget_inclusive: int,
    minimum_anchor_slack_unique_appends: int = 0,
    minimum_band_width_unique_appends: int = 1,
    target_dwell_unique_appends: int | None = None,
    master_calendar_pre_registered: bool = False,
    max_pre_amortization_checkpoint_budget_inclusive: int | None = None,
) -> dict[str, Any]:
    floor = _to_decimal(required_gain_share_floor, 'required_gain_share_floor')
    support = floor_conditioned_live_support(floor)
    checkpoint_mode = 'post_amortized_master_calendar' if master_calendar_pre_registered else 'mode_specific'

    eligible_tiers_by_floor = [tier for tier in TIERS if floor <= tier['actual_floor']]
    tier_evaluations: list[dict[str, Any]] = []
    feasible_tiers: list[dict[str, Any]] = []

    for tier in eligible_tiers_by_floor:
        passes_cap = max_hard_cap_budget_inclusive >= tier['exact_hard_cap']
        cap_shortfall = max(0, tier['exact_hard_cap'] - max_hard_cap_budget_inclusive)

        if master_calendar_pre_registered:
            passes_checkpoint = True
            checkpoint_shortfall = 0
            required_checkpoint_budget = MASTER_CALENDAR_CHECKPOINTS
        else:
            required_checkpoint_budget = tier['mode_specific_checkpoint_count']
            if max_pre_amortization_checkpoint_budget_inclusive is None:
                passes_checkpoint = True
                checkpoint_shortfall = 0
            else:
                passes_checkpoint = max_pre_amortization_checkpoint_budget_inclusive >= tier['mode_specific_checkpoint_count']
                checkpoint_shortfall = max(0, tier['mode_specific_checkpoint_count'] - max_pre_amortization_checkpoint_budget_inclusive)

        passes_slack = minimum_anchor_slack_unique_appends <= tier['minimum_anchor_slack_unique_appends']
        slack_shortfall = max(0, minimum_anchor_slack_unique_appends - tier['minimum_anchor_slack_unique_appends'])

        passes_band_width = minimum_band_width_unique_appends <= tier['exact_dwell_band_width_unique_appends']
        band_width_shortfall = max(0, minimum_band_width_unique_appends - tier['exact_dwell_band_width_unique_appends'])

        if target_dwell_unique_appends is None:
            passes_target_dwell = True
            target_dwell_repair = None
        else:
            passes_target_dwell = tier['exact_dwell_band_start_unique_appends'] <= target_dwell_unique_appends <= tier['exact_dwell_band_end_unique_appends']
            target_dwell_repair = None if passes_target_dwell else _nearest_live_dwell([(tier['exact_dwell_band_start_unique_appends'], tier['exact_dwell_band_end_unique_appends'])], target_dwell_unique_appends)

        feasible = passes_cap and passes_checkpoint and passes_slack and passes_band_width and passes_target_dwell
        if feasible:
            feasible_tiers.append(tier)

        tier_evaluations.append(
            {
                'tier': tier['tier'],
                'actual_certified_gain_share_floor_of_full_dynamic_savings': float(tier['actual_floor']),
                'rounded_label_minimum_gain_share_of_full_dynamic_savings': float(tier['rounded_label']),
                'exact_hard_cap': tier['exact_hard_cap'],
                'mode_specific_checkpoint_count': tier['mode_specific_checkpoint_count'],
                'post_amortized_checkpoint_count': MASTER_CALENDAR_CHECKPOINTS,
                'required_checkpoint_budget_in_this_mode': required_checkpoint_budget,
                'minimum_anchor_slack_unique_appends': tier['minimum_anchor_slack_unique_appends'],
                'exact_dwell_band_width_unique_appends': tier['exact_dwell_band_width_unique_appends'],
                'exact_dwell_band_start_unique_appends': tier['exact_dwell_band_start_unique_appends'],
                'exact_dwell_band_end_unique_appends': tier['exact_dwell_band_end_unique_appends'],
                'canonical_anchor_minimum_dwell_unique_appends': tier['canonical_anchor_minimum_dwell_unique_appends'],
                'passes_cap': passes_cap,
                'cap_shortfall': cap_shortfall,
                'passes_checkpoint_budget': passes_checkpoint,
                'checkpoint_shortfall': checkpoint_shortfall,
                'passes_minimum_anchor_slack': passes_slack,
                'anchor_slack_shortfall': slack_shortfall,
                'passes_minimum_band_width': passes_band_width,
                'band_width_shortfall': band_width_shortfall,
                'passes_target_dwell': passes_target_dwell,
                'target_dwell_shortfall_repair_within_tier': target_dwell_repair,
                'feasible': feasible,
            }
        )

    strongest_feasible_tier = feasible_tiers[0]['tier'] if feasible_tiers else None

    if strongest_feasible_tier is not None:
        status = 'exact_tier_available'
        blocking_summary = 'none'
        recommended_repair_family = None
    else:
        status = 'no_current_exact_tier'
        if floor > NEAR_EXACT_FLOOR:
            blocking_summary = 'required_floor_above_current_exact_frontier'
            recommended_repair_family = 'lower_required_floor_or_extend_frontier'
        elif target_dwell_unique_appends is not None and not _contains(support, target_dwell_unique_appends):
            if target_dwell_unique_appends < 2:
                blocking_summary = 'target_dwell_below_current_exact_menu'
            elif 3 <= target_dwell_unique_appends <= 7:
                blocking_summary = 'target_dwell_inside_internal_exact_gap'
            elif target_dwell_unique_appends > 32:
                blocking_summary = 'target_dwell_above_current_exact_menu'
            else:
                blocking_summary = 'target_dwell_pruned_by_required_floor'
            recommended_repair_family = 'retarget_dwell_to_nearest_live_support_or_weaken_floor'
        elif floor > NEAR_OPTIMAL_FLOOR and minimum_anchor_slack_unique_appends > 0:
            blocking_summary = 'high_floor_positive_slack_conflict'
            recommended_repair_family = 'lower_required_floor_to_0.980481_or_drop_slack_to_zero'
        elif floor > NEAR_OPTIMAL_FLOOR and minimum_band_width_unique_appends > 1:
            blocking_summary = 'high_floor_bandwidth_conflict'
            recommended_repair_family = 'lower_required_floor_to_0.980481_or_drop_band_width_to_one'
        elif eligible_tiers_by_floor and all(not row['passes_cap'] for row in tier_evaluations):
            blocking_summary = 'hard_cap_underflow'
            recommended_repair_family = 'raise_cap_budget_or_lower_required_floor'
        elif eligible_tiers_by_floor and all(not row['passes_checkpoint_budget'] for row in tier_evaluations):
            blocking_summary = 'checkpoint_underflow_before_amortization'
            recommended_repair_family = 'raise_checkpoint_budget_or_pre_register_master_calendar'
        elif eligible_tiers_by_floor and all(not row['passes_minimum_anchor_slack'] for row in tier_evaluations):
            blocking_summary = 'minimum_anchor_slack_too_high'
            recommended_repair_family = 'lower_slack_requirement_or_lower_required_floor'
        elif eligible_tiers_by_floor and all(not row['passes_minimum_band_width'] for row in tier_evaluations):
            blocking_summary = 'minimum_band_width_too_high'
            recommended_repair_family = 'lower_band_width_requirement_or_lower_required_floor'
        else:
            blocking_summary = 'mixed_constraint_failure'
            recommended_repair_family = 'inspect_tier_deficits_for_smallest_relaxation'

    return {
        'tool': str(Path(__file__).resolve()),
        'input': {
            'required_gain_share_floor': float(floor),
            'max_hard_cap_budget_inclusive': max_hard_cap_budget_inclusive,
            'minimum_anchor_slack_unique_appends': minimum_anchor_slack_unique_appends,
            'minimum_band_width_unique_appends': minimum_band_width_unique_appends,
            'target_dwell_unique_appends': target_dwell_unique_appends,
            'master_calendar_pre_registered': master_calendar_pre_registered,
            'max_pre_amortization_checkpoint_budget_inclusive': max_pre_amortization_checkpoint_budget_inclusive,
        },
        'checkpoint_mode': checkpoint_mode,
        'floor_conditioned_live_support_components': [
            {'start_unique_appends': start, 'end_unique_appends': end} for start, end in support
        ],
        'nearest_live_support_repair_for_target_dwell': None if target_dwell_unique_appends is None else _nearest_live_dwell(support, target_dwell_unique_appends),
        'eligible_tiers_by_floor': [tier['tier'] for tier in eligible_tiers_by_floor],
        'tier_evaluations': tier_evaluations,
        'strongest_feasible_tier': strongest_feasible_tier,
        'status': status,
        'blocking_summary': blocking_summary,
        'recommended_repair_family': recommended_repair_family,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Executable compact repeat-state uncertainty request oracle.')
    parser.add_argument('--required-floor', required=True)
    parser.add_argument('--max-hard-cap', required=True, type=int)
    parser.add_argument('--min-slack', default=0, type=int)
    parser.add_argument('--min-band-width', default=1, type=int)
    parser.add_argument('--target-dwell', type=int)
    parser.add_argument('--master-calendar-pre-registered', action='store_true')
    parser.add_argument('--max-pre-amortization-checkpoints', type=int)
    return parser


def main() -> None:
    args = _parser().parse_args()
    payload = classify_request(
        required_gain_share_floor=args.required_floor,
        max_hard_cap_budget_inclusive=args.max_hard_cap,
        minimum_anchor_slack_unique_appends=args.min_slack,
        minimum_band_width_unique_appends=args.min_band_width,
        target_dwell_unique_appends=args.target_dwell,
        master_calendar_pre_registered=args.master_calendar_pre_registered,
        max_pre_amortization_checkpoint_budget_inclusive=args.max_pre_amortization_checkpoints,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
