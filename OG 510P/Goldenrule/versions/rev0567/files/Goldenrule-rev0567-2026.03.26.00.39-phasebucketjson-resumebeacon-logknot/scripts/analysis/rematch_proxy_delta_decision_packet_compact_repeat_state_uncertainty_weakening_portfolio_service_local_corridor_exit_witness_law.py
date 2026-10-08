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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law import (
    build_axis_run_rows,
    build_positive_service_local_axis_persistence_rows,
    select_local_axis_persistence,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law import (
    build_positive_service_local_witness_rows,
)


class WeakeningPortfolioServiceLocalCorridorExitWitnessLawError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_signature_to_local_witness_row() -> dict[str, dict[str, Any]]:
    return {
        row['current_signature']: row
        for row in build_positive_service_local_witness_rows()
    }


@lru_cache(maxsize=1)
def build_signature_to_local_axis_persistence_row() -> dict[str, dict[str, Any]]:
    return {
        row['current_signature']: row
        for row in build_positive_service_local_axis_persistence_rows()
    }



def _classify_boundary_transition(current_unlock_kind: str, boundary_unlock_kind: str) -> str:
    if current_unlock_kind == 'terminal':
        return 'terminal'
    if boundary_unlock_kind == 'terminal':
        return 'terminal_entry'
    if current_unlock_kind == 'suffix_only' and boundary_unlock_kind == 'exact_only':
        return 'suffix_to_exact_bridge'
    if current_unlock_kind == 'exact_only' and boundary_unlock_kind == 'suffix_only':
        return 'exact_to_suffix_bridge'
    if current_unlock_kind == 'suffix_only' and boundary_unlock_kind == 'shared_diagonal':
        return 'suffix_to_shared_kink'
    if current_unlock_kind == 'shared_diagonal' and boundary_unlock_kind == 'suffix_only':
        return 'shared_to_suffix_kink'
    raise WeakeningPortfolioServiceLocalCorridorExitWitnessLawError(
        'unexpected corridor exit transition '
        f'{current_unlock_kind!r} -> {boundary_unlock_kind!r}'
    )



def select_local_corridor_exit_witness(minimum_service_share: float) -> dict[str, Any]:
    persistence = select_local_axis_persistence(minimum_service_share)
    current_signature = persistence['current_signature']
    current_row = build_signature_to_local_axis_persistence_row()[current_signature]
    current_unlock_kind = current_row['next_unlock_kind']

    if current_unlock_kind == 'terminal':
        return {
            'minimum_service_share': minimum_service_share,
            'current_signature': current_signature,
            'current_unlock_kind': 'terminal',
            'current_corridor_steps_remaining': 0,
            'current_corridor_terminal_signature': current_signature,
            'boundary_unlock_kind': 'terminal',
            'boundary_next_signature_after_relaxation': None,
            'boundary_transition_kind': 'terminal',
            'next_corridor_steps': 0,
            'next_corridor_unlock_kind': 'terminal',
        }

    corridor_terminal_signature = current_row['run_terminal_signature_after_persistence']
    boundary_row = build_signature_to_local_witness_row()[corridor_terminal_signature]
    boundary_unlock_kind = boundary_row['next_unlock_kind']
    boundary_next_signature = boundary_row['next_signature_after_relaxation']
    boundary_transition_kind = _classify_boundary_transition(
        current_unlock_kind,
        boundary_unlock_kind,
    )

    if boundary_next_signature is None:
        next_corridor_steps = 0
        next_corridor_unlock_kind = 'terminal'
    else:
        next_corridor_row = build_signature_to_local_axis_persistence_row()[corridor_terminal_signature]
        next_corridor_steps = next_corridor_row['persistence_steps_remaining']
        next_corridor_unlock_kind = next_corridor_row['next_unlock_kind']

    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': current_signature,
        'current_unlock_kind': current_unlock_kind,
        'current_corridor_steps_remaining': current_row['persistence_steps_remaining'],
        'current_corridor_terminal_signature': corridor_terminal_signature,
        'boundary_unlock_kind': boundary_unlock_kind,
        'boundary_next_signature_after_relaxation': boundary_next_signature,
        'boundary_transition_kind': boundary_transition_kind,
        'next_corridor_steps': next_corridor_steps,
        'next_corridor_unlock_kind': next_corridor_unlock_kind,
    }


