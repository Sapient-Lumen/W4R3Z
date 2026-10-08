#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_upgrade_witness_law import (
    build_local_unlock_histogram,
    build_positive_service_local_witness_rows,
    build_service_local_upgrade_witness_snapshot,
    build_shared_local_unlock_summary,
    select_local_upgrade_witness,
)


def main() -> None:
    witness = select_local_upgrade_witness(0.40)
    assert witness['current_signature'] == 'E1_S2'
    assert witness['next_unlock_kind'] == 'suffix_only'
    assert witness['next_unlock_threshold_fraction'] == '33/91'
    assert witness['next_signature_after_relaxation'] == 'E1_S3'

    witness = select_local_upgrade_witness(0.05)
    assert witness['current_signature'] == 'E2_S7'
    assert witness['next_unlock_kind'] == 'exact_only'
    assert witness['next_unlock_threshold_fraction'] == '4/91'
    assert witness['next_signature_after_relaxation'] == 'E3_S7'

    witness = select_local_upgrade_witness(0.011)
    assert witness['current_signature'] == 'E3_S8'
    assert witness['next_unlock_kind'] == 'shared_diagonal'
    assert witness['next_unlock_threshold_fraction'] == '1/91'
    assert witness['next_signature_after_relaxation'] == 'E4_S9'

    witness = select_local_upgrade_witness(0.0001)
    assert witness['current_signature'] == 'E6_S11'
    assert witness['next_unlock_kind'] == 'terminal'
    assert witness['next_signature_after_relaxation'] is None

    rows = build_positive_service_local_witness_rows()
    assert len(rows) == 17
    assert all(
        row['next_signature_after_relaxation'] == row['expected_next_signature']
        for row in rows[:-1]
    )
    assert rows[-1]['current_signature'] == 'E6_S11'
    assert rows[-1]['next_unlock_kind'] == 'terminal'

    assert build_local_unlock_histogram() == {
        'exact_only': 5,
        'suffix_only': 10,
        'shared_diagonal': 1,
        'terminal': 1,
    }
    assert build_shared_local_unlock_summary() == {
        'current_signature': 'E3_S8',
        'next_signature_after_relaxation': 'E4_S9',
        'next_unlock_threshold_fraction': '1/91',
        'state_index': 11,
    }

    report = build_service_local_upgrade_witness_snapshot()
    assert report['headline_findings']['statewise_next_signature_matches_staircase_successor'] is True
    print('weakening portfolio service local upgrade witness law checks passed')


if __name__ == '__main__':
    main()
