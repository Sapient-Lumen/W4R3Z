from __future__ import annotations

import json
import sys
from pathlib import Path
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.opening_counterfactual import build_counterfactual_specs
from src.muc5.opening_counterfactual_repeat import run_repeated_opening_counterfactual_panel
from src.muc5.payoff import load_seed_decks, write_csv

REV = "rev0031"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    seed_decks = load_seed_decks(DATA / "seed_decks.json")
    # rev0030 used 24 paired openings and 2 branch rollouts.  This scale probe
    # bumps both dimensions modestly without retraining a new policy yet.  The
    # aim is to measure how noisy the keep-vs-mulligan labels remain.
    specs = build_counterfactual_specs(seed_decks, samples_per_shell_life=3, base_seed=31000)
    specs = tuple(replace(s, max_decisions=440) for s in specs)
    result = run_repeated_opening_counterfactual_panel(specs, rollout_reps=3, rollout_seed_stride=9151, revision=REV)
    write_csv(DATA / "rev0031_repeated_cf_scale_branch_games.csv", result.branch_rows)
    write_csv(DATA / "rev0031_repeated_cf_scale_pairs.csv", result.paired_rows)
    write_csv(DATA / "rev0031_repeated_cf_scale_cpp_transitions.csv", [r.as_dict() for r in result.transition_rows])
    payload = dict(result.summary)
    # Add a few label-budget diagnostics that matter for the next training pass.
    non_tie = [r for r in result.paired_rows if r.get("better_branch_mean") != "tie"]
    confident = [r for r in result.paired_rows if float(r.get("abs_delta_mean", 0.0) or 0.0) >= 0.25]
    payload.update({
        "non_tie_pairs": len(non_tie),
        "confident_abs_delta_ge_025_pairs": len(confident),
        "scale_note": "modest budget increase over rev0030; not a new model, just better label-budget diagnostics",
    })
    (DATA / "rev0031_repeated_cf_scale_summary.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
