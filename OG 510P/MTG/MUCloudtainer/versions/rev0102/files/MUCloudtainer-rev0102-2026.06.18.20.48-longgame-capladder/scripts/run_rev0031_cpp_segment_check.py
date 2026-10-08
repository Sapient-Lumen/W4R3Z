from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_segment import build_nochoice_segment_specs, run_nochoice_segment_cpp_panel
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import repeated_counterfactual_mulligan_gate_bundles

REV = "rev0031"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    all_strategies = repeated_counterfactual_mulligan_gate_bundles(DATA / "seed_decks.json")
    # Pick a deliberately mixed panel: baseline, rule mulligans, learned mulligans,
    # and repeated-counterfactual mulligans across the three shells.  This keeps
    # the segment checker exposed to realistic current traffic without making the
    # revision too slow to regenerate.
    wanted_suffixes = {"keep", "business", "outcome", "repeatcf"}
    strategies = [s for s in all_strategies if s.strategy_id.rsplit("_", 1)[-1] in wanted_suffixes]
    strategies = strategies[:12]
    specs = build_nochoice_segment_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=3100000,
        max_decisions=620,
        limit_pairs=48,
    )
    game_rows, segment_rows, summary = run_nochoice_segment_cpp_panel(specs, revision=REV)
    write_csv(DATA / "rev0031_cpp_segment_games.csv", game_rows)
    write_csv(DATA / "rev0031_cpp_segment_rows.csv", segment_rows)

    # Small length histogram for auditing what the segment kernel actually saw.
    hist: dict[str, int] = {}
    for row in segment_rows:
        key = str(row.get("length"))
        hist[key] = hist.get(key, 0) + 1
    payload = summary.as_dict()
    payload["segment_length_histogram"] = dict(sorted(hist.items(), key=lambda kv: int(kv[0])))
    payload["strategy_count"] = len(strategies)
    payload["spec_count"] = len(specs)
    (DATA / "rev0031_cpp_segment_summary.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
