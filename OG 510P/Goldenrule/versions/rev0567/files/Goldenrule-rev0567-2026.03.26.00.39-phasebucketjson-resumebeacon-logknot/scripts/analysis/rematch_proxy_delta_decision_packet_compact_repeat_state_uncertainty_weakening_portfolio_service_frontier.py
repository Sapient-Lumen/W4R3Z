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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law import (
    build_portfolio_width_profile_rows,
)


class WeakeningPortfolioServiceFrontierError(RuntimeError):
    pass


PROFILE_ORDER = [
    'exact_only',
    'precision_hitchhike_only',
    'suffix_hitchhike_only',
    'any_single_axis_hitchhike',
]
EFFICIENT_PROFILE_ORDER = [
    'exact_only',
    'suffix_hitchhike_only',
    'any_single_axis_hitchhike',
]
SERVICE_LEVELS = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]


@lru_cache(maxsize=1)
def build_portfolio_service_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_portfolio_width_profile_rows():
        exact = row['minimal_profile_counts']['exact_only']
        precision = row['minimal_profile_counts']['precision_hitchhike_only']
        suffix = row['minimal_profile_counts']['suffix_hitchhike_only']
        total = row['total_portfolios']
        coverage_counts = {
            'exact_only': exact,
            'precision_hitchhike_only': exact + precision,
            'suffix_hitchhike_only': exact + suffix,
            'any_single_axis_hitchhike': total,
        }
        coverage_shares = {
            label: {
                'numerator': count,
                'denominator': total,
                'value': count / total,
            }
            for label, count in coverage_counts.items()
        }
        rows.append(
            {
                'portfolio_size': row['portfolio_size'],
                'total_portfolios': total,
                'coverage_counts': coverage_counts,
                'coverage_shares': coverage_shares,
                'precision_profile_is_dominated_by_suffix_profile': (
                    coverage_counts['precision_hitchhike_only'] <= coverage_counts['suffix_hitchhike_only']
                ),
                'precision_profile_is_strictly_dominated_by_suffix_profile': (
                    coverage_counts['precision_hitchhike_only'] < coverage_counts['suffix_hitchhike_only']
                ),
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_profile_max_service_levels() -> dict[str, dict[str, Any]]:
    rows = build_portfolio_service_rows()
    result: dict[str, dict[str, Any]] = {}
    for label in PROFILE_ORDER:
        best_row = max(rows, key=lambda row, key=label: row['coverage_shares'][key]['value'])
        result[label] = {
            'maximum_coverage_share': best_row['coverage_shares'][label],
            'attained_at_portfolio_size': best_row['portfolio_size'],
        }
    return result


def select_minimal_profile_by_width_and_service_level(
    portfolio_size: int,
    minimum_service_share: float,
) -> dict[str, Any]:
    rows = build_portfolio_service_rows()
    matches = [row for row in rows if row['portfolio_size'] == portfolio_size]
    if len(matches) != 1:
        raise WeakeningPortfolioServiceFrontierError(
            f'expected one width row for {portfolio_size}, found {len(matches)}'
        )
    row = matches[0]
    for label in EFFICIENT_PROFILE_ORDER:
        share = row['coverage_shares'][label]
        if share['value'] >= minimum_service_share:
            return {
                'portfolio_size': portfolio_size,
                'minimum_service_share': minimum_service_share,
                'selected_profile_label': label,
                'selected_profile_coverage_share': share,
                'width_row': row,
            }
    raise WeakeningPortfolioServiceFrontierError(
        f'no admissible profile found for width {portfolio_size} and service share {minimum_service_share}'
    )


@lru_cache(maxsize=1)
def build_service_level_frontier_rows() -> list[dict[str, Any]]:
    rows = build_portfolio_service_rows()
    frontier_rows: list[dict[str, Any]] = []
    for level in SERVICE_LEVELS:
        exact_last = max(
            (row['portfolio_size'] for row in rows if row['coverage_shares']['exact_only']['value'] >= level),
            default=None,
        )
        suffix_last = max(
            (row['portfolio_size'] for row in rows if row['coverage_shares']['suffix_hitchhike_only']['value'] >= level),
            default=None,
        )
        dual_first = next(
            row['portfolio_size']
            for row in rows
            if row['coverage_shares']['suffix_hitchhike_only']['value'] < level
        )
        frontier_rows.append(
            {
                'minimum_service_share': level,
                'exact_only_last_sufficient_width': exact_last,
                'suffix_hitchhike_only_last_sufficient_width': suffix_last,
                'dual_axis_first_minimally_required_width': dual_first,
            }
        )
    return frontier_rows



def build_weakening_portfolio_service_frontier_snapshot() -> dict[str, Any]:
    service_rows = build_portfolio_service_rows()
    max_service = build_profile_max_service_levels()
    frontier_rows = build_service_level_frontier_rows()

    if not all(row['precision_profile_is_dominated_by_suffix_profile'] for row in service_rows):
        raise WeakeningPortfolioServiceFrontierError(
            'precision_hitchhike_only should be weakly dominated by suffix_hitchhike_only at every width'
        )
    if not all(
        row['precision_profile_is_strictly_dominated_by_suffix_profile']
        for row in service_rows
        if row['coverage_counts']['precision_hitchhike_only'] > 0 or row['coverage_counts']['suffix_hitchhike_only'] > 0
    ):
        raise WeakeningPortfolioServiceFrontierError(
            'precision_hitchhike_only should be strictly dominated by suffix_hitchhike_only whenever either one-axis profile still covers any width-conditioned mass'
        )

    max_service_map = {
        label: data['maximum_coverage_share']['value'] for label, data in max_service.items()
    }
    expected_max_service_map = {
        'exact_only': 6 / 15,
        'precision_hitchhike_only': 10 / 15,
        'suffix_hitchhike_only': 11 / 15,
        'any_single_axis_hitchhike': 1.0,
    }
    if max_service_map != expected_max_service_map:
        raise WeakeningPortfolioServiceFrontierError(
            f'unexpected profile maxima {max_service_map}'
        )

    frontier_map = {
        row['minimum_service_share']: {
            'exact_only_last_sufficient_width': row['exact_only_last_sufficient_width'],
            'suffix_hitchhike_only_last_sufficient_width': row['suffix_hitchhike_only_last_sufficient_width'],
            'dual_axis_first_minimally_required_width': row['dual_axis_first_minimally_required_width'],
        }
        for row in frontier_rows
    }
    expected_frontier_map = {
        0.1: {
            'exact_only_last_sufficient_width': 2,
            'suffix_hitchhike_only_last_sufficient_width': 5,
            'dual_axis_first_minimally_required_width': 6,
        },
        0.25: {
            'exact_only_last_sufficient_width': 1,
            'suffix_hitchhike_only_last_sufficient_width': 3,
            'dual_axis_first_minimally_required_width': 4,
        },
        0.5: {
            'exact_only_last_sufficient_width': None,
            'suffix_hitchhike_only_last_sufficient_width': 2,
            'dual_axis_first_minimally_required_width': 3,
        },
        0.75: {
            'exact_only_last_sufficient_width': None,
            'suffix_hitchhike_only_last_sufficient_width': None,
            'dual_axis_first_minimally_required_width': 1,
        },
        0.9: {
            'exact_only_last_sufficient_width': None,
            'suffix_hitchhike_only_last_sufficient_width': None,
            'dual_axis_first_minimally_required_width': 1,
        },
        0.95: {
            'exact_only_last_sufficient_width': None,
            'suffix_hitchhike_only_last_sufficient_width': None,
            'dual_axis_first_minimally_required_width': 1,
        },
        0.99: {
            'exact_only_last_sufficient_width': None,
            'suffix_hitchhike_only_last_sufficient_width': None,
            'dual_axis_first_minimally_required_width': 1,
        },
    }
    if frontier_map != expected_frontier_map:
        raise WeakeningPortfolioServiceFrontierError(
            f'unexpected service frontier {frontier_map}'
        )

    selector_examples = [
        select_minimal_profile_by_width_and_service_level(1, 0.25),
        select_minimal_profile_by_width_and_service_level(1, 0.5),
        select_minimal_profile_by_width_and_service_level(1, 0.75),
        select_minimal_profile_by_width_and_service_level(3, 0.25),
        select_minimal_profile_by_width_and_service_level(4, 0.25),
        select_minimal_profile_by_width_and_service_level(6, 0.1),
    ]

    return {
        'focus': 'Choose weakening overshoot profiles by width-conditioned service level when only batch width is known, and prune dominated profiles from the stochastic governance menu.',
        'headline_findings': {
            'profile_maximum_service_share': max_service_map,
            'precision_hitchhike_only_is_dominated_by_suffix_hitchhike_only_at_every_width': True,
            'efficient_width_only_service_frontier_profiles': EFFICIENT_PROFILE_ORDER,
            'dual_axis_is_forced_for_service_targets_above': max_service_map['suffix_hitchhike_only'],
            'service_target_0_5_dual_axis_begins_at_width': frontier_map[0.5]['dual_axis_first_minimally_required_width'],
            'service_target_0_25_dual_axis_begins_at_width': frontier_map[0.25]['dual_axis_first_minimally_required_width'],
            'suffix_hitchhike_only_last_sufficient_width_for_service_target_0_1': frontier_map[0.1]['suffix_hitchhike_only_last_sufficient_width'],
            'suffix_hitchhike_only_last_sufficient_width_for_service_target_0_25': frontier_map[0.25]['suffix_hitchhike_only_last_sufficient_width'],
            'suffix_hitchhike_only_last_sufficient_width_for_service_target_0_5': frontier_map[0.5]['suffix_hitchhike_only_last_sufficient_width'],
            'no_one_axis_profile_reaches_service_target_0_75': True,
        },
        'decision_rules': [
            'When only width is known, drop `precision_hitchhike_only` from the probabilistic governance menu: `suffix_hitchhike_only` covers at least as much width-conditioned mass at every width and strictly more whenever one-axis coverage still exists.',
            'Treat service targets above `11/15 ≈ 0.733` as immediate dual-axis cases even for singleton batches; no one-axis profile can ever reach them under the current hole-family geometry.',
            'Use `suffix_hitchhike_only` only for low or moderate service targets on tiny batches: up to width `5` for a 10% target, up to width `3` for a 25% target, and up to width `2` for a 50% target.',
            'Use `exact_only` only for extremely conservative low-service governance: it reaches 10% coverage only through width `2` and 25% coverage only at width `1`.',
            'Treat any future width where `precision_hitchhike_only` beats or ties `suffix_hitchhike_only` on frontier efficiency, or any future one-axis service maximum above `11/15`, as an immediate redesign signal for the current staircase and hole-family asymmetry.',
        ],
        'profile_max_service_levels': max_service,
        'service_level_frontier_rows': frontier_rows,
        'portfolio_service_rows': service_rows,
        'selector_examples': selector_examples,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_service_frontier_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
