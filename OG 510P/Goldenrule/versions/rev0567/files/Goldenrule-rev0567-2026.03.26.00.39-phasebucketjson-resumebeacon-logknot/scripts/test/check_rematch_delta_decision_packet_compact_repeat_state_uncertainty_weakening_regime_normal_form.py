#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form import (
    build_weakening_regime_normal_form_snapshot,
    normalize_weakening_threshold,
)


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    regime0 = normalize_weakening_threshold(0)
    regime10 = normalize_weakening_threshold(10)
    regime11 = normalize_weakening_threshold(11)
    regime12 = normalize_weakening_threshold(12)
    regime17 = normalize_weakening_threshold(17)
    regime23 = normalize_weakening_threshold(23)
    regime99 = normalize_weakening_threshold(99)

    _assert_equal(regime0['regime_code'], 'fully_sticky', 'threshold 0 regime')
    _assert_equal(regime10['regime_code'], 'suffix_release', 'threshold 10 regime')
    _assert_equal(regime11['regime_code'], 'middle_only_precision_relief', 'threshold 11 regime')
    _assert_equal(regime12['regime_code'], 'staged_relaxed_release', 'threshold 12 regime')
    _assert_equal(regime17['regime_code'], 'direct_entry_relaxed_release', 'threshold 17 regime')
    _assert_equal(regime23['regime_code'], 'full_release', 'threshold 23 regime')
    _assert_equal(regime99['normalized_threshold_unique_appends'], 23, 'thresholds above 23 normalize to full release')

    _assert_equal(regime10['eventual_relaxed_anchor_states_from_stronger_tiers'], [18], 'threshold 10 stronger-tier eventual relaxed set')
    _assert_equal(regime11['eventual_relaxed_anchor_states_from_stronger_tiers'], [18], 'threshold 11 does not enlarge relaxed basin')
    _assert_equal(regime11['middle_band_neutral_release_states'], [2], 'threshold 11 middle-band precision release')
    _assert_equal(regime11['newly_admitted_one_shot_weakening_cases'], ['2:precision_anchor@middle_band->near_optimal'], 'threshold 11 newly admitted case')

    _assert_equal(regime12['eventual_relaxed_anchor_states_from_stronger_tiers'], [8, 13, 18], 'threshold 12 stronger-tier eventual relaxed set')
    _assert_equal(regime12['direct_relaxed_anchor_states_from_stronger_tiers'], [13, 18], 'threshold 12 stronger-tier direct relaxed set')
    _assert_equal(regime17['eventual_relaxed_anchor_states_from_stronger_tiers'], [8, 13, 18], 'threshold 17 stronger-tier eventual relaxed set')
    _assert_equal(regime17['direct_relaxed_anchor_states_from_stronger_tiers'], [8, 13, 18], 'threshold 17 stronger-tier direct relaxed set')
    _assert_equal(regime23['direct_relaxed_anchor_states_from_stronger_tiers'], [2, 8, 13, 18], 'threshold 23 stronger-tier direct relaxed set')

    _assert_equal(regime12['closure_summary']['final_anchor_counts'], {'2': 7, '13': 6, '25': 5}, 'threshold 12 final counts')
    _assert_equal(regime17['closure_summary']['final_anchor_counts'], {'2': 7, '13': 6, '25': 5}, 'threshold 17 final counts')
    _assert_equal(regime12['closure_summary']['max_cycles_to_settle'], 3, 'threshold 12 settle depth')
    _assert_equal(regime17['closure_summary']['max_cycles_to_settle'], 2, 'threshold 17 settle depth')

    snapshot = build_weakening_regime_normal_form_snapshot()
    _assert_equal(snapshot['headline_findings']['named_regime_count'], 6, 'named regime count')

    print('weakening regime normal form checks passed')


if __name__ == '__main__':
    main()
