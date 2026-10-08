#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_path_atlas_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {(row['start_tier'], row['end_tier']): row for row in report['route_rows']}
    examples = {row['example_label']: row for row in report['examples']}

    assert findings['canonical_anchor_targets_unique_appends'] == [2, 13, 25]
    assert findings['ordered_distinct_anchor_routes'] == 6
    assert findings['unique_total_shift_values_unique_appends'] == [11, 12, 23]
    assert findings['outer_pair_total_shift_unique_appends'] == 23
    assert findings['outer_pair_total_shift_is_symmetric'] is True
    assert findings['outer_pair_phase_count_asymmetry'] == {
        'near_exact_to_lower_guarantee': 3,
        'lower_guarantee_to_near_exact': 1,
    }
    assert findings['strengthening_routes_to_precision_collapse_directly'] is True
    assert findings['weakening_from_precision_starts_at_boundary_8'] is True
    assert findings['weakening_to_lower_guarantee_requires_boundary_19_before_anchor_25'] is True
    assert findings['unique_transient_boundary_nodes_unique_appends'] == [8, 18, 19]

    assert rows[('near_exact', 'near_optimal')]['route_unique_appends'] == [2, 8, 13]
    assert rows[('near_exact', 'near_optimal')]['step_count'] == 2
    assert rows[('near_exact', 'near_optimal')]['total_absolute_dwell_shift_unique_appends'] == 11

    assert rows[('near_exact', 'lower_guarantee')]['route_unique_appends'] == [2, 8, 19, 25]
    assert rows[('near_exact', 'lower_guarantee')]['step_count'] == 3
    assert rows[('near_exact', 'lower_guarantee')]['total_absolute_dwell_shift_unique_appends'] == 23

    assert rows[('near_optimal', 'near_exact')]['route_unique_appends'] == [13, 2]
    assert rows[('near_optimal', 'near_exact')]['step_count'] == 1
    assert rows[('near_optimal', 'near_exact')]['total_absolute_dwell_shift_unique_appends'] == 11

    assert rows[('near_optimal', 'lower_guarantee')]['route_unique_appends'] == [13, 19, 25]
    assert rows[('near_optimal', 'lower_guarantee')]['step_count'] == 2
    assert rows[('near_optimal', 'lower_guarantee')]['total_absolute_dwell_shift_unique_appends'] == 12

    assert rows[('lower_guarantee', 'near_exact')]['route_unique_appends'] == [25, 2]
    assert rows[('lower_guarantee', 'near_exact')]['step_count'] == 1
    assert rows[('lower_guarantee', 'near_exact')]['total_absolute_dwell_shift_unique_appends'] == 23

    assert rows[('lower_guarantee', 'near_optimal')]['route_unique_appends'] == [25, 18, 13]
    assert rows[('lower_guarantee', 'near_optimal')]['step_count'] == 2
    assert rows[('lower_guarantee', 'near_optimal')]['total_absolute_dwell_shift_unique_appends'] == 12

    assert examples['precision_weakening_to_non_fragile_anchor']['route_unique_appends'] == [2, 8, 13]
    assert examples['precision_full_relaxation_to_relaxed_anchor']['route_unique_appends'] == [2, 8, 19, 25]
    assert examples['relaxed_suffix_high_floor_collapse_to_precision']['route_unique_appends'] == [25, 2]
    assert examples['relaxed_suffix_strengthening_to_non_fragile_anchor']['route_unique_appends'] == [25, 18, 13]

    print('canonical anchor retuning now compresses to six exact ordered routes over anchors 2, 13, and 25')


if __name__ == '__main__':
    main()
