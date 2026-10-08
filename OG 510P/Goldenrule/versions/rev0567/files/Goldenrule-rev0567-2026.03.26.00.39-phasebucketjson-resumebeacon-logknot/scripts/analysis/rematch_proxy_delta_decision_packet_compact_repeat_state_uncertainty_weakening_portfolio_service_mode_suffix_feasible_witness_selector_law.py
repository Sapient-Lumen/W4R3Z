#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law import (
    build_state_code_to_row,
    select_service_mode_suffix_counter,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law import (
    build_family_examples,
    build_realized_bounded_window_intervals,
    select_constraint_family_intersection,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law import (
    build_source_rank_to_state_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law import (
    source_rank,
)


class WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_rows_by_code() -> dict[str, dict[str, Any]]:
    return build_state_code_to_row()


@lru_cache(maxsize=1)
def build_rank_to_code() -> dict[int, str]:
    return build_source_rank_to_state_code()


@lru_cache(maxsize=1)
def build_code_to_rank() -> dict[str, int]:
    return {state_code: source_rank(state_code) for state_code in build_rows_by_code()}


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def _select_rank(lower_rank: int, upper_rank: int, policy: str, preferred_state_code: str | None) -> tuple[int, dict[str, Any]]:
    if policy == 'earliest':
        return lower_rank, {'policy': 'earliest'}
    if policy == 'latest':
        return upper_rank, {'policy': 'latest'}
    if policy == 'lower_median':
        return (lower_rank + upper_rank) // 2, {'policy': 'lower_median'}
    if policy == 'upper_median':
        return (lower_rank + upper_rank + 1) // 2, {'policy': 'upper_median'}
    if policy == 'nearest_preferred':
        if preferred_state_code is None:
            raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('nearest_preferred policy requires preferred_state_code')
        preferred_rank = build_code_to_rank()[preferred_state_code]
        selected_rank = _clamp(preferred_rank, lower_rank, upper_rank)
        return selected_rank, {
            'policy': 'nearest_preferred',
            'preferred_state_code': preferred_state_code,
            'preferred_source_rank': preferred_rank,
            'projection_distance_in_rank_units': abs(preferred_rank - selected_rank),
        }
    raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError(f'unknown witness selection policy: {policy}')


def select_feasible_witness(
    constraints: list[dict[str, Any]],
    *,
    policy: str = 'nearest_preferred',
    preferred_state_code: str | None = None,
) -> dict[str, Any]:
    family = select_constraint_family_intersection(constraints)
    result: dict[str, Any] = {
        'policy': policy,
        'preferred_state_code': preferred_state_code,
        'family': family,
    }
    if not family['feasible']:
        result['selection_status'] = 'infeasible'
        result['selected_state_code'] = None
        result['selected_source_rank'] = None
        result['selected_signature'] = None
        result['selection_certificate'] = {'blocker_certificate': family['blocker_certificate']}
        return result

    selected_rank, certificate = _select_rank(
        family['lower_rank_bound'],
        family['upper_rank_bound'],
        policy,
        preferred_state_code,
    )
    selected_state_code = build_rank_to_code()[selected_rank]
    result['selection_status'] = 'selected'
    result['selected_state_code'] = selected_state_code
    result['selected_source_rank'] = selected_rank
    result['selected_signature'] = build_rows_by_code()[selected_state_code]['current_signature']
    result['selection_certificate'] = certificate
    return result


@lru_cache(maxsize=1)
def build_witness_selector_examples() -> list[dict[str, Any]]:
    feasible_family = [
        {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
        {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
    ]
    singleton_family = [
        {'constraint_label': 'share_0_02', 'state_code': select_service_mode_suffix_counter(0.02)['state_code'], 'minimum_service_share': 0.02, 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
        {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
    ]
    infeasible_family = [
        {'constraint_label': 'share_0_40', 'state_code': select_service_mode_suffix_counter(0.40)['state_code'], 'minimum_service_share': 0.40, 'max_forward_steps': 2, 'max_backward_steps': 1},
        {'constraint_label': 'share_0_0074', 'state_code': select_service_mode_suffix_counter(0.0074)['state_code'], 'minimum_service_share': 0.0074, 'max_forward_steps': 1, 'max_backward_steps': 3},
        {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
    ]
    return [
        select_feasible_witness(feasible_family, policy='earliest'),
        select_feasible_witness(feasible_family, policy='latest'),
        select_feasible_witness(feasible_family, policy='nearest_preferred', preferred_state_code='S10'),
        select_feasible_witness(feasible_family, policy='nearest_preferred', preferred_state_code='T0'),
        select_feasible_witness(singleton_family, policy='nearest_preferred', preferred_state_code='E1'),
        select_feasible_witness(infeasible_family, policy='nearest_preferred', preferred_state_code='S8'),
    ]


@lru_cache(maxsize=1)
def build_witness_selector_validation_summary() -> dict[str, Any]:
    realized = build_realized_bounded_window_intervals()
    all_codes = list(build_code_to_rank())
    nearest_projection_validation_count = 0
    lower_median_validation_count = 0
    upper_median_validation_count = 0
    earliest_latest_validation_count = 0

    for row in realized:
        interval_ranks = list(range(row['lower_rank'], row['upper_rank'] + 1))
        earliest = select_feasible_witness([
            {
                'constraint_label': row['interval_key'],
                'state_code': row['first_realizer']['state_code'],
                'max_forward_steps': row['first_realizer']['max_forward_steps'],
                'max_backward_steps': row['first_realizer']['max_backward_steps'],
            }
        ], policy='earliest')
        latest = select_feasible_witness([
            {
                'constraint_label': row['interval_key'],
                'state_code': row['first_realizer']['state_code'],
                'max_forward_steps': row['first_realizer']['max_forward_steps'],
                'max_backward_steps': row['first_realizer']['max_backward_steps'],
            }
        ], policy='latest')
        earliest_latest_validation_count += 1
        if earliest['selected_source_rank'] != row['lower_rank']:
            raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('earliest selection mismatch')
        if latest['selected_source_rank'] != row['upper_rank']:
            raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('latest selection mismatch')

        lower_median = select_feasible_witness([
            {
                'constraint_label': row['interval_key'],
                'state_code': row['first_realizer']['state_code'],
                'max_forward_steps': row['first_realizer']['max_forward_steps'],
                'max_backward_steps': row['first_realizer']['max_backward_steps'],
            }
        ], policy='lower_median')
        upper_median = select_feasible_witness([
            {
                'constraint_label': row['interval_key'],
                'state_code': row['first_realizer']['state_code'],
                'max_forward_steps': row['first_realizer']['max_forward_steps'],
                'max_backward_steps': row['first_realizer']['max_backward_steps'],
            }
        ], policy='upper_median')
        lower_median_validation_count += 1
        upper_median_validation_count += 1
        if lower_median['selected_source_rank'] != (row['lower_rank'] + row['upper_rank']) // 2:
            raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('lower median selection mismatch')
        if upper_median['selected_source_rank'] != (row['lower_rank'] + row['upper_rank'] + 1) // 2:
            raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('upper median selection mismatch')

        for preferred_state_code in all_codes:
            preferred_rank = build_code_to_rank()[preferred_state_code]
            brute_force_rank = min(interval_ranks, key=lambda rank: (abs(rank - preferred_rank), rank))
            selection = select_feasible_witness([
                {
                    'constraint_label': row['interval_key'],
                    'state_code': row['first_realizer']['state_code'],
                    'max_forward_steps': row['first_realizer']['max_forward_steps'],
                    'max_backward_steps': row['first_realizer']['max_backward_steps'],
                }
            ], policy='nearest_preferred', preferred_state_code=preferred_state_code)
            nearest_projection_validation_count += 1
            if selection['selected_source_rank'] != brute_force_rank:
                raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('nearest projection mismatch')

    infeasible_example = build_family_examples()[2]
    infeasible_selection = select_feasible_witness(
        [
            {
                'constraint_label': row['constraint_label'],
                'state_code': row['state_code'],
                'max_forward_steps': row['max_forward_steps'],
                'max_backward_steps': row['max_backward_steps'],
                **({'minimum_service_share': row['minimum_service_share']} if 'minimum_service_share' in row else {}),
            }
            for row in infeasible_example['constraints']
        ],
        policy='nearest_preferred',
        preferred_state_code='S8',
    )
    if infeasible_selection['selection_status'] != 'infeasible':
        raise WeakeningPortfolioServiceModeSuffixFeasibleWitnessSelectorLawError('infeasible selection should stay infeasible')

    return {
        'realized_interval_count': len(realized),
        'nearest_projection_validation_count': nearest_projection_validation_count,
        'earliest_latest_validation_count': earliest_latest_validation_count,
        'lower_median_validation_count': lower_median_validation_count,
        'upper_median_validation_count': upper_median_validation_count,
        'all_feasible_nearest_witnesses_match_interval_clamp': True,
        'infeasible_selection_stays_blocked': True,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    return {
        'validation_summary': build_witness_selector_validation_summary(),
        'selection_examples': build_witness_selector_examples(),
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_feasible_witness_selector_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Collapse feasible positive-service local weakening family selection into interval clamp arithmetic so '
            'future inheritors can move from merged bounded requirements to a concrete witness code without replaying '
            'the local chain.'
        ),
        'headline_findings': build_headline_findings(),
        'decision_rules': [
            'First merge bounded local weakening requirements with the feasibility-intersection law and keep only the overlap interval `[lower_rank_bound, upper_rank_bound]` when the family is feasible.',
            'Pick the earliest feasible witness by choosing `lower_rank_bound`, the latest by choosing `upper_rank_bound`, and the nearest feasible witness to any preferred local code by clamping its source rank into that same interval.',
            'Treat lower and upper medians as the midpoint witnesses for even or odd overlap intervals; no extra geometry beyond closed interval arithmetic is present in the current positive-service local chain.',
            'Carry the old blocker certificate forward unchanged when the family is infeasible: witness selection adds no new failure mode beyond interval disjointness.',
        ],
        'selection_examples': build_witness_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasible_witness_selector_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_feasible_witness_selector_snapshot(), indent=2, sort_keys=True))
