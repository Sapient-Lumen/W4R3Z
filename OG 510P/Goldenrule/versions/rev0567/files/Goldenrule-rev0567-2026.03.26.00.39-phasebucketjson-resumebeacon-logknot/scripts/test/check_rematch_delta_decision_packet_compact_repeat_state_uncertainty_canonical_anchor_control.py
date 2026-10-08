#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control import (
    decide_canonical_anchor_control,
)

REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_canonical_anchor_control_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    rows = {
        (row['current_tier'], row['floor_interval_label']): row
        for row in report['default_nonbinding_budget_control_matrix']
    }
    examples = {row['example_label']: row['decision'] for row in report['examples']}

    assert findings['control_matrix_shape'] == {'current_tiers': 3, 'floor_intervals': 3, 'ordered_states': 9}
    assert findings['holds_in_default_matrix'] == 3
    assert findings['weakens_in_default_matrix'] == 3
    assert findings['strengthens_in_default_matrix'] == 3
    assert findings['largest_cap_release_in_default_matrix'] == -8
    assert findings['largest_checkpoint_release_in_default_matrix'] == -9
    assert findings['largest_cap_increase_in_default_matrix'] == 8
    assert findings['largest_checkpoint_increase_in_default_matrix'] == 9

    assert rows[('near_exact', 'up_to_lower_guarantee_floor')]['selected_steady_tier'] == 'lower_guarantee'
    assert rows[('near_exact', 'up_to_lower_guarantee_floor')]['action_family'] == 'weaken'
    assert rows[('near_exact', 'up_to_lower_guarantee_floor')]['route_unique_appends'] == [2, 8, 19, 25]

    assert rows[('near_exact', 'middle_band')]['selected_steady_tier'] == 'near_optimal'
    assert rows[('near_exact', 'middle_band')]['route_unique_appends'] == [2, 8, 13]

    assert rows[('near_exact', 'precision_band')]['selected_steady_tier'] == 'near_exact'
    assert rows[('near_exact', 'precision_band')]['status'] == 'hold_current_anchor'

    assert rows[('near_optimal', 'up_to_lower_guarantee_floor')]['selected_steady_tier'] == 'lower_guarantee'
    assert rows[('near_optimal', 'up_to_lower_guarantee_floor')]['route_unique_appends'] == [13, 19, 25]

    assert rows[('near_optimal', 'middle_band')]['selected_steady_tier'] == 'near_optimal'
    assert rows[('near_optimal', 'middle_band')]['status'] == 'hold_current_anchor'

    assert rows[('near_optimal', 'precision_band')]['selected_steady_tier'] == 'near_exact'
    assert rows[('near_optimal', 'precision_band')]['route_unique_appends'] == [13, 2]

    assert rows[('lower_guarantee', 'up_to_lower_guarantee_floor')]['selected_steady_tier'] == 'lower_guarantee'
    assert rows[('lower_guarantee', 'up_to_lower_guarantee_floor')]['status'] == 'hold_current_anchor'

    assert rows[('lower_guarantee', 'middle_band')]['selected_steady_tier'] == 'near_optimal'
    assert rows[('lower_guarantee', 'middle_band')]['route_unique_appends'] == [25, 18, 13]

    assert rows[('lower_guarantee', 'precision_band')]['selected_steady_tier'] == 'near_exact'
    assert rows[('lower_guarantee', 'precision_band')]['route_unique_appends'] == [25, 2]

    assert examples['release_precision_premium_when_floor_drops']['status'] == 'retune_to_new_anchor'
    assert examples['release_precision_premium_when_floor_drops']['selected_steady_tier'] == 'lower_guarantee'
    assert examples['release_precision_premium_when_floor_drops']['selected_minus_current_deltas'] == {
        'exact_hard_cap_change_selected_minus_current': -8,
        'mode_specific_checkpoint_change_selected_minus_current': -9,
        'post_amortized_checkpoint_change_selected_minus_current': 0,
        'minimum_anchor_slack_change_selected_minus_current': 6,
        'exact_dwell_band_width_change_selected_minus_current': 13,
        'anchor_shift_selected_minus_current': 23,
    }

    assert examples['upgrade_relaxed_anchor_to_middle_lane']['status'] == 'retune_to_new_anchor'
    assert examples['upgrade_relaxed_anchor_to_middle_lane']['action_family'] == 'strengthen'
    assert examples['upgrade_relaxed_anchor_to_middle_lane']['route_plan']['route_unique_appends'] == [25, 18, 13]

    assert examples['hold_middle_anchor_when_already_minimal']['status'] == 'hold_current_anchor'
    assert examples['hold_middle_anchor_when_already_minimal']['route_plan'] is None

    assert examples['precision_request_with_positive_slack_is_infeasible']['status'] == 'no_canonical_exact_tier'
    assert examples['precision_request_with_positive_slack_is_infeasible']['blocking_summary'] == 'high_floor_positive_slack_conflict'
    assert examples['precision_request_with_positive_slack_is_infeasible']['recommended_repair_family'] == 'lower_required_floor_to_0.980481_or_drop_slack_to_zero'

    direct = decide_canonical_anchor_control(
        current_tier='near_exact',
        required_gain_share_floor='0.95',
        max_hard_cap_budget_inclusive=5,
        minimum_anchor_slack_unique_appends=2,
        minimum_band_width_unique_appends=4,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=8,
    )
    assert direct['status'] == 'retune_to_new_anchor'
    assert direct['action_family'] == 'weaken'
    assert direct['current_anchor_already_satisfies_request'] is False
    assert direct['selected_steady_tier'] == 'near_optimal'
    assert direct['route_plan']['route_unique_appends'] == [2, 8, 13]

    floor_only = decide_canonical_anchor_control(
        current_tier='lower_guarantee',
        required_gain_share_floor='0.84',
        max_hard_cap_budget_inclusive=3,
        minimum_anchor_slack_unique_appends=6,
        minimum_band_width_unique_appends=14,
        master_calendar_pre_registered=False,
        max_pre_amortization_checkpoint_budget_inclusive=5,
    )
    assert floor_only['status'] == 'hold_current_anchor'
    assert floor_only['selected_steady_tier'] == 'lower_guarantee'
    assert floor_only['feasible_tiers_sorted_cheap_to_expensive'] == ['lower_guarantee']

    print('canonical steady-state exact-uncertainty control now compresses to a 3x3 hold/weaken/strengthen matrix plus explicit infeasibility blockers')


if __name__ == '__main__':
    main()
