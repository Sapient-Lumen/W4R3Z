#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_burden_axis_law import (
    build_geometric_arrival_live_burden_axis_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_burden_axis_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['nonnegative_state_admitted_contexts'] > 0
    assert summary['nonnegative_state_rejected_contexts'] > 0
    assert summary['nonnegative_universal_admitted_contexts'] > 0
    assert summary['nonnegative_universal_rejected_contexts'] > 0
    assert summary['zero_burden_state_contexts'] > 0
    assert summary['zero_burden_universal_contexts'] > 0
    assert summary['state_equivalent_member_checks'] > 0
    assert summary['universal_equivalent_member_checks'] > 0
    assert summary['state_burden_ladders_with_strict_drop'] > 0
    assert summary['universal_burden_ladders_with_strict_drop'] > 0
    assert summary['burden_spectrum_pair_plateaus'] > 0
    assert summary['minimum_unique_burden_classes_per_hazard_deadline'] >= 1
    print('shared-state equiprobable geometric-arrival live burden-axis law checks passed')


if __name__ == '__main__':
    main()
