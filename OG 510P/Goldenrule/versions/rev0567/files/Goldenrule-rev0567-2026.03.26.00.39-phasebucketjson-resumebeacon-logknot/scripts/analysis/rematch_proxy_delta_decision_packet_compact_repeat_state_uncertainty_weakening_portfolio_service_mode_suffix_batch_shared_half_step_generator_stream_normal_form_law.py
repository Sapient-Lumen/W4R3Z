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
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law import (
    apply_shared_half_step_interval_kernel,
)

MAX_SOURCE_RANK = 16
HALF_STEP_SELECTOR_INDEX_COUNT = 33


class WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(RuntimeError):
    pass


def _normalize_generator_interval(interval: list[int] | tuple[int, int]) -> tuple[int, int]:
    if len(interval) != 2:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
            'generator interval must contain exactly two ranks'
        )
    lower_rank = int(interval[0])
    upper_rank = int(interval[1])
    if lower_rank < 0 or upper_rank < lower_rank or upper_rank > MAX_SOURCE_RANK:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
            'generator interval must stay within the realized 17-state path bounds'
        )
    return lower_rank, upper_rank


@lru_cache(maxsize=1)
def build_one_sided_generator_catalog() -> list[list[int]]:
    return [list(interval) for interval in build_distinct_one_sided_generator_intervals()]


@lru_cache(maxsize=1)
def build_generator_kind_lookup() -> dict[tuple[int, int], str]:
    lookup: dict[tuple[int, int], str] = {}
    for interval in build_distinct_one_sided_generator_intervals():
        lower_rank, upper_rank = interval
        if lower_rank == 0 and upper_rank == MAX_SOURCE_RANK:
            kind = 'identity'
        elif lower_rank == 0:
            kind = 'upper_cap'
        elif upper_rank == MAX_SOURCE_RANK:
            kind = 'lower_floor'
        else:
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
                'every generator interval in this catalog should be one-sided'
            )
        lookup[(lower_rank, upper_rank)] = kind
    return lookup


@lru_cache(maxsize=1)
def build_generator_action_lookup() -> dict[tuple[int, int], tuple[int, ...]]:
    return {
        tuple(interval): tuple(
            apply_shared_half_step_interval_kernel(
                interval,
                half_step_selector_index=half_step_selector_index,
            )['projected_half_step_witness_index']
            for half_step_selector_index in range(HALF_STEP_SELECTOR_INDEX_COUNT)
        )
        for interval in build_distinct_one_sided_generator_intervals()
    }


NormalFormState = tuple[str, int, int] | tuple[str, int]


@lru_cache(maxsize=None)
def build_stream_normal_form(
    generator_stream: tuple[tuple[int, int], ...],
) -> NormalFormState:
    state: NormalFormState = ('interval', 0, MAX_SOURCE_RANK)
    for interval in generator_stream:
        state = update_stream_normal_form(state, interval)
    return state


@lru_cache(maxsize=None)
def update_stream_normal_form(
    state: NormalFormState,
    generator_interval: list[int] | tuple[int, int],
) -> NormalFormState:
    lower_rank, upper_rank = _normalize_generator_interval(generator_interval)
    kind = build_generator_kind_lookup()[(lower_rank, upper_rank)]
    if kind == 'identity':
        return state

    if state[0] == 'interval':
        current_lower_rank = int(state[1])
        current_upper_rank = int(state[2])
        if kind == 'lower_floor':
            next_lower_rank = max(current_lower_rank, lower_rank)
            if next_lower_rank <= current_upper_rank:
                return ('interval', next_lower_rank, current_upper_rank)
            return ('constant', lower_rank)
        next_upper_rank = min(current_upper_rank, upper_rank)
        if current_lower_rank <= next_upper_rank:
            return ('interval', current_lower_rank, next_upper_rank)
        return ('constant', upper_rank)

    constant_rank = int(state[1])
    if kind == 'lower_floor':
        return ('constant', max(constant_rank, lower_rank))
    return ('constant', min(constant_rank, upper_rank))


@lru_cache(maxsize=None)
def build_half_step_kernel_from_normal_form(state: NormalFormState) -> tuple[int, ...]:
    if state[0] == 'interval':
        lower_rank = int(state[1])
        upper_rank = int(state[2])
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
    doubled_constant_rank = 2 * int(state[1])
    return (doubled_constant_rank,) * HALF_STEP_SELECTOR_INDEX_COUNT


