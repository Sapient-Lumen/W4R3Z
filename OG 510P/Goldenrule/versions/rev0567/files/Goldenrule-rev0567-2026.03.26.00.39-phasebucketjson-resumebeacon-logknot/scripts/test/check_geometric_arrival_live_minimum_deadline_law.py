#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analysis.geometric_arrival_live_minimum_deadline_law import (
    build_geometric_arrival_live_minimum_deadline_validation_summary,
)


def main() -> None:
    summary = build_geometric_arrival_live_minimum_deadline_validation_summary()
    assert summary['validated_state_contexts'] > 0
    assert summary['validated_universal_contexts'] > 0
    assert summary['positive_finite_state_contexts'] > 0
    assert summary['positive_impossible_state_contexts'] > 0
    assert summary['zero_margin_state_contexts'] > 0
    assert summary['odd_minimum_state_deadlines'] == summary['positive_finite_state_contexts']
    assert summary['odd_minimum_universal_deadlines'] == summary['positive_finite_universal_contexts']
    assert summary['state_even_deadline_predecessor_equivalences'] > 0
    assert summary['universal_even_deadline_predecessor_equivalences'] > 0
    print('shared-state equiprobable geometric-arrival live minimum-deadline law checks passed')


if __name__ == '__main__':
    main()
