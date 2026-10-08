#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_hazard_staircase_law import (
    build_geometric_arrival_live_hazard_staircase_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_hazard_staircase_validation_summary()
    assert summary['validated_state_ladders'] > 0
    assert summary['validated_universal_ladders'] > 0
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['state_monotone_class_ladders'] == summary['validated_state_ladders']
    assert summary['universal_monotone_class_ladders'] == summary['validated_universal_ladders']
    assert summary['state_nonincreasing_finite_deadline_ladders'] == summary['validated_state_ladders']
    assert summary['universal_nonincreasing_finite_deadline_ladders'] == summary['validated_universal_ladders']
    assert summary['state_suffix_finite_ladders'] == summary['validated_state_ladders']
    assert summary['universal_suffix_finite_ladders'] == summary['validated_universal_ladders']
    assert summary['state_finite_deadline_observations'] > 0
    assert summary['universal_finite_deadline_observations'] > 0
    assert summary['state_finite_deadline_observations'] == summary['state_odd_finite_deadline_observations']
    assert summary['universal_finite_deadline_observations'] == summary['universal_odd_finite_deadline_observations']
    assert summary['state_deadline_drop_ladders'] > 0
    assert summary['universal_deadline_drop_ladders'] > 0
    assert summary['state_deadline_drop_events'] >= summary['state_deadline_drop_ladders']
    assert summary['universal_deadline_drop_events'] >= summary['universal_deadline_drop_ladders']
    assert summary['state_class_improvement_ladders'] > 0
    assert summary['universal_class_improvement_ladders'] > 0
    print('shared-state equiprobable geometric-arrival live hazard-staircase law checks passed')


if __name__ == '__main__':
    main()
