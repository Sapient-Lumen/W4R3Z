#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law import (
    build_dense_codec_arithmetic_decode_validation_summary,
)


def main() -> None:
    summary = build_dense_codec_arithmetic_decode_validation_summary()
    assert summary['exact_dense_interval_state_decoder_equivalence_count'] == 153
    assert summary['exact_dense_interval_state_roundtrip_count'] == 153
    assert summary['exact_dense_shortest_word_state_choice_decoder_equivalence_count'] == 513
    assert summary['exact_dense_shortest_word_decoder_equivalence_count'] == 513
    assert summary['exact_dense_shortest_word_roundtrip_count'] == 513
    assert summary['exact_shortest_word_catalog_count'] == 513
    assert summary['exact_local_choice_branch_count'] == 513
    assert summary['interval_dense_decode_legacy_scan_iteration_total'] == 969
    assert math.isclose(summary['interval_dense_decode_legacy_scan_iteration_mean'], 969 / 153)
    assert summary['interval_dense_decode_legacy_scan_iteration_max'] == 17
    assert summary['shortest_word_dense_decode_legacy_scan_iteration_total'] == 1120
    assert math.isclose(summary['shortest_word_dense_decode_legacy_scan_iteration_mean_over_full_catalog'], 1120 / 513)
    assert summary['shortest_word_dense_decode_legacy_scan_iteration_max'] == 14
    assert summary['total_legacy_scan_iterations_removed_by_exhaustive_arithmetic_revalidation'] == 2089
    assert summary['interval_dense_decode_formula'] == 'a = (35 - ceil_sqrt(1225 - 8*i)) // 2; b = a + i - a*(35-a)//2'
    assert summary['interior_nonsingleton_dense_decode_formula'] == 'a = 1 + (29 - ceil_sqrt(841 - 8*s)) // 2; b = a + 1 + s - (a-1)*(30-a)//2'
    assert summary['dense_interval_and_dense_word_codecs_now_admit_tableless_arithmetic_decode'] is True
    print('ok')


if __name__ == '__main__':
    main()
