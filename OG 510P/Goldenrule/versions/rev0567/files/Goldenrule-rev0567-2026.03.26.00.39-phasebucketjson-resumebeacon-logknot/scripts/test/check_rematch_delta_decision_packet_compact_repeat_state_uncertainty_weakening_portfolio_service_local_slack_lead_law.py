#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_local_slack_lead_law import (
    build_advantage_histogram,
    build_local_slack_consistency_summary,
    build_nearest_nonterminal_tie_summary,
    build_positive_service_local_slack_rows,
    build_service_local_slack_lead_snapshot,
    build_smallest_axis_tax_frontier,
    select_local_slack_lead,
)


def main() -> None:
    row = select_local_slack_lead(0.40)
    assert row['current_signature'] == 'E1_S2'
    assert row['advantage_kind'] == 'suffix_advantage'
    assert row['signed_slack_lead_fraction'] == '20/91'
    assert row['next_unlock_kind'] == 'suffix_only'

    row = select_local_slack_lead(0.05)
    assert row['current_signature'] == 'E2_S7'
    assert row['advantage_kind'] == 'exact_advantage'
    assert row['signed_slack_lead_fraction'] == '-5/273'
    assert row['next_unlock_kind'] == 'exact_only'

    row = select_local_slack_lead(0.011)
    assert row['current_signature'] == 'E3_S8'
    assert row['advantage_kind'] == 'shared_tie'
    assert row['signed_slack_lead_fraction'] == '0/1'
    assert row['next_unlock_kind'] == 'shared_diagonal'

    row = select_local_slack_lead(0.0001)
    assert row['current_signature'] == 'E6_S11'
    assert row['advantage_kind'] == 'terminal'
    assert row['signed_slack_lead_fraction'] is None

    row = select_local_slack_lead(0.000466200466)
    assert row['current_signature'] == 'E5_S11'
    assert row['advantage_kind'] == 'exact_only_remaining'
    assert row['next_unlock_kind'] == 'exact_only'

    rows = build_positive_service_local_slack_rows()
    assert len(rows) == 17
    assert build_advantage_histogram() == {
        'suffix_advantage': 10,
        'exact_advantage': 4,
        'shared_tie': 1,
        'exact_only_remaining': 1,
        'suffix_only_remaining': 0,
        'terminal': 1,
    }
    assert build_local_slack_consistency_summary()['advantage_sign_recovers_next_unlock_kind'] is True
    assert build_nearest_nonterminal_tie_summary() == {
        'state_index': 14,
        'current_signature': 'E5_S10',
        'advantage_kind': 'suffix_advantage',
        'next_unlock_kind': 'suffix_only',
        'absolute_slack_lead_fraction': '8/15015',
    }
    frontier = build_smallest_axis_tax_frontier()
    assert frontier[0]['current_signature'] == 'E5_S10'
    assert frontier[1]['current_signature'] == 'E4_S10'

    report = build_service_local_slack_lead_snapshot()
    assert report['headline_findings']['constant_bandwise_axis_tax_interpretation_holds'] is True
    print('weakening portfolio service local slack lead law checks passed')


if __name__ == '__main__':
    main()
