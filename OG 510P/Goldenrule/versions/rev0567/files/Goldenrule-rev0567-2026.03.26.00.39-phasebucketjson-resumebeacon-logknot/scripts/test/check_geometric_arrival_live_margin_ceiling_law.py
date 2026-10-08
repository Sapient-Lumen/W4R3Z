#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_margin_ceiling_law import (
    build_geometric_arrival_live_margin_ceiling_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_margin_ceiling_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['positive_state_ceiling_contexts'] > 0
    assert summary['zero_only_state_contexts'] > 0
    assert summary['positive_universal_ceiling_contexts'] > 0
    assert summary['zero_only_universal_contexts'] > 0
    assert summary['validated_state_boundary_checks'] > 0
    assert summary['validated_universal_boundary_checks'] > 0
    assert summary['state_odd_even_pair_plateaus'] > 0
    assert summary['universal_odd_even_pair_plateaus'] > 0
    print('shared-state equiprobable geometric-arrival live margin ceiling law checks passed')


if __name__ == '__main__':
    main()
