#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder import (
    build_recovery_ladder,
    build_threshold_band_progression,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form import (
    REGIME_BANDS,
    normalize_weakening_threshold,
)


class WeakeningBudgetSelectorError(ValueError):
    pass


BUDGET_MIN = 0
BUDGET_MAX = 5



def _band_rows() -> list[dict[str, Any]]:
    return build_threshold_band_progression()



def _recovery_rows() -> list[dict[str, Any]]:
    return build_recovery_ladder()



def _recovered_case_labels_for_budget(budget: int) -> list[str]:
    rows = _recovery_rows()
    return [row['recovered_case_label'] for row in rows[:budget]]



def _next_locked_case_for_budget(budget: int) -> dict[str, Any] | None:
    rows = _recovery_rows()
    if budget >= len(rows):
        return None
    row = rows[budget]
    return {
        'recovery_kind': row['recovery_kind'],
        'minimal_budget_to_unlock': budget + 1,
        'minimal_threshold_to_unlock_unique_appends': row['minimal_recovery_threshold_unique_appends'],
        'recovered_case_label': row['recovered_case_label'],
    }



def _clamp_budget(requested_budget: int) -> tuple[int, bool]:
    clamped = min(max(requested_budget, BUDGET_MIN), BUDGET_MAX)
    return clamped, clamped != requested_budget



def select_weakening_regime_by_recovered_case_budget(max_recovered_base_weakening_cases: int) -> dict[str, Any]:
    if not isinstance(max_recovered_base_weakening_cases, int):
        raise WeakeningBudgetSelectorError('max_recovered_base_weakening_cases must be an integer')
    clamped_budget, was_clamped = _clamp_budget(max_recovered_base_weakening_cases)
    band_row = _band_rows()[clamped_budget]
    regime = normalize_weakening_threshold(band_row['representative_threshold_unique_appends'])
    recovered_cases = _recovered_case_labels_for_budget(clamped_budget)
    next_locked = _next_locked_case_for_budget(clamped_budget)
    return {
        'tool': str(Path(__file__).resolve()),
        'status': 'selected_named_regime_by_budget',
        'requested_max_recovered_base_weakening_cases': max_recovered_base_weakening_cases,
        'selected_recovered_base_weakening_case_budget': clamped_budget,
        'requested_budget_was_clamped': was_clamped,
        'selected_threshold_unique_appends': regime['normalized_threshold_unique_appends'],
        'selected_threshold_band_label': regime['threshold_band_label'],
        'selected_regime_code': regime['regime_code'],
        'selected_regime_label': regime['regime_label'],
        'selected_operator_summary': regime['operator_summary'],
        'selected_recovered_case_count': band_row['recovered_case_count'],
        'selected_recovered_cases': recovered_cases,
        'selected_newly_admitted_cases_vs_previous_budget': regime['newly_admitted_one_shot_weakening_cases'],
        'remaining_deferred_case_count': band_row['remaining_deferred_case_count'],
        'next_locked_case': next_locked,
        'selection_reason': 'pick the most permissive named weakening regime whose recovered base-weakening case count does not exceed the stated governance budget',
    }



def build_weakening_budget_selector_snapshot() -> dict[str, Any]:
    ladder = _recovery_rows()
    budget_catalog = [select_weakening_regime_by_recovered_case_budget(budget) for budget in range(BUDGET_MIN, BUDGET_MAX + 1)]
    marginal_costs = [
        {
            'budget_step': row['minimal_recovery_threshold_unique_appends'],
            'recovered_case_budget_after_step': index + 1,
            'recovery_kind': row['recovery_kind'],
            'recovered_case_label': row['recovered_case_label'],
        }
        for index, row in enumerate(ladder)
    ]
    capability_min_budgets = {
        'any_relaxed_release_from_stronger_tiers': 1,
        'middle_band_precision_relief': 2,
        'neutral_anchor_relaxed_release_eventually': 3,
        'direct_entry_boundary_relaxed_release': 4,
        'direct_precision_relaxed_release': 5,
    }
    return {
        'focus': 'Recast the weakening-threshold menu as a governance budget over recovered base weakening cases so inheritors can choose policy stickiness by allowed exposure count rather than threshold numerology.',
        'headline_findings': {
            'main_rule': 'Because the exact weakening menu is a serial five-case recovery ladder, every recovered-case budget from 0 through 5 selects exactly one named regime with no gaps and no redundant budgets.',
            'recoverable_base_weakening_case_count': len(ladder),
            'valid_recovered_case_budgets': list(range(BUDGET_MIN, BUDGET_MAX + 1)),
            'exact_budget_to_threshold_map_unique_appends': {
                str(entry['selected_recovered_base_weakening_case_budget']): entry['selected_threshold_unique_appends']
                for entry in budget_catalog
            },
            'minimal_budget_by_capability': capability_min_budgets,
            'serial_budget_steps_match_breakpoints': [row['minimal_recovery_threshold_unique_appends'] for row in ladder],
        },
        'decision_rules': [
            'Choose weakening policy first by how many concrete deferred base weakenings you are willing to restore, not by raw threshold magnitudes.',
            'Use the largest named regime whose recovered-case count stays within the stated budget; because the menu is serial and prefix-closed, this choice is unique.',
            'Each additional budget unit restores exactly one concrete weakening case in the audited ladder order.',
            'Budget 2 is the highest setting that still forbids neutral-anchor relaxed release, budget 3 is the first that allows it, budget 4 is the first that allows direct 8→25 release, and budget 5 is full base-policy recovery.',
            'Treat any future change that makes two budgets select the same recovered-case set, or skips a budget count, as a substantive policy redesign.',
        ],
        'budget_catalog': budget_catalog,
        'marginal_budget_steps': marginal_costs,
        'analysis_script': 'scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_budget_selector.py',
        'source_reports': [
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot_20260308.json',
            'artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_capability_selector_snapshot_20260308.json',
        ],
    }



def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Select a weakening regime by recovered base-weakening case budget.')
    parser.add_argument('--max-recovered-base-weakening-cases', required=True, type=int)
    return parser



def main() -> None:
    args = _parser().parse_args()
    print(json.dumps(select_weakening_regime_by_recovered_case_budget(args.max_recovered_base_weakening_cases), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
