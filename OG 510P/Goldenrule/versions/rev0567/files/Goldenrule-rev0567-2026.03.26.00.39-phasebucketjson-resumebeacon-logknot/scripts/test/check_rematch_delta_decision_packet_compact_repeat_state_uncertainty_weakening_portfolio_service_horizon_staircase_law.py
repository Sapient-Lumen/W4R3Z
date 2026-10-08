#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_positive_service_staircase_states,
    build_positive_service_staircase_transitions,
    build_service_horizon_staircase_snapshot,
    build_shared_threshold_summary,
    build_staircase_path_word,
    build_transition_histogram,
    select_signature_by_minimum_service_share,
)


def main() -> None:
    states = build_positive_service_staircase_states()
    assert len(states) == 17
    assert states[0]['signature'] == 'E0_S0'
    assert states[-1]['signature'] == 'E6_S11'

    transitions = build_positive_service_staircase_transitions()
    assert len(transitions) == 16
    assert build_transition_histogram() == {
        'suffix_only': 10,
        'exact_only': 5,
        'diagonal_shared': 1,
    }
    assert build_staircase_path_word() == 'SSESSSESSESDSESE'

    shared = build_shared_threshold_summary()
    assert shared == {
        'shared_threshold_numerator': 1,
        'shared_threshold_denominator': 91,
        'from_signature': 'E3_S8',
        'to_signature': 'E4_S9',
        'transition_index': 11,
    }

    assert select_signature_by_minimum_service_share(0.75) == 'E0_S0'
    assert select_signature_by_minimum_service_share(0.11) == 'E2_S5'
    assert select_signature_by_minimum_service_share(1 / 91) == 'E4_S9'
    assert select_signature_by_minimum_service_share(0.010989010989010991 + 1e-6) == 'E3_S8'
    assert select_signature_by_minimum_service_share(0.0) == 'E15_S15'

    report = build_service_horizon_staircase_snapshot()
    assert report['headline_findings']['positive_service_state_count'] == 17
    assert report['headline_findings']['shared_diagonal_threshold_value'] == 1 / 91
    assert report['headline_findings']['zero_service_signature'] == 'E15_S15'
    print('weakening portfolio service horizon staircase law checks passed')


if __name__ == '__main__':
    main()
