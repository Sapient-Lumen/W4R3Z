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
    build_positive_service_mode_suffix_counter_rows,
    build_state_code_chain,
    build_state_code_to_row,
    select_service_mode_suffix_counter,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law import (
    build_exact_counter_support,
    build_shared_counter_support,
    successor_state_code,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law import (
    strict_predecessor_state_code,
)


class WeakeningPortfolioServiceModeSuffixRankClockLawError(RuntimeError):
    pass


SOURCE_CODE = 'S10'
TERMINAL_CODE = 'T0'


def _parse_state_code(state_code: str) -> tuple[str, int]:
    if len(state_code) < 2:
        raise WeakeningPortfolioServiceModeSuffixRankClockLawError(f'invalid state code {state_code!r}')
    mode = state_code[0]
    try:
        counter = int(state_code[1:])
    except ValueError as exc:
        raise WeakeningPortfolioServiceModeSuffixRankClockLawError(f'invalid state code {state_code!r}') from exc
    return mode, counter


@lru_cache(maxsize=1)
def build_support_sets() -> dict[str, set[int]]:
    return {
        'exact': set(build_exact_counter_support()),
        'shared': set(build_shared_counter_support()),
    }


@lru_cache(maxsize=None)
def bridge_tail_count(counter: int) -> int:
    if counter < 0:
        raise WeakeningPortfolioServiceModeSuffixRankClockLawError('counter must be nonnegative')
    if counter == 0:
        return 0
    supports = build_support_sets()
    return sum(1 for value in supports['exact'] if value <= counter - 1) + sum(
        1 for value in supports['shared'] if value <= counter - 1
    )


@lru_cache(maxsize=None)
def current_bridge_tax(mode_code: str) -> int:
    if mode_code in {'S', 'T'}:
        return 0
    if mode_code in {'E', 'D'}:
        return 1
    raise WeakeningPortfolioServiceModeSuffixRankClockLawError(f'unknown mode code {mode_code!r}')


@lru_cache(maxsize=None)
def terminal_distance_clock(state_code: str) -> int:
    mode, counter = _parse_state_code(state_code)
    if mode == 'T':
        return 0
    return counter + bridge_tail_count(counter) + current_bridge_tax(mode)


@lru_cache(maxsize=1)
def build_max_clock() -> int:
    return terminal_distance_clock(SOURCE_CODE)


@lru_cache(maxsize=None)
def source_rank(state_code: str) -> int:
    return build_max_clock() - terminal_distance_clock(state_code)


@lru_cache(maxsize=None)
def pairwise_path_distance(left_state_code: str, right_state_code: str) -> int:
    return abs(terminal_distance_clock(left_state_code) - terminal_distance_clock(right_state_code))


@lru_cache(maxsize=1)
def build_clock_basis_summary() -> dict[str, Any]:
    return {
        'source_code': SOURCE_CODE,
        'terminal_code': TERMINAL_CODE,
        'max_clock': build_max_clock(),
        'exact_counter_support': build_exact_counter_support(),
        'shared_counter_support': build_shared_counter_support(),
        'clock_formula': 'counter + bridge_tail_count(counter) + current_bridge_tax(mode), with T0 fixed at 0',
        'bridge_tail_count_rule': 'count exact/shared supports at counters <= k-1',
        'current_bridge_tax_rule': {'suffix_only': 0, 'exact_only': 1, 'shared_diagonal': 1, 'terminal': 0},
    }


@lru_cache(maxsize=1)
def build_rank_clock_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    archived_rows = build_positive_service_mode_suffix_counter_rows()
    chain = build_state_code_chain()
    for index, row in enumerate(archived_rows):
        code = row['state_code']
        mode_code, counter = _parse_state_code(code)
        predicted_terminal_distance = terminal_distance_clock(code)
        predicted_source_rank = source_rank(code)
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'state_code': code,
                'mode': row['mode'],
                'mode_code': mode_code,
                'suffix_only_steps_remaining': row['suffix_only_steps_remaining'],
                'counter': counter,
                'bridge_tail_count': bridge_tail_count(counter),
                'current_bridge_tax': current_bridge_tax(mode_code),
                'predicted_terminal_distance_clock': predicted_terminal_distance,
                'archived_terminal_distance_clock': len(chain) - 1 - index,
                'predicted_source_rank': predicted_source_rank,
                'archived_source_rank': index,
                'clock_matches_archive': predicted_terminal_distance == len(chain) - 1 - index,
                'rank_matches_archive': predicted_source_rank == index,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_clock_chain() -> list[int]:
    return [terminal_distance_clock(code) for code in build_state_code_chain()]


@lru_cache(maxsize=1)
def build_rank_chain() -> list[int]:
    return [source_rank(code) for code in build_state_code_chain()]


@lru_cache(maxsize=1)
def build_clock_validation_summary() -> dict[str, Any]:
    rows = build_rank_clock_rows()
    codes = build_state_code_chain()
    pairwise_matches = True
    pair_count = 0
    for left, right in itertools.combinations(codes, 2):
        pair_count += 1
        expected = abs(codes.index(left) - codes.index(right))
        if pairwise_path_distance(left, right) != expected:
            pairwise_matches = False
            break
    return {
        'all_rows_match_archived_terminal_distance': all(row['clock_matches_archive'] for row in rows),
        'all_rows_match_archived_source_rank': all(row['rank_matches_archive'] for row in rows),
        'clock_chain_is_dense_16_to_0': build_clock_chain() == list(range(build_max_clock(), -1, -1)),
        'rank_chain_is_dense_0_to_16': build_rank_chain() == list(range(0, build_max_clock() + 1)),
        'source_rank_plus_terminal_distance_equals_max_clock_everywhere': all(
            source_rank(code) + terminal_distance_clock(code) == build_max_clock() for code in codes
        ),
        'successor_decrements_clock_by_one_everywhere_except_absorbing_terminal': all(
            terminal_distance_clock(successor_state_code(code)) == max(terminal_distance_clock(code) - 1, 0)
            for code in codes
        ),
        'strict_predecessor_increments_clock_by_one_everywhere_except_source_boundary': all(
            strict_predecessor_state_code(code) is None or terminal_distance_clock(strict_predecessor_state_code(code)) == terminal_distance_clock(code) + 1
            for code in codes
        ),
        'pairwise_path_distance_matches_absolute_clock_difference': pairwise_matches,
        'pairwise_validation_count': pair_count,
    }


@lru_cache(maxsize=1)
def build_mode_clock_summary() -> dict[str, Any]:
    rows = build_rank_clock_rows()
    summary: dict[str, list[int]] = {
        'suffix_only': [],
        'exact_only': [],
        'shared_diagonal': [],
        'terminal': [],
    }
    for row in rows:
        summary[row['mode']].append(row['predicted_terminal_distance_clock'])
    return {
        'terminal_distance_clock_support_by_mode': summary,
        'exact_modes_are_the_odd_clock_spikes_except_terminal_entry_gap': summary['exact_only'] == [14, 10, 7, 3, 1],
        'shared_mode_is_the_unique_clock_5_spike': summary['shared_diagonal'] == [5],
        'suffix_mode_fills_every_remaining_positive_clock': summary['suffix_only'] == [16, 15, 13, 12, 11, 9, 8, 6, 4, 2],
    }


@lru_cache(maxsize=1)
def build_distance_examples() -> list[dict[str, Any]]:
    example_codes = ['S10', 'E8', 'D2', 'E0', 'T0']
    rows_by_code = build_state_code_to_row()
    pairs = [('S10', 'T0'), ('E8', 'D2'), ('S8', 'E3'), ('D2', 'E0')]
    examples: list[dict[str, Any]] = []
    for left, right in pairs:
        left_row = rows_by_code[left]
        right_signature = rows_by_code[right]['current_signature'] if right in rows_by_code else 'terminal_absorbing'
        examples.append(
            {
                'left_state_code': left,
                'left_signature': left_row['current_signature'],
                'right_state_code': right,
                'right_signature': right_signature,
                'left_terminal_distance_clock': terminal_distance_clock(left),
                'right_terminal_distance_clock': terminal_distance_clock(right),
                'pairwise_path_distance': pairwise_path_distance(left, right),
            }
        )
    selector_targets = [0.40, 0.0184, 0.0074, 0.0001]
    for target in selector_targets:
        selected = select_service_mode_suffix_counter(target)
        code = selected['state_code']
        examples.append(
            {
                'minimum_service_share': target,
                'current_signature': selected['current_signature'],
                'state_code': code,
                'terminal_distance_clock': terminal_distance_clock(code),
                'source_rank': source_rank(code),
                'next_state_code': successor_state_code(code),
                'strict_predecessor_state_code': strict_predecessor_state_code(code),
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_service_mode_suffix_rank_clock_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Collapse the recent reversible mode-suffix local weakening chain into one scalar '
            'rank clock so future inheritors can read forward step, backstep, and pairwise path '
            'distance as arithmetic rather than graph lookup.'
        ),
        'headline_findings': {
            'clock_basis_summary': build_clock_basis_summary(),
            'clock_validation_summary': build_clock_validation_summary(),
            'mode_clock_summary': build_mode_clock_summary(),
            'clock_chain': build_clock_chain(),
            'rank_chain': build_rank_chain(),
        },
        'decision_rules': [
            'Treat every positive-service local weakening code as a single scalar terminal-distance clock together with the existing mode label.',
            'Compute the clock in closed form as `counter + bridge_tail_count(counter) + current_bridge_tax(mode)` with bridge tail counting exact/shared supports at counters `<= k-1`, and terminal fixed at `0`.',
            'Use source rank as `max_clock - terminal_distance_clock`; this turns the archived chain into the dense rank interval `0..16` and the terminal-distance chain into `16..0`.',
            'Read successor, strict predecessor, and pairwise path distance arithmetically: successor decrements clock by one, predecessor increments it by one (except the source boundary), and path distance is the absolute clock difference.',
            'Treat any future archive revision that breaks dense clock/rank coverage, pairwise absolute-distance recovery, or the current bridge-tax/support basis as a redesign signal.',
        ],
        'positive_service_mode_suffix_rank_clock_rows': build_rank_clock_rows(),
        'distance_examples': build_distance_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_rank_clock_law.py',
    }


def main() -> None:
    print(json.dumps(build_service_mode_suffix_rank_clock_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