@lru_cache(maxsize=None)
def apply_generator_stream_directly(
    generator_stream: tuple[tuple[int, int], ...],
) -> tuple[int, ...]:
    action_lookup = build_generator_action_lookup()
    output = tuple(range(HALF_STEP_SELECTOR_INDEX_COUNT))
    for interval in generator_stream:
        generator_output = action_lookup[interval]
        output = tuple(generator_output[half_step_selector_index] for half_step_selector_index in output)
    return output


@lru_cache(maxsize=None)
def serialize_stream_normal_form(state: NormalFormState) -> dict[str, Any]:
    if state[0] == 'interval':
        return {
            'normal_form_kind': 'interval',
            'interval': [int(state[1]), int(state[2])],
            'projected_half_step_witness_index_range': [2 * int(state[1]), 2 * int(state[2])],
        }
    return {
        'normal_form_kind': 'constant',
        'constant_rank': int(state[1]),
        'projected_half_step_witness_index': 2 * int(state[1]),
    }


@lru_cache(maxsize=1)
def build_batch_shared_half_step_generator_stream_counterexample() -> dict[str, Any]:
    floor_then_cap_stream = ((1, MAX_SOURCE_RANK), (0, 0))
    cap_then_floor_stream = ((0, 0), (1, MAX_SOURCE_RANK))
    floor_then_cap_state = build_stream_normal_form(floor_then_cap_stream)
    cap_then_floor_state = build_stream_normal_form(cap_then_floor_stream)
    if floor_then_cap_state == cap_then_floor_state:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
            'the counterexample should distinguish the weaker extrema+latch summary'
        )
    return {
        'shared_weaker_summary': {
            'max_floor_rank': 1,
            'min_cap_rank': 0,
            'infeasible_latch': True,
        },
        'floor_then_cap_stream': [list(interval) for interval in floor_then_cap_stream],
        'floor_then_cap_normal_form': serialize_stream_normal_form(floor_then_cap_state),
        'cap_then_floor_stream': [list(interval) for interval in cap_then_floor_stream],
        'cap_then_floor_normal_form': serialize_stream_normal_form(cap_then_floor_state),
        'floor_then_cap_direct_output_half_step_index': apply_generator_stream_directly(floor_then_cap_stream)[0],
        'cap_then_floor_direct_output_half_step_index': apply_generator_stream_directly(cap_then_floor_stream)[0],
    }


@lru_cache(maxsize=1)
def build_batch_shared_half_step_generator_stream_examples() -> list[dict[str, Any]]:
    feasible_stream = ((3, MAX_SOURCE_RANK), (0, 8), (2, MAX_SOURCE_RANK), (0, 10))
    collapsed_to_upper_stream = ((1, MAX_SOURCE_RANK), (0, 0))
    collapsed_to_lower_stream = ((0, 0), (1, MAX_SOURCE_RANK))
    absorbing_constant_stream = ((0, 0), (1, MAX_SOURCE_RANK), (5, MAX_SOURCE_RANK), (0, 2))
    return [
        {
            'feasible_stream_reduces_to_one_interval_normal_form': {
                'generator_stream': [list(interval) for interval in feasible_stream],
                'normal_form': serialize_stream_normal_form(build_stream_normal_form(feasible_stream)),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(feasible_stream)),
            }
        },
        {
            'disjoint_floor_then_cap_stream_collapses_to_upper_constant': {
                'generator_stream': [list(interval) for interval in collapsed_to_upper_stream],
                'normal_form': serialize_stream_normal_form(build_stream_normal_form(collapsed_to_upper_stream)),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(collapsed_to_upper_stream)),
            }
        },
        {
            'disjoint_cap_then_floor_stream_collapses_to_lower_constant': {
                'generator_stream': [list(interval) for interval in collapsed_to_lower_stream],
                'normal_form': serialize_stream_normal_form(build_stream_normal_form(collapsed_to_lower_stream)),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(collapsed_to_lower_stream)),
            }
        },
        {
            'once_constant_every_further_generator_keeps_the_stream_constant': {
                'generator_stream': [list(interval) for interval in absorbing_constant_stream],
                'normal_form': serialize_stream_normal_form(build_stream_normal_form(absorbing_constant_stream)),
                'direct_output_half_step_witness_indices': list(apply_generator_stream_directly(absorbing_constant_stream)),
            }
        },
    ]


