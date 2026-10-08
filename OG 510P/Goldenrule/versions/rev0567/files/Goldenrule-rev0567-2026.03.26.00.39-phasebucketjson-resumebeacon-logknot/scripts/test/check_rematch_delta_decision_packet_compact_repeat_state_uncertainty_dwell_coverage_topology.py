#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    coverage = {row['tier']: row for row in report['coverage_rows']}

    assert findings['exact_covered_dwell_intervals_unique_appends'] == [[2, 2], [8, 32]]
    assert findings['largest_internal_exact_dwell_gap_unique_appends'] == [3, 4, 5, 6, 7]
    assert findings['largest_internal_exact_dwell_gap_width_unique_appends'] == 5
    assert findings['exact_precision_band_is_isolated'] is True
    assert findings['next_exact_non_precision_band_starts_at_unique_appends'] == 8
    assert findings['near_optimal_and_lower_guarantee_bands_are_contiguous'] is True
    assert findings['no_current_exact_positive_slack_band_below_unique_appends'] == 8

    assert tiers['near_exact']['exact_dwell_band_start_unique_appends'] == 2
    assert tiers['near_exact']['exact_dwell_band_end_unique_appends'] == 2
    assert tiers['near_optimal']['exact_dwell_band_start_unique_appends'] == 8
    assert tiers['near_optimal']['exact_dwell_band_end_unique_appends'] == 18
    assert tiers['lower_guarantee']['exact_dwell_band_start_unique_appends'] == 19
    assert tiers['lower_guarantee']['exact_dwell_band_end_unique_appends'] == 32

    assert coverage['near_exact']['relation_to_previous_exact_band'] == 'first_exact_band'
    assert coverage['near_optimal']['relation_to_previous_exact_band'] == 'separated_from_previous_exact_band_by_internal_gap'
    assert coverage['near_optimal']['internal_gap_from_previous_exact_band_unique_appends'] == 5
    assert coverage['near_optimal']['intervening_uncovered_dwell_values_unique_appends'] == [3, 4, 5, 6, 7]
    assert coverage['lower_guarantee']['relation_to_previous_exact_band'] == 'adjacent_or_overlapping_with_previous_exact_band'
    assert coverage['lower_guarantee']['internal_gap_from_previous_exact_band_unique_appends'] == 0

    print('uncertainty dwell-coverage topology stays exact: the current certified menu covers dwell 2 and dwell 8-32, with a real internal gap at dwell 3-7 that should be skipped during exact retuning')


if __name__ == '__main__':
    main()
