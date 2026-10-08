#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector import (
    build_weakening_budget_selector_snapshot,
    select_weakening_regime_by_recovered_case_budget,
)



def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise SystemExit(f'{label}: expected {expected!r}, got {actual!r}')



def main() -> None:
    budget0 = select_weakening_regime_by_recovered_case_budget(0)
    _assert_equal(budget0['selected_threshold_unique_appends'], 0, 'budget 0 threshold')
    _assert_equal(budget0['selected_regime_label'], 'fully sticky', 'budget 0 regime')
    _assert_equal(budget0['selected_recovered_case_count'], 0, 'budget 0 recovered count')

    budget1 = select_weakening_regime_by_recovered_case_budget(1)
    _assert_equal(budget1['selected_threshold_unique_appends'], 7, 'budget 1 threshold')
    _assert_equal(budget1['selected_recovered_case_count'], 1, 'budget 1 recovered count')
    _assert_equal(budget1['next_locked_case']['minimal_budget_to_unlock'], 2, 'budget 1 next lock budget')

    budget2 = select_weakening_regime_by_recovered_case_budget(2)
    _assert_equal(budget2['selected_threshold_unique_appends'], 11, 'budget 2 threshold')
    _assert_equal(budget2['selected_regime_label'], 'middle-only precision relief', 'budget 2 regime')

    budget3 = select_weakening_regime_by_recovered_case_budget(3)
    _assert_equal(budget3['selected_threshold_unique_appends'], 12, 'budget 3 threshold')
    _assert_equal(budget3['selected_recovered_case_count'], 3, 'budget 3 recovered count')

    budget4 = select_weakening_regime_by_recovered_case_budget(4)
    _assert_equal(budget4['selected_threshold_unique_appends'], 17, 'budget 4 threshold')
    _assert_equal(budget4['selected_recovered_case_count'], 4, 'budget 4 recovered count')

    budget5 = select_weakening_regime_by_recovered_case_budget(5)
    _assert_equal(budget5['selected_threshold_unique_appends'], 23, 'budget 5 threshold')
    _assert_equal(budget5['selected_regime_label'], 'full release', 'budget 5 regime')
    _assert_equal(budget5['next_locked_case'], None, 'budget 5 next lock')

    over = select_weakening_regime_by_recovered_case_budget(9)
    _assert_equal(over['selected_threshold_unique_appends'], 23, 'clamped threshold')
    _assert_equal(over['requested_budget_was_clamped'], True, 'clamped flag')
    _assert_equal(over['selected_recovered_base_weakening_case_budget'], 5, 'clamped budget')

    report = build_weakening_budget_selector_snapshot()
    _assert_equal(report['headline_findings']['recoverable_base_weakening_case_count'], 5, 'headline case count')
    _assert_equal(report['headline_findings']['valid_recovered_case_budgets'], [0, 1, 2, 3, 4, 5], 'headline valid budgets')
    _assert_equal(report['headline_findings']['minimal_budget_by_capability']['direct_precision_relaxed_release'], 5, 'headline full release budget')
    _assert_equal(len(report['budget_catalog']), 6, 'budget catalog size')
    _assert_equal(len(report['marginal_budget_steps']), 5, 'marginal step count')

    print('weakening budget selector checks passed')


if __name__ == '__main__':
    main()
