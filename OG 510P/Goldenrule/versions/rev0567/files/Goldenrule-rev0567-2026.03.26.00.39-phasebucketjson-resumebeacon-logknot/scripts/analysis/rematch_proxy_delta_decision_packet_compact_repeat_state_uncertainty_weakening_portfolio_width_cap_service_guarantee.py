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

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier import (
    EFFICIENT_PROFILE_ORDER,
    SERVICE_LEVELS,
    build_portfolio_service_rows,
    select_minimal_profile_by_width_and_service_level,
)


class WeakeningPortfolioWidthCapServiceGuaranteeError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def build_portfolio_width_cap_service_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_portfolio_service_rows():
        rows.append(
            {
                'maximum_portfolio_size': row['portfolio_size'],
                'worst_case_width': row['portfolio_size'],
                'guaranteed_coverage_counts': row['coverage_counts'],
                'guaranteed_coverage_shares': row['coverage_shares'],
                'reused_exact_width_row_without_loss': True,
            }
        )
    return rows


@lru_cache(maxsize=1)
def build_profile_monotonicity_summary() -> dict[str, list[float]]:
    rows = build_portfolio_width_cap_service_rows()
    summary: dict[str, list[float]] = {}
    for label in EFFICIENT_PROFILE_ORDER:
        summary[label] = [row['guaranteed_coverage_shares'][label]['value'] for row in rows]
    return summary


def select_minimal_profile_by_max_width_and_service_level(
    maximum_portfolio_size: int,
    minimum_service_share: float,
) -> dict[str, Any]:
    rows = build_portfolio_width_cap_service_rows()
    matches = [row for row in rows if row['maximum_portfolio_size'] == maximum_portfolio_size]
    if len(matches) != 1:
        raise WeakeningPortfolioWidthCapServiceGuaranteeError(
            f'expected one width-cap row for {maximum_portfolio_size}, found {len(matches)}'
        )
    row = matches[0]
    for label in EFFICIENT_PROFILE_ORDER:
        share = row['guaranteed_coverage_shares'][label]
        if share['value'] >= minimum_service_share:
            return {
                'maximum_portfolio_size': maximum_portfolio_size,
                'minimum_service_share': minimum_service_share,
                'selected_profile_label': label,
                'selected_profile_guaranteed_share': share,
                'width_cap_row': row,
            }
    raise WeakeningPortfolioWidthCapServiceGuaranteeError(
        f'no admissible profile found for width cap {maximum_portfolio_size} and service share {minimum_service_share}'
    )


@lru_cache(maxsize=1)
def build_width_cap_service_frontier_rows() -> list[dict[str, Any]]:
    rows = build_portfolio_width_cap_service_rows()
    frontier_rows: list[dict[str, Any]] = []
    for level in SERVICE_LEVELS:
        exact_last = max(
            (
                row['maximum_portfolio_size']
                for row in rows
                if row['guaranteed_coverage_shares']['exact_only']['value'] >= level
            ),
            default=None,
        )
        suffix_last = max(
            (
                row['maximum_portfolio_size']
                for row in rows
                if row['guaranteed_coverage_shares']['suffix_hitchhike_only']['value'] >= level
            ),
            default=None,
        )
        dual_first = next(
            row['maximum_portfolio_size']
            for row in rows
            if row['guaranteed_coverage_shares']['suffix_hitchhike_only']['value'] < level
        )
        frontier_rows.append(
            {
                'minimum_service_share': level,
                'exact_only_last_safe_width_cap': exact_last,
                'suffix_hitchhike_only_last_safe_width_cap': suffix_last,
                'dual_axis_first_required_width_cap': dual_first,
            }
        )
    return frontier_rows


@lru_cache(maxsize=1)
def build_selector_equivalence_examples() -> list[dict[str, Any]]:
    examples: list[tuple[int, float]] = [
        (1, 0.25),
        (1, 0.5),
        (1, 0.75),
        (3, 0.25),
        (4, 0.25),
        (6, 0.1),
    ]
    rows: list[dict[str, Any]] = []
    for width, service in examples:
        exact = select_minimal_profile_by_width_and_service_level(width, service)
        cap = select_minimal_profile_by_max_width_and_service_level(width, service)
        rows.append(
            {
                'width': width,
                'minimum_service_share': service,
                'exact_width_selected_profile_label': exact['selected_profile_label'],
                'width_cap_selected_profile_label': cap['selected_profile_label'],
                'selectors_coincide': exact['selected_profile_label'] == cap['selected_profile_label'],
            }
        )
    return rows



