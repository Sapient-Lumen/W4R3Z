#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_frontier import (
    build_portfolio_service_rows,
    build_profile_max_service_levels,
    build_service_level_frontier_rows,
    select_minimal_profile_by_width_and_service_level,
)


def main() -> int:
    rows = build_portfolio_service_rows()
    if not all(row['precision_profile_is_dominated_by_suffix_profile'] for row in rows):
        print('portfolio-service-frontier: precision profile should be weakly dominated by suffix profile at every width', file=sys.stderr)
        return 1
    if not all(
        row['precision_profile_is_strictly_dominated_by_suffix_profile']
        for row in rows
        if row['coverage_counts']['precision_hitchhike_only'] > 0 or row['coverage_counts']['suffix_hitchhike_only'] > 0
    ):
        print('portfolio-service-frontier: precision profile should be strictly dominated while one-axis coverage remains', file=sys.stderr)
        return 1

    maxima = {
        label: row['maximum_coverage_share']['value']
        for label, row in build_profile_max_service_levels().items()
    }
    expected_maxima = {
        'exact_only': 6 / 15,
        'precision_hitchhike_only': 10 / 15,
        'suffix_hitchhike_only': 11 / 15,
        'any_single_axis_hitchhike': 1.0,
    }
    if maxima != expected_maxima:
        print(f'portfolio-service-frontier: unexpected maxima {maxima}', file=sys.stderr)
        return 1

    frontier = {
        row['minimum_service_share']: row
        for row in build_service_level_frontier_rows()
    }
    if frontier[0.5]['dual_axis_first_minimally_required_width'] != 3:
        print('portfolio-service-frontier: 50% service should force dual-axis by width 3', file=sys.stderr)
        return 1
    if frontier[0.25]['suffix_hitchhike_only_last_sufficient_width'] != 3:
        print('portfolio-service-frontier: suffix-only should last through width 3 for 25% service', file=sys.stderr)
        return 1
    if frontier[0.75]['dual_axis_first_minimally_required_width'] != 1:
        print('portfolio-service-frontier: 75% service should force dual-axis immediately', file=sys.stderr)
        return 1

    examples = [
        (1, 0.25, 'exact_only'),
        (1, 0.5, 'suffix_hitchhike_only'),
        (1, 0.75, 'any_single_axis_hitchhike'),
        (3, 0.25, 'suffix_hitchhike_only'),
        (4, 0.25, 'any_single_axis_hitchhike'),
        (6, 0.1, 'any_single_axis_hitchhike'),
    ]
    for width, service, expected in examples:
        selected = select_minimal_profile_by_width_and_service_level(width, service)
        if selected['selected_profile_label'] != expected:
            print(
                f'portfolio-service-frontier: width {width} service {service} expected {expected} but got {selected["selected_profile_label"]}',
                file=sys.stderr,
            )
            return 1

    print('portfolio-service-frontier: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
