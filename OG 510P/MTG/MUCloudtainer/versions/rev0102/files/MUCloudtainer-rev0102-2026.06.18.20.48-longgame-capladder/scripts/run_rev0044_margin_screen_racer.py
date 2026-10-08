from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_margin_screen import (
    collect_margin_screened_online_racing,
    evaluate_margin_screen_model,
    load_historical_margin_rows,
    save_margin_screen_model,
    train_margin_screen_model,
)
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import (
    adaptive_counterfactual_action_ranker_bundles,
    budgeted_counterfactual_action_ranker_bundles,
    disagreement_counterfactual_action_ranker_bundles,
    outcome_ranker_probe_bundles,
)

REV = "rev0044"
DATA = ROOT / "data"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    history_paths = [
        DATA / "rev0034_action_counterfactual_candidates.csv",
        DATA / "rev0035_action_counterfactual_candidates.csv",
        DATA / "rev0036_adaptive_action_counterfactual_candidates.csv",
        DATA / "rev0038_disagreement_action_counterfactual_candidates.csv",
        DATA / "rev0043_hard_online_racing_candidates.csv",
    ]
    history_rows = load_historical_margin_rows(history_paths)
    model, holdout_eval = train_margin_screen_model(
        history_rows,
        revision=REV,
        source_files=[p.name for p in history_paths if p.exists()],
        seed=44044,
        holdout_fraction=0.30,
        l2=0.20,
    )
    save_margin_screen_model(model, DATA / "rev0044_margin_screen_model.json")
    write_csv(DATA / "rev0044_margin_screen_holdout_eval.csv", holdout_eval)

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
        base_seed=4404400,
        max_decisions=420,
        limit_games=22,
    )
    margin_rows, selected, candidates, branches, allocations, votes, transitions, summary = collect_margin_screened_online_racing(
        specs,
        model=model,
        revision=REV,
        min_unique_screen_votes=1,
        max_behavior_frames=220,
        candidate_pool_situations=30,
        selected_situations=10,
        high_action_threshold=5,
        max_actions_per_frame=3,
        branch_action_budget=5,
        base_rollouts_per_action=1,
        max_extra_rollouts_per_situation=4,
        adaptive_stop_margin=0.40,
        adaptive_target_confidence=0.55,
        branch_max_decisions=420,
        ranker_revision="rev0034",
        max_per_behavior_game=2,
    )

    write_csv(DATA / "rev0044_margin_screen_pool.csv", margin_rows)
    write_csv(DATA / "rev0044_margin_online_racing_selected.csv", selected)
    write_csv(DATA / "rev0044_margin_online_racing_candidates.csv", candidates)
    write_csv(DATA / "rev0044_margin_online_racing_branch_games.csv", branches)
    write_csv(DATA / "rev0044_margin_online_racing_allocations.csv", allocations)
    write_csv(DATA / "rev0044_margin_online_racing_votes.csv", votes)
    write_csv(DATA / "rev0044_margin_online_racing_cpp_transitions.csv", transitions)

    cand_df = pd.DataFrame(candidates)
    branch_df = pd.DataFrame(branches)
    selected_df = pd.DataFrame(selected)
    alloc_df = pd.DataFrame(allocations)
    pool_df = pd.DataFrame(margin_rows)
    if not cand_df.empty:
        sit = cand_df.groupby("situation_id").agg(
            action_count=("action_count", "first"),
            branched_action_count=("branched_action_count", "first"),
            situation_best_margin=("situation_best_margin", "first"),
            label_confidence_proxy=("label_confidence_proxy", "first"),
            total_adaptive_extra=("total_adaptive_extra_rollouts", "first"),
            stopped_early=("adaptive_stopped_early", "first"),
            behavior_chosen_is_best=("behavior_chosen_is_best", "max"),
            margin_predicted_margin=("margin_predicted_margin", "first"),
            margin_screen_score=("margin_screen_score", "first"),
        ).reset_index()
        sit.to_csv(DATA / "rev0044_margin_online_racing_situation_summary.csv", index=False)
    else:
        sit = pd.DataFrame()
        write_csv(DATA / "rev0044_margin_online_racing_situation_summary.csv", [])

    audit = {
        "history_situation_rows": int(len(history_rows)),
        "model_train_rows": int(model.train_rows),
        "model_holdout_rows": int(model.holdout_rows),
        "holdout_rmse": float(model.metrics.get("rmse", 0.0)),
        "holdout_top_quartile_decisive_rate": float(model.metrics.get("top_quartile_decisive_rate", 0.0)),
        "holdout_baseline_decisive_rate": float(model.metrics.get("baseline_decisive_rate", 0.0)),
        "pool_rows": int(len(margin_rows)),
        "selected_rows": int(len(selected)),
        "candidate_rows": int(len(candidates)),
        "branch_rows": int(len(branches)),
        "allocation_rows": int(len(allocations)),
        "vote_rows": int(len(votes)),
        "transition_rows": int(len(transitions)),
        "situation_rows": int(len(sit)),
        "branch_truncations": int((branch_df["winner"].astype(str) == "None").sum()) if not branch_df.empty else 0,
        "adaptive_allocation_rows": int((alloc_df["phase"].astype(str) == "adaptive").sum()) if not alloc_df.empty else 0,
        "high_action_selected": int((selected_df["action_count"].astype(int) >= 5).sum()) if not selected_df.empty else 0,
        "mean_action_count": float(selected_df["action_count"].astype(float).mean()) if not selected_df.empty else 0.0,
        "mean_predicted_margin_selected": float(selected_df["margin_predicted_margin"].astype(float).mean()) if "margin_predicted_margin" in selected_df else 0.0,
        "mean_pool_predicted_margin": float(pool_df["predicted_margin"].astype(float).mean()) if not pool_df.empty else 0.0,
        "decisive_situations": int(summary.decisive_situations),
        "decisive_per_100_rollouts": float(summary.decisive_per_100_rollouts),
        "mean_label_confidence_proxy": float(summary.mean_label_confidence_proxy),
    }
    out = {
        "revision": REV,
        "codename": "marginscreen-labelseeker",
        "model": model.as_dict(),
        "summary": summary.as_dict(),
        "audit": audit,
        "notes": [
            "Margin-screen model is a public-feature queueing aid, not a gameplay policy.",
            "The model is trained only from historical audited branch labels and then used to rerank a public hard-frame candidate pool.",
            "Hidden true state is used only by the offline branch labeler/referee after public frame selection.",
            "C++ remains a shadow checker under Python semantics; rev0044 adds no new authoritative C++ kernel.",
        ],
    }
    (DATA / "rev0044_margin_screen_racing_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
