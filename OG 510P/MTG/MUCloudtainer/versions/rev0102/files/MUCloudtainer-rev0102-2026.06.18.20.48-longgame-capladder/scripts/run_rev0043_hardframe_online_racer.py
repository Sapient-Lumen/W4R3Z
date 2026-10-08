from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_hard_racing import collect_hard_frame_online_racing
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import (
    adaptive_counterfactual_action_ranker_bundles,
    budgeted_counterfactual_action_ranker_bundles,
    disagreement_counterfactual_action_ranker_bundles,
    outcome_ranker_probe_bundles,
)

REV = "rev0043"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    base = outcome_ranker_probe_bundles(DATA / "seed_decks.json")
    try:
        dis = disagreement_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        dis = ()
    try:
        bud = budgeted_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        bud = ()
    try:
        ada = adaptive_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")
    except Exception:
        ada = ()
    behavior_strategies = tuple(base[:4]) + tuple(dis[:3]) + tuple(bud[:2]) + tuple(ada[:2])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=4304400,
        max_decisions=420,
        limit_games=20,
    )
    selected, candidates, branches, allocations, votes, transitions, summary = collect_hard_frame_online_racing(
        specs,
        revision=REV,
        max_behavior_frames=180,
        max_situations=10,
        high_action_threshold=5,
        max_actions_per_frame=3,
        branch_action_budget=5,
        base_rollouts_per_action=1,
        max_extra_rollouts_per_situation=4,
        adaptive_stop_margin=0.40,
        adaptive_target_confidence=0.55,
        branch_max_decisions=260,
        ranker_revision="rev0034",
        max_per_behavior_game=2,
    )
    write_csv(DATA / "rev0043_hard_online_racing_selected.csv", selected)
    write_csv(DATA / "rev0043_hard_online_racing_candidates.csv", candidates)
    write_csv(DATA / "rev0043_hard_online_racing_branch_games.csv", branches)
    write_csv(DATA / "rev0043_hard_online_racing_allocations.csv", allocations)
    write_csv(DATA / "rev0043_hard_online_racing_votes.csv", votes)
    write_csv(DATA / "rev0043_hard_online_racing_cpp_transitions.csv", transitions)

    cand_df = pd.DataFrame(candidates)
    branch_df = pd.DataFrame(branches)
    selected_df = pd.DataFrame(selected)
    alloc_df = pd.DataFrame(allocations)
    if not cand_df.empty:
        sit = cand_df.groupby("situation_id").agg(
            action_count=("action_count", "first"),
            branched_action_count=("branched_action_count", "first"),
            situation_best_margin=("situation_best_margin", "first"),
            label_confidence_proxy=("label_confidence_proxy", "first"),
            total_adaptive_extra=("total_adaptive_extra_rollouts", "first"),
            stopped_early=("adaptive_stopped_early", "first"),
            behavior_chosen_is_best=("behavior_chosen_is_best", "max"),
        ).reset_index()
        sit.to_csv(DATA / "rev0043_hard_online_racing_situation_summary.csv", index=False)
    else:
        sit = pd.DataFrame()
        write_csv(DATA / "rev0043_hard_online_racing_situation_summary.csv", [])

    audit = {
        "selected_rows": int(len(selected)),
        "candidate_rows": int(len(candidates)),
        "branch_rows": int(len(branches)),
        "allocation_rows": int(len(allocations)),
        "vote_rows": int(len(votes)),
        "transition_rows": int(len(transitions)),
        "situation_rows": int(len(sit)),
        "branch_truncations": int((branch_df["winner"].astype(str) == "None").sum()) if not branch_df.empty else 0,
        "adaptive_allocation_rows": int((alloc_df["phase"].astype(str) == "adaptive").sum()) if not alloc_df.empty else 0,
        "base_allocation_rows": int((alloc_df["phase"].astype(str) == "base").sum()) if not alloc_df.empty else 0,
        "high_action_selected": int((selected_df["action_count"].astype(int) >= 5).sum()) if not selected_df.empty else 0,
        "mean_action_count": float(selected_df["action_count"].astype(float).mean()) if not selected_df.empty else 0.0,
        "decisive_situations": int(summary.decisive_situations),
        "decisive_per_100_rollouts": float(summary.decisive_per_100_rollouts),
        "mean_label_confidence_proxy": float(summary.mean_label_confidence_proxy),
    }
    out = {
        "revision": REV,
        "codename": "hardonline-racecollector",
        "summary": summary.as_dict(),
        "audit": audit,
        "notes": [
            "This revision makes the hard-frame adaptive collector live: rollouts are spent online, not audited after a full fixed branch matrix is generated.",
            "Frame selection is public-only; hidden true state is only used by the offline branch labeler/referee.",
            "C++ still shadows transitions under Python semantics rather than becoming authoritative.",
            "No gameplay policy is promoted in this revision.",
        ],
    }
    (DATA / "rev0043_hard_online_racing_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
