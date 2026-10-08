#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path
from functools import lru_cache
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver import (
    classify_saved_state,
    saved_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector import (
    BUDGET_MAX,
    BUDGET_MIN,
    select_weakening_regime_by_recovered_case_budget,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis import (
    decide_saved_state_with_weakening_hysteresis,
)

DEFAULT_CURRENT_STATES = saved_states()
DEFAULT_FLOORS = ['0.84', '0.95', '0.99']
ACTION_FAMILIES = ['hold', 'stabilize', 'weaken', 'strengthen', 'infeasible']


class WeakeningBudgetLiveActionSurfaceError(RuntimeError):
    pass



@lru_cache(maxsize=None)
def _budget_selector(budget: int) -> dict[str, Any]:
    return select_weakening_regime_by_recovered_case_budget(budget)


def _decision_for_budget(current_state: int, floor: str, budget: int) -> dict[str, Any]:
    selector = _budget_selector(budget)
    return decide_saved_state_with_weakening_hysteresis(
        current_dwell_unique_appends=current_state,
        required_gain_share_floor=floor,
        max_hard_cap_budget_inclusive=11,
        minimum_anchor_slack_unique_appends=0,
        minimum_band_width_unique_appends=1,
        max_pre_amortization_checkpoint_budget_inclusive=14,
        max_forced_weakening_shift_unique_appends=selector['selected_threshold_unique_appends'],
    )



def _decision_signature(decision: dict[str, Any]) -> tuple[Any, ...]:
    route = None if decision['route_plan'] is None else tuple(decision['route_plan']['route_unique_appends'])
    return (
        decision['action_family'],
        decision['status'],
        decision['selected_steady_tier'],
        decision['selected_anchor_unique_appends'],
        route,
    )



def _live_case_label(current_state: int, floor: str, decision: dict[str, Any]) -> str:
    state = classify_saved_state(current_state)
    route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
    return f"{state['state_label']} @ floor {floor} -> {decision['selected_steady_tier']} via {route}"



@lru_cache(maxsize=1)
def build_budget_action_surface() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for budget in range(BUDGET_MIN, BUDGET_MAX + 1):
        selector = _budget_selector(budget)
        decisions: list[dict[str, Any]] = []
        action_counts = {action: 0 for action in ACTION_FAMILIES}
        released_live_weakenings: list[dict[str, Any]] = []
        for current_state in DEFAULT_CURRENT_STATES:
            for floor in DEFAULT_FLOORS:
                decision = _decision_for_budget(current_state, floor, budget)
                action_counts[decision['action_family']] = action_counts.get(decision['action_family'], 0) + 1
                state = classify_saved_state(current_state)
                route = None if decision['route_plan'] is None else decision['route_plan']['route_unique_appends']
                case = {
                    'current_state_unique_appends': current_state,
                    'current_state_label': state['state_label'],
                    'required_gain_share_floor': floor,
                    'action_family': decision['action_family'],
                    'status': decision['status'],
                    'selected_steady_tier': decision['selected_steady_tier'],
                    'selected_anchor_unique_appends': decision['selected_anchor_unique_appends'],
                    'route_unique_appends': route,
                }
                decisions.append(case)
                if decision['action_family'] == 'weaken':
                    released_live_weakenings.append(
                        {
                            **case,
                            'live_case_label': _live_case_label(current_state, floor, decision),
                        }
                    )
        rows.append(
            {
                'budget': budget,
                'selected_threshold_unique_appends': selector['selected_threshold_unique_appends'],
                'selected_threshold_band_label': selector['selected_threshold_band_label'],
                'selected_regime_label': selector['selected_regime_label'],
                'action_counts': action_counts,
                'released_live_weakening_count': len(released_live_weakenings),
                'released_live_weakenings': released_live_weakenings,
                'live_matrix': decisions,
            }
        )
    return rows



@lru_cache(maxsize=1)
def build_marginal_live_flips() -> list[dict[str, Any]]:
    surface = build_budget_action_surface()
    flips: list[dict[str, Any]] = []
    for prev_row, next_row in zip(surface, surface[1:]):
        previous_cases = {
            (case['current_state_unique_appends'], case['required_gain_share_floor']): case
            for case in prev_row['live_matrix']
        }
        next_cases = {
            (case['current_state_unique_appends'], case['required_gain_share_floor']): case
            for case in next_row['live_matrix']
        }
        changed: list[dict[str, Any]] = []
        for key, prev_case in previous_cases.items():
            next_case = next_cases[key]
            prev_signature = (
                prev_case['action_family'],
                prev_case['status'],
                prev_case['selected_steady_tier'],
                prev_case['selected_anchor_unique_appends'],
                tuple(prev_case['route_unique_appends']) if prev_case['route_unique_appends'] is not None else None,
            )
            next_signature = (
                next_case['action_family'],
                next_case['status'],
                next_case['selected_steady_tier'],
                next_case['selected_anchor_unique_appends'],
                tuple(next_case['route_unique_appends']) if next_case['route_unique_appends'] is not None else None,
            )
            if prev_signature != next_signature:
                state = classify_saved_state(prev_case['current_state_unique_appends'])
                changed.append(
                    {
                        'state_transition_budget_step': next_row['budget'],
                        'current_state_unique_appends': prev_case['current_state_unique_appends'],
                        'current_state_label': state['state_label'],
                        'required_gain_share_floor': prev_case['required_gain_share_floor'],
                        'from_action_family': prev_case['action_family'],
                        'from_status': prev_case['status'],
                        'from_selected_steady_tier': prev_case['selected_steady_tier'],
                        'from_selected_anchor_unique_appends': prev_case['selected_anchor_unique_appends'],
                        'from_route_unique_appends': prev_case['route_unique_appends'],
                        'to_action_family': next_case['action_family'],
                        'to_status': next_case['status'],
                        'to_selected_steady_tier': next_case['selected_steady_tier'],
                        'to_selected_anchor_unique_appends': next_case['selected_anchor_unique_appends'],
                        'to_route_unique_appends': next_case['route_unique_appends'],
                        'activated_live_case_label': _live_case_label(
                            prev_case['current_state_unique_appends'],
                            prev_case['required_gain_share_floor'],
                            {
                                'selected_steady_tier': next_case['selected_steady_tier'],
                                'route_plan': None if next_case['route_unique_appends'] is None else {'route_unique_appends': next_case['route_unique_appends']},
                            },
                        ),
                    }
                )
        if len(changed) != 1:
            raise WeakeningBudgetLiveActionSurfaceError(
                f'expected exactly one live case to flip at budget {next_row["budget"]}, found {len(changed)}'
            )
        flips.extend(changed)
    return flips



def build_weakening_budget_live_action_surface_snapshot() -> dict[str, Any]:
    surface = build_budget_action_surface()
    flips = build_marginal_live_flips()

    weaken_counts = [row['released_live_weakening_count'] for row in surface]
    if weaken_counts != [0, 1, 2, 3, 4, 5]:
        raise WeakeningBudgetLiveActionSurfaceError(f'unexpected weaken counts by budget: {weaken_counts}')

    strengthen_counts = [row['action_counts']['strengthen'] for row in surface]
    if len(set(strengthen_counts)) != 1:
        raise WeakeningBudgetLiveActionSurfaceError(f'strengthen count drifted across budgets: {strengthen_counts}')

    return {
        'focus': 'Project the recovered-case budget menu onto the full saved-state live controller so inheritors can see exactly which concrete operating instruction changes at each budget step.',
        'headline_findings': {
            'live_matrix_case_count': len(DEFAULT_CURRENT_STATES) * len(DEFAULT_FLOORS),
            'released_live_weakening_count_by_budget': {
                str(row['budget']): row['released_live_weakening_count'] for row in surface
            },
            'constant_strengthening_count_across_budgets': strengthen_counts[0],
            'hold_count_by_budget': {str(row['budget']): row['action_counts']['hold'] for row in surface},
            'stabilize_count_by_budget': {str(row['budget']): row['action_counts']['stabilize'] for row in surface},
            'exactly_one_live_matrix_flip_per_budget_step': True,
            'flip_source_action_family_sequence': [row['from_action_family'] for row in flips],
            'flip_target_action_family_sequence': [row['to_action_family'] for row in flips],
        },
        'decision_rules': [
            'Treat the weakening budget as a live-action exposure budget over the default 18-case saved-state matrix, not just as a symbolic threshold level.',
            'Every extra budget unit activates exactly one additional live weakening case and leaves all strengthenings unchanged.',
            'Budget steps 1 and 4 release transient-boundary cases by converting stabilize -> weaken; steps 2, 3, and 5 release canonical-anchor cases by converting hold -> weaken.',
            'Because only one live instruction changes per budget step, future menu edits can be audited as named operational flips rather than fuzzy changes in permissiveness.',
            'When governance wants to know the operational effect of a relaxation, read the next budget step as the next concrete state/floor pair that will stop being sticky.',
        ],
        'budget_action_surface': [
            {
                key: value
                for key, value in row.items()
                if key != 'live_matrix'
            }
            for row in surface
        ],
        'marginal_live_flips': flips,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_live_action_surface.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_saved_state_resolver_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Audit how weakening budgets change the full saved-state live controller surface.')
    parser.add_argument('--pretty', action='store_true')
    return parser



def main() -> None:
    args = _parser().parse_args()
    report = build_weakening_budget_live_action_surface_snapshot()
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
