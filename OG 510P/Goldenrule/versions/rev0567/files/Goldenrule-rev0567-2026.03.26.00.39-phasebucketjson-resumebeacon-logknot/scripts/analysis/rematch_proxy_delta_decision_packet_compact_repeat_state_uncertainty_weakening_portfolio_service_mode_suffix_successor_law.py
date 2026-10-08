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
    build_positive_service_mode_suffix_counter_rows,
    build_state_code_chain,
    build_state_code_to_row,
    select_service_mode_suffix_counter,
)


class WeakeningPortfolioServiceModeSuffixSuccessorLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_exact_counter_support() -> list[int]:
    return [
        row['suffix_only_steps_remaining']
        for row in build_positive_service_mode_suffix_counter_rows()
        if row['mode'] == 'exact_only'
    ]


@lru_cache(maxsize=1)
def build_shared_counter_support() -> list[int]:
    return [
        row['suffix_only_steps_remaining']
        for row in build_positive_service_mode_suffix_counter_rows()
        if row['mode'] == 'shared_diagonal'
    ]


@lru_cache(maxsize=1)
def build_support_basis_summary() -> dict[str, Any]:
    exact_support = build_exact_counter_support()
    shared_support = build_shared_counter_support()
    exact_support_set = set(exact_support)
    shared_support_set = set(shared_support)
    suffix_counters = [
        row['suffix_only_steps_remaining']
        for row in build_positive_service_mode_suffix_counter_rows()
        if row['mode'] == 'suffix_only'
    ]
    stay_suffix_currents: list[int] = []
    handoff_exact_currents: list[int] = []
    handoff_shared_currents: list[int] = []
    for counter in suffix_counters:
        next_counter = counter - 1
        if next_counter in shared_support_set:
            handoff_shared_currents.append(counter)
        elif next_counter in exact_support_set:
            handoff_exact_currents.append(counter)
        else:
            stay_suffix_currents.append(counter)
    return {
        'exact_counter_support': exact_support,
        'shared_counter_support': shared_support,
        'suffix_stay_current_counters': stay_suffix_currents,
        'suffix_exact_handoff_current_counters': handoff_exact_currents,
        'suffix_shared_handoff_current_counters': handoff_shared_currents,
        'bridge_exact_current_counters': [counter for counter in exact_support if counter > 0],
        'terminal_exact_current_counter': [0],
        'bridge_shared_current_counters': shared_support,
    }


def _parse_state_code(state_code: str) -> tuple[str, int]:
    if len(state_code) < 2:
        raise WeakeningPortfolioServiceModeSuffixSuccessorLawError(f'invalid state code {state_code!r}')
    mode = state_code[0]
    try:
        counter = int(state_code[1:])
    except ValueError as exc:
        raise WeakeningPortfolioServiceModeSuffixSuccessorLawError(f'invalid state code {state_code!r}') from exc
    return mode, counter


@lru_cache(maxsize=None)
def successor_state_code(state_code: str) -> str:
    mode, counter = _parse_state_code(state_code)
    exact_support = set(build_exact_counter_support())
    shared_support = set(build_shared_counter_support())

    if mode == 'S':
        if counter <= 0:
            raise WeakeningPortfolioServiceModeSuffixSuccessorLawError('suffix mode must have positive counter')
        next_counter = counter - 1
        if next_counter in shared_support:
            return f'D{next_counter}'
        if next_counter in exact_support:
            return f'E{next_counter}'
        return f'S{next_counter}'
    if mode == 'E':
        return 'T0' if counter == 0 else f'S{counter}'
    if mode == 'D':
        return f'S{counter}'
    if mode == 'T':
        return 'T0'
    raise WeakeningPortfolioServiceModeSuffixSuccessorLawError(f'unknown mode code {mode!r}')


