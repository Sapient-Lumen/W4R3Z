#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law import (
    PROFILE_ORDER,
    build_demand_family_catalog,
    build_portfolio_demand_universe,
    select_minimal_guardrail_profile_for_portfolio,
)


class WeakeningPortfolioWidthLawError(RuntimeError):
    pass


def _comb(n: int, k: int) -> int:
    if k < 0 or n < k:
        return 0
    return math.comb(n, k)


@lru_cache(maxsize=1)
def build_portfolio_width_profile_rows() -> list[dict[str, Any]]:
    catalog = build_demand_family_catalog()
    exact_count = len(catalog['exact_only'])
    precision_count = len(catalog['precision_hitchhike_only'])
    suffix_count = len(catalog['suffix_hitchhike_only'])
    universe_size = len(build_portfolio_demand_universe())

    rows: list[dict[str, Any]] = []
    for portfolio_size in range(1, universe_size + 1):
        total = _comb(universe_size, portfolio_size)
        exact_only = _comb(exact_count, portfolio_size)
        precision_only = _comb(exact_count + precision_count, portfolio_size) - exact_only
        suffix_only = _comb(exact_count + suffix_count, portfolio_size) - exact_only
        dual_axis = total - (exact_only + precision_only + suffix_only)
        minimal_counts = {
            'exact_only': exact_only,
            'precision_hitchhike_only': precision_only,
            'suffix_hitchhike_only': suffix_only,
            'any_single_axis_hitchhike': dual_axis,
        }
        minimal_shares = {
            label: {
                'numerator': count,
                'denominator': total,
                'value': count / total,
            }
            for label, count in minimal_counts.items()
        }
        rows.append(
            {
                'portfolio_size': portfolio_size,
                'total_portfolios': total,
                'minimal_profile_counts': minimal_counts,
                'minimal_profile_shares': minimal_shares,
                'dual_axis_majority': dual_axis > (total / 2),
                'dual_axis_universal': dual_axis == total,
                'exact_only_still_possible': exact_only > 0,
                'precision_only_still_possible': precision_only > 0,
                'suffix_only_still_possible': suffix_only > 0,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_portfolio_width_profile_rows_enumerated() -> list[dict[str, Any]]:
    universe = build_portfolio_demand_universe()
    rows: list[dict[str, Any]] = []
    for portfolio_size in range(1, len(universe) + 1):
        counts = Counter()
        for combo in combinations(universe, portfolio_size):
            selection = select_minimal_guardrail_profile_for_portfolio(list(combo))
            counts[selection['minimal_profile_label']] += 1
        rows.append(
            {
                'portfolio_size': portfolio_size,
                'total_portfolios': sum(counts.values()),
                'minimal_profile_counts': {label: counts.get(label, 0) for label in PROFILE_ORDER},
            }
        )
    return rows


def _size_where(predicate) -> int | None:
    for row in build_portfolio_width_profile_rows():
        if predicate(row):
            return row['portfolio_size']
    return None



def build_weakening_portfolio_width_law_snapshot() -> dict[str, Any]:
    closed_form_rows = build_portfolio_width_profile_rows()
    enumerated_rows = build_portfolio_width_profile_rows_enumerated()
    if [
        (row['portfolio_size'], row['total_portfolios'], row['minimal_profile_counts'])
        for row in closed_form_rows
    ] != [
        (row['portfolio_size'], row['total_portfolios'], row['minimal_profile_counts'])
        for row in enumerated_rows
    ]:
        raise WeakeningPortfolioWidthLawError('closed-form width partition drifted from enumeration')

    dual_axis_majority_size = _size_where(lambda row: row['dual_axis_majority'])
    dual_axis_universal_size = _size_where(lambda row: row['dual_axis_universal'])
    exact_only_last_possible = max(
        row['portfolio_size'] for row in closed_form_rows if row['exact_only_still_possible']
    )
    precision_only_last_possible = max(
        row['portfolio_size'] for row in closed_form_rows if row['precision_only_still_possible']
    )
    suffix_only_last_possible = max(
        row['portfolio_size'] for row in closed_form_rows if row['suffix_only_still_possible']
    )

    example_sizes = [1, 4, 11, 12]
    example_rows = [row for row in closed_form_rows if row['portfolio_size'] in example_sizes]

    return {
        'focus': 'Condition the weakening overshoot-axis guardrail law on portfolio width so inheritors can choose admission profiles by batch size instead of only by pointwise or aggregate family logic.',
        'headline_findings': {
            'portfolio_width_count': len(closed_form_rows),
            'dual_axis_majority_begins_at_portfolio_size': dual_axis_majority_size,
            'dual_axis_universality_begins_at_portfolio_size': dual_axis_universal_size,
            'exact_only_last_possible_portfolio_size': exact_only_last_possible,
            'precision_only_last_possible_portfolio_size': precision_only_last_possible,
            'suffix_only_last_possible_portfolio_size': suffix_only_last_possible,
            'size_11_last_non_dual_axis_exception_count': next(
                row['minimal_profile_counts']['suffix_hitchhike_only']
                for row in closed_form_rows
                if row['portfolio_size'] == 11
            ),
            'size_12_and_above_force_dual_axis_permission': True,
            'closed_form_width_partition_matches_enumeration': True,
        },
        'decision_rules': [
            'Treat portfolio size 1 as the only width where dual-axis permission is never minimally required.',
            'By portfolio size 4, dual-axis permission is already the majority minimal profile, so broad mixed workloads should default to it unless the batch is deliberately curated.',
            'By portfolio size 12, dual-axis permission is universal because no one-axis family can cover that many distinct primitive demands.',
            'Exact-only governance is impossible beyond width 6; precision-only governance is impossible beyond width 10; suffix-only governance is impossible beyond width 11.',
            'Use width-conditioned profile shares as a workload prior: larger batches should be governed by the dual-axis profile unless there is an explicit reason to keep them one-family pure.',
        ],
        'portfolio_width_profile_rows': closed_form_rows,
        'portfolio_width_examples': example_rows,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_width_law_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
