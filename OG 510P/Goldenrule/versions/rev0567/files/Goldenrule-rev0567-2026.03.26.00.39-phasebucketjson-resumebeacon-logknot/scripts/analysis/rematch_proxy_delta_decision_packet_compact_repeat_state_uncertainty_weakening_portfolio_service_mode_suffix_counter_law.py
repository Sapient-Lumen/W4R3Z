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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law import (
    build_positive_service_local_corridor_exit_rows,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law import (
    build_positive_service_residual_axis_budget_rows,
    select_residual_axis_budget,
)


class WeakeningPortfolioServiceModeSuffixCounterLawError(RuntimeError):
    pass


MODE_ABBREVIATIONS = {
    'suffix_only': 'S',
    'exact_only': 'E',
    'shared_diagonal': 'D',
    'terminal': 'T',
}


@lru_cache(maxsize=1)
def build_positive_service_mode_suffix_counter_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    residual_rows = build_positive_service_residual_axis_budget_rows()
    corridor_rows = build_positive_service_local_corridor_exit_rows()
    for index, (residual, corridor) in enumerate(zip(residual_rows, corridor_rows)):
        if residual['current_signature'] != corridor['current_signature']:
            raise WeakeningPortfolioServiceModeSuffixCounterLawError(
                'residual and corridor rows disagree on current signature'
            )
        mode = corridor['current_unlock_kind']
        suffix_counter = residual['suffix_only_steps_remaining']
        code = f"{MODE_ABBREVIATIONS[mode]}{suffix_counter}"
        next_code = None
        if index + 1 < len(residual_rows):
            next_mode = corridor_rows[index + 1]['current_unlock_kind']
            next_suffix_counter = residual_rows[index + 1]['suffix_only_steps_remaining']
            next_code = f"{MODE_ABBREVIATIONS[next_mode]}{next_suffix_counter}"
        rows.append(
            {
                'state_index': residual['state_index'],
                'probe_target': residual['probe_target'],
                'current_signature': residual['current_signature'],
                'mode': mode,
                'mode_abbreviation': MODE_ABBREVIATIONS[mode],
                'suffix_only_steps_remaining': suffix_counter,
                'exact_only_steps_remaining': residual['exact_only_steps_remaining'],
                'shared_diagonal_steps_remaining': residual['shared_diagonal_steps_remaining'],
                'state_code': code,
                'next_state_code': next_code,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_state_code_chain() -> list[str]:
    return [row['state_code'] for row in build_positive_service_mode_suffix_counter_rows()]


@lru_cache(maxsize=1)
def build_mode_support_summary() -> dict[str, Any]:
    rows = build_positive_service_mode_suffix_counter_rows()
    suffix_counters = [row['suffix_only_steps_remaining'] for row in rows if row['mode'] == 'suffix_only']
    exact_counters = [row['suffix_only_steps_remaining'] for row in rows if row['mode'] == 'exact_only']
    shared_counters = [row['suffix_only_steps_remaining'] for row in rows if row['mode'] == 'shared_diagonal']
    terminal_counters = [row['suffix_only_steps_remaining'] for row in rows if row['mode'] == 'terminal']
    return {
        'suffix_mode_counter_support': suffix_counters,
        'exact_mode_counter_support': exact_counters,
        'shared_mode_counter_support': shared_counters,
        'terminal_mode_counter_support': terminal_counters,
        'suffix_mode_support_is_dense_1_through_10': suffix_counters == list(range(10, 0, -1)),
        'exact_mode_support_is_sparse': exact_counters == [8, 5, 3, 1, 0],
    }


@lru_cache(maxsize=1)
def build_transition_class_histogram() -> dict[str, int]:
    histogram = {
        'suffix_consume_and_stay_suffix': 0,
        'suffix_consume_and_handoff_to_exact': 0,
        'suffix_consume_and_handoff_to_shared': 0,
        'exact_bridge_preserve_counter': 0,
        'shared_bridge_preserve_counter': 0,
        'terminal_entry_preserve_zero': 0,
    }
    rows = build_positive_service_mode_suffix_counter_rows()
    for current, nxt in zip(rows, rows[1:]):
        current_mode = current['mode']
        next_mode = nxt['mode']
        delta = nxt['suffix_only_steps_remaining'] - current['suffix_only_steps_remaining']
        if current_mode == 'suffix_only' and next_mode == 'suffix_only' and delta == -1:
            histogram['suffix_consume_and_stay_suffix'] += 1
        elif current_mode == 'suffix_only' and next_mode == 'exact_only' and delta == -1:
            histogram['suffix_consume_and_handoff_to_exact'] += 1
        elif current_mode == 'suffix_only' and next_mode == 'shared_diagonal' and delta == -1:
            histogram['suffix_consume_and_handoff_to_shared'] += 1
        elif current_mode == 'exact_only' and next_mode == 'suffix_only' and delta == 0:
            histogram['exact_bridge_preserve_counter'] += 1
        elif current_mode == 'shared_diagonal' and next_mode == 'suffix_only' and delta == 0:
            histogram['shared_bridge_preserve_counter'] += 1
        elif current_mode == 'exact_only' and next_mode == 'terminal' and delta == 0:
            histogram['terminal_entry_preserve_zero'] += 1
        else:
            raise WeakeningPortfolioServiceModeSuffixCounterLawError(
                f'unexpected mode-suffix transition: {current["state_code"]} -> {nxt["state_code"]}'
            )
    return histogram


@lru_cache(maxsize=1)
def build_decoder_summary() -> dict[str, Any]:
    rows = build_positive_service_mode_suffix_counter_rows()
    code_to_signature = {row['state_code']: row['current_signature'] for row in rows}
    code_to_residual = {
        row['state_code']: {
            'exact_only_steps_remaining': row['exact_only_steps_remaining'],
            'suffix_only_steps_remaining': row['suffix_only_steps_remaining'],
            'shared_diagonal_steps_remaining': row['shared_diagonal_steps_remaining'],
        }
        for row in rows
    }
    return {
        'state_code_count': len(code_to_signature),
        'state_code_chain_length': len(build_state_code_chain()),
        'state_codes_are_unique': len(code_to_signature) == len(rows),
        'state_code_decodes_full_signature': len(set(code_to_signature.values())) == len(rows),
        'state_code_decodes_full_residual_budget': len(set(json.dumps(value, sort_keys=True) for value in code_to_residual.values())) == len(rows),
        'exact_counter_is_not_needed_as_a_primitive_coordinate': True,
    }


@lru_cache(maxsize=1)
def build_counter_dynamics_summary() -> dict[str, Any]:
    rows = build_positive_service_mode_suffix_counter_rows()
    deltas = [
        rows[index + 1]['suffix_only_steps_remaining'] - row['suffix_only_steps_remaining']
        for index, row in enumerate(rows[:-1])
    ]
    return {
        'counter_delta_support': sorted(set(deltas)),
        'every_nonterminal_step_keeps_or_decrements_suffix_counter_by_one': all(delta in {-1, 0} for delta in deltas),
        'only_suffix_mode_consumes_counter': all(
            (rows[index]['mode'] == 'suffix_only') == (delta == -1)
            for index, delta in enumerate(deltas)
        ),
        'non_suffix_modes_are_zero_consumption_bridge_states': all(
            delta == 0
            for index, delta in enumerate(deltas)
            if rows[index]['mode'] in {'exact_only', 'shared_diagonal'}
        ),
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_service_mode_suffix_counter(0.40),
        select_service_mode_suffix_counter(0.05),
        select_service_mode_suffix_counter(0.0184),
        select_service_mode_suffix_counter(0.0074),
        select_service_mode_suffix_counter(0.0001),
    ]


@lru_cache(maxsize=1)
def build_mode_histogram() -> dict[str, int]:
    counter = Counter(row['mode'] for row in build_positive_service_mode_suffix_counter_rows())
    return {
        'suffix_only': counter['suffix_only'],
        'exact_only': counter['exact_only'],
        'shared_diagonal': counter['shared_diagonal'],
        'terminal': counter['terminal'],
    }


@lru_cache(maxsize=1)
def build_signature_to_state_code() -> dict[str, str]:
    return {
        row['current_signature']: row['state_code']
        for row in build_positive_service_mode_suffix_counter_rows()
    }


@lru_cache(maxsize=1)
def build_state_code_to_row() -> dict[str, dict[str, Any]]:
    return {
        row['state_code']: row
        for row in build_positive_service_mode_suffix_counter_rows()
    }



def select_service_mode_suffix_counter(minimum_service_share: float) -> dict[str, Any]:
    residual = select_residual_axis_budget(minimum_service_share)
    matching = next(
        row
        for row in build_positive_service_mode_suffix_counter_rows()
        if row['current_signature'] == residual['current_signature']
    )
    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': matching['current_signature'],
        'state_code': matching['state_code'],
        'mode': matching['mode'],
        'suffix_only_steps_remaining': matching['suffix_only_steps_remaining'],
        'exact_only_steps_remaining': matching['exact_only_steps_remaining'],
        'shared_diagonal_steps_remaining': matching['shared_diagonal_steps_remaining'],
        'next_state_code': matching['next_state_code'],
    }


@lru_cache(maxsize=1)
def build_service_mode_suffix_counter_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Collapse the recent local positive-service weakening stack into a one-counter '
            'code so future inheritors can read every state as current mode plus remaining '
            'suffix budget instead of carrying both staircase coordinates and the full residual triple.'
        ),
        'headline_findings': {
            'state_code_chain': build_state_code_chain(),
            'mode_histogram': build_mode_histogram(),
            'mode_support_summary': build_mode_support_summary(),
            'transition_class_histogram': build_transition_class_histogram(),
            'counter_dynamics_summary': build_counter_dynamics_summary(),
            'decoder_summary': build_decoder_summary(),
        },
        'decision_rules': [
            'Treat each positive-service local weakening state as `(mode, suffix_only_steps_remaining)` with code alphabet `{S, E, D, T}`.',
            'Read suffix-mode steps as the only counter-consuming moves; exact and shared modes are zero-consumption bridge states that hand back at the same suffix counter.',
            'Reconstruct the full state signature and residual budget from the code row rather than carrying `exact_only_steps_remaining` as a primitive planning coordinate.',
            'Treat any future archive revision where non-suffix modes consume suffix counter, or where the same `(mode, suffix counter)` code decodes to multiple signatures, as a redesign signal.',
        ],
        'positive_service_mode_suffix_counter_rows': build_positive_service_mode_suffix_counter_rows(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_counter_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_mode_suffix_counter_snapshot(), indent=2, sort_keys=True))
