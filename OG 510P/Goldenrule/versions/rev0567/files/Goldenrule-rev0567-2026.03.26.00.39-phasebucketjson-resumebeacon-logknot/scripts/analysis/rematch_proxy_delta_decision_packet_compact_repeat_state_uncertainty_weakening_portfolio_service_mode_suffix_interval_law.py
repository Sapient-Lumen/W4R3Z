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
    build_state_code_chain,
    build_state_code_to_row,
    select_service_mode_suffix_counter,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law import (
    strict_predecessor_state_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law import (
    build_max_clock,
    pairwise_path_distance,
    source_rank,
    terminal_distance_clock,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law import (
    successor_state_code,
)


class WeakeningPortfolioServiceModeSuffixIntervalLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_source_rank_to_state_code() -> dict[int, str]:
    return {
        source_rank(code): code
        for code in build_state_code_chain()
    }


@lru_cache(maxsize=1)
def build_clock_to_state_code() -> dict[int, str]:
    return {
        terminal_distance_clock(code): code
        for code in build_state_code_chain()
    }


@lru_cache(maxsize=1)
def build_chain_rows_by_code() -> dict[str, dict[str, Any]]:
    return build_state_code_to_row()


@lru_cache(maxsize=None)
def step_forward(state_code: str, steps: int) -> str:
    if steps < 0:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError('steps must be nonnegative')
    code = state_code
    for _ in range(steps):
        code = successor_state_code(code)
    return code


@lru_cache(maxsize=None)
def step_backward(state_code: str, steps: int) -> str:
    if steps < 0:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError('steps must be nonnegative')
    code = state_code
    for _ in range(steps):
        predecessor = strict_predecessor_state_code(code)
        if predecessor is None:
            return code
        code = predecessor
    return code


@lru_cache(maxsize=None)
def select_mode_suffix_clock_interval(state_code: str, max_forward_steps: int, max_backward_steps: int) -> dict[str, Any]:
    if max_forward_steps < 0 or max_backward_steps < 0:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError('step budgets must be nonnegative')
    rows_by_code = build_chain_rows_by_code()
    if state_code not in rows_by_code:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError(f'unknown state code {state_code!r}')

    current_rank = source_rank(state_code)
    current_clock = terminal_distance_clock(state_code)
    max_clock = build_max_clock()

    lower_rank = max(0, current_rank - max_backward_steps)
    upper_rank = min(max_clock, current_rank + max_forward_steps)
    lower_clock = max(0, current_clock - max_forward_steps)
    upper_clock = min(max_clock, current_clock + max_backward_steps)

    if lower_rank + upper_clock != max_clock or upper_rank + lower_clock != max_clock:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError('rank and clock bounds disagree')

    rank_to_code = build_source_rank_to_state_code()
    interval_codes = [rank_to_code[rank] for rank in range(lower_rank, upper_rank + 1)]
    boundary_backward_code = rank_to_code[lower_rank]
    boundary_forward_code = rank_to_code[upper_rank]

    effective_backward_steps = min(max_backward_steps, current_rank)
    effective_forward_steps = min(max_forward_steps, current_clock)
    replay_backward = [step_backward(state_code, step) for step in range(0, effective_backward_steps + 1)]
    replay_forward = [step_forward(state_code, step) for step in range(0, effective_forward_steps + 1)]
    replay_codes = [rank_to_code[rank] for rank in range(lower_rank, current_rank)] + replay_forward

    return {
        'state_code': state_code,
        'current_signature': rows_by_code[state_code]['current_signature'],
        'current_mode': rows_by_code[state_code]['mode'],
        'current_source_rank': current_rank,
        'current_terminal_distance_clock': current_clock,
        'max_backward_steps': max_backward_steps,
        'max_forward_steps': max_forward_steps,
        'lower_source_rank': lower_rank,
        'upper_source_rank': upper_rank,
        'lower_terminal_distance_clock': lower_clock,
        'upper_terminal_distance_clock': upper_clock,
        'interval_cardinality': upper_rank - lower_rank + 1,
        'boundary_backward_code': boundary_backward_code,
        'boundary_forward_code': boundary_forward_code,
        'interval_state_codes': interval_codes,
        'interval_source_ranks': list(range(lower_rank, upper_rank + 1)),
        'interval_terminal_distance_clocks_descending': list(range(upper_clock, lower_clock - 1, -1)),
        'replay_backward_codes': replay_backward,
        'replay_forward_codes': replay_forward,
        'replay_union_codes': replay_codes,
        'interval_matches_replay_union': interval_codes == replay_codes,
        'forward_boundary_matches_step_budget': boundary_forward_code == step_forward(state_code, max_forward_steps),
        'backward_boundary_matches_step_budget': boundary_backward_code == step_backward(state_code, max_backward_steps),
    }


@lru_cache(maxsize=None)
def select_service_mode_suffix_clock_interval(
    minimum_service_share: float,
    max_forward_steps: int,
    max_backward_steps: int,
) -> dict[str, Any]:
    selected = select_service_mode_suffix_counter(minimum_service_share)
    interval = select_mode_suffix_clock_interval(
        selected['state_code'],
        max_forward_steps=max_forward_steps,
        max_backward_steps=max_backward_steps,
    )
    return {
        'minimum_service_share': minimum_service_share,
        **interval,
    }


@lru_cache(maxsize=None)
def select_clock_segment(left_state_code: str, right_state_code: str) -> dict[str, Any]:
    rows_by_code = build_chain_rows_by_code()
    if left_state_code not in rows_by_code or right_state_code not in rows_by_code:
        raise WeakeningPortfolioServiceModeSuffixIntervalLawError('segment endpoints must be valid state codes')

    left_rank = source_rank(left_state_code)
    right_rank = source_rank(right_state_code)
    lower_rank = min(left_rank, right_rank)
    upper_rank = max(left_rank, right_rank)
    rank_to_code = build_source_rank_to_state_code()
    interval_codes = [rank_to_code[rank] for rank in range(lower_rank, upper_rank + 1)]
    return {
        'left_state_code': left_state_code,
        'right_state_code': right_state_code,
        'left_signature': rows_by_code[left_state_code]['current_signature'],
        'right_signature': rows_by_code[right_state_code]['current_signature'],
        'left_source_rank': left_rank,
        'right_source_rank': right_rank,
        'left_terminal_distance_clock': terminal_distance_clock(left_state_code),
        'right_terminal_distance_clock': terminal_distance_clock(right_state_code),
        'segment_state_codes': interval_codes,
        'segment_cardinality': len(interval_codes),
        'pairwise_path_distance': pairwise_path_distance(left_state_code, right_state_code),
        'segment_cardinality_matches_distance_plus_one': len(interval_codes) == pairwise_path_distance(left_state_code, right_state_code) + 1,
    }


@lru_cache(maxsize=1)
def build_interval_examples() -> list[dict[str, Any]]:
    return [
        select_service_mode_suffix_clock_interval(0.40, max_forward_steps=2, max_backward_steps=1),
        select_service_mode_suffix_clock_interval(0.05, max_forward_steps=3, max_backward_steps=2),
        select_service_mode_suffix_clock_interval(0.0184, max_forward_steps=2, max_backward_steps=2),
        select_service_mode_suffix_clock_interval(0.0074, max_forward_steps=1, max_backward_steps=4),
        select_service_mode_suffix_clock_interval(0.0001, max_forward_steps=2, max_backward_steps=3),
    ]


@lru_cache(maxsize=1)
def build_segment_examples() -> list[dict[str, Any]]:
    return [
        select_clock_segment('S10', 'T0'),
        select_clock_segment('E8', 'D2'),
        select_clock_segment('S8', 'E3'),
        select_clock_segment('D2', 'E0'),
    ]


@lru_cache(maxsize=1)
def build_interval_validation_summary() -> dict[str, Any]:
    codes = build_state_code_chain()
    validations = 0
    all_windows_match = True
    all_segment_cardinalities_match = True
    maximum_interval_cardinality = 0
    clipped_forward_examples = 0
    clipped_backward_examples = 0

    for code in codes:
        current_clock = terminal_distance_clock(code)
        current_rank = source_rank(code)
        for max_forward in range(0, build_max_clock() + 1):
            for max_backward in range(0, build_max_clock() + 1):
                validations += 1
                interval = select_mode_suffix_clock_interval(code, max_forward, max_backward)
                maximum_interval_cardinality = max(maximum_interval_cardinality, interval['interval_cardinality'])
                if not interval['interval_matches_replay_union']:
                    all_windows_match = False
                if interval['lower_terminal_distance_clock'] != max(0, current_clock - max_forward):
                    all_windows_match = False
                if interval['upper_terminal_distance_clock'] != min(build_max_clock(), current_clock + max_backward):
                    all_windows_match = False
                if interval['lower_source_rank'] != max(0, current_rank - max_backward):
                    all_windows_match = False
                if interval['upper_source_rank'] != min(build_max_clock(), current_rank + max_forward):
                    all_windows_match = False
                if interval['interval_cardinality'] != interval['upper_source_rank'] - interval['lower_source_rank'] + 1:
                    all_windows_match = False
                if max_forward > current_clock:
                    clipped_forward_examples += 1
                if max_backward > current_rank:
                    clipped_backward_examples += 1

    for left in codes:
        for right in codes:
            segment = select_clock_segment(left, right)
            if not segment['segment_cardinality_matches_distance_plus_one']:
                all_segment_cardinalities_match = False

    return {
        'window_validation_count': validations,
        'every_bounded_neighborhood_is_a_contiguous_rank_interval': all_windows_match,
        'every_segment_cardinality_matches_distance_plus_one': all_segment_cardinalities_match,
        'maximum_interval_cardinality': maximum_interval_cardinality,
        'full_chain_is_realized_as_one_interval': maximum_interval_cardinality == len(codes),
        'clipped_forward_validation_count': clipped_forward_examples,
        'clipped_backward_validation_count': clipped_backward_examples,
    }


@lru_cache(maxsize=1)
def build_interval_headline_findings() -> dict[str, Any]:
    return {
        'max_clock': build_max_clock(),
        'source_code': build_state_code_chain()[0],
        'terminal_code': build_state_code_chain()[-1],
        'window_validation_summary': build_interval_validation_summary(),
        'segment_examples': build_segment_examples(),
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_interval_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Collapse bounded local positive-service weakening navigation into exact clock/rank intervals '
            'so future inheritors can answer neighborhood, containment, and subpath queries without replaying '
            'the mode-suffix chain.'
        ),
        'headline_findings': build_interval_headline_findings(),
        'decision_rules': [
            'Treat any bounded local navigation budget `(max_backward_steps, max_forward_steps)` as one clipped interval in source-rank or terminal-distance-clock coordinates.',
            'Read forward-only local relaxation horizon from the lower clock bound `max(0, current_clock - max_forward_steps)` and backward-only local tightening horizon from the upper clock bound `min(max_clock, current_clock + max_backward_steps)`.',
            'Answer segment queries between two local codes by taking the closed rank interval between their source ranks; segment cardinality is always `pairwise_path_distance + 1`.',
            'Treat any future revision where bounded local windows develop holes, or where segment size stops matching distance plus one, as a redesign signal for the current positive-service local automaton.',
        ],
        'interval_examples': build_interval_examples(),
        'segment_examples': build_segment_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_interval_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_interval_snapshot(), indent=2, sort_keys=True))
