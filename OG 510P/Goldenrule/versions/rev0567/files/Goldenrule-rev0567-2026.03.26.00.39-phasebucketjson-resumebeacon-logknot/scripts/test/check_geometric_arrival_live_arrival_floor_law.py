#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_arrival_floor_law import (
    build_geometric_arrival_live_arrival_floor_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_arrival_floor_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['state_arrival_ladders'] == summary['validated_state_contexts']
    assert summary['universal_arrival_ladders'] == summary['validated_universal_contexts']
    assert summary['state_single_crossing_ladders'] == summary['state_arrival_ladders']
    assert summary['universal_single_crossing_ladders'] == summary['universal_arrival_ladders']
    assert summary['state_ladders_with_positive_growth'] > 0
    assert summary['universal_ladders_with_positive_growth'] > 0
    assert summary['state_continuous_floor_exists_contexts'] > 0
    assert summary['state_impossible_contexts'] > 0
    assert summary['universal_continuous_floor_exists_contexts'] > 0
    assert summary['universal_impossible_contexts'] > 0
    assert summary['state_one_tick_closed_form_checks'] > 0
    assert summary['universal_one_tick_closed_form_checks'] > 0
    assert summary['state_derivative_certificates'] > 0
    assert summary['universal_derivative_certificates'] > 0
    print('shared-state equiprobable geometric-arrival live arrival-floor law checks passed')


if __name__ == '__main__':
    main()
