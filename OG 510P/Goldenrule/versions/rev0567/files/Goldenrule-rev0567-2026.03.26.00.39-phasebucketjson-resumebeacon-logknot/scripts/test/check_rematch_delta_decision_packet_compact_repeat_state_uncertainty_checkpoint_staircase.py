#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    near_exact_rows = {row['expected_repeat_lookups']: row for row in report['near_exact_boundary_rows']}

    assert findings['checkpoint_union_counts_descending_by_guarantee'] == [14, 8, 5]
    assert findings['near_exact_union_transition_checkpoint_count'] == 14
    assert findings['near_optimal_union_transition_checkpoint_count'] == 8
    assert findings['lower_guarantee_union_transition_checkpoint_count'] == 5
    assert findings['near_exact_extra_checkpoints_vs_near_optimal'] == [9, 15, 31, 38, 54, 255]
    assert findings['near_optimal_removed_checkpoints_when_relaxing_to_lower_guarantee'] == [24, 63, 230, 239]
    assert findings['lower_guarantee_adds_unique_checkpoint_56'] is True

    near_exact = tiers['near_exact']
    assert near_exact['exact_hard_cap'] == 11
    assert near_exact['representative_anchor_minimum_dwell_unique_appends'] == 2
    assert near_exact['union_transition_checkpoints_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 63, 111, 143, 159, 230, 239, 255]
    assert near_exact['transition_range'] == {'minimum_selected_transition_count': 2, 'maximum_selected_transition_count': 11}
    assert near_exact['worst_case_gain_share_of_full_dynamic_savings'] == 0.999822

    near_optimal = tiers['near_optimal']
    assert near_optimal['exact_hard_cap'] == 5
    assert near_optimal['representative_anchor_minimum_dwell_unique_appends'] == 13
    assert near_optimal['union_transition_checkpoints_unique_appends'] == [24, 47, 63, 111, 143, 159, 230, 239]
    assert near_optimal['transition_range'] == {'minimum_selected_transition_count': 2, 'maximum_selected_transition_count': 5}

    lower = tiers['lower_guarantee']
    assert lower['exact_hard_cap'] == 3
    assert lower['representative_anchor_minimum_dwell_unique_appends'] == 25
    assert lower['union_transition_checkpoints_unique_appends'] == [47, 56, 111, 143, 159]
    assert lower['transition_range'] == {'minimum_selected_transition_count': 0, 'maximum_selected_transition_count': 3}

    assert near_exact_rows[0.15]['selected_transition_count'] == 2
    assert near_exact_rows[0.15]['minimum_interval_width_unique_appends'] == 9
    assert near_exact_rows[0.15]['transition_boundaries_unique_appends'] == [230, 239]
    assert near_exact_rows[0.18]['selected_transition_count'] == 11
    assert near_exact_rows[0.18]['minimum_interval_width_unique_appends'] == 6
    assert near_exact_rows[0.18]['transition_boundaries_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 63, 111, 159, 239]
    assert near_exact_rows[0.25]['selected_transition_count'] == 5
    assert near_exact_rows[0.25]['minimum_interval_width_unique_appends'] == 2
    assert near_exact_rows[0.25]['transition_boundaries_unique_appends'] == [47, 111, 143, 239, 255]

    print('uncertainty checkpoint staircase report matches the saved exact tiers and certifies the near-exact dwell-2 checkpoint surface')


if __name__ == '__main__':
    main()
