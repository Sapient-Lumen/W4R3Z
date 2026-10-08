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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law import (
    build_positive_service_local_witness_rows,
    select_local_upgrade_witness,
)


class WeakeningPortfolioServiceLocalAxisPersistenceLawError(RuntimeError):
    pass


def _nonterminal_witness_rows() -> list[dict[str, Any]]:
    rows = build_positive_service_local_witness_rows()
    return [row for row in rows if row['next_unlock_kind'] != 'terminal']


@lru_cache(maxsize=1)
def build_axis_run_rows() -> list[dict[str, Any]]:
    rows = _nonterminal_witness_rows()
    if not rows:
        return []

    run_rows: list[dict[str, Any]] = []
    run_start = 0
    while run_start < len(rows):
        unlock_kind = rows[run_start]['next_unlock_kind']
        run_end = run_start
        while run_end + 1 < len(rows) and rows[run_end + 1]['next_unlock_kind'] == unlock_kind:
            run_end += 1

        start_row = rows[run_start]
        end_row = rows[run_end]
        run_rows.append(
            {
                'run_index': len(run_rows),
                'unlock_kind': unlock_kind,
                'start_state_index': start_row['state_index'],
                'end_state_index': end_row['state_index'],
                'run_step_count': run_end - run_start + 1,
                'start_signature': start_row['current_signature'],
                'terminal_signature_after_run': end_row['next_signature_after_relaxation'],
            }
        )
        run_start = run_end + 1

    return run_rows


@lru_cache(maxsize=1)
def build_state_index_to_run_row() -> dict[int, dict[str, Any]]:
    mapping: dict[int, dict[str, Any]] = {}
    for run in build_axis_run_rows():
        for state_index in range(run['start_state_index'], run['end_state_index'] + 1):
            mapping[state_index] = run
    return mapping


def select_local_axis_persistence(minimum_service_share: float) -> dict[str, Any]:
    witness = select_local_upgrade_witness(minimum_service_share)
    current_signature = witness['current_signature']
    state_index = next(
        row['state_index']
        for row in build_positive_service_local_witness_rows()
        if row['current_signature'] == current_signature
    )

    if witness['next_unlock_kind'] == 'terminal':
        return {
            'minimum_service_share': minimum_service_share,
            'state_index': state_index,
            'current_signature': current_signature,
            'next_unlock_kind': 'terminal',
            'persistence_steps_remaining': 0,
            'run_index': None,
            'run_start_signature': current_signature,
            'run_terminal_signature_after_persistence': current_signature,
        }

    run = build_state_index_to_run_row()[state_index]
    persistence_steps_remaining = run['end_state_index'] - state_index + 1
    return {
        'minimum_service_share': minimum_service_share,
        'state_index': state_index,
        'current_signature': current_signature,
        'next_unlock_kind': witness['next_unlock_kind'],
        'persistence_steps_remaining': persistence_steps_remaining,
        'run_index': run['run_index'],
        'run_start_signature': run['start_signature'],
        'run_terminal_signature_after_persistence': run['terminal_signature_after_run'],
    }


