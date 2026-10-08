#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_width_cap_service_guarantee import (
    build_portfolio_width_cap_service_rows,
    build_profile_monotonicity_summary,
    build_selector_equivalence_examples,
    build_width_cap_service_frontier_rows,
    select_minimal_profile_by_max_width_and_service_level,
)


def main() -> int:
    rows = build_portfolio_width_cap_service_rows()
    monotonicity = build_profile_monotonicity_summary()

    if not all(
        values[i] >= values[i + 1]
        for values in monotonicity.values()
        for i in range(len(values) - 1)
    ):
        print('portfolio-width-cap-service-guarantee: efficient profile guarantee sequences should be monotone nonincreasing', file=sys.stderr)
        return 1

    if rows[0]['guaranteed_coverage_shares']['suffix_hitchhike_only']['value'] != 11 / 15:
        print('portfolio-width-cap-service-guarantee: suffix-only best guaranteed service should be 11/15 at cap 1', file=sys.stderr)
        return 1

    frontier = {row['minimum_service_share']: row for row in build_width_cap_service_frontier_rows()}
    if frontier[0.1]['suffix_hitchhike_only_last_safe_width_cap'] != 5:
        print('portfolio-width-cap-service-guarantee: suffix-only should remain safe through cap 5 for 10% service', file=sys.stderr)
        return 1
    if frontier[0.25]['dual_axis_first_required_width_cap'] != 4:
        print('portfolio-width-cap-service-guarantee: 25% robust service should force dual-axis at cap 4', file=sys.stderr)
        return 1
    if frontier[0.5]['dual_axis_first_required_width_cap'] != 3:
        print('portfolio-width-cap-service-guarantee: 50% robust service should force dual-axis at cap 3', file=sys.stderr)
        return 1

    examples = [
        (1, 0.25, 'exact_only'),
        (1, 0.5, 'suffix_hitchhike_only'),
        (1, 0.75, 'any_single_axis_hitchhike'),
        (3, 0.25, 'suffix_hitchhike_only'),
        (4, 0.25, 'any_single_axis_hitchhike'),
        (6, 0.1, 'any_single_axis_hitchhike'),
    ]
    for width_cap, service, expected in examples:
        selected = select_minimal_profile_by_max_width_and_service_level(width_cap, service)
        if selected['selected_profile_label'] != expected:
            print(
                f'portfolio-width-cap-service-guarantee: cap {width_cap} service {service} expected {expected} but got {selected["selected_profile_label"]}',
                file=sys.stderr,
            )
            return 1

    if not all(row['selectors_coincide'] for row in build_selector_equivalence_examples()):
        print('portfolio-width-cap-service-guarantee: exact-width and width-cap selectors should coincide at the same endpoint width', file=sys.stderr)
        return 1

    print('portfolio-width-cap-service-guarantee: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
