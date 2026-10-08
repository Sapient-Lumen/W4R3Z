#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_packet_compact_repeat_state_canonical_anchor_labels_snapshot_20260308.json'


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    report = _load(REPORT)
    findings = report['headline_findings']
    tiers = {row['tier']: row for row in report['tier_rows']}

    assert findings['near_exact_canonical_anchor_minimum_dwell_unique_appends'] == 2
    assert findings['near_optimal_canonical_anchor_minimum_dwell_unique_appends'] == 13
    assert findings['lower_guarantee_canonical_anchor_minimum_dwell_unique_appends'] == 25
    assert findings['near_optimal_has_unique_exact_center'] is True
    assert findings['lower_guarantee_tied_exact_centers_unique_appends'] == [25, 26]

    assert tiers['near_exact']['center_candidates_unique_appends'] == [2]
    assert tiers['near_optimal']['center_candidates_unique_appends'] == [13]
    assert tiers['lower_guarantee']['center_candidates_unique_appends'] == [25, 26]

    assert tiers['near_exact']['prior_overlap_anchor_minimum_dwell_unique_appends'] == 1
    assert tiers['near_optimal']['prior_overlap_anchor_minimum_dwell_unique_appends'] == 9
    assert tiers['lower_guarantee']['prior_overlap_anchor_minimum_dwell_unique_appends'] == 16

    assert tiers['near_exact']['canonical_shift_vs_prior_overlap_anchor_unique_appends'] == 1
    assert tiers['near_optimal']['canonical_shift_vs_prior_overlap_anchor_unique_appends'] == 4
    assert tiers['lower_guarantee']['canonical_shift_vs_prior_overlap_anchor_unique_appends'] == 9

    assert tiers['near_exact']['canonical_anchor_rule'] == 'single_exact_center'
    assert tiers['near_optimal']['canonical_anchor_rule'] == 'single_exact_center'
    assert tiers['lower_guarantee']['canonical_anchor_rule'] == 'lower_of_two_tied_exact_centers'

    print('canonical anchor labels stay exact: current uncertainty-tier names should come from the centers of the exact certified bands, stabilizing the labels at dwell 2, 13, and 25')


if __name__ == '__main__':
    main()
