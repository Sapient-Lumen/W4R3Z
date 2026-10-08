#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector import (
    build_weakening_capability_selector_snapshot,
    select_weakening_regime_by_capabilities,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    sticky = select_weakening_regime_by_capabilities()
    _assert_equal(sticky['status'], 'selected_named_regime', 'sticky status')
    _assert_equal(sticky['selected_threshold_unique_appends'], 0, 'sticky threshold')

    suffix_only = select_weakening_regime_by_capabilities(
        require_any_relaxed_release_from_stronger_tiers=True,
        forbid_relaxed_basin_growth_beyond_neutral_exit=True,
    )
    _assert_equal(suffix_only['selected_threshold_unique_appends'], 7, 'suffix-only threshold')
    _assert_equal(suffix_only['selected_regime_label'], 'suffix release', 'suffix-only regime label')

    middle_only = select_weakening_regime_by_capabilities(
        require_middle_band_precision_relief=True,
        forbid_relaxed_basin_growth_beyond_neutral_exit=True,
    )
    _assert_equal(middle_only['selected_threshold_unique_appends'], 11, 'middle-only threshold')
    _assert_equal(middle_only['selected_capabilities']['admits_middle_band_precision_relief'], True, 'middle-only precision relief flag')
    _assert_equal(middle_only['selected_capabilities']['forbids_relaxed_basin_growth_beyond_neutral_exit'], True, 'middle-only basin preservation flag')

    staged = select_weakening_regime_by_capabilities(require_neutral_anchor_relaxed_release=True)
    _assert_equal(staged['selected_threshold_unique_appends'], 12, 'staged neutral release threshold')
    _assert_equal(staged['selected_capabilities']['admits_direct_entry_boundary_relaxed_release'], False, 'staged release should not be direct from 8')

    direct_entry = select_weakening_regime_by_capabilities(require_direct_entry_boundary_relaxed_release=True)
    _assert_equal(direct_entry['selected_threshold_unique_appends'], 17, 'direct entry threshold')
    _assert_equal(direct_entry['selected_capabilities']['admits_direct_entry_boundary_relaxed_release'], True, 'direct entry flag')

    full = select_weakening_regime_by_capabilities(require_direct_precision_relaxed_release=True)
    _assert_equal(full['selected_threshold_unique_appends'], 23, 'full release threshold')
    _assert_equal(full['selected_capabilities']['admits_direct_precision_relaxed_release'], True, 'direct precision flag')

    impossible = select_weakening_regime_by_capabilities(
        require_neutral_anchor_relaxed_release=True,
        forbid_relaxed_basin_growth_beyond_neutral_exit=True,
    )
    _assert_equal(impossible['status'], 'no_named_regime_satisfies_promises', 'impossible status')
    if not impossible['incompatibility_notes']:
        raise SystemExit('expected incompatibility notes for impossible promise bundle')

    report = build_weakening_capability_selector_snapshot()
    _assert_equal(report['headline_findings']['minimal_thresholds_by_capability_unique_appends']['middle_band_precision_relief'], 11, 'headline middle relief threshold')
    _assert_equal(report['headline_findings']['minimal_thresholds_by_capability_unique_appends']['neutral_anchor_relaxed_release_eventually'], 12, 'headline neutral release threshold')
    _assert_equal(len(report['objective_catalog']), 6, 'objective catalog size')
    _assert_equal(len(report['infeasible_objectives']), 2, 'infeasible catalog size')

    print('weakening capability selector checks passed')


if __name__ == '__main__':
    main()
