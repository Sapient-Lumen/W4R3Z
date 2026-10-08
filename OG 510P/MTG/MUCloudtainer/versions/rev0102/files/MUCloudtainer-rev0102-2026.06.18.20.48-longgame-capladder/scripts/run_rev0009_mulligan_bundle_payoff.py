#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import aggregate_payoff_rows, build_payoff_rows, mulligan_strategy_bundles, write_csv


def main() -> None:
    strategies = mulligan_strategy_bundles(ROOT / "data" / "seed_decks.json")
    rows = build_payoff_rows(strategies, life_totals=(20, 40), reps=1, base_seed=99000, max_decisions=500)
    agg = aggregate_payoff_rows(rows)
    write_csv(ROOT / "data" / "rev0009_mulligan_bundle_payoff_games.csv", rows)
    write_csv(ROOT / "data" / "rev0009_mulligan_bundle_payoff_aggregate.csv", agg)
    summary = {
        "strategies": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(agg),
        "life_totals": [20, 40],
        "mulligan_policies": sorted({str(s.mulligan_policy) for s in strategies}),
        "max_decision_games": sum(1 for r in rows if str(r.get("loss_reason")) == "max_decisions_reached"),
        "note": "Smoke data only. The point is to prove deck+mulligan+pilot bundles can be cross-played with seat-specific mulligan policies.",
    }
    (ROOT / "data" / "rev0009_mulligan_bundle_payoff_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
