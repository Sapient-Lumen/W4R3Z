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
    build_positive_service_horizon_bands,
    select_upgrade_schedule_by_minimum_service_share,
)


class WeakeningPortfolioServiceHorizonStaircaseLawError(RuntimeError):
    pass


def _signature(exact_horizon: int, suffix_horizon: int) -> str:
    return f'E{exact_horizon}_S{suffix_horizon}'


@lru_cache(maxsize=1)
def build_positive_service_staircase_states() -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = []
    for index, band in enumerate(build_positive_service_horizon_bands()):
        exact_horizon = band['exact_only_support_horizon']
        suffix_horizon = band['suffix_hitchhike_only_support_horizon']
        states.append(
            {
                'state_index': index,
                'interval_kind': band['interval_kind'],
                'lower_bound_exclusive': band['lower_bound_exclusive'],
                'upper_bound_inclusive': band['upper_bound_inclusive'],
                'probe_target': band['probe_target'],
                'exact_only_support_horizon': exact_horizon,
                'suffix_hitchhike_only_support_horizon': suffix_horizon,
                'signature': _signature(exact_horizon, suffix_horizon),
            }
        )
    return states


@lru_cache(maxsize=1)
def build_positive_service_staircase_transitions() -> list[dict[str, Any]]:
    states = build_positive_service_staircase_states()
    transitions: list[dict[str, Any]] = []
    for current_state, next_state in zip(states[:-1], states[1:]):
        exact_increment = (
            next_state['exact_only_support_horizon']
            - current_state['exact_only_support_horizon']
        )
        suffix_increment = (
            next_state['suffix_hitchhike_only_support_horizon']
            - current_state['suffix_hitchhike_only_support_horizon']
        )
        step_kind_map = {
            (0, 1): 'suffix_only',
            (1, 0): 'exact_only',
            (1, 1): 'diagonal_shared',
        }
        step_kind = step_kind_map.get((exact_increment, suffix_increment))
        if step_kind is None:
            raise WeakeningPortfolioServiceHorizonStaircaseLawError(
                'expected all positive-service staircase transitions to be unit axis or diagonal steps '
                f'but saw increments {(exact_increment, suffix_increment)} between '
                f"{current_state['signature']} and {next_state['signature']}"
            )
        threshold = current_state['lower_bound_exclusive']
        threshold_fraction = Fraction(threshold).limit_denominator(1_000_000)
        transitions.append(
            {
                'transition_index': len(transitions),
                'crossed_threshold_value': threshold,
                'crossed_threshold_numerator': threshold_fraction.numerator,
                'crossed_threshold_denominator': threshold_fraction.denominator,
                'from_signature': current_state['signature'],
                'to_signature': next_state['signature'],
                'exact_increment': exact_increment,
                'suffix_increment': suffix_increment,
                'step_kind': step_kind,
            }
        )
    return transitions