@lru_cache(maxsize=1)
def build_batch_shared_half_step_generator_stream_normal_form_validation_summary() -> dict[str, Any]:
    generator_catalog = [tuple(interval) for interval in build_distinct_one_sided_generator_intervals()]
    generator_count = len(generator_catalog)
    initial_state: NormalFormState = ('interval', 0, MAX_SOURCE_RANK)
    identity_output = tuple(range(HALF_STEP_SELECTOR_INDEX_COUNT))
    frontier_states: dict[NormalFormState, tuple[int, ...]] = {initial_state: identity_output}
    frontier_counts: Counter[NormalFormState] = Counter({initial_state: 1})
    state_first_depth: dict[NormalFormState, int] = {}
    all_states: dict[NormalFormState, tuple[int, ...]] = {initial_state: identity_output}
    depth_state_count: dict[int, int] = {}
    depth_interval_stream_count: dict[int, int] = {}
    depth_constant_stream_count: dict[int, int] = {}
    total_stream_count = 0

    for depth in range(1, 5):
        next_frontier_states: dict[NormalFormState, tuple[int, ...]] = {}
        next_frontier_counts: Counter[NormalFormState] = Counter()
        for state, direct_output in frontier_states.items():
            multiplicity = frontier_counts[state]
            for generator_interval in generator_catalog:
                next_state = update_stream_normal_form(state, generator_interval)
                generator_output = build_generator_action_lookup()[generator_interval]
                next_direct_output = tuple(generator_output[index] for index in direct_output)
                if (
                    next_state in next_frontier_states
                    and next_frontier_states[next_state] != next_direct_output
                ):
                    raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
                        'all streams that reduce to the same normal form must induce the same direct half-step kernel'
                    )
                next_frontier_states[next_state] = next_direct_output
                next_frontier_counts[next_state] += multiplicity
                state_first_depth.setdefault(next_state, depth)
        frontier_states = next_frontier_states
        frontier_counts = next_frontier_counts
        all_states.update(frontier_states)
        depth_state_count[depth] = len(frontier_states)
        depth_interval_stream_count[depth] = sum(
            count for state, count in frontier_counts.items() if state[0] == 'interval'
        )
        depth_constant_stream_count[depth] = sum(
            count for state, count in frontier_counts.items() if state[0] == 'constant'
        )
        total_stream_count += sum(frontier_counts.values())

    for state, direct_output in all_states.items():
        if direct_output != build_half_step_kernel_from_normal_form(state):
            raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
                'every reachable normal form must match the direct composed half-step kernel'
            )

    constant_states = sorted(state for state in all_states if state[0] == 'constant')
    interval_states = sorted(state for state in all_states if state[0] == 'interval')
    interval_to_interval_transition_count = 0
    interval_to_constant_transition_count = 0
    constant_to_constant_transition_count = 0
    for state in all_states:
        for generator_interval in generator_catalog:
            next_state = update_stream_normal_form(state, generator_interval)
            if state[0] == 'interval' and next_state[0] == 'interval':
                interval_to_interval_transition_count += 1
            elif state[0] == 'interval' and next_state[0] == 'constant':
                interval_to_constant_transition_count += 1
            elif state[0] == 'constant' and next_state[0] == 'constant':
                constant_to_constant_transition_count += 1
            else:
                raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
                    'constant normal forms should be absorbing under one-sided generator composition'
                )

    represented_half_step_input_output_case_count = total_stream_count * HALF_STEP_SELECTOR_INDEX_COUNT
    expected_total_stream_count = sum(generator_count**depth for depth in range(1, 5))
    if total_stream_count != expected_total_stream_count:
        raise WeakeningPortfolioServiceModeSuffixBatchSharedHalfStepGeneratorStreamNormalFormLawError(
            'every ordered one-sided generator stream of length 1..4 should be counted exactly once'
        )

    counterexample = build_batch_shared_half_step_generator_stream_counterexample()

    return {
        'validated_distinct_one_sided_generator_interval_count': generator_count,
        'validated_one_sided_generator_stream_length_range': [1, 4],
        'validated_ordered_one_sided_generator_stream_count': total_stream_count,
        'represented_half_step_input_output_case_count': represented_half_step_input_output_case_count,
        'reachable_normal_form_count': len(all_states),
        'reachable_interval_normal_form_count': len(interval_states),
        'reachable_constant_normal_form_count': len(constant_states),
        'reachable_interval_normal_forms_match_realized_feasible_kernel_catalog': len(interval_states) == 153,
        'reachable_constant_normal_forms_cover_all_path_ranks': [state[1] for state in constant_states] == list(range(MAX_SOURCE_RANK + 1)),
        'every_reachable_normal_form_matches_direct_composition': True,
        'normal_form_state_count_by_depth': depth_state_count,
        'depth_interval_stream_count': depth_interval_stream_count,
        'depth_constant_stream_count': depth_constant_stream_count,
        'all_reachable_normal_forms_appear_by_depth_two': max(state_first_depth.values()) == 2,
        'interval_normal_form_first_depth_spectrum': dict(sorted(Counter(
            state_first_depth[state] for state in interval_states
        ).items())),
        'constant_normal_form_first_depth_spectrum': dict(sorted(Counter(
            state_first_depth[state] for state in constant_states
        ).items())),
        'constant_normal_forms_are_absorbing': True,
        'interval_to_interval_generator_transition_count': interval_to_interval_transition_count,
        'interval_to_constant_generator_transition_count': interval_to_constant_transition_count,
        'constant_to_constant_generator_transition_count': constant_to_constant_transition_count,
        'weaker_extrema_and_infeasible_latch_summary_is_not_exact': True,
        'exact_counterexample_shared_extrema_and_latch_but_different_normal_forms': counterexample,
    }


