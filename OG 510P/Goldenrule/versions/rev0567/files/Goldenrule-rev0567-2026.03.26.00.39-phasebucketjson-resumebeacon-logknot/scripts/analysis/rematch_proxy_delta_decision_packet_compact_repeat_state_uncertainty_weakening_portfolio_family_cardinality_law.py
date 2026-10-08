#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails import (
    build_overshoot_axis_guardrail_profiles,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier import (
    EFFICIENT_PROFILE_ORDER,
    build_portfolio_service_rows,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee import (
    build_portfolio_width_cap_service_rows,
)


class WeakeningPortfolioFamilyCardinalityLawError(RuntimeError):
    pass


PROFILE_ORDER = [
    'exact_only',
    'precision_hitchhike_only',
    'suffix_hitchhike_only',
    'any_single_axis_hitchhike',
]


@lru_cache(maxsize=1)
def build_admissible_family_sizes() -> dict[str, int]:
    profiles = build_overshoot_axis_guardrail_profiles()
    result = {
        profile['profile_label']: profile['admitted_coordinate_count']
        for profile in profiles
    }
    expected = {
        'exact_only': 6,
        'precision_hitchhike_only': 10,
        'suffix_hitchhike_only': 11,
        'any_single_axis_hitchhike': 15,
    }
    if result != expected:
        raise WeakeningPortfolioFamilyCardinalityLawError(
            f'unexpected admissible family sizes: {result}'
        )
    return result


def _comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def coverage_share_from_family_size(admissible_family_size: int, width: int, universe_size: int) -> dict[str, Any]:
    numerator = _comb(admissible_family_size, width)
    denominator = _comb(universe_size, width)
    value = 0.0 if denominator == 0 else numerator / denominator
    return {
        'numerator': numerator,
        'denominator': denominator,
        'value': value,
    }


@lru_cache(maxsize=1)
def build_closed_form_service_rows() -> list[dict[str, Any]]:
    family_sizes = build_admissible_family_sizes()
    universe_size = family_sizes['any_single_axis_hitchhike']
    rows: list[dict[str, Any]] = []
    for width in range(1, universe_size + 1):
        coverage_shares = {
            label: coverage_share_from_family_size(size, width, universe_size)
            for label, size in family_sizes.items()
        }
        rows.append(
            {
                'portfolio_size': width,
                'closed_form_coverage_shares': coverage_shares,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_width_threshold_summary() -> list[dict[str, Any]]:
    family_sizes = build_admissible_family_sizes()
    universe_size = family_sizes['any_single_axis_hitchhike']
    summary: list[dict[str, Any]] = []
    for label in PROFILE_ORDER:
        size = family_sizes[label]
        summary.append(
            {
                'profile_label': label,
                'admissible_family_size': size,
                'singleton_service_share': {
                    'numerator': size,
                    'denominator': universe_size,
                    'value': size / universe_size,
                },
                'last_width_with_positive_service': size,
                'first_width_with_zero_service': None if size == universe_size else size + 1,
            }
        )
    return summary


@lru_cache(maxsize=1)
def build_cardinality_law_examples() -> list[dict[str, Any]]:
    family_sizes = build_admissible_family_sizes()
    universe_size = family_sizes['any_single_axis_hitchhike']
    examples = [
        ('exact_only', 2),
        ('precision_hitchhike_only', 3),
        ('suffix_hitchhike_only', 5),
        ('suffix_hitchhike_only', 11),
        ('any_single_axis_hitchhike', 12),
    ]
    rows: list[dict[str, Any]] = []
    for label, width in examples:
        share = coverage_share_from_family_size(family_sizes[label], width, universe_size)
        rows.append(
            {
                'profile_label': label,
                'width': width,
                'family_size': family_sizes[label],
                'closed_form_share': share,
                'formula': f"C({family_sizes[label]},{width})/C({universe_size},{width})",
            }
        )
    return rows



def build_weakening_portfolio_family_cardinality_law_snapshot() -> dict[str, Any]:
    family_sizes = build_admissible_family_sizes()
    universe_size = family_sizes['any_single_axis_hitchhike']
    closed_form_rows = build_closed_form_service_rows()
    enumerated_service_rows = build_portfolio_service_rows()
    width_cap_rows = build_portfolio_width_cap_service_rows()
    threshold_summary = build_width_threshold_summary()
    examples = build_cardinality_law_examples()

    for closed_form_row, service_row, width_cap_row in zip(
        closed_form_rows,
        enumerated_service_rows,
        width_cap_rows,
        strict=True,
    ):
        if closed_form_row['portfolio_size'] != service_row['portfolio_size']:
            raise WeakeningPortfolioFamilyCardinalityLawError('closed-form service row misaligned with exact-width service row')
        if closed_form_row['portfolio_size'] != width_cap_row['maximum_portfolio_size']:
            raise WeakeningPortfolioFamilyCardinalityLawError('closed-form service row misaligned with width-cap service row')
        if closed_form_row['closed_form_coverage_shares'] != service_row['coverage_shares']:
            raise WeakeningPortfolioFamilyCardinalityLawError(
                f"closed-form service row drifted from exact-width service row at width {closed_form_row['portfolio_size']}"
            )
        if closed_form_row['closed_form_coverage_shares'] != width_cap_row['guaranteed_coverage_shares']:
            raise WeakeningPortfolioFamilyCardinalityLawError(
                f"closed-form service row drifted from width-cap guarantee row at width {closed_form_row['portfolio_size']}"
            )

    if family_sizes['suffix_hitchhike_only'] <= family_sizes['precision_hitchhike_only']:
        raise WeakeningPortfolioFamilyCardinalityLawError(
            'suffix family should be strictly larger than precision family under the current staircase'
        )

    derived_positive_support_cutoffs = {
        row['profile_label']: row['last_width_with_positive_service']
        for row in threshold_summary
    }
    if derived_positive_support_cutoffs != {
        'exact_only': 6,
        'precision_hitchhike_only': 10,
        'suffix_hitchhike_only': 11,
        'any_single_axis_hitchhike': 15,
    }:
        raise WeakeningPortfolioFamilyCardinalityLawError(
            f'unexpected positive-support cutoffs: {derived_positive_support_cutoffs}'
        )

    singleton_ceiling_map = {
        row['profile_label']: row['singleton_service_share']['value']
        for row in threshold_summary
    }
    if singleton_ceiling_map != {
        'exact_only': 6 / 15,
        'precision_hitchhike_only': 10 / 15,
        'suffix_hitchhike_only': 11 / 15,
        'any_single_axis_hitchhike': 1.0,
    }:
        raise WeakeningPortfolioFamilyCardinalityLawError(
            f'unexpected singleton service ceiling map: {singleton_ceiling_map}'
        )

    return {
        'focus': 'Collapse the recent width-conditioned weakening service stack to an exact combinatorial law driven only by admissible-family cardinalities inside the 15-point primitive demand box.',
        'headline_findings': {
            'admissible_family_sizes': family_sizes,
            'universe_size': universe_size,
            'all_exact_width_service_rows_match_closed_form_choose_ratios': True,
            'all_width_cap_guarantee_rows_match_the_same_closed_form_choose_ratios': True,
            'service_share_formula': 'coverage(width, profile) = C(admissible_family_size(profile), width) / C(15, width)',
            'suffix_dominates_precision_because_its_family_is_larger': True,
            'suffix_minus_precision_family_gap': family_sizes['suffix_hitchhike_only'] - family_sizes['precision_hitchhike_only'],
            'best_one_axis_singleton_service_ceiling': singleton_ceiling_map['suffix_hitchhike_only'],
            'exact_only_positive_support_ends_after_width': family_sizes['exact_only'],
            'precision_only_positive_support_ends_after_width': family_sizes['precision_hitchhike_only'],
            'suffix_only_positive_support_ends_after_width': family_sizes['suffix_hitchhike_only'],
        },
        'decision_rules': [
            'Treat the admissible-family size vector `{6,10,11,15}` as the sufficient statistic for the current stochastic weakening stack: once those four counts are fixed, width-conditioned service and width-cap guarantees are fully determined.',
            'Compute exact-width or width-cap service for profile `P` and width `w` with the same choose ratio `C(K_P, w) / C(15, w)`; the cap case adds no new combinatorics because it already collapses to the endpoint width.',
            'Read the one-axis dominance `suffix_hitchhike_only > precision_hitchhike_only` as a pure cardinality fact `11 > 10`, not as a delicate probabilistic artifact.',
            'Read one-axis dropout widths directly from family sizes: exact-only dies after width `6`, precision-only after width `10`, and suffix-only after width `11`.',
            'Treat any future change in the admissible-family size vector `{6,10,11,15}` as a redesign signal that automatically propagates to the service frontier, confidence ladder, and width-cap guarantee results.',
        ],
        'width_threshold_summary': threshold_summary,
        'closed_form_service_rows': closed_form_rows,
        'cardinality_law_examples': examples,
        'efficient_profile_order': EFFICIENT_PROFILE_ORDER,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_family_cardinality_law_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
