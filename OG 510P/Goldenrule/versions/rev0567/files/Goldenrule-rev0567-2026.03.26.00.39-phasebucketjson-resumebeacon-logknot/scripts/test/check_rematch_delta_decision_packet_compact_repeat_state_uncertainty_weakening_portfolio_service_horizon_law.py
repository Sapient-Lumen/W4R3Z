#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_law import (
    build_horizon_cutoff_summary,
    build_positive_service_horizon_bands,
    build_service_horizon_snapshot,
    select_upgrade_schedule_by_minimum_service_share,
)


def main() -> None:
    schedule_50 = select_upgrade_schedule_by_minimum_service_share(0.5)
    assert schedule_50['exact_only_support_horizon'] == 0
    assert schedule_50['suffix_hitchhike_only_support_horizon'] == 2
    assert schedule_50['first_width_requiring_any_single_axis_hitchhike'] == 3

    schedule_10 = select_upgrade_schedule_by_minimum_service_share(0.1)
    assert schedule_10['exact_only_support_horizon'] == 2
    assert schedule_10['suffix_hitchhike_only_support_horizon'] == 5
    assert schedule_10['minimal_profile_width_bands'] == [
        {'profile_label': 'exact_only', 'start_width': 1, 'end_width': 2},
        {'profile_label': 'suffix_hitchhike_only', 'start_width': 3, 'end_width': 5},
        {'profile_label': 'any_single_axis_hitchhike', 'start_width': 6, 'end_width': 15},
    ]

    schedule_001 = select_upgrade_schedule_by_minimum_service_share(0.01)
    assert schedule_001['exact_only_support_horizon'] == 4
    assert schedule_001['suffix_hitchhike_only_support_horizon'] == 9
    assert schedule_001['first_width_requiring_any_single_axis_hitchhike'] == 10

    schedule_0 = select_upgrade_schedule_by_minimum_service_share(0.0)
    assert schedule_0['exact_only_support_horizon'] == 15
    assert schedule_0['suffix_hitchhike_only_support_horizon'] == 15
    assert schedule_0['first_width_requiring_any_single_axis_hitchhike'] == 0

    bands = build_positive_service_horizon_bands()
    assert len(bands) == 17
    assert bands[0]['exact_only_support_horizon'] == 0
    assert bands[0]['suffix_hitchhike_only_support_horizon'] == 0
    assert bands[-1]['exact_only_support_horizon'] == 6
    assert bands[-1]['suffix_hitchhike_only_support_horizon'] == 11

    assert build_horizon_cutoff_summary() == {
        'maximum_exact_only_support_horizon': 15,
        'maximum_suffix_hitchhike_only_support_horizon': 15,
        'minimum_positive_service_target_forcing_dual_axis_at_width_1_numerator': 11,
        'minimum_positive_service_target_forcing_dual_axis_at_width_1_denominator': 15,
    }

    report = build_service_horizon_snapshot()
    assert report['headline_findings']['positive_service_horizon_band_count'] == 17
    assert report['headline_findings']['analytic_horizon_selector_matches_width_and_width_cap_selectors'] is True
    print('weakening portfolio service horizon law checks passed')


if __name__ == '__main__':
    main()
