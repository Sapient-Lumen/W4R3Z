#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law import (
    build_state_code_chain,
    build_state_code_to_row,
    select_service_mode_suffix_counter,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law import (
    build_max_clock,
    build_source_rank_to_state_code,
    select_mode_suffix_clock_interval,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law import (
    source_rank,
)


class WeakeningPortfolioServiceModeSuffixFeasibilityIntersectionLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_state_rows_by_code() -> dict[str, dict[str, Any]]:
    return build_state_code_to_row()


@lru_cache(maxsize=1)
def build_all_closed_rank_intervals() -> list[dict[str, Any]]:
    rank_to_code = build_source_rank_to_state_code()
    intervals: list[dict[str, Any]] = []
    max_clock = build_max_clock()
    for lower_rank in range(0, max_clock + 1):
        for upper_rank in range(lower_rank, max_clock + 1):
            intervals.append(
                {
                    'interval_key': f'[{lower_rank},{upper_rank}]',
                    'lower_rank': lower_rank,
                    'upper_rank': upper_rank,
                    'cardinality': upper_rank - lower_rank + 1,
                    'state_codes': [rank_to_code[rank] for rank in range(lower_rank, upper_rank + 1)],
                }
            )
    return intervals


@lru_cache(maxsize=1)
def build_realized_bounded_window_intervals() -> list[dict[str, Any]]:
    realized: dict[tuple[int, int], dict[str, Any]] = {}
    rows_by_code = build_state_rows_by_code()
    for state_code in build_state_code_chain():
        for max_forward_steps in range(0, build_max_clock() + 1):
            for max_backward_steps in range(0, build_max_clock() + 1):
                window = select_mode_suffix_clock_interval(
                    state_code,
                    max_forward_steps=max_forward_steps,
                    max_backward_steps=max_backward_steps,
                )
                key = (window['lower_source_rank'], window['upper_source_rank'])
                if key not in realized:
                    realized[key] = {
                        'interval_key': f'[{key[0]},{key[1]}]',
                        'lower_rank': key[0],
                        'upper_rank': key[1],
                        'cardinality': window['interval_cardinality'],
                        'state_codes': window['interval_state_codes'],
                        'first_realizer': {
                            'state_code': state_code,
                            'current_signature': rows_by_code[state_code]['current_signature'],
                            'max_forward_steps': max_forward_steps,
                            'max_backward_steps': max_backward_steps,
                        },
                    }
    return [realized[key] for key in sorted(realized)]


def _normalize_constraint(constraint: dict[str, Any]) -> dict[str, Any]:
    state_code = constraint['state_code']
    max_forward_steps = int(constraint.get('max_forward_steps', 0))
    max_backward_steps = int(constraint.get('max_backward_steps', 0))
    if max_forward_steps < 0 or max_backward_steps < 0:
        raise WeakeningPortfolioServiceModeSuffixFeasibilityIntersectionLawError('constraint budgets must be nonnegative')
    row = build_state_rows_by_code()[state_code]
    window = select_mode_suffix_clock_interval(
        state_code,
        max_forward_steps=max_forward_steps,
        max_backward_steps=max_backward_steps,
    )
    normalized = {
        'constraint_label': constraint.get('constraint_label', f'{state_code}|b{max_backward_steps}|f{max_forward_steps}'),
        'state_code': state_code,
        'current_signature': row['current_signature'],
        'current_source_rank': source_rank(state_code),
        'max_forward_steps': max_forward_steps,
        'max_backward_steps': max_backward_steps,
        'lower_rank': window['lower_source_rank'],
        'upper_rank': window['upper_source_rank'],
        'interval_key': f"[{window['lower_source_rank']},{window['upper_source_rank']}]",
        'boundary_backward_code': window['boundary_backward_code'],
        'boundary_forward_code': window['boundary_forward_code'],
    }
    if 'minimum_service_share' in constraint:
        normalized['minimum_service_share'] = constraint['minimum_service_share']
    return normalized


@lru_cache(maxsize=None)
def select_constraint_family_intersection_from_json(encoded_constraints: str) -> dict[str, Any]:
    constraints = json.loads(encoded_constraints)
    normalized = [_normalize_constraint(constraint) for constraint in constraints]
    if not normalized:
        raise WeakeningPortfolioServiceModeSuffixFeasibilityIntersectionLawError('constraint family must be nonempty')

    lower_rank = max(constraint['lower_rank'] for constraint in normalized)
    upper_rank = min(constraint['upper_rank'] for constraint in normalized)
    feasible = lower_rank <= upper_rank
    rank_to_code = build_source_rank_to_state_code()
    witness_state_codes = [rank_to_code[rank] for rank in range(lower_rank, upper_rank + 1)] if feasible else []

    disjoint_pairs: list[dict[str, Any]] = []
    pairwise_overlap = True
    for left, right in itertools.combinations(normalized, 2):
        overlaps = not (left['upper_rank'] < right['lower_rank'] or right['upper_rank'] < left['lower_rank'])
        if not overlaps:
            pairwise_overlap = False
            disjoint_pairs.append(
                {
                    'left_constraint_label': left['constraint_label'],
                    'right_constraint_label': right['constraint_label'],
                    'left_interval_key': left['interval_key'],
                    'right_interval_key': right['interval_key'],
                }
            )

    blocker_certificate = None
    if not feasible:
        max_lower_constraint = max(normalized, key=lambda row: (row['lower_rank'], row['upper_rank'], row['constraint_label']))
        min_upper_constraint = min(normalized, key=lambda row: (row['upper_rank'], row['lower_rank'], row['constraint_label']))
        blocker_certificate = {
            'left_constraint_label': max_lower_constraint['constraint_label'],
            'right_constraint_label': min_upper_constraint['constraint_label'],
            'left_interval_key': max_lower_constraint['interval_key'],
            'right_interval_key': min_upper_constraint['interval_key'],
            'gap_size_in_rank_units': max_lower_constraint['lower_rank'] - min_upper_constraint['upper_rank'] - 1,
        }

    return {
        'constraints': normalized,
        'family_size': len(normalized),
        'lower_rank_bound': lower_rank,
        'upper_rank_bound': upper_rank,
        'feasible': feasible,
        'pairwise_overlap': pairwise_overlap,
        'pairwise_overlap_matches_global_feasibility': pairwise_overlap == feasible,
        'intersection_cardinality': len(witness_state_codes),
        'witness_state_codes': witness_state_codes,
        'blocker_certificate': blocker_certificate,
        'all_disjoint_pairs': disjoint_pairs,
    }


def select_constraint_family_intersection(constraints: list[dict[str, Any]]) -> dict[str, Any]:
    return select_constraint_family_intersection_from_json(json.dumps(constraints, sort_keys=True))


@lru_cache(maxsize=1)
def build_family_examples() -> list[dict[str, Any]]:
    return [
        select_constraint_family_intersection(
            [
                {'constraint_label': 'source_relax6', 'state_code': 'S10', 'max_forward_steps': 6, 'max_backward_steps': 0},
                {'constraint_label': 'middle_exact_band', 'state_code': 'E8', 'max_forward_steps': 2, 'max_backward_steps': 1},
                {'constraint_label': 'suffix_bridge', 'state_code': 'S7', 'max_forward_steps': 1, 'max_backward_steps': 1},
            ]
        ),
        select_constraint_family_intersection(
            [
                {'constraint_label': 'share_0_02', 'state_code': select_service_mode_suffix_counter(0.02)['state_code'], 'minimum_service_share': 0.02, 'max_forward_steps': 1, 'max_backward_steps': 1},
                {'constraint_label': 'tail_exact', 'state_code': 'E1', 'max_forward_steps': 1, 'max_backward_steps': 1},
                {'constraint_label': 'singleton_s2', 'state_code': 'S2', 'max_forward_steps': 0, 'max_backward_steps': 0},
            ]
        ),
        select_constraint_family_intersection(
            [
                {'constraint_label': 'share_0_40', 'state_code': select_service_mode_suffix_counter(0.40)['state_code'], 'minimum_service_share': 0.40, 'max_forward_steps': 2, 'max_backward_steps': 1},
                {'constraint_label': 'share_0_0074', 'state_code': select_service_mode_suffix_counter(0.0074)['state_code'], 'minimum_service_share': 0.0074, 'max_forward_steps': 1, 'max_backward_steps': 3},
                {'constraint_label': 'terminal_only', 'state_code': 'T0', 'max_forward_steps': 0, 'max_backward_steps': 1},
            ]
        ),
    ]


@lru_cache(maxsize=1)
def build_feasibility_intersection_validation_summary() -> dict[str, Any]:
    all_intervals = build_all_closed_rank_intervals()
    realized = build_realized_bounded_window_intervals()
    catalog_keys = {(row['lower_rank'], row['upper_rank']) for row in all_intervals}
    realized_keys = {(row['lower_rank'], row['upper_rank']) for row in realized}

    pair_validation_count = 0
    infeasible_pair_count = 0
    for left, right in itertools.combinations(realized, 2):
        pair_validation_count += 1
        family = select_constraint_family_intersection(
            [
                {
                    'constraint_label': left['interval_key'],
                    'state_code': left['first_realizer']['state_code'],
                    'max_forward_steps': left['first_realizer']['max_forward_steps'],
                    'max_backward_steps': left['first_realizer']['max_backward_steps'],
                },
                {
                    'constraint_label': right['interval_key'],
                    'state_code': right['first_realizer']['state_code'],
                    'max_forward_steps': right['first_realizer']['max_forward_steps'],
                    'max_backward_steps': right['first_realizer']['max_backward_steps'],
                },
            ]
        )
        if not family['pairwise_overlap_matches_global_feasibility']:
            raise WeakeningPortfolioServiceModeSuffixFeasibilityIntersectionLawError('pairwise/global feasibility mismatch for pair')
        if not family['feasible']:
            infeasible_pair_count += 1
            if family['blocker_certificate'] is None:
                raise WeakeningPortfolioServiceModeSuffixFeasibilityIntersectionLawError('missing blocker certificate for infeasible pair')

    triple_validation_count = 0
    triple_pairwise_implies_global = True
    for left, middle, right in itertools.combinations(realized, 3):
        triple_validation_count += 1
        family = select_constraint_family_intersection(
            [
                {
                    'constraint_label': left['interval_key'],
                    'state_code': left['first_realizer']['state_code'],
                    'max_forward_steps': left['first_realizer']['max_forward_steps'],
                    'max_backward_steps': left['first_realizer']['max_backward_steps'],
                },
                {
                    'constraint_label': middle['interval_key'],
                    'state_code': middle['first_realizer']['state_code'],
                    'max_forward_steps': middle['first_realizer']['max_forward_steps'],
                    'max_backward_steps': middle['first_realizer']['max_backward_steps'],
                },
                {
                    'constraint_label': right['interval_key'],
                    'state_code': right['first_realizer']['state_code'],
                    'max_forward_steps': right['first_realizer']['max_forward_steps'],
                    'max_backward_steps': right['first_realizer']['max_backward_steps'],
                },
            ]
        )
        if family['pairwise_overlap'] and not family['feasible']:
            triple_pairwise_implies_global = False
            break

    return {
        'max_clock': build_max_clock(),
        'catalog_interval_count': len(all_intervals),
        'expected_closed_interval_count': (build_max_clock() + 1) * (build_max_clock() + 2) // 2,
        'realized_bounded_window_interval_count': len(realized),
        'all_closed_rank_intervals_realized': realized_keys == catalog_keys,
        'pair_validation_count': pair_validation_count,
        'infeasible_pair_count': infeasible_pair_count,
        'every_infeasible_pair_has_two_constraint_blocker_certificate': True,
        'triple_validation_count': triple_validation_count,
        'pairwise_overlap_implies_global_feasibility_for_all_triples': triple_pairwise_implies_global,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    return {
        'validation_summary': build_feasibility_intersection_validation_summary(),
        'family_examples': build_family_examples(),
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_feasibility_intersection_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Collapse multi-constraint positive-service local weakening feasibility into exact clock-interval '
            'intersection so future inheritors can merge bounded local requirements without replaying the full '
            'mode-suffix chain.'
        ),
        'headline_findings': build_headline_findings(),
        'decision_rules': [
            'Convert every bounded local weakening requirement into one closed source-rank interval `[lower_rank, upper_rank]` on the dense `16 -> 0` clock path.',
            'A whole family is feasible exactly when `max(lower_rank) <= min(upper_rank)`; any code in that closed intersection interval satisfies every current requirement at once.',
            'Treat disjointness of one interval pair as a complete infeasibility certificate for the current local automaton: every infeasible family has a two-constraint blocker pair.',
            'Treat any future revision where some closed rank intervals stop being realizable, or where pairwise-overlapping interval families lose a common witness, as a redesign signal for the current positive-service local service path.',
        ],
        'family_examples': build_family_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_feasibility_intersection_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_feasibility_intersection_snapshot(), indent=2, sort_keys=True))
