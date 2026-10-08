#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law import (
    build_distinct_one_sided_generator_intervals,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law import (
    HALF_STEP_SELECTOR_INDEX_COUNT,
    MAX_SOURCE_RANK,
    apply_generator_stream_directly,
    build_batch_shared_half_step_generator_stream_counterexample,
    build_batch_shared_half_step_generator_stream_normal_form_validation_summary,
)


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(RuntimeError):
    pass


FeasibleIntervalKernelState = tuple[int, int]



def _normalize_generator_interval(interval: list[int] | tuple[int, int]) -> tuple[int, int]:
    if len(interval) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
            'generator interval must contain exactly two ranks'
        )
    lower_rank = int(interval[0])
    upper_rank = int(interval[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
            'generator interval must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=1)
def build_one_sided_generator_catalog() -> list[list[int]]:
    return [list(interval) for interval in build_distinct_one_sided_generator_intervals()]


@lru_cache(maxsize=None)
def update_feasible_interval_kernel_state(
    state: FeasibleIntervalKernelState,
    generator_interval: list[int] | tuple[int, int],
) -> FeasibleIntervalKernelState:
    current_lower_rank = int(state[0])
    current_upper_rank = int(state[1])
    if current_lower_rank < 0 or current_upper_rank < current_lower_rank or current_upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
            'state must stay inside the realized feasible interval catalog'
        )

    lower_rank, upper_rank = _normalize_generator_interval(generator_interval)
    if lower_rank == 0 and upper_rank == MAX_SOURCE_RANK:
        return state
    if upper_rank == MAX_SOURCE_RANK:
        next_lower_rank = max(current_lower_rank, lower_rank)
        if next_lower_rank <= current_upper_rank:
            return (next_lower_rank, current_upper_rank)
        return (lower_rank, lower_rank)
    next_upper_rank = min(current_upper_rank, upper_rank)
    if current_lower_rank <= next_upper_rank:
        return (current_lower_rank, next_upper_rank)
    return (upper_rank, upper_rank)


@lru_cache(maxsize=None)
def build_half_step_kernel_from_feasible_interval_state(
    state: FeasibleIntervalKernelState,
) -> tuple[int, ...]:
    lower_rank = int(state[0])
    upper_rank = int(state[1])
    doubled_lower_rank = 2 * lower_rank
    doubled_upper_rank = 2 * upper_rank
    return tuple(
        doubled_lower_rank
        if half_step_selector_index < doubled_lower_rank
        else doubled_upper_rank
        if half_step_selector_index > doubled_upper_rank
        else half_step_selector_index
        for half_step_selector_index in range(HALF_STEP_SELECTOR_INDEX_COUNT)
    )


@lru_cache(maxsize=None)
def build_feasible_interval_kernel_state_from_generator_stream(
    generator_stream: tuple[tuple[int, int], ...],
) -> FeasibleIntervalKernelState:
    state: FeasibleIntervalKernelState = (0, MAX_SOURCE_RANK)
    for interval in generator_stream:
        state = update_feasible_interval_kernel_state(state, interval)
    return state


@lru_cache(maxsize=None)
def serialize_feasible_interval_kernel_state(
    state: FeasibleIntervalKernelState,
) -> dict[str, Any]:
    return {
        'interval': [int(state[0]), int(state[1])],
        'projected_half_step_witness_index_range': [2 * int(state[0]), 2 * int(state[1])],
        'is_singleton_interval': int(state[0]) == int(state[1]),
    }


@lru_cache(maxsize=1)
def build_batch_shared_half_step_generator_stream_feasible_interval_examples() -> list[dict[str, Any]]:
    feasible_stream = ((3, MAX_SOURCE_RANK), (0, 8), (2, MAX_SOURCE_RANK), (0, 10))
    floor_then_cap_stream = ((1, MAX_SOURCE_RANK), (0, 0))
    cap_then_floor_stream = ((0, 0), (1, MAX_SOURCE_RANK))
    singleton_stays_singleton_stream = ((0, 0), (1, MAX_SOURCE_RANK), (5, MAX_SOURCE_RANK), (0, 2))
    return [
        {
            'feasible_stream_reduces_to_interval_kernel': {
                'generator_stream': [list(interval) for interval in feasible_stream],
                'interval_kernel_state': serialize_feasible_interval_kernel_state(
                    build_feasible_interval_kernel_state_from_generator_stream(feasible_stream)
                ),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(feasible_stream)),
            }
        },
        {
            'disjoint_floor_then_cap_stream_reduces_to_singleton_interval_kernel': {
                'generator_stream': [list(interval) for interval in floor_then_cap_stream],
                'interval_kernel_state': serialize_feasible_interval_kernel_state(
                    build_feasible_interval_kernel_state_from_generator_stream(floor_then_cap_stream)
                ),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(floor_then_cap_stream)),
            }
        },
        {
            'disjoint_cap_then_floor_stream_reduces_to_singleton_interval_kernel': {
                'generator_stream': [list(interval) for interval in cap_then_floor_stream],
                'interval_kernel_state': serialize_feasible_interval_kernel_state(
                    build_feasible_interval_kernel_state_from_generator_stream(cap_then_floor_stream)
                ),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(cap_then_floor_stream)),
            }
        },
        {
            'once_singleton_every_later_generator_keeps_the_stream_singleton': {
                'generator_stream': [list(interval) for interval in singleton_stays_singleton_stream],
                'interval_kernel_state': serialize_feasible_interval_kernel_state(
                    build_feasible_interval_kernel_state_from_generator_stream(singleton_stays_singleton_stream)
                ),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(singleton_stays_singleton_stream)),
            }
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_generator_stream_feasible_interval_validation_summary() -> dict[str, Any]:
    generator_catalog = [tuple(interval) for interval in build_distinct_one_sided_generator_intervals()]
    generator_count = len(generator_catalog)
    initial_state: FeasibleIntervalKernelState = (0, MAX_SOURCE_RANK)
    identity_output = tuple(range(HALF_STEP_SELECTOR_INDEX_COUNT))
    frontier_states: dict[FeasibleIntervalKernelState, tuple[int, ...]] = {initial_state: identity_output}
    frontier_counts: Counter[FeasibleIntervalKernelState] = Counter({initial_state: 1})
    state_first_depth: dict[FeasibleIntervalKernelState, int] = {initial_state: 0}
    all_states: dict[FeasibleIntervalKernelState, tuple[int, ...]] = {initial_state: identity_output}
    depth_state_count: dict[int, int] = {}
    depth_singleton_stream_count: dict[int, int] = {}
    depth_nonsingleton_stream_count: dict[int, int] = {}
    total_stream_count = 0

    for depth in range(1, 5):
        next_frontier_states: dict[FeasibleIntervalKernelState, tuple[int, ...]] = {}
        next_frontier_counts: Counter[FeasibleIntervalKernelState] = Counter()
        for state, direct_output in frontier_states.items():
            multiplicity = frontier_counts[state]
            for generator_interval in generator_catalog:
                next_state = update_feasible_interval_kernel_state(state, generator_interval)
                generator_output = build_half_step_kernel_from_feasible_interval_state(
                    update_feasible_interval_kernel_state((0, MAX_SOURCE_RANK), generator_interval)
                )
                next_direct_output = tuple(generator_output[index] for index in direct_output)
                if (
                    next_state in next_frontier_states
                    and next_frontier_states[next_state] != next_direct_output
                ):
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
                        'all streams that reduce to the same feasible interval must induce the same direct half-step kernel'
                    )
                next_frontier_states[next_state] = next_direct_output
                next_frontier_counts[next_state] += multiplicity
                state_first_depth.setdefault(next_state, depth)
        frontier_states = next_frontier_states
        frontier_counts = next_frontier_counts
        all_states.update(frontier_states)
        depth_state_count[depth] = len(frontier_states)
        depth_singleton_stream_count[depth] = sum(
            count for state, count in frontier_counts.items() if state[0] == state[1]
        )
        depth_nonsingleton_stream_count[depth] = sum(
            count for state, count in frontier_counts.items() if state[0] < state[1]
        )
        total_stream_count += sum(frontier_counts.values())

    for state, direct_output in all_states.items():
        if direct_output != build_half_step_kernel_from_feasible_interval_state(state):
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
                'every reachable feasible interval state must match the direct composed half-step kernel'
            )

    singleton_states = sorted(state for state in all_states if state[0] == state[1])
    nonsingleton_states = sorted(state for state in all_states if state[0] < state[1])
    nonsingleton_to_nonsingleton_transition_count = 0
    nonsingleton_to_singleton_transition_count = 0
    singleton_to_singleton_transition_count = 0
    singleton_to_nonsingleton_transition_count = 0
    for state in all_states:
        for generator_interval in generator_catalog:
            next_state = update_feasible_interval_kernel_state(state, generator_interval)
            if state[0] < state[1] and next_state[0] < next_state[1]:
                nonsingleton_to_nonsingleton_transition_count += 1
            elif state[0] < state[1] and next_state[0] == next_state[1]:
                nonsingleton_to_singleton_transition_count += 1
            elif state[0] == state[1] and next_state[0] == next_state[1]:
                singleton_to_singleton_transition_count += 1
            else:
                singleton_to_nonsingleton_transition_count += 1

    normal_form_validation = build_batch_shared_half_step_generator_stream_normal_form_validation_summary()
    represented_half_step_input_output_case_count = total_stream_count * HALF_STEP_SELECTOR_INDEX_COUNT
    expected_total_stream_count = sum(generator_count**depth for depth in range(1, 5))
    if total_stream_count != expected_total_stream_count:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
            'every ordered one-sided generator stream of length 1..4 should be counted exactly once'
        )
    if singleton_to_nonsingleton_transition_count != 0:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamFeasibleIntervalLawError(
            'singleton intervals should stay singleton under every later one-sided generator'
        )

    counterexample = build_batch_shared_half_step_generator_stream_counterexample()

    return {
        'validated_distinct_one_sided_generator_interval_count': generator_count,
        'validated_one_sided_generator_stream_length_range': [1, 4],
        'validated_ordered_one_sided_generator_stream_count': total_stream_count,
        'represented_half_step_input_output_case_count': represented_half_step_input_output_case_count,
        'reachable_exact_feasible_interval_kernel_count': len(all_states),
        'reachable_singleton_interval_kernel_count': len(singleton_states),
        'reachable_nonsingleton_interval_kernel_count': len(nonsingleton_states),
        'reachable_exact_feasible_interval_kernels_match_realized_catalog': len(all_states) == 153,
        'every_reachable_exact_feasible_interval_kernel_matches_direct_composition': True,
        'all_reachable_exact_feasible_interval_kernels_appear_by_depth_two': max(state_first_depth.values()) == 2,
        'singleton_interval_first_depth_spectrum': dict(sorted(Counter(
            state_first_depth[state] for state in singleton_states
        ).items())),
        'nonsingleton_interval_first_depth_spectrum': dict(sorted(Counter(
            state_first_depth[state] for state in nonsingleton_states
        ).items())),
        'normal_form_family_count_before_singleton_interval_quotient': normal_form_validation['reachable_normal_form_count'],
        'singleton_interval_quotient_removes_duplicate_constant_vs_singleton_pairs': normal_form_validation['reachable_normal_form_count'] - len(all_states),
        'every_previous_constant_normal_form_quotients_to_matching_singleton_interval': normal_form_validation['reachable_constant_normal_form_count'] == len(singleton_states),
        'depth_state_count': depth_state_count,
        'depth_singleton_stream_count': depth_singleton_stream_count,
        'depth_nonsingleton_stream_count': depth_nonsingleton_stream_count,
        'nonsingleton_to_nonsingleton_generator_transition_count': nonsingleton_to_nonsingleton_transition_count,
        'nonsingleton_to_singleton_generator_transition_count': nonsingleton_to_singleton_transition_count,
        'singleton_to_singleton_generator_transition_count': singleton_to_singleton_transition_count,
        'singleton_to_nonsingleton_generator_transition_count': singleton_to_nonsingleton_transition_count,
        'singleton_intervals_are_absorbing_as_exact_kernels': True,
        'weaker_extrema_and_infeasible_latch_summary_is_not_exact_but_singleton_interval_quotient_is': True,
        'exact_counterexample_singleton_interval_quotient_resolves_the_old_latch_failure': {
            'shared_weaker_summary': counterexample['shared_weaker_summary'],
            'floor_then_cap_feasible_interval_kernel': serialize_feasible_interval_kernel_state(
                build_feasible_interval_kernel_state_from_generator_stream(((1, MAX_SOURCE_RANK), (0, 0)))
            ),
            'cap_then_floor_feasible_interval_kernel': serialize_feasible_interval_kernel_state(
                build_feasible_interval_kernel_state_from_generator_stream(((0, 0), (1, MAX_SOURCE_RANK)))
            ),
        },
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_generator_stream_feasible_interval_validation_summary()
    return {
        'every_ordered_one_sided_generator_stream_reduces_exactly_to_one_feasible_interval_kernel': True,
        'reachable_exact_feasible_interval_kernel_count': validation['reachable_exact_feasible_interval_kernel_count'],
        'reachable_singleton_interval_kernel_count': validation['reachable_singleton_interval_kernel_count'],
        'reachable_nonsingleton_interval_kernel_count': validation['reachable_nonsingleton_interval_kernel_count'],
        'validated_ordered_one_sided_generator_stream_count': validation['validated_ordered_one_sided_generator_stream_count'],
        'represented_half_step_input_output_case_count': validation['represented_half_step_input_output_case_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'After a batch path-L2 or path-Linf request has been normalized to the shared half-step lattice, reduce every ordered stream of one-sided floor/cap generators online to one exact feasible interval kernel [a,b] with a <= b.',
        'Start the normalized stream state at feasible interval [0,16]. Updating by K_[a,16] either raises the active lower bound inside the current interval or, if it overshoots the current upper bound, collapses directly to the singleton interval [a,a]; updating by K_[0,b] is the symmetric upper-cap rule with singleton [b,b].',
        'Do not store a separate constant-kernel tag downstream. Singleton feasible intervals [c,c] already realize the same exact half-step kernel as the older constant state C_c and remain singleton under every later one-sided generator update.',
        'Do not summarize disjoint one-sided generator streams only by max_floor_rank, min_cap_rank, and an infeasible latch: floor-then-cap and cap-then-floor can share those three values while reducing to different singleton intervals.',
        'Because the exact downstream quotient is just the realized 153 feasible intervals on the current path, future inheritors can persist one interval kernel state instead of raw generator histories or the larger 170-state interval-or-constant family.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Ordered one-sided normalized half-step generator streams reduce exactly to one feasible interval kernel, with singleton intervals already covering the old constant cases.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'feasible_interval_examples': build_batch_shared_half_step_generator_stream_feasible_interval_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_generator_stream_feasible_interval_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
