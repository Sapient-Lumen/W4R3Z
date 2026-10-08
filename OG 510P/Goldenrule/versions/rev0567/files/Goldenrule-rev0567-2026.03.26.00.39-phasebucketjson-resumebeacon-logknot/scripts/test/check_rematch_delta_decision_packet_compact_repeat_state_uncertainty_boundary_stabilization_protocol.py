#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_boundary_stabilization_protocol_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    band_rows = {row['tier']: row for row in report['band_rows']}
    protocol_rows = {row['protocol_label']: row for row in report['protocol_rows']}
    examples = {row['example_label']: row for row in report['examples']}

    assert findings['canonical_anchor_targets_unique_appends'] == [2, 13, 25]
    assert findings['first_step_boundary_targets_unique_appends'] == [2, 8, 18, 19]
    assert findings['precision_singleton_needs_no_recentering'] is True
    assert findings['neutral_band_boundary_to_anchor_recentering_is_symmetric'] is True
    assert findings['neutral_band_boundary_to_anchor_recentering_distance_unique_appends'] == 5
    assert findings['relaxed_suffix_entry_boundary_to_anchor_recentering_distance_unique_appends'] == 6
    assert findings['maximum_optional_recentering_distance_unique_appends'] == 6
    assert findings['all_steady_mode_recentering_targets_are_canonical_anchors'] is True
    assert findings['boundary_landings_8_18_19_are_transient_by_default'] is True

    assert band_rows['near_exact']['support_boundaries_unique_appends'] == [2]
    assert band_rows['near_exact']['boundary_to_anchor_recentering_distances_unique_appends'] == [0]
    assert band_rows['near_optimal']['support_boundaries_unique_appends'] == [8, 18]
    assert band_rows['near_optimal']['canonical_anchor_minimum_dwell_unique_appends'] == 13
    assert band_rows['near_optimal']['boundary_to_anchor_recentering_distances_unique_appends'] == [5, 5]
    assert band_rows['lower_guarantee']['canonical_anchor_minimum_dwell_unique_appends'] == 25
    assert band_rows['lower_guarantee']['entry_boundary_to_anchor_recentering_distance_unique_appends'] == 6

    assert protocol_rows['strengthen_relaxed_suffix_to_neutral_band']['first_boundary_target_unique_appends'] == 18
    assert protocol_rows['strengthen_relaxed_suffix_to_neutral_band']['canonical_anchor_target_unique_appends'] == 13
    assert protocol_rows['strengthen_relaxed_suffix_to_neutral_band']['optional_recentering_distance_unique_appends'] == 5
    assert protocol_rows['strengthen_any_live_region_to_precision_singleton']['first_boundary_target_unique_appends'] == 2
    assert protocol_rows['strengthen_any_live_region_to_precision_singleton']['canonical_anchor_target_unique_appends'] == 2
    assert protocol_rows['strengthen_any_live_region_to_precision_singleton']['optional_recentering_distance_unique_appends'] == 0
    assert protocol_rows['weaken_precision_to_neutral_band']['first_boundary_target_unique_appends'] == 8
    assert protocol_rows['weaken_precision_to_neutral_band']['canonical_anchor_target_unique_appends'] == 13
    assert protocol_rows['weaken_precision_to_neutral_band']['optional_recentering_distance_unique_appends'] == 5
    assert protocol_rows['weaken_neutral_band_to_relaxed_suffix']['first_boundary_target_unique_appends'] == 19
    assert protocol_rows['weaken_neutral_band_to_relaxed_suffix']['canonical_anchor_target_unique_appends'] == 25
    assert protocol_rows['weaken_neutral_band_to_relaxed_suffix']['optional_recentering_distance_unique_appends'] == 6

    assert examples['relaxed_suffix_strengthens_then_recenters_to_13']['steady_mode_anchor_unique_appends'] == 13
    assert examples['precision_weakens_then_recenters_to_13']['first_boundary_target_unique_appends'] == 8
    assert examples['neutral_band_weakens_then_recenters_to_25']['steady_mode_anchor_unique_appends'] == 25
    assert examples['high_floor_strengthening_stops_at_2']['steady_mode_anchor_unique_appends'] == 2

    print('boundary repairs and steady-mode anchors now form an exact two-phase stabilization protocol over anchors 2, 13, and 25')


if __name__ == '__main__':
    main()
