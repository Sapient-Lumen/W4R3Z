#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_residual_axis_budget_law import (
    build_balanced_budget_state_summary,
    build_budget_consistency_summary,
    build_diagonal_budget_phase_summary,
    build_phase_histogram,
    build_residual_balance_histogram,
    build_service_residual_axis_budget_snapshot,
    select_residual_axis_budget,
)


def main() -> None:
    row = select_residual_axis_budget(0.40)
    assert row['current_signature'] == 'E1_S2'
    assert row['shared_diagonal_steps_remaining'] == 1
    assert row['exact_only_steps_remaining'] == 4
    assert row['suffix_only_steps_remaining'] == 8
    assert row['total_relaxation_steps_remaining'] == 13
    assert row['phase_kind'] == 'pre_diagonal'
    assert row['residual_balance_kind'] == 'suffix_heavier'

    row = select_residual_axis_budget(0.05)
    assert row['current_signature'] == 'E2_S7'
    assert row['shared_diagonal_steps_remaining'] == 1
    assert row['exact_only_steps_remaining'] == 3
    assert row['suffix_only_steps_remaining'] == 3
    assert row['total_relaxation_steps_remaining'] == 7
    assert row['residual_balance_kind'] == 'balanced'

    row = select_residual_axis_budget(0.011)
    assert row['current_signature'] == 'E3_S8'
    assert row['shared_diagonal_steps_remaining'] == 1
    assert row['exact_only_steps_remaining'] == 2
    assert row['suffix_only_steps_remaining'] == 2
    assert row['phase_kind'] == 'pre_diagonal'

    row = select_residual_axis_budget(0.01)
    assert row['current_signature'] == 'E4_S9'
    assert row['shared_diagonal_steps_remaining'] == 0
    assert row['exact_only_steps_remaining'] == 2
    assert row['suffix_only_steps_remaining'] == 2
    assert row['total_relaxation_steps_remaining'] == 4
    assert row['phase_kind'] == 'post_diagonal'

    row = select_residual_axis_budget(0.0001)
    assert row['current_signature'] == 'E6_S11'
    assert row['shared_diagonal_steps_remaining'] == 0
    assert row['exact_only_steps_remaining'] == 0
    assert row['suffix_only_steps_remaining'] == 0
    assert row['total_relaxation_steps_remaining'] == 0
    assert row['phase_kind'] == 'terminal'

    assert build_phase_histogram() == {
        'pre_diagonal': 12,
        'post_diagonal': 4,
        'terminal': 1,
    }
    assert build_residual_balance_histogram() == {
        'suffix_heavier': 10,
        'exact_heavier': 2,
        'balanced': 5,
    }
    assert build_diagonal_budget_phase_summary() == {
        'shared_diagonal_budget_lives_in_prefix_count': 12,
        'last_signature_with_shared_diagonal_budget_live': 'E3_S8',
        'first_signature_after_shared_diagonal_budget_is_spent': 'E4_S9',
        'post_diagonal_nonterminal_state_count': 4,
    }
    assert build_budget_consistency_summary() == {
        'total_relaxation_steps_match_staircase_distance_to_terminal': True,
        'shared_diagonal_budget_is_prefix_contiguous': True,
        'residual_axis_budget_fully_summarizes_future_path_shape': True,
    }
    assert build_balanced_budget_state_summary() == {
        'balanced_state_count': 5,
        'balanced_signatures': ['E2_S7', 'E3_S8', 'E4_S9', 'E5_S10', 'E6_S11'],
    }

    report = build_service_residual_axis_budget_snapshot()
    assert report['headline_findings']['budget_consistency_summary']['total_relaxation_steps_match_staircase_distance_to_terminal'] is True
    print('weakening portfolio service residual axis budget law checks passed')


if __name__ == '__main__':
    main()
