#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}
    thresholds = report['threshold_rows']

    assert findings['rounded_labels_are_conservative_not_tight'] is True
    assert findings['largest_hidden_headroom_tier'] == 'near_optimal'
    assert abs(findings['strongest_exact_tier_not_needed_until_required_floor_exceeds'] - 0.980481) < 1e-9
    assert findings['near_optimal_is_cheapest_exact_tier_for_required_floor_interval'] == '(0.870482, 0.980481]'
    assert findings['near_exact_required_floor_interval'] == '(0.980481, 0.999822]'
    assert findings['no_current_exact_tier_above_required_floor'] == '(0.999822, 1.000000]'

    assert abs(tiers['lower_guarantee']['certified_headroom_above_rounded_label'] - 0.020482) < 1e-9
    assert abs(tiers['near_optimal']['certified_headroom_above_rounded_label'] - 0.030481) < 1e-9
    assert abs(tiers['near_exact']['certified_headroom_above_rounded_label'] - 0.009822) < 1e-9

    assert thresholds[0]['required_gain_share_floor_interval'] == '[0, 0.870482]'
    assert thresholds[0]['cheapest_exact_feasible_tier'] == 'lower_guarantee'
    assert thresholds[1]['required_gain_share_floor_interval'] == '(0.870482, 0.980481]'
    assert thresholds[1]['cheapest_exact_feasible_tier'] == 'near_optimal'
    assert thresholds[2]['required_gain_share_floor_interval'] == '(0.980481, 0.999822]'
    assert thresholds[2]['cheapest_exact_feasible_tier'] == 'near_exact'
    assert thresholds[3]['required_gain_share_floor_interval'] == '(0.999822, 1.000000]'
    assert thresholds[3]['cheapest_exact_feasible_tier'] == 'none'

    print('uncertainty guarantee threshold selector stays exact: choose lanes by the actual certified floors 0.870482, 0.980481, and 0.999822, not by the rounded labels 0.85, 0.95, and 0.99')


if __name__ == '__main__':
    main()
