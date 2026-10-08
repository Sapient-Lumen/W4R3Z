#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_positive_service_staircase_states,
    build_staircase_path_word,
)


class WeakeningPortfolioServiceThresholdProvenanceLawError(RuntimeError):
    pass


UNIVERSE_SIZE = 15
PROFILE_FAMILY_SIZES = {
    'exact_only': 6,
    'suffix_hitchhike_only': 11,
}
PROFILE_SYMBOLS = {
    'exact_only': 'E',
    'suffix_hitchhike_only': 'S',
    'shared_collision': 'D',
}



def _coverage_fraction(family_size: int, width: int) -> Fraction:
    return Fraction(math.comb(family_size, width), math.comb(UNIVERSE_SIZE, width))


@lru_cache(maxsize=1)
def build_profile_threshold_ladders() -> dict[str, list[dict[str, Any]]]:
    ladders: dict[str, list[dict[str, Any]]] = {}
    for profile_label, family_size in PROFILE_FAMILY_SIZES.items():
        rows: list[dict[str, Any]] = []
        for width in range(1, family_size + 1):
            fraction = _coverage_fraction(family_size, width)
            rows.append(
                {
                    'profile_label': profile_label,
                    'portfolio_size': width,
                    'threshold_numerator': fraction.numerator,
                    'threshold_denominator': fraction.denominator,
                    'threshold_value': float(fraction),
                }
            )
        rows.sort(key=lambda row: row['threshold_value'], reverse=True)
        ladders[profile_label] = rows
    return ladders


