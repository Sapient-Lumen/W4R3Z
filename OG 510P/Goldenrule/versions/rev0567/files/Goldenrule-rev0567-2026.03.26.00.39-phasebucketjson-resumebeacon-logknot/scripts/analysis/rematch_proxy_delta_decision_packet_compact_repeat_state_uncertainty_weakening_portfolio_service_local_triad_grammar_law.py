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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law import (
    build_axis_run_rows,
    build_positive_service_local_axis_persistence_rows,
    select_local_axis_persistence,
)


class WeakeningPortfolioServiceLocalTriadGrammarLawError(RuntimeError):
    pass


TRIAD_ABBREVIATIONS = {
    'suffix_only': 'S',
    'exact_only': 'E',
    'shared_diagonal': 'D',
    'terminal': 'T',
}


TRIAD_FAMILY_BY_KINDS = {
    ('suffix_only', 'exact_only', 'suffix_only'): 'alternating_bridge_core',
    ('exact_only', 'suffix_only', 'exact_only'): 'alternating_bridge_core',
    ('exact_only', 'suffix_only', 'shared_diagonal'): 'diagonal_neighborhood',
    ('suffix_only', 'shared_diagonal', 'suffix_only'): 'diagonal_neighborhood',
    ('shared_diagonal', 'suffix_only', 'exact_only'): 'diagonal_neighborhood',
    ('suffix_only', 'exact_only', 'terminal'): 'terminal_tail',
    ('exact_only', 'terminal', 'terminal'): 'terminal_tail',
    ('terminal', 'terminal', 'terminal'): 'terminal',
}


TRIAD_SHARED_VISIBILITY_DEPTH = {
    0: 'current',
    1: 'next',
    2: 'second_next',
}


@lru_cache(maxsize=1)
def build_signature_to_local_triad_row() -> dict[str, dict[str, Any]]:
    return {
        row['current_signature']: row
        for row in build_positive_service_local_triad_rows()
    }



def _corridor_triad_kinds_from_run_index(run_index: int | None) -> tuple[str, str, str]:
    if run_index is None:
        return ('terminal', 'terminal', 'terminal')

    run_rows = build_axis_run_rows()
    triad: list[str] = [run_rows[run_index]['unlock_kind']]
    for offset in (1, 2):
        triad.append(
            run_rows[run_index + offset]['unlock_kind']
            if run_index + offset < len(run_rows)
            else 'terminal'
        )
    return tuple(triad)



def _triad_signature(kinds: tuple[str, str, str]) -> str:
    return '-'.join(TRIAD_ABBREVIATIONS[kind] for kind in kinds)



def _triad_family(kinds: tuple[str, str, str]) -> str:
    try:
        return TRIAD_FAMILY_BY_KINDS[kinds]
    except KeyError as exc:
        raise WeakeningPortfolioServiceLocalTriadGrammarLawError(
            f'unexpected corridor triad kinds: {kinds!r}'
        ) from exc



def _shared_visibility_depth(kinds: tuple[str, str, str]) -> str | None:
    for index, kind in enumerate(kinds):
        if kind == 'shared_diagonal':
            return TRIAD_SHARED_VISIBILITY_DEPTH[index]
    return None



def select_local_corridor_triad(minimum_service_share: float) -> dict[str, Any]:
    persistence = select_local_axis_persistence(minimum_service_share)
    current_signature = persistence['current_signature']
    row = build_signature_to_local_triad_row()[current_signature]
    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': current_signature,
        'state_index': row['state_index'],
        'corridor_triad_signature': row['corridor_triad_signature'],
        'current_corridor_kind': row['current_corridor_kind'],
        'next_corridor_kind': row['next_corridor_kind'],
        'second_next_corridor_kind': row['second_next_corridor_kind'],
        'triad_family': row['triad_family'],
        'shared_visibility_depth': row['shared_visibility_depth'],
    }


@lru_cache(maxsize=1)
def build_positive_service_local_triad_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_positive_service_local_axis_persistence_rows():
        kinds = _corridor_triad_kinds_from_run_index(row['run_index'])
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'corridor_triad_signature': _triad_signature(kinds),
                'current_corridor_kind': kinds[0],
                'next_corridor_kind': kinds[1],
                'second_next_corridor_kind': kinds[2],
                'triad_family': _triad_family(kinds),
                'shared_visibility_depth': _shared_visibility_depth(kinds),
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_triad_histogram() -> dict[str, int]:
    counter = Counter(row['corridor_triad_signature'] for row in build_positive_service_local_triad_rows())
    ordered = ['S-E-S', 'E-S-E', 'E-S-D', 'S-D-S', 'D-S-E', 'S-E-T', 'E-T-T', 'T-T-T']
    return {key: counter.get(key, 0) for key in ordered}


