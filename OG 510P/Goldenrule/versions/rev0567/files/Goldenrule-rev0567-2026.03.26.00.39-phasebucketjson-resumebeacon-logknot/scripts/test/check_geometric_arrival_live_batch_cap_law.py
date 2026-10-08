#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_batch_cap_law import (
    build_geometric_arrival_live_batch_cap_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_batch_cap_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['validated_state_frontier_checks'] > 0
    assert summary['validated_universal_frontier_checks'] > 0
    assert summary['positive_state_feasible_contexts'] > 0
    assert summary['positive_state_impossible_contexts'] > 0
    assert summary['zero_margin_state_contexts'] > 0
    assert summary['state_odd_even_pair_plateaus'] > 0
    assert summary['universal_odd_even_pair_plateaus'] > 0
    print('shared-state equiprobable geometric-arrival live batch-cap law checks passed')


if __name__ == '__main__':
    main()
