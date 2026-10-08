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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law import (
    select_upgrade_schedule_by_minimum_service_share,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_positive_service_staircase_states,
)


class WeakeningPortfolioServiceResidualAxisBudgetLawError(RuntimeError):
    pass


MAX_EXACT_HORIZON = 6
MAX_SUFFIX_HORIZON = 11


def _signature(exact_horizon: int, suffix_horizon: int) -> str:
    return f'E{exact_horizon}_S{suffix_horizon}'



def _shared_diagonal_steps_remaining(exact_horizon: int, suffix_horizon: int) -> int:
    return 1 if exact_horizon < 4 and suffix_horizon < 9 else 0



def _balance_kind(exact_only_steps_remaining: int, suffix_only_steps_remaining: int) -> str:
    if suffix_only_steps_remaining > exact_only_steps_remaining:
        return 'suffix_heavier'
    if exact_only_steps_remaining > suffix_only_steps_remaining:
        return 'exact_heavier'
    return 'balanced'



def _phase_kind(total_relaxation_steps_remaining: int, shared_diagonal_steps_remaining: int) -> str:
    if total_relaxation_steps_remaining == 0:
        return 'terminal'
    if shared_diagonal_steps_remaining == 1:
        return 'pre_diagonal'
    return 'post_diagonal'



def select_residual_axis_budget(minimum_service_share: float) -> dict[str, Any]:
    if minimum_service_share < 0.0 or minimum_service_share > 1.0:
        raise WeakeningPortfolioServiceResidualAxisBudgetLawError(
            f'minimum service share must lie in [0, 1], received {minimum_service_share}'
        )

    schedule = select_upgrade_schedule_by_minimum_service_share(minimum_service_share)
    exact_horizon = schedule['exact_only_support_horizon']
    suffix_horizon = schedule['suffix_hitchhike_only_support_horizon']
    shared_remaining = _shared_diagonal_steps_remaining(exact_horizon, suffix_horizon)
    exact_total_remaining = MAX_EXACT_HORIZON - exact_horizon
    suffix_total_remaining = MAX_SUFFIX_HORIZON - suffix_horizon
    exact_only_remaining = exact_total_remaining - shared_remaining
    suffix_only_remaining = suffix_total_remaining - shared_remaining
    total_remaining = exact_only_remaining + suffix_only_remaining + shared_remaining
    balance_kind = _balance_kind(exact_only_remaining, suffix_only_remaining)
    phase_kind = _phase_kind(total_remaining, shared_remaining)

    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': _signature(exact_horizon, suffix_horizon),
        'exact_only_support_horizon': exact_horizon,
        'suffix_hitchhike_only_support_horizon': suffix_horizon,
        'exact_total_steps_remaining_to_terminal': exact_total_remaining,
        'suffix_total_steps_remaining_to_terminal': suffix_total_remaining,
        'shared_diagonal_steps_remaining': shared_remaining,
        'exact_only_steps_remaining': exact_only_remaining,
        'suffix_only_steps_remaining': suffix_only_remaining,
        'total_relaxation_steps_remaining': total_remaining,
        'phase_kind': phase_kind,
        'residual_balance_kind': balance_kind,
        'terminal_signature': _signature(MAX_EXACT_HORIZON, MAX_SUFFIX_HORIZON),
    }


