from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.payoff import aggregate_payoff_rows, build_payoff_rows, default_strategy_bundles, write_csv


def main() -> None:
    strategies = default_strategy_bundles(ROOT / "data" / "seed_decks.json")
    rows = build_payoff_rows(strategies, reps=1, base_seed=808000, max_decisions=500)
    agg = aggregate_payoff_rows(rows)
    write_csv(ROOT / "data" / "rev0008_payoff_games.csv", rows)
    write_csv(ROOT / "data" / "rev0008_payoff_aggregate.csv", agg)
    score_by_life = {}
    for life in sorted({int(r["starting_life"]) for r in rows}):
        life_rows = [r for r in rows if int(r["starting_life"]) == life]
        score_by_life[str(life)] = sum(float(r["p0_score"]) for r in life_rows) / max(1, len(life_rows))
    summary = {
        "revision": "rev0008",
        "strategies": [s.as_dict() for s in strategies],
        "games": len(rows),
        "aggregate_rows": len(agg),
        "life_totals": sorted({int(r["starting_life"]) for r in rows}),
        "agents": sorted({str(r["agent0"]) for r in rows} | {str(r["agent1"]) for r in rows}),
        "decks": sorted({str(r["deck0"]) for r in rows} | {str(r["deck1"]) for r in rows}),
        "loss_reasons": dict(Counter(str(r["loss_reason"]) for r in rows)),
        "mean_p0_score_by_life": score_by_life,
        "mean_decisions": sum(float(r["decisions"]) for r in rows) / max(1, len(rows)),
    }
    (ROOT / "data" / "rev0008_payoff_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