def build_weakening_portfolio_width_cap_service_guarantee_snapshot() -> dict[str, Any]:
    rows = build_portfolio_width_cap_service_rows()
    monotonicity = build_profile_monotonicity_summary()
    frontier_rows = build_width_cap_service_frontier_rows()
    selector_examples = build_selector_equivalence_examples()

    if not all(
        values[i] >= values[i + 1]
        for values in monotonicity.values()
        for i in range(len(values) - 1)
    ):
        raise WeakeningPortfolioWidthCapServiceGuaranteeError(
            'all efficient profile guarantees should be monotone nonincreasing in the width cap'
        )

    source_rows = build_portfolio_service_rows()
    for cap_row, exact_row in zip(rows, source_rows, strict=True):
        if cap_row['maximum_portfolio_size'] != exact_row['portfolio_size']:
            raise WeakeningPortfolioWidthCapServiceGuaranteeError('width-cap row misaligned with exact-width row')
        if cap_row['guaranteed_coverage_shares'] != exact_row['coverage_shares']:
            raise WeakeningPortfolioWidthCapServiceGuaranteeError(
                'width-cap guarantee row should exactly reuse the endpoint exact-width service row'
            )

    frontier_map = {
        row['minimum_service_share']: {
            'exact_only_last_safe_width_cap': row['exact_only_last_safe_width_cap'],
            'suffix_hitchhike_only_last_safe_width_cap': row['suffix_hitchhike_only_last_safe_width_cap'],
            'dual_axis_first_required_width_cap': row['dual_axis_first_required_width_cap'],
        }
        for row in frontier_rows
    }
    expected_frontier_map = {
        0.1: {
            'exact_only_last_safe_width_cap': 2,
            'suffix_hitchhike_only_last_safe_width_cap': 5,
            'dual_axis_first_required_width_cap': 6,
        },
        0.25: {
            'exact_only_last_safe_width_cap': 1,
            'suffix_hitchhike_only_last_safe_width_cap': 3,
            'dual_axis_first_required_width_cap': 4,
        },
        0.5: {
            'exact_only_last_safe_width_cap': None,
            'suffix_hitchhike_only_last_safe_width_cap': 2,
            'dual_axis_first_required_width_cap': 3,
        },
        0.75: {
            'exact_only_last_safe_width_cap': None,
            'suffix_hitchhike_only_last_safe_width_cap': None,
            'dual_axis_first_required_width_cap': 1,
        },
        0.9: {
            'exact_only_last_safe_width_cap': None,
            'suffix_hitchhike_only_last_safe_width_cap': None,
            'dual_axis_first_required_width_cap': 1,
        },
        0.95: {
            'exact_only_last_safe_width_cap': None,
            'suffix_hitchhike_only_last_safe_width_cap': None,
            'dual_axis_first_required_width_cap': 1,
        },
        0.99: {
            'exact_only_last_safe_width_cap': None,
            'suffix_hitchhike_only_last_safe_width_cap': None,
            'dual_axis_first_required_width_cap': 1,
        },
    }
    if frontier_map != expected_frontier_map:
        raise WeakeningPortfolioWidthCapServiceGuaranteeError(
            f'unexpected width-cap frontier {frontier_map}'
        )

    if not all(row['selectors_coincide'] for row in selector_examples):
        raise WeakeningPortfolioWidthCapServiceGuaranteeError(
            'exact-width and width-cap selectors should coincide at matching endpoint widths'
        )

    return {
        'focus': 'Choose weakening overshoot profiles by guaranteed service over any batch width up to a cap, and show that robust width-cap planning collapses losslessly to the worst-case endpoint width.',
        'headline_findings': {
            'robust_width_cap_planning_reuses_the_endpoint_exact_width_row_without_loss': True,
            'efficient_profile_guarantees_are_monotone_nonincreasing_in_width_cap': True,
            'best_one_axis_guaranteed_service_ceiling': 11 / 15,
            'suffix_hitchhike_only_last_safe_width_cap_for_service_target_0_1': frontier_map[0.1]['suffix_hitchhike_only_last_safe_width_cap'],
            'suffix_hitchhike_only_last_safe_width_cap_for_service_target_0_25': frontier_map[0.25]['suffix_hitchhike_only_last_safe_width_cap'],
            'suffix_hitchhike_only_last_safe_width_cap_for_service_target_0_5': frontier_map[0.5]['suffix_hitchhike_only_last_safe_width_cap'],
            'dual_axis_first_required_width_cap_for_service_target_0_5': frontier_map[0.5]['dual_axis_first_required_width_cap'],
            'service_targets_above_11_over_15_force_dual_axis_even_for_width_cap_1': True,
            'selector_equivalence_examples_all_match': True,
        },
        'decision_rules': [
            'When the only width information is an upper bound `W`, evaluate guaranteed service at width `W`; no additional set-level width modeling is needed because every efficient profile is monotone nonincreasing in the cap.',
            'Treat the existing width-conditioned frontier as a robust guarantee frontier as well: exact-width selection at width `W` and width-cap selection for any width up to `W` are identical under the current staircase.',
            'Use `suffix_hitchhike_only` only on tiny capped workloads with low service targets: through cap `5` for a 10% guarantee, through cap `3` for a 25% guarantee, and through cap `2` for a 50% guarantee.',
            'Treat any service target above `11/15 ≈ 0.733` as an immediate dual-axis requirement even under capped uncertainty; no one-axis profile can guarantee more than that even at cap `1`.',
            'Treat any future nonmonotone width-cap guarantee sequence, or any future divergence between exact-width and width-cap selectors at the same endpoint width, as an immediate redesign signal for the current batch-width geometry.',
        ],
        'profile_monotonicity_summary': monotonicity,
        'width_cap_service_frontier_rows': frontier_rows,
        'portfolio_width_cap_service_rows': rows,
        'selector_equivalence_examples': selector_examples,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_overshoot_axis_guardrails_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_width_cap_service_guarantee_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