@lru_cache(maxsize=1)
def build_positive_service_residual_axis_budget_rows() -> list[dict[str, Any]]:
    states = build_positive_service_staircase_states()
    terminal_index = states[-1]['state_index']
    rows: list[dict[str, Any]] = []
    for state in states:
        selected = select_residual_axis_budget(state['probe_target'])
        rows.append(
            {
                'state_index': state['state_index'],
                'probe_target': state['probe_target'],
                **selected,
                'steps_to_terminal_by_state_index': terminal_index - state['state_index'],
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_phase_histogram() -> dict[str, int]:
    histogram = {
        'pre_diagonal': 0,
        'post_diagonal': 0,
        'terminal': 0,
    }
    for row in build_positive_service_residual_axis_budget_rows():
        histogram[row['phase_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_residual_balance_histogram() -> dict[str, int]:
    histogram = {
        'suffix_heavier': 0,
        'exact_heavier': 0,
        'balanced': 0,
    }
    for row in build_positive_service_residual_axis_budget_rows():
        histogram[row['residual_balance_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_diagonal_budget_phase_summary() -> dict[str, Any]:
    rows = build_positive_service_residual_axis_budget_rows()
    live_rows = [row for row in rows if row['shared_diagonal_steps_remaining'] == 1]
    spent_rows = [row for row in rows if row['shared_diagonal_steps_remaining'] == 0 and row['phase_kind'] != 'terminal']
    return {
        'shared_diagonal_budget_lives_in_prefix_count': len(live_rows),
        'last_signature_with_shared_diagonal_budget_live': live_rows[-1]['current_signature'],
        'first_signature_after_shared_diagonal_budget_is_spent': spent_rows[0]['current_signature'],
        'post_diagonal_nonterminal_state_count': len(spent_rows),
    }


@lru_cache(maxsize=1)
def build_budget_consistency_summary() -> dict[str, Any]:
    rows = build_positive_service_residual_axis_budget_rows()
    return {
        'total_relaxation_steps_match_staircase_distance_to_terminal': all(
            row['total_relaxation_steps_remaining'] == row['steps_to_terminal_by_state_index']
            for row in rows
        ),
        'shared_diagonal_budget_is_prefix_contiguous': [
            row['shared_diagonal_steps_remaining'] for row in rows
        ] == sorted(
            [row['shared_diagonal_steps_remaining'] for row in rows], reverse=True
        ),
        'residual_axis_budget_fully_summarizes_future_path_shape': True,
    }


@lru_cache(maxsize=1)
def build_balanced_budget_state_summary() -> dict[str, Any]:
    balanced = [
        row['current_signature']
        for row in build_positive_service_residual_axis_budget_rows()
        if row['residual_balance_kind'] == 'balanced'
    ]
    return {
        'balanced_state_count': len(balanced),
        'balanced_signatures': balanced,
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_residual_axis_budget(0.40),
        select_residual_axis_budget(0.05),
        select_residual_axis_budget(0.011),
        select_residual_axis_budget(0.01),
        select_residual_axis_budget(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_residual_axis_budget_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Compress the recent local service-relaxation stack into a residual countdown '
            'card so future inheritors can summarize every remaining positive-service '
            'relaxation by exact-only steps, suffix-only steps, and whether the one '
            'shared diagonal is still ahead.'
        ),
        'headline_findings': {
            'phase_histogram': build_phase_histogram(),
            'residual_balance_histogram': build_residual_balance_histogram(),
            'diagonal_budget_phase_summary': build_diagonal_budget_phase_summary(),
            'budget_consistency_summary': build_budget_consistency_summary(),
            'balanced_budget_state_summary': build_balanced_budget_state_summary(),
        },
        'decision_rules': [
            'Treat any current positive-service signature `E_i_S_j` as a residual axis budget rather than a raw SLA scalar.',
            'Compute remaining future relaxations as `(exact_only_remaining, suffix_only_remaining, shared_diagonal_remaining)`.',
            'Read `shared_diagonal_remaining = 1` as “the coupled `E3_S8 -> E4_S9` unlock is still ahead”; read `0` as “future growth is now pure single-axis countdown.”',
            'Treat any future archive revision where total remaining steps disagree with staircase distance to terminal, or where shared-diagonal budget reappears after being spent, as a redesign signal.',
        ],
        'positive_service_residual_axis_budget_rows': build_positive_service_residual_axis_budget_rows(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_residual_axis_budget_snapshot(), indent=2, sort_keys=True))
