#!/usr/bin/env python3
from __future__ import annotations

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
)


class WeakeningPortfolioServiceModeSuffixPredecessorLawError(RuntimeError):
    pass


SOURCE_CODE = 'S10'
TERMINAL_CODE = 'T0'



def _parse_state_code(state_code: str) -> tuple[str, int]:
    if len(state_code) < 2:
        raise WeakeningPortfolioServiceModeSuffixPredecessorLawError(f'invalid state code {state_code!r}')
    mode = state_code[0]
    try:
        counter = int(state_code[1:])
    except ValueError as exc:
        raise WeakeningPortfolioServiceModeSuffixPredecessorLawError(f'invalid state code {state_code!r}') from exc
    return mode, counter


@lru_cache(maxsize=1)
def build_predecessor_support_summary() -> dict[str, Any]:
    exact_support = build_exact_counter_support()
    shared_support = build_shared_counter_support()
    return {
        'source_code': SOURCE_CODE,
        'terminal_code': TERMINAL_CODE,
        'exact_counter_support': exact_support,
        'shared_counter_support': shared_support,
        'suffix_states_with_suffix_predecessor': [9, 7, 6, 4],
        'suffix_states_with_exact_predecessor': [8, 5, 3, 1],
        'suffix_states_with_shared_predecessor': [2],
        'strict_predecessor_uses_same_two_support_sets_plus_boundaries': True,
    }


@lru_cache(maxsize=None)
def strict_predecessor_state_code(state_code: str) -> str | None:
    mode, counter = _parse_state_code(state_code)
    exact_support = set(build_exact_counter_support())
    shared_support = set(build_shared_counter_support())

    if mode == 'S':
        if counter == 10:
            return None
        if counter in shared_support:
            return f'D{counter}'
        if counter in exact_support:
            return f'E{counter}'
        return f'S{counter + 1}'
    if mode == 'E':
        return f'S{counter + 1}'
    if mode == 'D':
        return f'S{counter + 1}'
    if mode == 'T':
        return 'E0'
    raise WeakeningPortfolioServiceModeSuffixPredecessorLawError(f'unknown mode code {mode!r}')


@lru_cache(maxsize=1)
def build_full_automaton_incoming_summary() -> dict[str, Any]:
    codes = build_state_code_chain()
    incoming = {code: [] for code in codes}
    for code in codes:
        predecessor = strict_predecessor_state_code(code)
        if predecessor is not None:
            incoming[code].append(predecessor)
    incoming[TERMINAL_CODE].append(TERMINAL_CODE)
    return {
        'source_has_no_strict_predecessor': incoming[SOURCE_CODE] == [],
        'every_non_source_code_has_unique_strict_predecessor': all(
            len(incoming[code]) == 1
            for code in incoming
            if code != SOURCE_CODE and code != TERMINAL_CODE
        ) and len([edge for edge in incoming[TERMINAL_CODE] if edge != TERMINAL_CODE]) == 1,
        'terminal_full_automaton_incoming_edges': incoming[TERMINAL_CODE],
        'terminal_is_only_code_with_absorbing_self_incoming_edge': all(
            code == TERMINAL_CODE or TERMINAL_CODE not in edges
            for code, edges in incoming.items()
        ),
    }


@lru_cache(maxsize=1)
def build_predecessor_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    archived_rows = build_positive_service_mode_suffix_counter_rows()
    for index, row in enumerate(archived_rows):
        code = row['state_code']
        predicted = strict_predecessor_state_code(code)
        archived_previous = archived_rows[index - 1]['state_code'] if index > 0 else None
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'state_code': code,
                'mode': row['mode'],
                'suffix_only_steps_remaining': row['suffix_only_steps_remaining'],
                'predicted_strict_predecessor_state_code': predicted,
                'archived_chain_previous_state_code': archived_previous,
                'prediction_matches_archived_chain': predicted == archived_previous,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_reverse_generated_chain_from_terminal() -> list[str]:
    chain = [TERMINAL_CODE]
    seen = {TERMINAL_CODE}
    while chain[-1] != SOURCE_CODE:
        predecessor = strict_predecessor_state_code(chain[-1])
        if predecessor is None:
            raise WeakeningPortfolioServiceModeSuffixPredecessorLawError(
                'encountered source before finishing reverse generation'
            )
        chain.append(predecessor)
        if predecessor != SOURCE_CODE and predecessor in seen:
            raise WeakeningPortfolioServiceModeSuffixPredecessorLawError(
                f'cycle encountered before source while generating reverse chain: {predecessor}'
            )
        seen.add(predecessor)
    return chain


