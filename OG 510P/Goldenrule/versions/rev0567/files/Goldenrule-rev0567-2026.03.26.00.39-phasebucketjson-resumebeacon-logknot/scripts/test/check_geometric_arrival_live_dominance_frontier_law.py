#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_dominance_frontier_law import (
    build_geometric_arrival_live_dominance_frontier_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_dominance_frontier_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['state_prefix_reduction_matches'] == summary['validated_state_contexts']
    assert summary['universal_prefix_reduction_matches'] == summary['validated_universal_contexts']
    assert summary['admitted_state_contexts'] > 0
    assert summary['rejected_state_contexts'] > 0
    assert summary['admitted_universal_contexts'] > 0
    assert summary['rejected_universal_contexts'] > 0
    assert summary['prefix_step_certificates'] > 0
    assert summary['batch_step_certificates'] > 0
    assert summary['arrival_step_certificates'] > 0
    assert summary['hold_cost_step_certificates'] > 0
    assert summary['margin_step_certificates'] > 0
    assert summary['deadline_step_certificates'] > 0
    assert summary['strict_prefix_gains'] > 0
    assert summary['strict_batch_penalties'] > 0
    assert summary['strict_arrival_gains'] > 0
    assert summary['strict_hold_cost_penalties'] > 0
    assert summary['strict_margin_penalties'] > 0
    assert summary['strict_deadline_gains'] > 0
    for key in [
        'prefix_gain_example',
        'batch_penalty_example',
        'arrival_gain_example',
        'hold_cost_penalty_example',
        'margin_penalty_example',
        'deadline_gain_example',
    ]:
        assert summary[key] is not None
    print('shared-state equiprobable geometric-arrival live dominance-frontier law checks passed')


if __name__ == '__main__':
    main()
