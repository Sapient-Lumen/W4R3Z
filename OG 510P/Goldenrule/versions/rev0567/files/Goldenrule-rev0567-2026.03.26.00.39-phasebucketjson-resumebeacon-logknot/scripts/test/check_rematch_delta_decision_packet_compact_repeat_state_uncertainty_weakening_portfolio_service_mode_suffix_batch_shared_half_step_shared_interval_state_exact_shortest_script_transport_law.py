#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shared_interval_state_exact_shortest_script_transport_law import (
    build_shared_interval_state_exact_shortest_script_transport_validation_summary,
    recommend_shared_interval_state_exact_shortest_script_transport,
)


def main() -> int:
    summary = build_shared_interval_state_exact_shortest_script_transport_validation_summary()

    if summary['comparison_counts_by_batch_length']['1'] != {'loss': 270, 'strict_win': 179, 'tie': 64}:
        raise SystemExit('unexpected batch-length-1 comparison counts')
    if summary['comparison_counts_by_batch_length']['2'] != {'strict_win': 5197, 'tie': 116}:
        raise SystemExit('unexpected batch-length-2 comparison counts')
    if summary['comparison_counts_by_batch_length']['3'] != {'strict_win': 88353}:
        raise SystemExit('unexpected batch-length-3 comparison counts')
    if summary['strict_dominance_threshold_counter'] != {'1': 106, '2': 39, '3': 8}:
        raise SystemExit('unexpected strict-dominance threshold counts')
    if summary['max_strict_dominance_threshold'] != 3:
        raise SystemExit('shared-state strict-dominance threshold should top out at 3')
    if not summary['shared_state_transport_never_loses_at_batch_length_2']:
        raise SystemExit('batch-length-2 shared-state transport should never lose')
    if not summary['shared_state_transport_is_strictly_dominant_for_every_audited_case_at_batch_length_3']:
        raise SystemExit('batch-length-3 shared-state transport should be strictly dominant')

    if recommend_shared_interval_state_exact_shortest_script_transport((8, 8), 1)['recommendation'] != 'global_exact_shortest_word_prefix':
        raise SystemExit('one-word interior singleton should still defer to the standalone exact-word frontier')
    if recommend_shared_interval_state_exact_shortest_script_transport((8, 8), 2)['recommendation'] != 'shared_interval_state_prefix_plus_local_choice_prefixes':
        raise SystemExit('two-word shared-state exact batch should use the shared-state transport path')
    if recommend_shared_interval_state_exact_shortest_script_transport((8, 8), 3)['guarantee'] != 'strict_win':
        raise SystemExit('three-word shared-state exact batch should be strictly dominated by the shared-state transport path')
    if recommend_shared_interval_state_exact_shortest_script_transport((7, 12), 1)['guarantee'] != 'tie':
        raise SystemExit('one-word eight-bit interior nonsingleton should tie under the shared-state path')
    if recommend_shared_interval_state_exact_shortest_script_transport((0, 16), 1)['guarantee'] != 'strict_win':
        raise SystemExit('unique-word identity state should already be a strict shared-state win at one word')

    print('ok: shared-interval-state exact shortest-script transport law')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
