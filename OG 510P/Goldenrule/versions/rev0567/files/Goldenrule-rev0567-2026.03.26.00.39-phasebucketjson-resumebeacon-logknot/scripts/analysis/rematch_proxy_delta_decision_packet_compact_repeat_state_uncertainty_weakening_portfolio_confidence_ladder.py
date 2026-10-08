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


class WeakeningPortfolioConfidenceLadderError(RuntimeError):
    pass


CONFIDENCE_LEVELS = [0.5, 0.75, 0.9, 0.95, 0.99, 0.999]
SUFFIX_TAIL_LEVELS = [0.5, 0.75, 0.9, 1.0]


@lru_cache(maxsize=1)
def build_portfolio_confidence_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_portfolio_width_profile_rows():
        exact = row['minimal_profile_counts']['exact_only']
        precision = row['minimal_profile_counts']['precision_hitchhike_only']
        suffix = row['minimal_profile_counts']['suffix_hitchhike_only']
        non_dual = exact + precision + suffix
        dual = row['minimal_profile_counts']['any_single_axis_hitchhike']
        dual_share = row['minimal_profile_shares']['any_single_axis_hitchhike']
        tail_profile_shares = {
            'exact_only': {
                'numerator': exact,
                'denominator': non_dual,
                'value': (exact / non_dual) if non_dual else 0.0,
            },
            'precision_hitchhike_only': {
                'numerator': precision,
                'denominator': non_dual,
                'value': (precision / non_dual) if non_dual else 0.0,
            },
            'suffix_hitchhike_only': {
                'numerator': suffix,
                'denominator': non_dual,
                'value': (suffix / non_dual) if non_dual else 0.0,
            },
        }
        rows.append(
            {
                'portfolio_size': row['portfolio_size'],
                'total_portfolios': row['total_portfolios'],
                'dual_axis_share': dual_share,
                'non_dual_share': {
                    'numerator': non_dual,
                    'denominator': row['total_portfolios'],
                    'value': non_dual / row['total_portfolios'],
                },
                'dual_axis_count': dual,
                'non_dual_count': non_dual,
                'tail_profile_shares': tail_profile_shares,
                'suffix_dominates_non_dual_tail': suffix > max(exact, precision),
                'suffix_strict_majority_of_non_dual_tail': (suffix / non_dual) > 0.5 if non_dual else False,
                'precision_tail_exceptions_still_possible': precision > 0,
                'exact_tail_exceptions_still_possible': exact > 0,
            }
        )
    return rows


def _first_width_where(predicate) -> int | None:
    for row in build_portfolio_confidence_rows():
        if predicate(row):
            return row['portfolio_size']
    return None


@lru_cache(maxsize=1)
def build_dual_axis_confidence_thresholds() -> list[dict[str, Any]]:
    thresholds: list[dict[str, Any]] = []
    for level in CONFIDENCE_LEVELS:
        width = _first_width_where(lambda row, threshold=level: row['dual_axis_share']['value'] >= threshold)
        if width is None:
            raise WeakeningPortfolioConfidenceLadderError(
                f'failed to find width achieving dual-axis confidence {level}'
            )
        thresholds.append({'confidence_level': level, 'minimum_portfolio_size': width})
    return thresholds


@lru_cache(maxsize=1)
def build_suffix_tail_confidence_thresholds() -> list[dict[str, Any]]:
    thresholds: list[dict[str, Any]] = []
    for level in SUFFIX_TAIL_LEVELS:
        width = _first_width_where(
            lambda row, threshold=level: row['tail_profile_shares']['suffix_hitchhike_only']['value'] >= threshold
            if row['non_dual_count']
            else False
        )
        if width is None:
            raise WeakeningPortfolioConfidenceLadderError(
                f'failed to find width achieving suffix-tail confidence {level}'
            )
        thresholds.append({'suffix_tail_share_level': level, 'minimum_portfolio_size': width})
    return thresholds



