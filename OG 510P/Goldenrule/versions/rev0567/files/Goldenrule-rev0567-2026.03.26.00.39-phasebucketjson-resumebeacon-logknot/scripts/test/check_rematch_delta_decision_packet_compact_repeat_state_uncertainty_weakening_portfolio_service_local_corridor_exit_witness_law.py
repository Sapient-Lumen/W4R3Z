#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_corridor_exit_witness_law import (
    build_boundary_transition_histogram,
    build_bridge_summary,
    build_run_boundary_transition_histogram,
    build_corridor_exit_consistency_summary,
    build_kink_summary,
    build_service_local_corridor_exit_witness_snapshot,
    select_local_corridor_exit_witness,
)


def main() -> None:
    row = select_local_corridor_exit_witness(0.40)
    assert row['current_signature'] == 'E1_S2'
    assert row['current_unlock_kind'] == 'suffix_only'
    assert row['current_corridor_steps_remaining'] == 3
    assert row['current_corridor_terminal_signature'] == 'E1_S5'
    assert row['boundary_transition_kind'] == 'suffix_to_exact_bridge'
    assert row['boundary_unlock_kind'] == 'exact_only'
    assert row['boundary_next_signature_after_relaxation'] == 'E2_S5'
    assert row['next_corridor_unlock_kind'] == 'exact_only'
    assert row['next_corridor_steps'] == 1

    row = select_local_corridor_exit_witness(0.011)
    assert row['current_signature'] == 'E3_S8'
    assert row['current_unlock_kind'] == 'shared_diagonal'
    assert row['current_corridor_steps_remaining'] == 1
    assert row['current_corridor_terminal_signature'] == 'E4_S9'
    assert row['boundary_transition_kind'] == 'shared_to_suffix_kink'
    assert row['boundary_unlock_kind'] == 'suffix_only'
    assert row['boundary_next_signature_after_relaxation'] == 'E4_S10'
    assert row['next_corridor_unlock_kind'] == 'suffix_only'
    assert row['next_corridor_steps'] == 1

    row = select_local_corridor_exit_witness(0.01)
    assert row['current_signature'] == 'E4_S9'
    assert row['current_unlock_kind'] == 'suffix_only'
    assert row['current_corridor_steps_remaining'] == 1
    assert row['current_corridor_terminal_signature'] == 'E4_S10'
    assert row['boundary_transition_kind'] == 'suffix_to_exact_bridge'
    assert row['boundary_unlock_kind'] == 'exact_only'
    assert row['boundary_next_signature_after_relaxation'] == 'E5_S10'

    row = select_local_corridor_exit_witness(0.0001)
    assert row['current_signature'] == 'E6_S11'
    assert row['current_unlock_kind'] == 'terminal'
    assert row['current_corridor_steps_remaining'] == 0
    assert row['boundary_transition_kind'] == 'terminal'
    assert row['boundary_unlock_kind'] == 'terminal'
    assert row['next_corridor_unlock_kind'] == 'terminal'

    assert build_boundary_transition_histogram() == {
        'suffix_to_exact_bridge': 9,
        'exact_to_suffix_bridge': 4,
        'suffix_to_shared_kink': 1,
        'shared_to_suffix_kink': 1,
        'terminal_entry': 1,
        'terminal': 1,
    }
    assert build_run_boundary_transition_histogram() == {
        'suffix_to_exact_bridge': 5,
        'exact_to_suffix_bridge': 4,
        'suffix_to_shared_kink': 1,
        'shared_to_suffix_kink': 1,
        'terminal_entry': 1,
    }
    assert build_bridge_summary() == {
        'suffix_corridors_that_end_in_exact_bridges': 9,
        'exact_spikes_that_hand_back_to_suffix': 4,
        'last_exact_bridge_signature_before_terminal': 'E4_S10',
    }
    assert build_kink_summary() == {
        'suffix_to_shared_kink_count': 1,
        'suffix_to_shared_kink_signature': 'E3_S8',
        'shared_to_suffix_kink_count': 1,
        'shared_to_suffix_kink_signature': 'E3_S8',
    }
    assert build_corridor_exit_consistency_summary() == {
        'every_nonterminal_corridor_has_a_boundary_witness': True,
        'exact_only_corridors_never_transition_directly_to_exact_only_or_shared_diagonal': True,
        'shared_diagonal_is_a_single_step_bridge_back_to_suffix': True,
        'longer_than_one_step_next_corridor_exists_only_for_suffix': True,
    }

    report = build_service_local_corridor_exit_witness_snapshot()
    assert report['headline_findings']['corridor_exit_consistency_summary']['shared_diagonal_is_a_single_step_bridge_back_to_suffix'] is True
    print('weakening portfolio service local corridor exit witness law checks passed')


if __name__ == '__main__':
    main()