@lru_cache(maxsize=1)
def build_successor_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    archived_rows = build_positive_service_mode_suffix_counter_rows()
    for row in archived_rows:
        code = row['state_code']
        predicted = successor_state_code(code)
        archived_next = row['next_state_code'] if row['next_state_code'] is not None else 'T0'
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'state_code': code,
                'mode': row['mode'],
                'suffix_only_steps_remaining': row['suffix_only_steps_remaining'],
                'predicted_next_state_code': predicted,
                'archived_chain_next_state_code': archived_next,
                'prediction_matches_archived_chain': predicted == archived_next,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_successor_rule_summary() -> dict[str, Any]:
    support = build_support_basis_summary()
    return {
        'suffix_dispatch_rule': (
            'dispatch by next counter: shared support -> D_{k-1}, '
            'exact support -> E_{k-1}, otherwise S_{k-1}'
        ),
        'exact_bridge_rule': 'E_k -> S_k for k > 0; E_0 -> T_0',
        'shared_bridge_rule': 'D_2 -> S_2',
        'terminal_rule': 'T_0 -> T_0',
        'support_basis_size': len(support['exact_counter_support']) + len(support['shared_counter_support']),
        'closed_form_successor_needs_only_two_support_sets': True,
    }


@lru_cache(maxsize=1)
def build_generated_chain_from_start() -> list[str]:
    chain = ['S10']
    seen = {'S10'}
    while chain[-1] != 'T0':
        nxt = successor_state_code(chain[-1])
        chain.append(nxt)
        if nxt != 'T0' and nxt in seen:
            raise WeakeningPortfolioServiceModeSuffixSuccessorLawError(
                f'cycle encountered before terminal while generating chain: {nxt}'
            )
        seen.add(nxt)
    return chain


@lru_cache(maxsize=1)
def build_automaton_validation_summary() -> dict[str, Any]:
    rows = build_successor_rows()
    matches = [row['prediction_matches_archived_chain'] for row in rows]
    generated_chain = build_generated_chain_from_start()
    archived_chain = build_state_code_chain()
    return {
        'all_rows_match_archived_chain_successor': all(matches),
        'matched_row_count': sum(1 for value in matches if value),
        'row_count': len(rows),
        'generated_chain_matches_archived_chain': generated_chain == archived_chain,
        'generated_chain_length': len(generated_chain),
        'generated_chain_start': generated_chain[0],
        'generated_chain_terminal': generated_chain[-1],
        'terminal_is_absorbing_under_closed_form': successor_state_code('T0') == 'T0',
    }


@lru_cache(maxsize=1)
def build_successor_examples() -> list[dict[str, Any]]:
    examples = [
        select_service_mode_suffix_counter(0.40),
        select_service_mode_suffix_counter(0.05),
        select_service_mode_suffix_counter(0.0184),
        select_service_mode_suffix_counter(0.0074),
        select_service_mode_suffix_counter(0.0001),
    ]
    rows_by_code = build_state_code_to_row()
    enriched: list[dict[str, Any]] = []
    for example in examples:
        code = example['state_code']
        predicted_next = successor_state_code(code)
        next_row = rows_by_code.get(predicted_next)
        enriched.append(
            {
                'minimum_service_share': example['minimum_service_share'],
                'current_signature': example['current_signature'],
                'state_code': code,
                'predicted_next_state_code': predicted_next,
                'predicted_next_signature': next_row['current_signature'] if next_row else 'terminal_absorbing',
            }
        )
    return enriched


@lru_cache(maxsize=1)
def build_service_mode_suffix_successor_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Turn the recent mode-suffix local code into a closed-form successor automaton '
            'so future inheritors can step the entire positive-service weakening staircase '
            'from two small support sets instead of consulting any external chain table.'
        ),
        'headline_findings': {
            'support_basis_summary': build_support_basis_summary(),
            'successor_rule_summary': build_successor_rule_summary(),
            'automaton_validation_summary': build_automaton_validation_summary(),
            'generated_chain_from_start': build_generated_chain_from_start(),
        },
        'decision_rules': [
            'Treat the positive-service local weakening successor as a closed-form automaton over `(mode, suffix_only_steps_remaining)`.',
            'Dispatch every suffix state `S_k` by the support of the next counter `k-1`: shared support gives `D_{k-1}`, exact support gives `E_{k-1}`, and all remaining counters stay suffix as `S_{k-1}`.',
            'Treat exact and shared modes as bridge states: `E_k -> S_k` for `k > 0`, `E_0 -> T_0`, and `D_2 -> S_2`.',
            'Treat any future archive revision where the successor law needs more than the current exact/shared counter supports, or where the generated chain from `S10` no longer matches the archived chain, as a redesign signal.',
        ],
        'positive_service_mode_suffix_successor_rows': build_successor_rows(),
        'selector_examples': build_successor_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_successor_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_successor_snapshot(), indent=2, sort_keys=True))
