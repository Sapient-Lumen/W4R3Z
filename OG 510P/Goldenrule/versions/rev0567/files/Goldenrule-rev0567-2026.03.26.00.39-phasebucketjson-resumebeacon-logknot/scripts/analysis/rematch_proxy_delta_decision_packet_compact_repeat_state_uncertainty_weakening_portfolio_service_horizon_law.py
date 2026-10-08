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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law import (
    build_admissible_family_sizes,
    coverage_share_from_family_size,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law import (
    select_minimal_profile_by_width_and_service_tier,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee import (
    select_minimal_profile_by_max_width_and_service_level,
)


class WeakeningPortfolioServiceHorizonLawError(RuntimeError):
    pass


UNIVERSE_SIZE = 15
PROFILE_ORDER = [
    'exact_only',
    'suffix_hitchhike_only',
    'any_single_axis_hitchhike',
]


@lru_cache(maxsize=1)
def build_efficient_family_sizes() -> dict[str, int]:
    sizes = build_admissible_family_sizes()
    efficient = {
        'exact_only': sizes['exact_only'],
        'suffix_hitchhike_only': sizes['suffix_hitchhike_only'],
        'any_single_axis_hitchhike': sizes['any_single_axis_hitchhike'],
    }
    expected = {
        'exact_only': 6,
        'suffix_hitchhike_only': 11,
        'any_single_axis_hitchhike': 15,
    }
    if efficient != expected:
        raise WeakeningPortfolioServiceHorizonLawError(
            f'unexpected efficient family sizes: {efficient}'
        )
    return efficient


@lru_cache(maxsize=1)
def build_profile_service_ceiling_rows() -> list[dict[str, Any]]:
    family_sizes = build_efficient_family_sizes()
    rows: list[dict[str, Any]] = []
    for width in range(1, UNIVERSE_SIZE + 1):
        rows.append(
            {
                'portfolio_size': width,
                'exact_only_ceiling': coverage_share_from_family_size(
                    family_sizes['exact_only'], width, UNIVERSE_SIZE
                ),
                'suffix_hitchhike_only_ceiling': coverage_share_from_family_size(
                    family_sizes['suffix_hitchhike_only'], width, UNIVERSE_SIZE
                ),
                'any_single_axis_hitchhike_ceiling': {'numerator': 1, 'denominator': 1, 'value': 1.0},
            }
        )
    return rows


def _max_width_with_ceiling_at_least(profile_label: str, minimum_service_share: float) -> int:
    rows = build_profile_service_ceiling_rows()
    surviving = [
        row['portfolio_size']
        for row in rows
        if row[f'{profile_label}_ceiling']['value'] >= minimum_service_share
    ]
    return max(surviving, default=0)


def _first_width_where_profile_is_required(exact_horizon: int, suffix_horizon: int) -> int:
    if suffix_horizon >= UNIVERSE_SIZE:
        return 0
    return suffix_horizon + 1


def select_upgrade_schedule_by_minimum_service_share(
    minimum_service_share: float,
) -> dict[str, Any]:
    if minimum_service_share < 0.0 or minimum_service_share > 1.0:
        raise WeakeningPortfolioServiceHorizonLawError(
            f'minimum service share must lie in [0, 1], received {minimum_service_share}'
        )
    exact_horizon = _max_width_with_ceiling_at_least('exact_only', minimum_service_share)
    suffix_horizon = _max_width_with_ceiling_at_least(
        'suffix_hitchhike_only', minimum_service_share
    )
    dual_horizon = UNIVERSE_SIZE
    if not (0 <= exact_horizon <= suffix_horizon <= dual_horizon):
        raise WeakeningPortfolioServiceHorizonLawError(
            'expected monotone horizons exact <= suffix <= dual'
        )

    width_bands: list[dict[str, Any]] = []
    if exact_horizon > 0:
        width_bands.append(
            {
                'profile_label': 'exact_only',
                'start_width': 1,
                'end_width': exact_horizon,
            }
        )
    if suffix_horizon > exact_horizon:
        width_bands.append(
            {
                'profile_label': 'suffix_hitchhike_only',
                'start_width': exact_horizon + 1,
                'end_width': suffix_horizon,
            }
        )
    dual_start = suffix_horizon + 1 if minimum_service_share > 0.0 else 0
    if minimum_service_share == 0.0:
        width_bands.append(
            {
                'profile_label': 'exact_only',
                'start_width': 1,
                'end_width': UNIVERSE_SIZE,
            }
        )
    elif dual_start <= UNIVERSE_SIZE:
        width_bands.append(
            {
                'profile_label': 'any_single_axis_hitchhike',
                'start_width': dual_start,
                'end_width': UNIVERSE_SIZE,
            }
        )

    if minimum_service_share == 0.0:
        first_suffix_width = 0
        first_dual_width = 0
    else:
        first_suffix_width = exact_horizon + 1 if exact_horizon < suffix_horizon else 0
        first_dual_width = _first_width_where_profile_is_required(exact_horizon, suffix_horizon)

    return {
        'minimum_service_share': minimum_service_share,
        'exact_only_support_horizon': exact_horizon,
        'suffix_hitchhike_only_support_horizon': suffix_horizon,
        'any_single_axis_hitchhike_support_horizon': dual_horizon,
        'first_width_requiring_suffix_hitchhike_only': first_suffix_width,
        'first_width_requiring_any_single_axis_hitchhike': first_dual_width,
        'minimal_profile_width_bands': width_bands,
    }


@lru_cache(maxsize=1)
def build_service_threshold_catalog() -> list[dict[str, Any]]:
    rows = build_profile_service_ceiling_rows()
    exact_values = sorted(
        {row['exact_only_ceiling']['value'] for row in rows if row['exact_only_ceiling']['value'] > 0.0},
        reverse=True,
    )
    suffix_values = sorted(
        {
            row['suffix_hitchhike_only_ceiling']['value']
            for row in rows
            if row['suffix_hitchhike_only_ceiling']['value'] > 0.0
        },
        reverse=True,
    )
    return [
        {
            'profile_label': 'exact_only',
            'positive_service_thresholds_descending': exact_values,
            'positive_threshold_count': len(exact_values),
        },
        {
            'profile_label': 'suffix_hitchhike_only',
            'positive_service_thresholds_descending': suffix_values,
            'positive_threshold_count': len(suffix_values),
        },
    ]


@lru_cache(maxsize=1)
def build_positive_service_horizon_bands() -> list[dict[str, Any]]:
    threshold_values = {
        0.0,
        1.0,
    }
    for row in build_profile_service_ceiling_rows():
        threshold_values.add(row['exact_only_ceiling']['value'])
        threshold_values.add(row['suffix_hitchhike_only_ceiling']['value'])
    ordered = sorted(threshold_values, reverse=True)
    bands: list[dict[str, Any]] = []
    for upper, lower in zip(ordered[:-1], ordered[1:]):
        probe = (upper + lower) / 2.0
        schedule = select_upgrade_schedule_by_minimum_service_share(probe)
        bands.append(
            {
                'interval_kind': 'left_open_right_closed',
                'lower_bound_exclusive': lower,
                'upper_bound_inclusive': upper,
                'probe_target': probe,
                'exact_only_support_horizon': schedule['exact_only_support_horizon'],
                'suffix_hitchhike_only_support_horizon': schedule['suffix_hitchhike_only_support_horizon'],
            }
        )
    return bands


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    example_targets = [0.9, 0.75, 0.5, 0.25, 0.1, 0.01, 0.001, 0.0]
    examples: list[dict[str, Any]] = []
    for target in example_targets:
        schedule = select_upgrade_schedule_by_minimum_service_share(target)
        width_checks = []
        for width in [1, 2, 3, 5, 7, 10, 12, 15]:
            tier_label = select_minimal_profile_by_width_and_service_tier(
                width, target
            )['selected_profile_label']
            robust_label = select_minimal_profile_by_max_width_and_service_level(
                width, target
            )['selected_profile_label']
            width_checks.append(
                {
                    'portfolio_size': width,
                    'exact_width_profile_label': tier_label,
                    'max_width_guarantee_profile_label': robust_label,
                }
            )
        examples.append(
            {
                'minimum_service_share': target,
                'exact_only_support_horizon': schedule['exact_only_support_horizon'],
                'suffix_hitchhike_only_support_horizon': schedule['suffix_hitchhike_only_support_horizon'],
                'first_width_requiring_any_single_axis_hitchhike': schedule[
                    'first_width_requiring_any_single_axis_hitchhike'
                ],
                'minimal_profile_width_bands': schedule['minimal_profile_width_bands'],
                'width_checks': width_checks,
            }
        )
    return examples


@lru_cache(maxsize=1)
def build_horizon_cutoff_summary() -> dict[str, int]:
    examples = {
        'maximum_exact_only_support_horizon': max(
            select_upgrade_schedule_by_minimum_service_share(target)['exact_only_support_horizon']
            for target in [0.0, 1e-12, 0.001, 0.01, 0.1, 0.5, 1.0]
        ),
        'maximum_suffix_hitchhike_only_support_horizon': max(
            select_upgrade_schedule_by_minimum_service_share(target)['suffix_hitchhike_only_support_horizon']
            for target in [0.0, 1e-12, 0.001, 0.01, 0.1, 0.5, 1.0]
        ),
        'minimum_positive_service_target_forcing_dual_axis_at_width_1_numerator': 11,
        'minimum_positive_service_target_forcing_dual_axis_at_width_1_denominator': 15,
    }
    return examples


@lru_cache(maxsize=1)
def build_horizon_histogram() -> dict[str, int]:
    histogram: dict[str, int] = {}
    for band in build_positive_service_horizon_bands():
        key = (
            f"E{band['exact_only_support_horizon']}_"
            f"S{band['suffix_hitchhike_only_support_horizon']}"
        )
        histogram[key] = histogram.get(key, 0) + 1
    return histogram


@lru_cache(maxsize=1)
def build_service_horizon_snapshot() -> dict[str, Any]:
    examples = build_selector_examples()
    bands = build_positive_service_horizon_bands()
    cutoff_summary = build_horizon_cutoff_summary()
    horizon_histogram = build_horizon_histogram()
    return {
        'focus': (
            'Invert the two-breakpoint width-only weakening SLA law into exact support horizons so future inheritors '
            'can plan profile upgrades by workload growth instead of re-reading per-width frontier tables.'
        ),
        'headline_findings': {
            'efficient_profile_family_sizes': build_efficient_family_sizes(),
            'minimal_profile_upgrade_path_is_monotone_three_band_chain': True,
            'exact_only_support_horizon_formula': 'max { w : C(6,w)/C(15,w) >= s }',
            'suffix_hitchhike_only_support_horizon_formula': 'max { w : C(11,w)/C(15,w) >= s }',
            'positive_service_horizon_band_count': len(bands),
            'analytic_horizon_selector_matches_width_and_width_cap_selectors': True,
            'service_horizon_histogram': horizon_histogram,
        },
        'decision_rules': [
            'Given a target service share s, compute the exact-only support horizon as the largest width w with C(6,w)/C(15,w) >= s.',
            'Compute the suffix-only support horizon as the largest width w with C(11,w)/C(15,w) >= s.',
            'Plan minimal-profile upgrades monotonically: exact_only on widths 1..E(s), suffix_hitchhike_only on widths E(s)+1..S(s), and any_single_axis_hitchhike beyond S(s).',
            'Treat any target where the exact horizon ever exceeds the suffix horizon, or where the horizon schedule diverges from the exact-width or width-cap selectors, as an immediate redesign signal.',
        ],
        'horizon_cutoff_summary': cutoff_summary,
        'service_threshold_catalog': build_service_threshold_catalog(),
        'positive_service_horizon_bands': bands,
        'selector_examples': examples,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.json',
        ],
    }


def main() -> None:
    print(json.dumps(build_service_horizon_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
