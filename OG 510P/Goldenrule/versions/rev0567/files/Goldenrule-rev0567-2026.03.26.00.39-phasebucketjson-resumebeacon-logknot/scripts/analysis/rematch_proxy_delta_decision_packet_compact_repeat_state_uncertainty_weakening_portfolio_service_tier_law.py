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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law import (
    build_admissible_family_sizes,
    coverage_share_from_family_size,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier import (
    select_minimal_profile_by_width_and_service_level,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee import (
    select_minimal_profile_by_max_width_and_service_level,
)


class WeakeningPortfolioServiceTierLawError(RuntimeError):
    pass


UNIVERSE_SIZE = 15
EFFICIENT_PROFILE_ORDER = [
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
        raise WeakeningPortfolioServiceTierLawError(
            f'unexpected efficient family sizes: {efficient}'
        )
    return efficient


@lru_cache(maxsize=1)
def build_service_tier_rows() -> list[dict[str, Any]]:
    family_sizes = build_efficient_family_sizes()
    rows: list[dict[str, Any]] = []
    for width in range(1, UNIVERSE_SIZE + 1):
        exact_ceiling = coverage_share_from_family_size(
            family_sizes['exact_only'], width, UNIVERSE_SIZE
        )
        suffix_ceiling = coverage_share_from_family_size(
            family_sizes['suffix_hitchhike_only'], width, UNIVERSE_SIZE
        )
        dual_ceiling = coverage_share_from_family_size(
            family_sizes['any_single_axis_hitchhike'], width, UNIVERSE_SIZE
        )
        if exact_ceiling['value'] > 0.0:
            positive_tier_count = 3
        elif suffix_ceiling['value'] > 0.0:
            positive_tier_count = 2
        else:
            positive_tier_count = 1
        rows.append(
            {
                'portfolio_size': width,
                'exact_only_ceiling': exact_ceiling,
                'suffix_hitchhike_only_ceiling': suffix_ceiling,
                'dual_axis_ceiling': dual_ceiling,
                'positive_service_tier_count': positive_tier_count,
                'exact_only_is_positive_option': exact_ceiling['value'] > 0.0,
                'suffix_hitchhike_only_is_positive_option': suffix_ceiling['value'] > 0.0,
                'dual_axis_is_always_positive_option': True,
                'minimal_profile_regions': _build_minimal_profile_regions(
                    width, exact_ceiling, suffix_ceiling
                ),
            }
        )
    return rows


def _build_minimal_profile_regions(
    width: int,
    exact_ceiling: dict[str, Any],
    suffix_ceiling: dict[str, Any],
) -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    regions.append(
        {
            'profile_label': 'exact_only',
            'interval_kind': 'closed',
            'lower_bound': 0.0,
            'upper_bound': exact_ceiling,
            'width': width,
        }
    )
    if suffix_ceiling['value'] > exact_ceiling['value']:
        regions.append(
            {
                'profile_label': 'suffix_hitchhike_only',
                'interval_kind': 'left_open_right_closed',
                'lower_bound': exact_ceiling,
                'upper_bound': suffix_ceiling,
                'width': width,
            }
        )
    regions.append(
        {
            'profile_label': 'any_single_axis_hitchhike',
            'interval_kind': 'left_open_right_closed',
            'lower_bound': suffix_ceiling,
            'upper_bound': {'numerator': 1, 'denominator': 1, 'value': 1.0},
            'width': width,
        }
    )
    return regions


def select_minimal_profile_by_width_and_service_tier(
    portfolio_size: int,
    minimum_service_share: float,
) -> dict[str, Any]:
    if minimum_service_share < 0.0 or minimum_service_share > 1.0:
        raise WeakeningPortfolioServiceTierLawError(
            f'minimum service share must lie in [0, 1], received {minimum_service_share}'
        )
    rows = build_service_tier_rows()
    matches = [row for row in rows if row['portfolio_size'] == portfolio_size]
    if len(matches) != 1:
        raise WeakeningPortfolioServiceTierLawError(
            f'expected one service-tier row for width {portfolio_size}, found {len(matches)}'
        )
    row = matches[0]
    exact_ceiling = row['exact_only_ceiling']
    suffix_ceiling = row['suffix_hitchhike_only_ceiling']
    if minimum_service_share <= exact_ceiling['value']:
        label = 'exact_only'
        ceiling = exact_ceiling
    elif minimum_service_share <= suffix_ceiling['value']:
        label = 'suffix_hitchhike_only'
        ceiling = suffix_ceiling
    else:
        label = 'any_single_axis_hitchhike'
        ceiling = row['dual_axis_ceiling']
    return {
        'portfolio_size': portfolio_size,
        'minimum_service_share': minimum_service_share,
        'selected_profile_label': label,
        'selected_profile_ceiling': ceiling,
        'service_tier_row': row,
    }


@lru_cache(maxsize=1)
def build_selector_examples() -> list[dict[str, Any]]:
    rows = build_service_tier_rows()
    examples: list[dict[str, Any]] = []
    for width in [1, 3, 6, 7, 11, 12]:
        row = next(r for r in rows if r['portfolio_size'] == width)
        exact = row['exact_only_ceiling']['value']
        suffix = row['suffix_hitchhike_only_ceiling']['value']
        probe_targets = sorted(
            {
                0.0,
                exact,
                min(1.0, exact + 1e-9),
                suffix,
                min(1.0, suffix + 1e-9),
            }
        )
        for target in probe_targets:
            selection = select_minimal_profile_by_width_and_service_tier(width, target)
            examples.append(
                {
                    'portfolio_size': width,
                    'minimum_service_share': target,
                    'selected_profile_label': selection['selected_profile_label'],
                }
            )
    return examples


@lru_cache(maxsize=1)
def build_service_tier_cutoff_summary() -> dict[str, int]:
    rows = build_service_tier_rows()
    return {
        'last_width_with_exact_only_positive_service': max(
            row['portfolio_size'] for row in rows if row['exact_only_is_positive_option']
        ),
        'last_width_with_suffix_hitchhike_only_positive_service': max(
            row['portfolio_size']
            for row in rows
            if row['suffix_hitchhike_only_is_positive_option']
        ),
        'first_width_with_dual_axis_as_only_positive_service_option': min(
            row['portfolio_size']
            for row in rows
            if row['positive_service_tier_count'] == 1
        ),
    }


@lru_cache(maxsize=1)
def build_tier_count_histogram() -> dict[str, int]:
    histogram = {'1': 0, '2': 0, '3': 0}
    for row in build_service_tier_rows():
        histogram[str(row['positive_service_tier_count'])] += 1
    return histogram


def build_weakening_portfolio_service_tier_law_snapshot() -> dict[str, Any]:
    rows = build_service_tier_rows()
    family_sizes = build_efficient_family_sizes()
    tier_count_histogram = build_tier_count_histogram()
    cutoff_summary = build_service_tier_cutoff_summary()
    selector_examples = build_selector_examples()

    for width in range(1, UNIVERSE_SIZE + 1):
        test_targets = [
            0.0,
            1e-12,
            0.05,
            0.1,
            0.25,
            0.5,
            0.7333333333333333,
            0.75,
            0.9,
            0.99,
            1.0,
        ]
        row = next(r for r in rows if r['portfolio_size'] == width)
        exact_ceiling = row['exact_only_ceiling']['value']
        suffix_ceiling = row['suffix_hitchhike_only_ceiling']['value']
        test_targets.extend([
            exact_ceiling,
            min(1.0, exact_ceiling + 1e-12),
            suffix_ceiling,
            min(1.0, suffix_ceiling + 1e-12),
        ])
        for target in sorted(set(test_targets)):
            analytic = select_minimal_profile_by_width_and_service_tier(width, target)
            enumerated = select_minimal_profile_by_width_and_service_level(width, target)
            width_cap = select_minimal_profile_by_max_width_and_service_level(width, target)
            if analytic['selected_profile_label'] != enumerated['selected_profile_label']:
                raise WeakeningPortfolioServiceTierLawError(
                    f'analytic selector drifted from exact-width selector at width {width} and target {target}'
                )
            if analytic['selected_profile_label'] != width_cap['selected_profile_label']:
                raise WeakeningPortfolioServiceTierLawError(
                    f'analytic selector drifted from width-cap selector at width {width} and target {target}'
                )

    if tier_count_histogram != {'1': 4, '2': 5, '3': 6}:
        raise WeakeningPortfolioServiceTierLawError(
            f'unexpected service-tier-count histogram: {tier_count_histogram}'
        )

    if cutoff_summary != {
        'last_width_with_exact_only_positive_service': 6,
        'last_width_with_suffix_hitchhike_only_positive_service': 11,
        'first_width_with_dual_axis_as_only_positive_service_option': 12,
    }:
        raise WeakeningPortfolioServiceTierLawError(
            f'unexpected service-tier cutoff summary: {cutoff_summary}'
        )

    return {
        'focus': 'Collapse width-conditioned and width-cap weakening SLA planning to two exact service breakpoints per width: the exact-only ceiling and the one-axis suffix ceiling.',
        'headline_findings': {
            'efficient_profile_family_sizes': family_sizes,
            'service_tier_breakpoints_are_exact_choose_ratios': True,
            'exact_only_ceiling_formula': 'C(6, w) / C(15, w)',
            'suffix_hitchhike_only_ceiling_formula': 'C(11, w) / C(15, w)',
            'analytic_service_tier_selector_matches_exact_width_and_width_cap_selectors': True,
            'service_tier_count_histogram_by_width': tier_count_histogram,
            'last_width_with_exact_only_positive_service': cutoff_summary['last_width_with_exact_only_positive_service'],
            'last_width_with_suffix_hitchhike_only_positive_service': cutoff_summary['last_width_with_suffix_hitchhike_only_positive_service'],
            'first_width_with_dual_axis_as_only_positive_service_option': cutoff_summary['first_width_with_dual_axis_as_only_positive_service_option'],
        },
        'decision_rules': [
            'At any exact width or width cap `w`, compare the target service share only to two exact breakpoints: `C(6,w)/C(15,w)` and `C(11,w)/C(15,w)`.',
            'If the target service share is at most `C(6,w)/C(15,w)`, choose `exact_only`; if it exceeds that but is at most `C(11,w)/C(15,w)`, choose `suffix_hitchhike_only`; otherwise choose `any_single_axis_hitchhike`.',
            'Treat widths `1` through `6` as true three-tier SLA menus, widths `7` through `11` as two-tier menus where exact-only has already vanished, and widths `12` through `15` as dual-axis-only for any positive service target.',
            'Reuse the same analytic selector for width caps because capped-width guarantees already collapse losslessly to endpoint width under the current staircase.',
            'Treat any future width where more than two breakpoints are needed, or where the analytic two-breakpoint selector diverges from the exact-width or width-cap selectors, as an immediate redesign signal for the weakening portfolio geometry.',
        ],
        'service_tier_cutoff_summary': cutoff_summary,
        'service_tier_rows': rows,
        'selector_examples': selector_examples,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee_snapshot_20260308.json',
        ],
    }


def main() -> None:
    print(json.dumps(build_weakening_portfolio_service_tier_law_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
