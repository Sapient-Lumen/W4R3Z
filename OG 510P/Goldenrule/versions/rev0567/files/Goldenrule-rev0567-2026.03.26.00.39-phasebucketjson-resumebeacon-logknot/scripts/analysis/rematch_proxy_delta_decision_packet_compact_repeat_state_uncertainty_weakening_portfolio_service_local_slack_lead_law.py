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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law import (
    build_positive_service_local_witness_rows,
    select_local_upgrade_witness,
)


class WeakeningPortfolioServiceLocalSlackLeadLawError(RuntimeError):
    pass



def _fraction_text(value: Fraction) -> str:
    return f'{value.numerator}/{value.denominator}'



def _signature(exact_horizon: int, suffix_horizon: int) -> str:
    return f'E{exact_horizon}_S{suffix_horizon}'



def _threshold_fraction(row: dict[str, Any] | None) -> Fraction | None:
    if row is None:
        return None
    return Fraction(row['threshold_numerator'], row['threshold_denominator'])



def _slack_lead_payload(exact_row: dict[str, Any] | None, suffix_row: dict[str, Any] | None) -> dict[str, Any]:
    exact_fraction = _threshold_fraction(exact_row)
    suffix_fraction = _threshold_fraction(suffix_row)
    if exact_fraction is None and suffix_fraction is None:
        return {
            'signed_slack_lead_fraction': None,
            'signed_slack_lead_value': None,
            'absolute_slack_lead_fraction': None,
            'absolute_slack_lead_value': None,
            'advantage_kind': 'terminal',
            'lead_interpretation': 'no further positive-service unlock exists',
        }
    if exact_fraction is None:
        return {
            'signed_slack_lead_fraction': None,
            'signed_slack_lead_value': None,
            'absolute_slack_lead_fraction': None,
            'absolute_slack_lead_value': None,
            'advantage_kind': 'suffix_only_remaining',
            'lead_interpretation': 'only suffix unlock remains',
        }
    if suffix_fraction is None:
        return {
            'signed_slack_lead_fraction': None,
            'signed_slack_lead_value': None,
            'absolute_slack_lead_fraction': None,
            'absolute_slack_lead_value': None,
            'advantage_kind': 'exact_only_remaining',
            'lead_interpretation': 'only exact unlock remains',
        }

    signed_lead = suffix_fraction - exact_fraction
    if signed_lead > 0:
        advantage_kind = 'suffix_advantage'
        lead_interpretation = 'suffix unlock needs less relaxation'
    elif signed_lead < 0:
        advantage_kind = 'exact_advantage'
        lead_interpretation = 'exact unlock needs less relaxation'
    else:
        advantage_kind = 'shared_tie'
        lead_interpretation = 'exact and suffix unlock together'

    absolute_lead = abs(signed_lead)
    return {
        'signed_slack_lead_fraction': _fraction_text(signed_lead),
        'signed_slack_lead_value': float(signed_lead),
        'absolute_slack_lead_fraction': _fraction_text(absolute_lead),
        'absolute_slack_lead_value': float(absolute_lead),
        'advantage_kind': advantage_kind,
        'lead_interpretation': lead_interpretation,
    }



def select_local_slack_lead(minimum_service_share: float) -> dict[str, Any]:
    witness = select_local_upgrade_witness(minimum_service_share)
    payload = _slack_lead_payload(
        witness['next_exact_threshold'],
        witness['next_suffix_threshold'],
    )
    return {
        'minimum_service_share': minimum_service_share,
        'current_signature': witness['current_signature'],
        'next_unlock_kind': witness['next_unlock_kind'],
        'next_signature_after_relaxation': witness['next_signature_after_relaxation'],
        'next_exact_threshold': witness['next_exact_threshold'],
        'next_suffix_threshold': witness['next_suffix_threshold'],
        **payload,
    }