@lru_cache(maxsize=1)
def build_threshold_provenance_rows() -> list[dict[str, Any]]:
    threshold_sources: dict[Fraction, list[dict[str, Any]]] = {}
    for profile_rows in build_profile_threshold_ladders().values():
        for row in profile_rows:
            fraction = Fraction(row['threshold_numerator'], row['threshold_denominator'])
            threshold_sources.setdefault(fraction, []).append(
                {
                    'profile_label': row['profile_label'],
                    'portfolio_size': row['portfolio_size'],
                }
            )

    rows: list[dict[str, Any]] = []
    for index, fraction in enumerate(sorted(threshold_sources, reverse=True)):
        sources = sorted(
            threshold_sources[fraction],
            key=lambda source: (source['profile_label'], source['portfolio_size']),
        )
        if len(sources) == 1:
            provenance_kind = sources[0]['profile_label']
        elif {source['profile_label'] for source in sources} == set(PROFILE_FAMILY_SIZES):
            provenance_kind = 'shared_collision'
        else:
            raise WeakeningPortfolioServiceThresholdProvenanceLawError(
                f'unexpected source multiplicity at threshold {fraction}: {sources}'
            )
        rows.append(
            {
                'threshold_index_descending': index,
                'threshold_numerator': fraction.numerator,
                'threshold_denominator': fraction.denominator,
                'threshold_value': float(fraction),
                'source_count': len(sources),
                'provenance_kind': provenance_kind,
                'sources': sources,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_provenance_histogram() -> dict[str, int]:
    histogram = {
        'exact_only': 0,
        'suffix_hitchhike_only': 0,
        'shared_collision': 0,
    }
    for row in build_threshold_provenance_rows():
        histogram[row['provenance_kind']] += 1
    return histogram


@lru_cache(maxsize=1)
def build_source_event_count() -> int:
    return sum(len(rows) for rows in build_profile_threshold_ladders().values())


@lru_cache(maxsize=1)
def build_shared_collision_summary() -> dict[str, Any]:
    shared_rows = [
        row for row in build_threshold_provenance_rows() if row['provenance_kind'] == 'shared_collision'
    ]
    if len(shared_rows) != 1:
        raise WeakeningPortfolioServiceThresholdProvenanceLawError(
            f'expected exactly one shared collision row, found {len(shared_rows)}'
        )
    row = shared_rows[0]
    return {
        'threshold_numerator': row['threshold_numerator'],
        'threshold_denominator': row['threshold_denominator'],
        'threshold_index_descending': row['threshold_index_descending'],
        'sources': row['sources'],
    }


@lru_cache(maxsize=1)
def build_threshold_provenance_word() -> str:
    return ''.join(PROFILE_SYMBOLS[row['provenance_kind']] for row in build_threshold_provenance_rows())


@lru_cache(maxsize=1)
def build_reconstructed_positive_service_signatures() -> list[str]:
    exact_horizon = 0
    suffix_horizon = 0
    signatures = [f'E{exact_horizon}_S{suffix_horizon}']
    for row in build_threshold_provenance_rows():
        if row['provenance_kind'] == 'exact_only':
            exact_horizon += 1
        elif row['provenance_kind'] == 'suffix_hitchhike_only':
            suffix_horizon += 1
        elif row['provenance_kind'] == 'shared_collision':
            exact_horizon += 1
            suffix_horizon += 1
        else:
            raise WeakeningPortfolioServiceThresholdProvenanceLawError(
                f"unexpected provenance kind {row['provenance_kind']}"
            )
        signatures.append(f'E{exact_horizon}_S{suffix_horizon}')
    return signatures


@lru_cache(maxsize=1)
def build_threshold_source_order_by_profile() -> dict[str, list[int]]:
    order: dict[str, list[int]] = {label: [] for label in PROFILE_FAMILY_SIZES}
    for row in build_threshold_provenance_rows():
        for source in row['sources']:
            order[source['profile_label']].append(source['portfolio_size'])
    return order


@lru_cache(maxsize=1)
def build_service_threshold_provenance_summary() -> dict[str, Any]:
    ladders = build_profile_threshold_ladders()
    rows = build_threshold_provenance_rows()
    shared = build_shared_collision_summary()
    return {
        'exact_threshold_count': len(ladders['exact_only']),
        'suffix_threshold_count': len(ladders['suffix_hitchhike_only']),
        'source_threshold_event_count': build_source_event_count(),
        'unique_positive_threshold_count': len(rows),
        'shared_collision_count': 1,
        'positive_service_band_count': len(rows) + 1,
        'threshold_provenance_word': build_threshold_provenance_word(),
        'shared_collision_threshold_value': (
            shared['threshold_numerator'] / shared['threshold_denominator']
        ),
        'shared_collision_threshold_fraction': (
            f"{shared['threshold_numerator']}/{shared['threshold_denominator']}"
        ),
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    return [
        {
            'minimum_service_share': 0.40,
            'threshold_basis_signature': 'E1_S2',
        },
        {
            'minimum_service_share': 0.11,
            'threshold_basis_signature': 'E2_S5',
        },
        {
            'minimum_service_share': 1 / 91,
            'threshold_basis_signature': 'E4_S9',
        },
        {
            'minimum_service_share': 0.01,
            'threshold_basis_signature': 'E4_S10',
        },
        {
            'minimum_service_share': 0.0001,
            'threshold_basis_signature': 'E6_S11',
        },
    ]


@lru_cache(maxsize=1)
def build_service_threshold_provenance_snapshot() -> dict[str, Any]:
    ladders = build_profile_threshold_ladders()
    rows = build_threshold_provenance_rows()
    # The threshold scan and the positive-service staircase should enumerate the same 17 band signatures.
    reconstructed_band_signatures = build_reconstructed_positive_service_signatures()
    positive_state_signature_chain = [state['signature'] for state in build_positive_service_staircase_states()]
    return {
        'focus': (
            'Reduce the positive-service weakening SLA threshold catalog to a tiny '
            'two-ladder provenance basis whose sorted union reconstructs the full '
            'staircase.'
        ),
        'headline_findings': {
            **build_service_threshold_provenance_summary(),
            'reconstruction_matches_positive_service_staircase': (
                reconstructed_band_signatures == positive_state_signature_chain
            ),
            'staircase_path_word_matches_threshold_provenance_word': (
                build_threshold_provenance_word() == build_staircase_path_word()
            ),
        },
        'decision_rules': [
            'Treat the positive-service SLA threshold set as the sorted union of the exact-only ladder `C(6,w)/C(15,w)` for `w=1..6` and the suffix-only ladder `C(11,w)/C(15,w)` for `w=1..11`.',
            'Carry only the 16 unique positive thresholds forward; the 17th source event is absorbed by the lone shared collision at `1/91`.',
            'Reconstruct the whole positive-service staircase by starting at `E0_S0` and scanning the descending provenance word, adding one exact unit for `E`, one suffix unit for `S`, and one of each for the unique `D` step.',
            'Treat any future second collision, missing source threshold, or provenance word mismatch against the staircase path word as an immediate redesign signal.',
        ],
        'profile_threshold_ladders': ladders,
        'threshold_provenance_rows': rows,
        'shared_collision_summary': build_shared_collision_summary(),
        'reconstructed_positive_service_signatures': build_reconstructed_positive_service_signatures(),
        'positive_service_staircase_signatures': [
            state['signature'] for state in build_positive_service_staircase_states()
        ],
        'selector_examples': build_selector_examples(),
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law_snapshot_20260308.json',
        ],
        'analysis_script': (
            'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law.py'
        ),
    }


def main() -> None:
    print(json.dumps(build_service_threshold_provenance_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
