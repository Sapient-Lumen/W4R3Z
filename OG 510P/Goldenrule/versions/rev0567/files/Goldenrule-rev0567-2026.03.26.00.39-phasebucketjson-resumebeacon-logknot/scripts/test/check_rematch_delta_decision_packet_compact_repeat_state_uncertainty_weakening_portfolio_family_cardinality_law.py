#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_family_cardinality_law import (
    build_admissible_family_sizes,
    build_closed_form_service_rows,
    build_weakening_portfolio_family_cardinality_law_snapshot,
)


def main() -> None:
    family_sizes = build_admissible_family_sizes()
    assert family_sizes == {
        'exact_only': 6,
        'precision_hitchhike_only': 10,
        'suffix_hitchhike_only': 11,
        'any_single_axis_hitchhike': 15,
    }

    rows = build_closed_form_service_rows()
    suffix_width_1 = next(row for row in rows if row['portfolio_size'] == 1)['closed_form_coverage_shares']['suffix_hitchhike_only']
    exact_width_6 = next(row for row in rows if row['portfolio_size'] == 6)['closed_form_coverage_shares']['exact_only']
    suffix_width_12 = next(row for row in rows if row['portfolio_size'] == 12)['closed_form_coverage_shares']['suffix_hitchhike_only']

    assert suffix_width_1['numerator'] == 11 and suffix_width_1['denominator'] == 15
    assert exact_width_6['numerator'] == 1 and exact_width_6['denominator'] == 5005
    assert suffix_width_12['numerator'] == 0 and suffix_width_12['denominator'] == 455

    report = build_weakening_portfolio_family_cardinality_law_snapshot()
    assert report['headline_findings']['service_share_formula'] == 'coverage(width, profile) = C(admissible_family_size(profile), width) / C(15, width)'
    assert report['headline_findings']['suffix_minus_precision_family_gap'] == 1
    assert report['headline_findings']['best_one_axis_singleton_service_ceiling'] == 11 / 15
    print('weakening portfolio family cardinality law checks passed')


if __name__ == '__main__':
    main()
