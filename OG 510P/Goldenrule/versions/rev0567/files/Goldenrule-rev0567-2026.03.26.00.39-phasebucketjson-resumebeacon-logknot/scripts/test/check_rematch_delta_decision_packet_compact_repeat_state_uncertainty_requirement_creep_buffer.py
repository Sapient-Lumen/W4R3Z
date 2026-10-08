#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}

    assert findings['largest_absolute_requirement_creep_buffer_tier'] == 'near_optimal'
    assert findings['largest_relative_requirement_creep_buffer_tier'] == 'near_optimal'
    assert abs(findings['exact_requirement_creep_buffer_above_rounded_label']['lower_guarantee'] - 0.020482) < 1e-9
    assert abs(findings['exact_requirement_creep_buffer_above_rounded_label']['near_optimal'] - 0.030481) < 1e-9
    assert abs(findings['exact_requirement_creep_buffer_above_rounded_label']['near_exact'] - 0.009822) < 1e-9
    assert abs(findings['near_optimal_buffer_advantage_vs_lower_guarantee'] - 0.009999) < 1e-9
    assert abs(findings['near_optimal_buffer_advantage_vs_near_exact'] - 0.020659) < 1e-9
    assert abs(findings['near_optimal_buffer_multiple_vs_near_exact'] - 3.103339) < 1e-6
    assert abs(findings['do_not_pay_near_exact_until_required_floor_exceeds'] - 0.980481) < 1e-9
    assert abs(findings['near_exact_frontier_overflow_margin_below_1_0'] - 0.000178) < 1e-9

    assert tiers['lower_guarantee']['next_forced_change_kind'] == 'tier_escalation'
    assert abs(tiers['lower_guarantee']['next_forced_change_trigger_floor'] - 0.870482) < 1e-9
    assert tiers['near_optimal']['next_forced_change_kind'] == 'tier_escalation'
    assert abs(tiers['near_optimal']['next_forced_change_trigger_floor'] - 0.980481) < 1e-9
    assert tiers['near_exact']['next_forced_change_kind'] == 'frontier_overflow'
    assert abs(tiers['near_exact']['next_forced_change_trigger_floor'] - 0.999822) < 1e-9

    print('uncertainty requirement-creep buffer stays exact: the current 0.95 lane has the largest hidden floor margin above its rounded label, while the 0.99 lane has the smallest margin before frontier overflow')


if __name__ == '__main__':
    main()
