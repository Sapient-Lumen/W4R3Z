#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_horizon_staircase_law import (
    build_staircase_path_word,
)
from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_threshold_provenance_law import (
    build_profile_threshold_ladders,
    build_reconstructed_positive_service_signatures,
    build_service_threshold_provenance_snapshot,
    build_service_threshold_provenance_summary,
    build_shared_collision_summary,
    build_threshold_provenance_rows,
    build_threshold_provenance_word,
)


def main() -> None:
    ladders = build_profile_threshold_ladders()
    assert len(ladders['exact_only']) == 6
    assert len(ladders['suffix_hitchhike_only']) == 11
    assert ladders['exact_only'][0]['threshold_numerator'] == 2
    assert ladders['exact_only'][0]['threshold_denominator'] == 5
    assert ladders['suffix_hitchhike_only'][-1]['threshold_numerator'] == 1
    assert ladders['suffix_hitchhike_only'][-1]['threshold_denominator'] == 1365

    rows = build_threshold_provenance_rows()
    assert len(rows) == 16
    assert rows[0]['provenance_kind'] == 'suffix_hitchhike_only'
    assert rows[-1]['provenance_kind'] == 'exact_only'
    assert build_threshold_provenance_word() == 'SSESSSESSESDSESE'
    assert build_threshold_provenance_word() == build_staircase_path_word()

    shared = build_shared_collision_summary()
    assert shared == {
        'threshold_numerator': 1,
        'threshold_denominator': 91,
        'threshold_index_descending': 11,
        'sources': [
            {'profile_label': 'exact_only', 'portfolio_size': 4},
            {'profile_label': 'suffix_hitchhike_only', 'portfolio_size': 9},
        ],
    }

    reconstructed = build_reconstructed_positive_service_signatures()
    assert reconstructed[0] == 'E0_S0'
    assert reconstructed[-1] == 'E6_S11'
    assert len(reconstructed) == 17

    summary = build_service_threshold_provenance_summary()
    assert summary == {
        'exact_threshold_count': 6,
        'suffix_threshold_count': 11,
        'source_threshold_event_count': 17,
        'unique_positive_threshold_count': 16,
        'shared_collision_count': 1,
        'positive_service_band_count': 17,
        'threshold_provenance_word': 'SSESSSESSESDSESE',
        'shared_collision_threshold_value': 1 / 91,
        'shared_collision_threshold_fraction': '1/91',
    }

    report = build_service_threshold_provenance_snapshot()
    assert report['headline_findings']['reconstruction_matches_positive_service_staircase'] is True
    assert report['headline_findings']['staircase_path_word_matches_threshold_provenance_word'] is True
    print('weakening portfolio service threshold provenance law checks passed')


if __name__ == '__main__':
    main()