@lru_cache(maxsize=1)
def build_headline_findings() -> dict[str, Any]:
    validation = build_batch_shared_half_step_generator_stream_normal_form_validation_summary()
    return {
        'every_ordered_one_sided_generator_stream_reduces_exactly_to_one_interval_or_constant_normal_form': True,
        'reachable_normal_form_count': validation['reachable_normal_form_count'],
        'reachable_interval_normal_form_count': validation['reachable_interval_normal_form_count'],
        'reachable_constant_normal_form_count': validation['reachable_constant_normal_form_count'],
        'validated_ordered_one_sided_generator_stream_count': validation['validated_ordered_one_sided_generator_stream_count'],
        'represented_half_step_input_output_case_count': validation['represented_half_step_input_output_case_count'],
        'validation_summary': validation,
    }


@lru_cache(maxsize=1)
def build_decision_rules() -> list[str]:
    return [
        'After a batch path-L2 or path-Linf request has been normalized to the shared half-step lattice, reduce every ordered stream of one-sided floor/cap generators online to one of only two exact normal forms: an interval kernel K_[a,b] with a <= b, or a constant rank kernel C_c.',
        'Start the normalized stream state at interval [0,16]. Updating by K_[a,16] either raises the lower bound inside the interval or, if it overshoots the current upper bound, collapses the stream immediately to constant rank a; updating by K_[0,b] is the symmetric upper-cap rule.',
        'Once the stream has collapsed to constant rank c, stop carrying any interval metadata at all: every later lower-floor update becomes c <- max(c,a) and every later upper-cap update becomes c <- min(c,b).',
        'Do not summarize disjoint one-sided generator streams only by max_floor_rank, min_cap_rank, and an infeasible latch: floor-then-cap and cap-then-floor can share those three values while collapsing to different constant kernels.',
        'Because all 170 exact normal forms appear by stream length two on the current path, future inheritors can cache the downstream normalized generator-stream state in that finite interval-or-constant family instead of persisting raw generator histories.',
    ]


@lru_cache(maxsize=1)
def build_source_reports() -> list[str]:
    return [
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_executor_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_composition_law_snapshot_20260309.md',
        'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_boundary_generator_law_snapshot_20260309.md',
    ]


@lru_cache(maxsize=1)
def build_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_snapshot() -> dict[str, Any]:
    return {
        'focus': 'Ordered one-sided normalized half-step generator streams reduce exactly to one feasible interval kernel or one constant rank kernel.',
        'headline_findings': build_headline_findings(),
        'decision_rules': build_decision_rules(),
        'normal_form_examples': build_batch_shared_half_step_generator_stream_examples(),
        'source_reports': build_source_reports(),
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_batch_shared_half_step_generator_stream_normal_form_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
