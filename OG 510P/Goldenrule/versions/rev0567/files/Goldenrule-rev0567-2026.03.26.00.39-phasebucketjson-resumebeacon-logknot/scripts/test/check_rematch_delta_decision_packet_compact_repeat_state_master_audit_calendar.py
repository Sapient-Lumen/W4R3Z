#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_master_audit_calendar_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    groups = {row['group']: row for row in report['group_rows']}
    checkpoints = {row['unique_appends']: row['coverage_tags'] for row in report['checkpoint_rows']}

    assert findings['near_exact_subsumes_near_optimal_checkpoint_union_exactly'] is True
    assert findings['lower_guarantee_adds_only_checkpoint_56_beyond_near_exact'] is True
    assert findings['exact_master_transition_checkpoints_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 56, 63, 111, 143, 159, 230, 239, 255]
    assert findings['exact_master_transition_checkpoint_count'] == 15
    assert findings['structural_only_checkpoints_unique_appends'] == [79, 191]
    assert findings['structural_overlap_with_exact_checkpoints_unique_appends'] == [111, 239]
    assert findings['full_master_audit_checkpoints_unique_appends'] == [9, 15, 24, 31, 38, 47, 54, 56, 63, 79, 111, 143, 159, 191, 230, 239, 255]
    assert findings['full_master_audit_checkpoint_count'] == 17
    assert findings['rewrite_budgeted_mode_is_covered_by_full_master_calendar'] is True

    assert groups['all_exact_tiers']['checkpoints_unique_appends'] == [47, 111, 143, 159]
    assert groups['near_optimal_and_near_exact_only']['checkpoints_unique_appends'] == [24, 63, 230, 239]
    assert groups['near_exact_only']['checkpoints_unique_appends'] == [9, 15, 31, 38, 54, 255]
    assert groups['lower_guarantee_only']['checkpoints_unique_appends'] == [56]
    assert groups['structural_only']['checkpoints_unique_appends'] == [79, 191]

    assert checkpoints[56] == ['lower_guarantee_only', 'rewrite_budgeted_mode']
    assert checkpoints[79] == ['structural_only']
    assert checkpoints[111] == ['all_exact_tiers', 'structural_overlap', 'rewrite_budgeted_mode']
    assert checkpoints[239] == ['near_optimal_and_near_exact_only', 'structural_overlap', 'rewrite_budgeted_mode']
    assert checkpoints[255] == ['near_exact_only']

    print('master audit calendar report matches the saved exact tiers, structure checkpoints, and trusted-repeat fallback coverage')


if __name__ == '__main__':
    main()