@lru_cache(maxsize=1)
def build_transition_histogram() -> dict[str, int]:
    histogram = {
        'suffix_only': 0,
        'exact_only': 0,
        'diagonal_shared': 0,
    }
    for transition in build_positive_service_staircase_transitions():
        histogram[transition['step_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_staircase_path_word() -> str:
    encoding = {
        'suffix_only': 'S',
        'exact_only': 'E',
        'diagonal_shared': 'D',
    }
    return ''.join(
        encoding[transition['step_kind']]
        for transition in build_positive_service_staircase_transitions()
    )


@lru_cache(maxsize=1)
def build_shared_threshold_summary() -> dict[str, Any]:
    shared = [
        transition
        for transition in build_positive_service_staircase_transitions()
        if transition['step_kind'] == 'diagonal_shared'
    ]
    if len(shared) != 1:
        raise WeakeningPortfolioServiceHorizonStaircaseLawError(
            f'expected exactly one shared diagonal threshold, found {len(shared)}'
        )
    transition = shared[0]
    return {
        'shared_threshold_numerator': transition['crossed_threshold_numerator'],
        'shared_threshold_denominator': transition['crossed_threshold_denominator'],
        'from_signature': transition['from_signature'],
        'to_signature': transition['to_signature'],
        'transition_index': transition['transition_index'],
    }


@lru_cache(maxsize=1)
def build_staircase_summary() -> dict[str, Any]:
    states = build_positive_service_staircase_states()
    transitions = build_positive_service_staircase_transitions()
    zero_target_schedule = select_upgrade_schedule_by_minimum_service_share(0.0)
    return {
        'positive_service_state_count': len(states),
        'positive_service_transition_count': len(transitions),
        'positive_service_initial_signature': states[0]['signature'],
        'positive_service_terminal_signature': states[-1]['signature'],
        'zero_service_signature': _signature(
            zero_target_schedule['exact_only_support_horizon'],
            zero_target_schedule['suffix_hitchhike_only_support_horizon'],
        ),
        'all_positive_service_transitions_are_unit_axis_or_shared_diagonal_steps': True,
        'transition_histogram': build_transition_histogram(),
        'staircase_path_word': build_staircase_path_word(),
        'shared_threshold_summary': build_shared_threshold_summary(),
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        {
            'minimum_service_share': 0.75,
            'selected_signature': select_signature_by_minimum_service_share(0.75),
        },
        {
            'minimum_service_share': 0.11,
            'selected_signature': select_signature_by_minimum_service_share(0.11),
        },
        {
            'minimum_service_share': 1 / 91,
            'selected_signature': select_signature_by_minimum_service_share(1 / 91),
        },
        {
            'minimum_service_share': 0.01,
            'selected_signature': select_signature_by_minimum_service_share(0.01),
        },
        {
            'minimum_service_share': 0.0,
            'selected_signature': select_signature_by_minimum_service_share(0.0),
        },
    ]


@lru_cache(maxsize=1)
def build_state_histogram_by_exact_horizon() -> dict[str, int]:
    histogram: dict[str, int] = {}
    for state in build_positive_service_staircase_states():
        key = str(state['exact_only_support_horizon'])
        histogram[key] = histogram.get(key, 0) + 1
    return histogram


@lru_cache(maxsize=1)
def build_state_histogram_by_suffix_horizon() -> dict[str, int]:
    histogram: dict[str, int] = {}
    for state in build_positive_service_staircase_states():
        key = str(state['suffix_hitchhike_only_support_horizon'])
        histogram[key] = histogram.get(key, 0) + 1
    return histogram


def select_signature_by_minimum_service_share(minimum_service_share: float) -> str:
    schedule = select_upgrade_schedule_by_minimum_service_share(minimum_service_share)
    return _signature(
        schedule['exact_only_support_horizon'],
        schedule['suffix_hitchhike_only_support_horizon'],
    )


@lru_cache(maxsize=1)
def build_service_horizon_staircase_snapshot() -> dict[str, Any]:
    states = build_positive_service_staircase_states()
    transitions = build_positive_service_staircase_transitions()
    summary = build_staircase_summary()
    shared = summary['shared_threshold_summary']
    return {
        'focus': (
            'Collapse the recent width-only weakening SLA target geometry into one '
            'monotone staircase so future inheritors can reason in schedule states and '
            'threshold steps instead of rereading the full band catalog.'
        ),
        'headline_findings': {
            **summary,
            'positive_service_band_count_equals_state_count': len(states),
            'shared_diagonal_threshold_value': shared['shared_threshold_numerator'] / shared['shared_threshold_denominator'],
            'state_histogram_by_exact_horizon': build_state_histogram_by_exact_horizon(),
            'state_histogram_by_suffix_horizon': build_state_histogram_by_suffix_horizon(),
        },
        'decision_rules': [
            'Treat every positive-service target as one of 17 canonical staircase states indexed by `(exact horizon, suffix horizon)` rather than as a free-floating scalar.',
            'As service targets relax, expect only three threshold events: suffix-only growth, exact-only growth, or the single shared diagonal growth at `1/91`.',
            'Remember that target `0` sits off the positive-service staircase as the degenerate full-support signature `E15_S15`.',
            'Treat any future extra diagonal, non-unit jump, or non-monotone staircase transition as an immediate redesign signal.',
        ],
        'positive_service_staircase_states': states,
        'positive_service_staircase_transitions': transitions,
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_horizon_staircase_snapshot(), indent=2, sort_keys=True))
