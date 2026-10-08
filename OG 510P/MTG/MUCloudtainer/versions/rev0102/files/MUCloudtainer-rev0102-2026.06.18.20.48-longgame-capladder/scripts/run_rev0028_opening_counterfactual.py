from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.opening_counterfactual import build_counterfactual_specs, run_opening_counterfactual_panel
from src.muc5.payoff import load_seed_decks, write_csv

REV = "rev0028"
DATA = ROOT / "data"


def summarize_context(rows):
    groups = defaultdict(list)
    for row in rows:
        q = float(row["initial_hand_quality"])
        if q < 3.5:
            qbin = "bad_q_lt_3_5"
        elif q < 5.0:
            qbin = "border_q_3_5_to_5"
        elif q < 6.5:
            qbin = "good_q_5_to_6_5"
        else:
            qbin = "great_q_ge_6_5"
        key = (row["deck0"], int(row["starting_life"]), int(row["starting_player"]), row["fallback_mulligan0"], qbin)
        groups[key].append(row)
    out = []
    for (deck0, life, start, fallback, qbin), vals in sorted(groups.items()):
        deltas = [float(v["mulligan_minus_keep"]) for v in vals]
        out.append({
            "deck0": deck0,
            "starting_life": life,
            "starting_player": start,
            "fallback_mulligan0": fallback,
            "quality_bin": qbin,
            "pairs": len(vals),
            "mean_mulligan_minus_keep": sum(deltas) / len(deltas),
            "mulligan_better_rate": sum(1 for v in vals if v["better_branch"] == "mulligan") / len(vals),
            "keep_better_rate": sum(1 for v in vals if v["better_branch"] == "keep") / len(vals),
            "tie_rate": sum(1 for v in vals if v["better_branch"] == "tie") / len(vals),
            "truncation_pairs": sum(1 for v in vals if str(v.get("keep_truncation")).lower() in {"true", "1"} or str(v.get("mulligan_truncation")).lower() in {"true", "1"}),
        })
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    decks = load_seed_decks(DATA / "seed_decks.json")
    specs = build_counterfactual_specs(decks, samples_per_shell_life=6, base_seed=2802800)
    result = run_opening_counterfactual_panel(specs)

    write_csv(DATA / f"{REV}_opening_counterfactual_branch_games.csv", result.branch_rows)
    write_csv(DATA / f"{REV}_opening_counterfactual_pairs.csv", result.paired_rows)
    write_csv(DATA / f"{REV}_opening_counterfactual_context_summary.csv", summarize_context(result.paired_rows))
    write_csv(DATA / f"{REV}_opening_counterfactual_cpp_transitions.csv", [r.as_dict() for r in result.transition_rows])
    summary = dict(result.summary)
    summary.update({
        "codename": "openingcounterfactual-metacache",
        "branch_rows_path": f"data/{REV}_opening_counterfactual_branch_games.csv",
        "pairs_path": f"data/{REV}_opening_counterfactual_pairs.csv",
        "context_summary_path": f"data/{REV}_opening_counterfactual_context_summary.csv",
        "cpp_transitions_path": f"data/{REV}_opening_counterfactual_cpp_transitions.csv",
        "samples_per_shell_life": 6,
        "design_note": "Each pair forces player 0 to KEEP vs MULLIGAN from the exact same first seven-card look; opponent pregame state and transition seeds are held fixed across branches.",
    })
    (DATA / f"{REV}_opening_counterfactual_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