@lru_cache(maxsize=1)
def build_positive_service_local_axis_persistence_rows() -> list[dict[str, Any]]:
    terminal_row = next(
        row for row in build_positive_service_local_witness_rows() if row['next_unlock_kind'] == 'terminal'
    )
    rows: list[dict[str, Any]] = []
    for row in build_positive_service_local_witness_rows():
        if row['next_unlock_kind'] == 'terminal':
            rows.append(
                {
                    'state_index': row['state_index'],
                    'probe_target': row['probe_target'],
                    'current_signature': row['current_signature'],
                    'next_unlock_kind': 'terminal',
                    'persistence_steps_remaining': 0,
                    'run_index': None,
                    'run_start_signature': terminal_row['current_signature'],
                    'run_terminal_signature_after_persistence': terminal_row['current_signature'],
                }
            )
            continue

        run = build_state_index_to_run_row()[row['state_index']]
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'next_unlock_kind': row['next_unlock_kind'],
                'persistence_steps_remaining': run['end_state_index'] - row['state_index'] + 1,
                'run_index': run['run_index'],
                'run_start_signature': run['start_signature'],
                'run_terminal_signature_after_persistence': run['terminal_signature_after_run'],
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_run_histogram_by_unlock_kind() -> dict[str, int]:
    histogram = {
        'suffix_only': 0,
        'exact_only': 0,
        'shared_diagonal': 0,
    }
    for row in build_axis_run_rows():
        histogram[row['unlock_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_step_histogram_by_unlock_kind() -> dict[str, int]:
    histogram = {
        'suffix_only': 0,
        'exact_only': 0,
        'shared_diagonal': 0,
        'terminal': 0,
    }
    for row in build_positive_service_local_axis_persistence_rows():
        histogram[row['next_unlock_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_max_persistence_by_unlock_kind() -> dict[str, int]:
    maxima = {
        'suffix_only': 0,
        'exact_only': 0,
        'shared_diagonal': 0,
        'terminal': 0,
    }
    for row in build_positive_service_local_axis_persistence_rows():
        unlock_kind = row['next_unlock_kind']
        maxima[unlock_kind] = max(maxima[unlock_kind], row['persistence_steps_remaining'])
    return maxima


@lru_cache(maxsize=1)
def build_longest_suffix_run_summary() -> dict[str, Any]:
    suffix_runs = [row for row in build_axis_run_rows() if row['unlock_kind'] == 'suffix_only']
    longest = max(suffix_runs, key=lambda row: row['run_step_count'])
    return {
        'run_index': longest['run_index'],
        'run_step_count': longest['run_step_count'],
        'start_signature': longest['start_signature'],
        'terminal_signature_after_run': longest['terminal_signature_after_run'],
    }


@lru_cache(maxsize=1)
def build_exact_run_summary() -> dict[str, Any]:
    exact_runs = [row for row in build_axis_run_rows() if row['unlock_kind'] == 'exact_only']
    singleton = all(row['run_step_count'] == 1 for row in exact_runs)
    return {
        'exact_run_count': len(exact_runs),
        'all_exact_runs_are_singletons': singleton,
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_local_axis_persistence(0.40),
        select_local_axis_persistence(0.20),
        select_local_axis_persistence(0.05),
        select_local_axis_persistence(0.011),
        select_local_axis_persistence(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_local_axis_persistence_snapshot() -> dict[str, Any]:
    exact_summary = build_exact_run_summary()
    longest_suffix = build_longest_suffix_run_summary()
    return {
        'focus': (
            'Compress the local service-relaxation staircase into axis-persistence runs so '
            'future inheritors can see not just which axis unlocks next, but how long that '
            'axis keeps governing repeated relaxations before a different axis takes over.'
        ),
        'headline_findings': {
            'axis_run_count': len(build_axis_run_rows()),
            'run_histogram_by_unlock_kind': build_run_histogram_by_unlock_kind(),
            'step_histogram_by_unlock_kind': build_step_histogram_by_unlock_kind(),
            'max_persistence_by_unlock_kind': build_max_persistence_by_unlock_kind(),
            'all_exact_runs_are_singletons': exact_summary['all_exact_runs_are_singletons'],
            'longest_suffix_run_summary': longest_suffix,
            'shared_diagonal_run_count': build_run_histogram_by_unlock_kind()['shared_diagonal'],
        },
        'decision_rules': [
            'Treat `persistence_steps_remaining` as the local repeated-relaxation horizon for the currently winning axis.',
            'Remember that exact-only leadership is never persistent in the current staircase: every exact run is a singleton.',
            'Expect nontrivial repeated-relaxation persistence only on suffix-only runs, with current maximum length 3 from `E1_S2` through `E1_S5`.',
            'Treat any future exact run longer than one step, or any extra shared-diagonal run, as an immediate redesign signal.',
        ],
        'axis_run_rows': build_axis_run_rows(),
        'positive_service_local_axis_persistence_rows': build_positive_service_local_axis_persistence_rows(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_local_axis_persistence_snapshot(), indent=2, sort_keys=True))
