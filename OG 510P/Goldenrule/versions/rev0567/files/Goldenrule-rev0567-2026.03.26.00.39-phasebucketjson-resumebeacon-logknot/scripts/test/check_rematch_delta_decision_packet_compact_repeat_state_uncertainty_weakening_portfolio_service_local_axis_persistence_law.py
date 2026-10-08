#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_axis_persistence_law import (
    build_axis_run_rows,
    build_exact_run_summary,
    build_longest_suffix_run_summary,
    build_max_persistence_by_unlock_kind,
    build_run_histogram_by_unlock_kind,
    build_service_local_axis_persistence_snapshot,
    select_local_axis_persistence,
)


def main() -> None:
    row = select_local_axis_persistence(0.40)
    assert row['current_signature'] == 'E1_S2'
    assert row['next_unlock_kind'] == 'suffix_only'
    assert row['persistence_steps_remaining'] == 3
    assert row['run_start_signature'] == 'E1_S2'
    assert row['run_terminal_signature_after_persistence'] == 'E1_S5'

    row = select_local_axis_persistence(0.20)
    assert row['current_signature'] == 'E1_S4'
    assert row['next_unlock_kind'] == 'suffix_only'
    assert row['persistence_steps_remaining'] == 1

    row = select_local_axis_persistence(0.05)
    assert row['current_signature'] == 'E2_S7'
    assert row['next_unlock_kind'] == 'exact_only'
    assert row['persistence_steps_remaining'] == 1
    assert row['run_terminal_signature_after_persistence'] == 'E3_S7'

    row = select_local_axis_persistence(0.011)
    assert row['current_signature'] == 'E3_S8'
    assert row['next_unlock_kind'] == 'shared_diagonal'
    assert row['persistence_steps_remaining'] == 1
    assert row['run_terminal_signature_after_persistence'] == 'E4_S9'

    row = select_local_axis_persistence(0.0001)
    assert row['current_signature'] == 'E6_S11'
    assert row['next_unlock_kind'] == 'terminal'
    assert row['persistence_steps_remaining'] == 0

    runs = build_axis_run_rows()
    assert len(runs) == 12
    assert build_run_histogram_by_unlock_kind() == {
        'suffix_only': 6,
        'exact_only': 5,
        'shared_diagonal': 1,
    }
    assert build_max_persistence_by_unlock_kind() == {
        'suffix_only': 3,
        'exact_only': 1,
        'shared_diagonal': 1,
        'terminal': 0,
    }
    assert build_exact_run_summary() == {
        'exact_run_count': 5,
        'all_exact_runs_are_singletons': True,
    }
    assert build_longest_suffix_run_summary() == {
        'run_index': 2,
        'run_step_count': 3,
        'start_signature': 'E1_S2',
        'terminal_signature_after_run': 'E1_S5',
    }

    report = build_service_local_axis_persistence_snapshot()
    assert report['headline_findings']['all_exact_runs_are_singletons'] is True
    print('weakening portfolio service local axis persistence law checks passed')


if __name__ == '__main__':
    main()