def build_weakening_portfolio_confidence_ladder_snapshot() -> dict[str, Any]:
    rows = build_portfolio_confidence_rows()
    dual_thresholds = build_dual_axis_confidence_thresholds()
    suffix_thresholds = build_suffix_tail_confidence_thresholds()

    dual_threshold_map = {entry['confidence_level']: entry['minimum_portfolio_size'] for entry in dual_thresholds}
    suffix_threshold_map = {entry['suffix_tail_share_level']: entry['minimum_portfolio_size'] for entry in suffix_thresholds}

    if dual_threshold_map != {0.5: 4, 0.75: 5, 0.9: 7, 0.95: 8, 0.99: 10, 0.999: 11}:
        raise WeakeningPortfolioConfidenceLadderError(
            f'unexpected dual-axis confidence ladder: {dual_threshold_map}'
        )
    if suffix_threshold_map != {0.5: 3, 0.75: 8, 0.9: 10, 1.0: 11}:
        raise WeakeningPortfolioConfidenceLadderError(
            f'unexpected suffix-tail confidence ladder: {suffix_threshold_map}'
        )

    if not all(row['suffix_dominates_non_dual_tail'] for row in rows if row['portfolio_size'] >= 2 and row['non_dual_count']):
        raise WeakeningPortfolioConfidenceLadderError('suffix-only family should dominate every non-dual tail from width 2 onward')

    example_sizes = [1, 4, 5, 7, 8, 10, 11, 12]
    example_rows = [row for row in rows if row['portfolio_size'] in example_sizes]

    return {
        'focus': 'Quantify the confidence ladder for when random width-conditioned weakening portfolios minimally require dual-axis overshoot permission, and show how the residual one-axis exception tail collapses toward the suffix-only family as width grows.',
        'headline_findings': {
            'dual_axis_confidence_thresholds': dual_threshold_map,
            'suffix_tail_confidence_thresholds': suffix_threshold_map,
            'dual_axis_majority_begins_at_width': dual_threshold_map[0.5],
            'dual_axis_ninety_percent_begins_at_width': dual_threshold_map[0.9],
            'dual_axis_ninety_nine_percent_begins_at_width': dual_threshold_map[0.99],
            'dual_axis_ninety_nine_point_nine_percent_begins_at_width': dual_threshold_map[0.999],
            'suffix_tail_strict_majority_begins_at_width': suffix_threshold_map[0.5],
            'suffix_tail_three_quarters_begins_at_width': suffix_threshold_map[0.75],
            'suffix_tail_ninety_percent_begins_at_width': suffix_threshold_map[0.9],
            'suffix_tail_purity_begins_at_width': suffix_threshold_map[1.0],
            'suffix_only_family_dominates_every_non_dual_tail_from_width_2_onward': True,
            'precision_only_tail_persists_until_width': max(
                row['portfolio_size'] for row in rows if row['precision_tail_exceptions_still_possible']
            ),
            'exact_only_tail_persists_until_width': max(
                row['portfolio_size'] for row in rows if row['exact_tail_exceptions_still_possible']
            ),
        },
        'decision_rules': [
            'Use width 4 as the first point where a random portfolio is more likely than not to minimally require dual-axis permission.',
            'Use width 7 as the first point where dual-axis permission is a 90% prior, and width 10 as the first point where it is a 99% prior.',
            'Treat widths 8-11 as the suffix-tail regime: the rare surviving one-axis exceptions are increasingly concentrated in the suffix-only family.',
            'Do not spend operator attention on exact-only tails beyond width 6 or precision-only tails beyond width 10; their residual mass is already vanishing before the universal width-12 cutoff.',
            'Treat any future shift in the confidence ladder `{4,5,7,8,10,11}` or the suffix-tail ladder `{3,8,10,11}` as a redesign signal for the current staircase and hole-family geometry.',
        ],
        'dual_axis_confidence_thresholds': dual_thresholds,
        'suffix_tail_confidence_thresholds': suffix_thresholds,
        'portfolio_confidence_rows': rows,
        'portfolio_confidence_examples': example_rows,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_confidence_ladder.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_law_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_guardrail_law_snapshot_20260308.json',
        ],
    }



def main() -> None:
    print(json.dumps(build_weakening_portfolio_confidence_ladder_snapshot(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