@lru_cache(maxsize=1)
def build_triad_family_histogram() -> dict[str, int]:
    counter = Counter(row['triad_family'] for row in build_positive_service_local_triad_rows())
    ordered = ['alternating_bridge_core', 'diagonal_neighborhood', 'terminal_tail', 'terminal']
    return {key: counter.get(key, 0) for key in ordered}


@lru_cache(maxsize=1)
def build_shared_visibility_summary() -> dict[str, Any]:
    rows = build_positive_service_local_triad_rows()
    by_depth: dict[str, list[str]] = {'current': [], 'next': [], 'second_next': []}
    for row in rows:
        depth = row['shared_visibility_depth']
        if depth is not None:
            by_depth[depth].append(row['current_signature'])
    return {
        'shared_visible_current_count': len(by_depth['current']),
        'shared_visible_next_count': len(by_depth['next']),
        'shared_visible_second_next_count': len(by_depth['second_next']),
        'shared_visible_current_signatures': by_depth['current'],
        'shared_visible_next_signatures': by_depth['next'],
        'shared_visible_second_next_signatures': by_depth['second_next'],
    }


@lru_cache(maxsize=1)
def build_triad_consistency_summary() -> dict[str, Any]:
    rows = build_positive_service_local_triad_rows()
    nonterminal_rows = [row for row in rows if row['triad_family'] != 'terminal']
    alternating = [row for row in rows if row['triad_family'] == 'alternating_bridge_core']
    return {
        'triad_support_count': len(build_triad_histogram()),
        'every_nonterminal_triad_begins_with_its_current_corridor_kind': all(
            row['corridor_triad_signature'].split('-')[0] == TRIAD_ABBREVIATIONS[row['current_corridor_kind']]
            for row in nonterminal_rows
        ),
        'shared_diagonal_is_visible_at_exactly_one_local_horizon_depth_per_state': all(
            row['corridor_triad_signature'].count('D') <= 1
            for row in rows
        ),
        'alternating_bridge_core_uses_only_s_e_symbols': all(
            set(row['corridor_triad_signature'].split('-')) <= {'S', 'E'}
            for row in alternating
        ),
        'only_terminal_tail_or_terminal_triads_contain_t': all(
            ('T' in row['corridor_triad_signature']) == (row['triad_family'] in {'terminal_tail', 'terminal'})
            for row in rows
        ),
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_local_corridor_triad(0.40),
        select_local_corridor_triad(0.05),
        select_local_corridor_triad(0.0348),
        select_local_corridor_triad(0.0184),
        select_local_corridor_triad(0.0074),
        select_local_corridor_triad(0.0014),
        select_local_corridor_triad(0.00046),
        select_local_corridor_triad(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_local_triad_grammar_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Compress the recent local service boundary stack into a three-corridor '
            'lookahead grammar so future inheritors can recognize ordinary alternation, '
            'the unique diagonal neighborhood, and the terminal tail from one tiny local card.'
        ),
        'headline_findings': {
            'triad_histogram': build_triad_histogram(),
            'triad_family_histogram': build_triad_family_histogram(),
            'shared_visibility_summary': build_shared_visibility_summary(),
            'triad_consistency_summary': build_triad_consistency_summary(),
        },
        'decision_rules': [
            'Treat `S-E-S` and `E-S-E` as the ordinary alternating bridge core; together they cover the default local service geometry away from the diagonal and terminal tail.',
            'Treat `E-S-D`, `S-D-S`, and `D-S-E` as the entire audited diagonal neighborhood; any future extra triad with `D` is a redesign signal.',
            'Use `shared_visibility_depth` as a tiny proximity witness for the diagonal: it can be only `second_next`, `next`, `current`, or absent.',
            'Treat `S-E-T` and `E-T-T` as the only terminal-tail motifs; any future `T` inside an ordinary or diagonal triad is a redesign alarm.',
        ],
        'positive_service_local_triad_rows': build_positive_service_local_triad_rows(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_triad_grammar_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_local_triad_grammar_snapshot(), indent=2, sort_keys=True))
