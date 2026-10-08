#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_tier_law import (
    build_service_tier_cutoff_summary,
    build_service_tier_rows,
    build_tier_count_histogram,
    build_weakening_portfolio_service_tier_law_snapshot,
    select_minimal_profile_by_width_and_service_tier,
)


def main() -> None:
    rows = build_service_tier_rows()
    assert len(rows) == 15

    width_1 = next(row for row in rows if row['portfolio_size'] == 1)
    width_7 = next(row for row in rows if row['portfolio_size'] == 7)
    width_12 = next(row for row in rows if row['portfolio_size'] == 12)

    assert width_1['exact_only_ceiling']['numerator'] == 6
    assert width_1['suffix_hitchhike_only_ceiling']['numerator'] == 11
    assert width_1['positive_service_tier_count'] == 3

    assert width_7['exact_only_ceiling']['numerator'] == 0
    assert width_7['suffix_hitchhike_only_ceiling']['numerator'] == 330
    assert width_7['suffix_hitchhike_only_ceiling']['denominator'] == 6435
    assert width_7['positive_service_tier_count'] == 2

    assert width_12['suffix_hitchhike_only_ceiling']['numerator'] == 0
    assert width_12['positive_service_tier_count'] == 1

    assert select_minimal_profile_by_width_and_service_tier(1, 0.4)['selected_profile_label'] == 'exact_only'
    assert select_minimal_profile_by_width_and_service_tier(1, 0.5)['selected_profile_label'] == 'suffix_hitchhike_only'
    assert select_minimal_profile_by_width_and_service_tier(1, 0.8)['selected_profile_label'] == 'any_single_axis_hitchhike'
    assert select_minimal_profile_by_width_and_service_tier(7, 0.01)['selected_profile_label'] == 'suffix_hitchhike_only'
    assert select_minimal_profile_by_width_and_service_tier(7, 0.06)['selected_profile_label'] == 'any_single_axis_hitchhike'
    assert select_minimal_profile_by_width_and_service_tier(12, 1e-9)['selected_profile_label'] == 'any_single_axis_hitchhike'

    assert build_tier_count_histogram() == {'1': 4, '2': 5, '3': 6}
    assert build_service_tier_cutoff_summary() == {
        'last_width_with_exact_only_positive_service': 6,
        'last_width_with_suffix_hitchhike_only_positive_service': 11,
        'first_width_with_dual_axis_as_only_positive_service_option': 12,
    }

    report = build_weakening_portfolio_service_tier_law_snapshot()
    assert report['headline_findings']['analytic_service_tier_selector_matches_exact_width_and_width_cap_selectors'] is True
    assert report['headline_findings']['service_tier_count_histogram_by_width'] == {'1': 4, '2': 5, '3': 6}
    print('weakening portfolio service tier law checks passed')


if __name__ == '__main__':
    main()