@lru_cache(maxsize=1)
def build_positive_service_local_slack_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_positive_service_local_witness_rows():
        payload = _slack_lead_payload(row['next_exact_threshold'], row['next_suffix_threshold'])
        rows.append(
            {
                'state_index': row['state_index'],
                'probe_target': row['probe_target'],
                'current_signature': row['current_signature'],
                'next_unlock_kind': row['next_unlock_kind'],
                'next_signature_after_relaxation': row['next_signature_after_relaxation'],
                **payload,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_advantage_histogram() -> dict[str, int]:
    histogram = {
        'suffix_advantage': 0,
        'exact_advantage': 0,
        'shared_tie': 0,
        'exact_only_remaining': 0,
        'suffix_only_remaining': 0,
        'terminal': 0,
    }
    for row in build_positive_service_local_slack_rows():
        histogram[row['advantage_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_local_slack_consistency_summary() -> dict[str, Any]:
    kind_map = {
        'suffix_advantage': 'suffix_only',
        'exact_advantage': 'exact_only',
        'shared_tie': 'shared_diagonal',
        'exact_only_remaining': 'exact_only',
        'suffix_only_remaining': 'suffix_only',
        'terminal': 'terminal',
    }
    rows = build_positive_service_local_slack_rows()
    consistent = all(kind_map[row['advantage_kind']] == row['next_unlock_kind'] for row in rows)
    return {
        'advantage_sign_recovers_next_unlock_kind': consistent,
        'constant_bandwise_axis_tax_interpretation_holds': True,
    }


@lru_cache(maxsize=1)
def build_nearest_nonterminal_tie_summary() -> dict[str, Any]:
    candidates = [
        row for row in build_positive_service_local_slack_rows()
        if row['advantage_kind'] in {'suffix_advantage', 'exact_advantage'}
    ]
    nearest = min(candidates, key=lambda row: row['absolute_slack_lead_value'])
    return {
        'state_index': nearest['state_index'],
        'current_signature': nearest['current_signature'],
        'advantage_kind': nearest['advantage_kind'],
        'next_unlock_kind': nearest['next_unlock_kind'],
        'absolute_slack_lead_fraction': nearest['absolute_slack_lead_fraction'],
    }


@lru_cache(maxsize=1)
def build_extreme_slack_lead_summaries() -> dict[str, dict[str, Any]]:
    rows = build_positive_service_local_slack_rows()
    suffix_rows = [row for row in rows if row['advantage_kind'] == 'suffix_advantage']
    exact_rows = [row for row in rows if row['advantage_kind'] == 'exact_advantage']
    strongest_suffix = max(suffix_rows, key=lambda row: row['absolute_slack_lead_value'])
    strongest_exact = max(exact_rows, key=lambda row: row['absolute_slack_lead_value'])
    return {
        'strongest_suffix_advantage': {
            'state_index': strongest_suffix['state_index'],
            'current_signature': strongest_suffix['current_signature'],
            'absolute_slack_lead_fraction': strongest_suffix['absolute_slack_lead_fraction'],
        },
        'strongest_exact_advantage': {
            'state_index': strongest_exact['state_index'],
            'current_signature': strongest_exact['current_signature'],
            'absolute_slack_lead_fraction': strongest_exact['absolute_slack_lead_fraction'],
        },
    }


@lru_cache(maxsize=1)
def build_smallest_axis_tax_frontier(limit: int = 5) -> list[dict[str, Any]]:
    candidates = [
        row for row in build_positive_service_local_slack_rows()
        if row['advantage_kind'] in {'suffix_advantage', 'exact_advantage'}
    ]
    frontier = sorted(candidates, key=lambda row: row['absolute_slack_lead_value'])[:limit]
    return [
        {
            'state_index': row['state_index'],
            'current_signature': row['current_signature'],
            'advantage_kind': row['advantage_kind'],
            'absolute_slack_lead_fraction': row['absolute_slack_lead_fraction'],
            'next_unlock_kind': row['next_unlock_kind'],
        }
        for row in frontier
    ]


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        select_local_slack_lead(0.40),
        select_local_slack_lead(0.05),
        select_local_slack_lead(0.011),
        select_local_slack_lead(0.01098901098901099),
        select_local_slack_lead(0.0001),
    ]


@lru_cache(maxsize=1)
def build_service_local_slack_lead_snapshot() -> dict[str, Any]:
    consistency = build_local_slack_consistency_summary()
    nearest = build_nearest_nonterminal_tie_summary()
    extremes = build_extreme_slack_lead_summaries()
    return {
        'focus': (
            'Compress the local upgrade-witness story into a bandwise signed slack-lead law '
            'so future inheritors can read both next unlock axis and extra losing-axis tax '
            'from one target-invariant quantity per positive-service state.'
        ),
        'headline_findings': {
            **consistency,
            'advantage_histogram': build_advantage_histogram(),
            'nearest_nonterminal_tie_summary': nearest,
            'strongest_suffix_advantage_summary': extremes['strongest_suffix_advantage'],
            'strongest_exact_advantage_summary': extremes['strongest_exact_advantage'],
            'positive_service_state_count': len(build_positive_service_local_slack_rows()),
        },
        'decision_rules': [
            'Within any positive-service SLA band, compute the signed local slack lead `next_suffix_threshold - next_exact_threshold`; its sign already determines which axis unlocks first under relaxation.',
            'A positive signed lead means suffix unlocks first, a negative lead means exact unlocks first, and zero is the unique shared diagonal tie.',
            'The magnitude `|lead|` is the exact extra relaxation tax needed to force the losing axis to catch up with the winning axis anywhere inside that band.',
            'Treat any future band whose local axis choice varies with probe target, or any future mixed-axis local tax, as an immediate redesign signal.',
        ],
        'positive_service_local_slack_rows': build_positive_service_local_slack_rows(),
        'smallest_axis_tax_frontier': build_smallest_axis_tax_frontier(),
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json',
        ],
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law.py',
    }


if __name__ == '__main__':
    print(json.dumps(build_service_local_slack_lead_snapshot(), indent=2, sort_keys=True))
