#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law import (
    select_upgrade_schedule_by_minimum_service_share,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_positive_service_staircase_states,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law import (
    build_profile_threshold_ladders,
)


class WeakeningPortfolioServiceLocalUpgradeWitnessLawError(RuntimeError):
    pass


MAX_EXACT_HORIZON = 6
MAX_SUFFIX_HORIZON = 11


@lru_cache(maxsize=1)
def build_threshold_ladder_by_profile_and_width() -> dict[str, dict[int, dict[str, Any]]]:
    ladder_by_profile: dict[str, dict[int, dict[str, Any]]] = {
        'exact_only': {},
        'suffix_hitchhike_only': {},
    }
    for profile_label, rows in build_profile_threshold_ladders().items():
        for row in rows:
            ladder_by_profile[profile_label][row['portfolio_size']] = row
    return ladder_by_profile



def _signature(exact_horizon: int, suffix_horizon: int) -> str:
    return f'E{exact_horizon}_S{suffix_horizon}'



def _next_threshold_row(profile_label: str, next_width: int | None) -> dict[str, Any] | None:
    if next_width is None:
        return None
    return build_threshold_ladder_by_profile_and_width()[profile_label].get(next_width)



def _format_threshold_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        'profile_label': row['profile_label'],
        'portfolio_size': row['portfolio_size'],
        'threshold_numerator': row['threshold_numerator'],
        'threshold_denominator': row['threshold_denominator'],
        'threshold_value': row['threshold_value'],
    }



def select_local_upgrade_witness(minimum_service_share: float) -> dict[str, Any]:
    if minimum_service_share < 0.0 or minimum_service_share > 1.0:
        raise WeakeningPortfolioServiceLocalUpgradeWitnessLawError(
            f'minimum service share must lie in [0, 1], received {minimum_service_share}'
        )

    schedule = select_upgrade_schedule_by_minimum_service_share(minimum_service_share)
    exact_horizon = schedule['exact_only_support_horizon']
    suffix_horizon = schedule['suffix_hitchhike_only_support_horizon']

    exact_next_width = exact_horizon + 1 if exact_horizon < MAX_EXACT_HORIZON else None
    suffix_next_width = suffix_horizon + 1 if suffix_horizon < MAX_SUFFIX_HORIZON else None
    exact_next_row = _next_threshold_row('exact_only', exact_next_width)
    suffix_next_row = _next_threshold_row('suffix_hitchhike_only', suffix_next_width)

    exact_next_value = None if exact_next_row is None else exact_next_row['threshold_value']
    suffix_next_value = None if suffix_next_row is None else suffix_next_row['threshold_value']

    if exact_next_value is None and suffix_next_value is None:
        next_unlock_kind = 'terminal'
        next_unlock_threshold_value = None
        next_unlock_threshold_fraction = None
        next_signature = None
    elif exact_next_value is None:
        next_unlock_kind = 'suffix_only'
        next_unlock_threshold_value = suffix_next_value
        next_unlock_threshold_fraction = (
            f"{suffix_next_row['threshold_numerator']}/{suffix_next_row['threshold_denominator']}"
        )
        next_signature = _signature(exact_horizon, suffix_horizon + 1)
    elif suffix_next_value is None:
        next_unlock_kind = 'exact_only'
        next_unlock_threshold_value = exact_next_value
        next_unlock_threshold_fraction = (
            f"{exact_next_row['threshold_numerator']}/{exact_next_row['threshold_denominator']}"
        )
        next_signature = _signature(exact_horizon + 1, suffix_horizon)
    elif exact_next_value > suffix_next_value:
        next_unlock_kind = 'exact_only'
        next_unlock_threshold_value = exact_next_value
        next_unlock_threshold_fraction = (
            f"{exact_next_row['threshold_numerator']}/{exact_next_row['threshold_denominator']}"
        )
        next_signature = _signature(exact_horizon + 1, suffix_horizon)
    elif suffix_next_value > exact_next_value:
        next_unlock_kind = 'suffix_only'
        next_unlock_threshold_value = suffix_next_value
        next_unlock_threshold_fraction = (
            f"{suffix_next_row['threshold_numerator']}/{suffix_next_row['threshold_denominator']}"
        )
        next_signature = _signature(exact_horizon, suffix_horizon + 1)
    else:
        next_unlock_kind = 'shared_diagonal'
        next_unlock_threshold_value = exact_next_value
        next_unlock_threshold_fraction = (
            f"{exact_next_row['threshold_numerator']}/{exact_next_row['threshold_denominator']}"
        )
        next_signature = _signature(exact_horizon + 1, suffix_horizon + 1)

    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': _signature(exact_horizon, suffix_horizon),
        'exact_only_support_horizon': exact_horizon,
        'suffix_hitchhike_only_support_horizon': suffix_horizon,
        'next_exact_threshold': _format_threshold_row(exact_next_row),
        'next_suffix_threshold': _format_threshold_row(suffix_next_row),
        'next_unlock_kind': next_unlock_kind,
        'next_unlock_threshold_value': next_unlock_threshold_value,
        'next_unlock_threshold_fraction': next_unlock_threshold_fraction,
        'next_signature_after_relaxation': next_signature,
        'exact_relaxation_needed': (
            None
            if exact_next_value is None
            else max(0.0, minimum_service_share - exact_next_value)
        ),
        'suffix_relaxation_needed': (
            None
            if suffix_next_value is None
            else max(0.0, minimum_service_share - suffix_next_value)
        ),
    }