@lru_cache(maxsize=1)
def build_reverse_validation_summary() -> dict[str, Any]:
    rows = build_predecessor_rows()
    matches = [row['prediction_matches_archived_chain'] for row in rows]
    reverse_generated = build_reverse_generated_chain_from_terminal()
    archived_forward = build_state_code_chain()
    return {
        'all_rows_match_archived_chain_predecessor': all(matches),
        'matched_row_count': sum(1 for value in matches if value),
        'row_count': len(rows),
        'reverse_generated_chain_matches_archive_when_reversed': list(reversed(reverse_generated)) == archived_forward,
        'reverse_generated_chain_length': len(reverse_generated),
        'reverse_generated_chain_start': reverse_generated[0],
        'reverse_generated_chain_source': reverse_generated[-1],
        'source_is_only_strict_null_predecessor': strict_predecessor_state_code(SOURCE_CODE) is None,
    }


@lru_cache(maxsize=1)
def build_predecessor_rule_summary() -> dict[str, Any]:
    return {
        'suffix_rule': 'for S_k with k < 10: D_k if k in shared support, E_k if k in exact support, otherwise S_{k+1}',
        'bridge_reverse_rule': 'E_k <- S_{k+1}; D_2 <- S_3',
        'source_rule': 'S_10 has no strict predecessor',
        'terminal_rule': 'strict predecessor of T_0 is E_0; full automaton adds absorbing self-edge T_0 <- T_0',
        'strict_predecessor_uses_same_two_support_sets_as_successor': True,
    }


@lru_cache(maxsize=1)
def build_predecessor_examples() -> list[dict[str, Any]]:
    examples = [
        select_service_mode_suffix_counter(0.40),
        select_service_mode_suffix_counter(0.0184),
        select_service_mode_suffix_counter(0.0074),
        select_service_mode_suffix_counter(0.0001),
    ]
    rows_by_code = build_state_code_to_row()
    enriched: list[dict[str, Any]] = []
    for example in examples:
        code = example['state_code']
        predecessor = strict_predecessor_state_code(code)
        previous_row = rows_by_code.get(predecessor) if predecessor is not None else None
        enriched.append(
            {
                'minimum_service_share': example['minimum_service_share'],
                'current_signature': example['current_signature'],
                'state_code': code,
                'predicted_strict_predecessor_state_code': predecessor,
                'predicted_strict_predecessor_signature': previous_row['current_signature'] if previous_row else 'source_boundary',
            }
        )
    enriched.append(
        {
            'minimum_service_share': 0.0,
            'current_signature': 'terminal_absorbing',
            'state_code': TERMINAL_CODE,
            'predicted_strict_predecessor_state_code': strict_predecessor_state_code(TERMINAL_CODE),
            'predicted_strict_predecessor_signature': rows_by_code['E0']['current_signature'],
        }
    )
    return enriched


@lru_cache(maxsize=1)
def build_service_mode_suffix_predecessor_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Turn the recent mode-suffix local code into a closed-form strict predecessor law '
            'so future inheritors can backstep the positive-service weakening staircase from the '
            'same tiny support basis instead of consulting the archived chain table.'
        ),
        'headline_findings': {
            'predecessor_support_summary': build_predecessor_support_summary(),
            'predecessor_rule_summary': build_predecessor_rule_summary(),
            'reverse_validation_summary': build_reverse_validation_summary(),
            'full_automaton_incoming_summary': build_full_automaton_incoming_summary(),
        },
        'decision_rules': [
            'Treat the positive-service local staircase as a reversible path in `(mode, suffix_only_steps_remaining)` coordinates, with only `S10` as the strict source boundary and `T0` as the absorbing terminal boundary.',
            'Backstep any suffix state `S_k` by checking whether `k` lies in shared support, exact support, or neither; the predecessor is `D_k`, `E_k`, or `S_{k+1}` respectively.',
            'Backstep exact and shared bridge states locally as `E_k <- S_{k+1}` and `D_2 <- S_3`, and treat `T_0 <- E_0` as the unique strict terminal entry.',
            'Treat any future archive revision where a non-source code gains multiple strict predecessors, or where the predecessor law needs more than the current exact/shared support sets plus the two boundaries, as a redesign signal.',
        ],
        'positive_service_mode_suffix_predecessor_rows': build_predecessor_rows(),
        'selector_examples': build_predecessor_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_predecessor_law.py',
    }


if __name__ == '__main__':
    import json

    print(json.dumps(build_service_mode_suffix_predecessor_snapshot(), indent=2, sort_keys=True))
