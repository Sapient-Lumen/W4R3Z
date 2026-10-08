#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {row['required_gain_share_floor_interval']: row for row in report['support_rows']}
    assert findings['support_cliffs_by_floor'] == [
        {'floor_exclusive': 0.870482, 'removed_exact_dwell_support': '[19, 32]'},
        {'floor_exclusive': 0.980481, 'removed_exact_dwell_support': '[8, 18]'},
        {'floor_exclusive': 0.999822, 'removed_exact_dwell_support': '{2}'},
    ]
    assert findings['widest_live_support_interval'] == '{2} ∪ [8, 32]'
    assert findings['middle_interval_live_support'] == '{2} ∪ [8, 18]'
    assert findings['highest_floor_with_non_fragile_support'] == 0.980481
    assert findings['singleton_precision_support_interval'] == '{2}'
    assert findings['internal_exact_gap_persists_below_near_exact'] == '[3, 7]'
    assert findings['no_current_exact_support_above_floor'] == '(0.999822, 1.000000]'
    assert findings['supported_dwell_counts_descending_by_floor_interval'] == [
        {'required_gain_share_floor_interval': '[0, 0.870482]', 'supported_dwell_count_unique_appends': 26},
        {'required_gain_share_floor_interval': '(0.870482, 0.980481]', 'supported_dwell_count_unique_appends': 12},
        {'required_gain_share_floor_interval': '(0.980481, 0.999822]', 'supported_dwell_count_unique_appends': 1},
        {'required_gain_share_floor_interval': '(0.999822, 1.000000]', 'supported_dwell_count_unique_appends': 0},
    ]

    relaxed = rows['[0, 0.870482]']
    assert relaxed['strongest_exact_tier_still_needed'] == 'lower_guarantee'
    assert relaxed['live_support_set_notation'] == '{2} ∪ [8, 32]'
    assert relaxed['live_support_component_count'] == 2
    assert relaxed['supported_dwell_count_unique_appends'] == 26
    assert relaxed['continuous_non_precision_support_start_unique_appends'] == 8
    assert relaxed['continuous_non_precision_support_end_unique_appends'] == 32
    assert relaxed['canonical_anchor_choices_unique_appends'] == [2, 13, 25]
    assert relaxed['largest_removed_suffix_if_floor_tightens_again'] == '[19, 32]'

    middle = rows['(0.870482, 0.980481]']
    assert middle['strongest_exact_tier_still_needed'] == 'near_optimal'
    assert middle['live_support_set_notation'] == '{2} ∪ [8, 18]'
    assert middle['live_support_component_count'] == 2
    assert middle['supported_dwell_count_unique_appends'] == 12
    assert middle['continuous_non_precision_support_start_unique_appends'] == 8
    assert middle['continuous_non_precision_support_end_unique_appends'] == 18
    assert middle['canonical_anchor_choices_unique_appends'] == [2, 13]
    assert middle['largest_removed_suffix_if_floor_tightens_again'] == '[8, 18]'

    precise = rows['(0.980481, 0.999822]']
    assert precise['strongest_exact_tier_still_needed'] == 'near_exact'
    assert precise['live_support_set_notation'] == '{2}'
    assert precise['live_support_component_count'] == 1
    assert precise['supported_dwell_count_unique_appends'] == 1
    assert precise['continuous_non_precision_support_start_unique_appends'] is None
    assert precise['continuous_non_precision_support_end_unique_appends'] is None
    assert precise['canonical_anchor_choices_unique_appends'] == [2]
    assert precise['largest_removed_suffix_if_floor_tightens_again'] == '{2}'

    overflow = rows['(0.999822, 1.000000]']
    assert overflow['strongest_exact_tier_still_needed'] == 'none'
    assert overflow['live_support_set_notation'] == '∅'
    assert overflow['live_support_component_count'] == 0
    assert overflow['supported_dwell_count_unique_appends'] == 0
    assert overflow['canonical_anchor_choices_unique_appends'] == []

    cross = report['topology_crosscheck']
    assert cross['exact_covered_dwell_intervals_unique_appends'] == [[2, 2], [8, 32]]
    assert cross['exact_precision_band_is_isolated'] is True
    assert cross['next_exact_non_precision_band_starts_at_unique_appends'] == 8
    assert cross['largest_internal_exact_dwell_gap_unique_appends'] == [3, 4, 5, 6, 7]

    print('uncertainty floor-conditioned dwell support stays exact: floor tightening now removes certified dwell regions in three explicit cliffs')


if __name__ == '__main__':
    main()