@lru_cache(maxsize=1)
def build_positive_service_local_witness_rows() -> list[dict[str, Any]]:
    states = build_positive_service_staircase_states()
    rows: list[dict[str, Any]] = []
    for state, next_state in zip(states[:-1], states[1:]):
        witness = select_local_upgrade_witness(state['probe_target'])
        rows.append(
            {
                'state_index': state['state_index'],
                'probe_target': state['probe_target'],
                'current_signature': state['signature'],
                'next_unlock_kind': witness['next_unlock_kind'],
                'next_unlock_threshold_value': witness['next_unlock_threshold_value'],
                'next_unlock_threshold_fraction': witness['next_unlock_threshold_fraction'],
                'next_signature_after_relaxation': witness['next_signature_after_relaxation'],
                'expected_next_signature': next_state['signature'],
                'exact_relaxation_needed': witness['exact_relaxation_needed'],
                'suffix_relaxation_needed': witness['suffix_relaxation_needed'],
                'next_exact_threshold': witness['next_exact_threshold'],
                'next_suffix_threshold': witness['next_suffix_threshold'],
            }
        )
    terminal_state = states[-1]
    terminal_witness = select_local_upgrade_witness(terminal_state['probe_target'])
    rows.append(
        {
            'state_index': terminal_state['state_index'],
            'probe_target': terminal_state['probe_target'],
            'current_signature': terminal_state['signature'],
            'next_unlock_kind': terminal_witness['next_unlock_kind'],
            'next_unlock_threshold_value': terminal_witness['next_unlock_threshold_value'],
            'next_unlock_threshold_fraction': terminal_witness['next_unlock_threshold_fraction'],
            'next_signature_after_relaxation': terminal_witness['next_signature_after_relaxation'],
            'expected_next_signature': None,
            'exact_relaxation_needed': terminal_witness['exact_relaxation_needed'],
            'suffix_relaxation_needed': terminal_witness['suffix_relaxation_needed'],
            'next_exact_threshold': terminal_witness['next_exact_threshold'],
            'next_suffix_threshold': terminal_witness['next_suffix_threshold'],
        }
    )
    return rows


@lru_cache(maxsize=1)
def build_local_unlock_histogram() -> dict[str, int]:
    histogram = {
        'exact_only': 0,
        'suffix_only': 0,
        'shared_diagonal': 0,
        'terminal': 0,
    }
    for row in build_positive_service_local_witness_rows():
        histogram[row['next_unlock_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_shared_local_unlock_summary() -> dict[str, Any]:
    shared_rows = [
        row
        for row in build_positive_service_local_witness_rows()
        if row['next_unlock_kind'] == 'shared_diagonal'
    ]
    if len(shared_rows) != 1:
        raise WeakeningPortfolioServiceLocalUpgradeWitnessLawError(
            f'expected exactly one shared local unlock row, found {len(shared_rows)}'
        )
    row = shared_rows[0]
    return {
        'current_signature': row['current_signature'],
        'next_signature_after_relaxation': row['next_signature_after_relaxation'],
        'next_unlock_threshold_fraction': row['next_unlock_threshold_fraction'],
        'state_index': row['state_index'],
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_local_upgrade_witness(0.40),
        select_local_upgrade_witness(0.05),
        select_local_upgrade_witness(0.011),
        select_local_upgrade_witness(1 / 91),
        select_local_upgrade_witness(0.01),
        select_local_upgrade_witness(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_local_upgrade_witness_snapshot() -> dict[str, Any]:
    rows = build_positive_service_local_witness_rows()
    return {
        'focus': (
            'Turn the positive-service weakening SLA staircase into a local upgrade-witness '
            'card so future inheritors can answer, from any current target, which axis '
            'unlocks next and how much relaxation it needs.'
        ),
        'headline_findings': {
            'nonterminal_positive_service_states_have_local_upgrade_witness': True,
            'local_unlock_histogram': build_local_unlock_histogram(),
            'shared_local_unlock_summary': build_shared_local_unlock_summary(),
            'positive_service_state_count': len(rows),
            'statewise_next_signature_matches_staircase_successor': all(
                row['expected_next_signature'] == row['next_signature_after_relaxation']
                for row in rows[:-1]
            ),
        },
        'decision_rules': [
            'For any current SLA target, compute the current support signature `(exact horizon, suffix horizon)` and then inspect the next exact and next suffix threshold rows.',
            'The first additional width support unlocked by relaxing the target is always the larger of those two next-threshold values; equality means the unique shared diagonal unlock.',
            'Use the relaxation gaps `target - next_threshold` as the exact local slack needed for the next exact or suffix expansion from the current target.',
            'Treat any future state whose first relaxation event would require a mixed or skipped unlock as an immediate redesign signal.',
        ],
        'positive_service_local_witness_rows': rows,
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_local_upgrade_witness_snapshot(), indent=2, sort_keys=True))