@lru_cache(maxsize=1)
def build_positive_service_local_corridor_exit_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_positive_service_local_axis_persistence_rows():
        selected = select_local_corridor_exit_witness(row['probe_target'])
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                **selected,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_run_boundary_transition_histogram() -> dict[str, int]:
    histogram = {
        'suffix_to_exact_bridge': 0,
        'exact_to_suffix_bridge': 0,
        'suffix_to_shared_kink': 0,
        'shared_to_suffix_kink': 0,
        'terminal_entry': 0,
    }
    rows_by_signature = {row['current_signature']: row for row in build_positive_service_local_corridor_exit_rows()}
    for run in build_axis_run_rows():
        row = rows_by_signature[run['start_signature']]
        histogram[row['boundary_transition_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_boundary_transition_histogram() -> dict[str, int]:
    histogram = {
        'suffix_to_exact_bridge': 0,
        'exact_to_suffix_bridge': 0,
        'suffix_to_shared_kink': 0,
        'shared_to_suffix_kink': 0,
        'terminal_entry': 0,
        'terminal': 0,
    }
    for row in build_positive_service_local_corridor_exit_rows():
        histogram[row['boundary_transition_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_bridge_summary() -> dict[str, Any]:
    rows = build_positive_service_local_corridor_exit_rows()
    suffix_bridge_states = [
        row['current_signature']
        for row in rows
        if row['boundary_transition_kind'] == 'suffix_to_exact_bridge'
    ]
    exact_bridge_states = [
        row['current_signature']
        for row in rows
        if row['boundary_transition_kind'] == 'exact_to_suffix_bridge'
    ]
    return {
        'suffix_corridors_that_end_in_exact_bridges': len(suffix_bridge_states),
        'exact_spikes_that_hand_back_to_suffix': len(exact_bridge_states),
        'last_exact_bridge_signature_before_terminal': exact_bridge_states[-1],
    }


@lru_cache(maxsize=1)
def build_kink_summary() -> dict[str, Any]:
    rows = build_positive_service_local_corridor_exit_rows()
    suffix_to_shared = [
        row for row in rows if row['boundary_transition_kind'] == 'suffix_to_shared_kink'
    ]
    shared_to_suffix = [
        row for row in rows if row['boundary_transition_kind'] == 'shared_to_suffix_kink'
    ]
    return {
        'suffix_to_shared_kink_count': len(suffix_to_shared),
        'suffix_to_shared_kink_signature': suffix_to_shared[0]['current_corridor_terminal_signature'],
        'shared_to_suffix_kink_count': len(shared_to_suffix),
        'shared_to_suffix_kink_signature': shared_to_suffix[0]['current_signature'],
    }


@lru_cache(maxsize=1)
def build_corridor_exit_consistency_summary() -> dict[str, Any]:
    rows = build_positive_service_local_corridor_exit_rows()
    nonterminal = [row for row in rows if row['current_unlock_kind'] != 'terminal']
    return {
        'every_nonterminal_corridor_has_a_boundary_witness': all(
            row['boundary_unlock_kind'] in {'exact_only', 'suffix_only', 'shared_diagonal', 'terminal'}
            for row in nonterminal
        ),
        'exact_only_corridors_never_transition_directly_to_exact_only_or_shared_diagonal': all(
            row['boundary_unlock_kind'] in {'suffix_only', 'terminal'}
            for row in nonterminal
            if row['current_unlock_kind'] == 'exact_only'
        ),
        'shared_diagonal_is_a_single_step_bridge_back_to_suffix': [
            row['boundary_transition_kind']
            for row in rows
            if row['current_unlock_kind'] == 'shared_diagonal'
        ] == ['shared_to_suffix_kink'],
        'longer_than_one_step_next_corridor_exists_only_for_suffix': all(
            row['next_corridor_unlock_kind'] == 'suffix_only'
            for row in nonterminal
            if row['next_corridor_steps'] > 1
        ),
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_local_corridor_exit_witness(0.40),
        select_local_corridor_exit_witness(0.20),
        select_local_corridor_exit_witness(0.05),
        select_local_corridor_exit_witness(0.011),
        select_local_corridor_exit_witness(0.01),
        select_local_corridor_exit_witness(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_local_corridor_exit_witness_snapshot() -> dict[str, Any]:
    return {
        'focus': (
            'Compress the recent local service staircase stack into a nearest-boundary '
            'card so future inheritors can answer, from any current SLA target, how '
            'long the present corridor lasts and which corridor takes over after it ends.'
        ),
        'headline_findings': {
            'boundary_transition_histogram': build_boundary_transition_histogram(),
            'run_boundary_transition_histogram': build_run_boundary_transition_histogram(),
            'bridge_summary': build_bridge_summary(),
            'kink_summary': build_kink_summary(),
            'corridor_exit_consistency_summary': build_corridor_exit_consistency_summary(),
        },
        'decision_rules': [
            'Plan the next local service relaxation in two stages: current corridor steps remaining, then boundary unlock kind after that corridor ends.',
            'Treat `suffix_to_exact_bridge` as the default pre- and post-diagonal handoff motif, and `exact_to_suffix_bridge` as the return motif from exact singleton spikes.',
            'Treat `suffix_to_shared_kink` and `shared_to_suffix_kink` as the unique diagonal neighborhood; any extra kink transitions in future archive revisions are redesign signals.',
            'Treat any future exact-only corridor that hands off anywhere except suffix or terminal, or any future multi-step next corridor that is not suffix-only, as a redesign alarm.',
        ],
        'positive_service_local_corridor_exit_rows': build_positive_service_local_corridor_exit_rows(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_local_corridor_exit_witness_snapshot(), indent=2, sort_keys=True))
