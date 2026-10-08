from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_margin_screen import MarginScreenModel, load_historical_margin_rows, save_margin_screen_model, train_margin_screen_model
from src.muc5.action_yield_screen import (
    collect_yield_vs_hard_margin_queue_comparison,
    load_historical_yield_rows,
    save_yield_screen_model,
    train_yield_screen_model,
)
from src.muc5.payoff import write_csv
from src.muc5.strategy_sets import (
    adaptive_counterfactual_action_ranker_bundles,
    budgeted_counterfactual_action_ranker_bundles,
    disagreement_counterfactual_action_ranker_bundles,
    outcome_ranker_probe_bundles,
)

REV = "rev0046"
CODENAME = "yieldscreen-queuegate"
DATA = ROOT / "data"


def _history_paths() -> list[Path]:
    return [
        DATA / "rev0033_action_counterfactual_candidates.csv",
        DATA / "rev0034_action_counterfactual_candidates.csv",
        DATA / "rev0035_action_counterfactual_candidates.csv",
        DATA / "rev0036_adaptive_action_counterfactual_candidates.csv",
        DATA / "rev0038_disagreement_action_counterfactual_candidates.csv",
        DATA / "rev0043_hard_online_racing_candidates.csv",
        DATA / "rev0044_margin_online_racing_candidates.csv",
        DATA / "rev0045_margin_match_candidates.csv",
    ]


def _load_or_train_margin_model() -> MarginScreenModel:
    model_path = DATA / "rev0044_margin_screen_model.json"
    if model_path.exists():
        return MarginScreenModel.from_dict(json.loads(model_path.read_text()))
    rows = load_historical_margin_rows(_history_paths())
    model, _ = train_margin_screen_model(
        rows,
        revision="rev0044_rebuilt_for_rev0046",
        source_files=[p.name for p in _history_paths() if p.exists()],
        seed=44044,
        holdout_fraction=0.30,
        l2=0.20,
    )
    save_margin_screen_model(model, model_path)
    return model


def main() -> None:
    DATA.mkdir(exist_ok=True)
    history_paths = _history_paths()
    hist_rows = load_historical_yield_rows(history_paths)
    yield_model, yield_holdout = train_yield_screen_model(
        hist_rows,
        revision=REV,
        source_files=[p.name for p in history_paths if p.exists()],
        seed=46046,
        holdout_fraction=0.30,
        l2=0.35,
    )
    save_yield_screen_model(yield_model, DATA / "rev0046_yield_screen_model.json")
    pd.DataFrame(hist_rows).to_csv(DATA / "rev0046_yield_screen_training_rows.csv", index=False)
    pd.DataFrame(yield_holdout).to_csv(DATA / "rev0046_yield_screen_holdout_eval.csv", index=False)
    margin_model = _load_or_train_margin_model()

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
    behavior_strategies = tuple(base[:4]) + tuple(dis[:3]) + tuple(bud[:2]) + tuple(ada[:3])
    specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=4604600,
        max_decisions=420,
        limit_games=26,
    )

    (
        pool_rows,
        hard_rank_rows,
        margin_rank_rows,
        yield_rank_rows,
        selected_rows,
        method_rows,
        candidate_rows,
        branch_rows,
        allocation_rows,
        vote_rows,
        cpp_rows,
        summary,
    ) = collect_yield_vs_hard_margin_queue_comparison(
        specs,
        yield_model=yield_model,
        margin_model=margin_model,
        revision=REV,
        min_unique_screen_votes=1,
        max_behavior_frames=220,
        candidate_pool_situations=36,
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
        budget_rng_seed=46046,
    )

    write_csv(DATA / "rev0046_yield_match_pool.csv", pool_rows)
    write_csv(DATA / "rev0046_yield_match_hard_rank.csv", hard_rank_rows)
    write_csv(DATA / "rev0046_yield_match_margin_rank.csv", margin_rank_rows)
    write_csv(DATA / "rev0046_yield_match_yield_rank.csv", yield_rank_rows)
    write_csv(DATA / "rev0046_yield_match_selected.csv", selected_rows)
    write_csv(DATA / "rev0046_yield_match_methods.csv", method_rows)
    write_csv(DATA / "rev0046_yield_match_candidates.csv", candidate_rows)
    write_csv(DATA / "rev0046_yield_match_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0046_yield_match_allocations.csv", allocation_rows)
    write_csv(DATA / "rev0046_yield_match_votes.csv", vote_rows)
    write_csv(DATA / "rev0046_yield_match_cpp_transitions.csv", cpp_rows)

    methods_df = pd.DataFrame(method_rows)
    if not methods_df.empty:
        method_summary = methods_df.groupby("method").agg(
            selected_situations=("source_candidate_id", "count"),
            branched_situations=("branched", "sum"),
            decisive_situations=("decisive", "sum"),
            branch_rollouts=("branch_rollouts", "sum"),
            mean_margin=("situation_best_margin", "mean"),
            mean_confidence=("label_confidence_proxy", "mean"),
            mean_action_count=("action_count", "mean"),
            selected_by_all_three=("selected_by_all_three", "sum"),
        ).reset_index()
        method_summary["decisive_per_100_rollouts"] = 100.0 * method_summary["decisive_situations"] / method_summary["branch_rollouts"].clip(lower=1)
        method_summary.to_csv(DATA / "rev0046_yield_match_method_summary.csv", index=False)
    else:
        write_csv(DATA / "rev0046_yield_match_method_summary.csv", [])

    if candidate_rows:
        df = pd.DataFrame(candidate_rows)
        sit = df.groupby("situation_id").agg(
            source_candidate_id=("source_candidate_id", "first"),
            action_count=("action_count", "first"),
            branched_action_count=("branched_action_count", "first"),
            situation_best_margin=("situation_best_margin", "first"),
            label_confidence_proxy=("label_confidence_proxy", "first"),
            total_adaptive_extra=("total_adaptive_extra_rollouts", "first"),
            stopped_early=("adaptive_stopped_early", "first"),
            behavior_chosen_is_best=("behavior_chosen_is_best", "max"),
        ).reset_index()
        sit.to_csv(DATA / "rev0046_yield_match_situation_summary.csv", index=False)
    else:
        write_csv(DATA / "rev0046_yield_match_situation_summary.csv", [])

    out = {
        "revision": REV,
        "codename": CODENAME,
        "yield_model": yield_model.as_dict(),
        "margin_model_revision": margin_model.revision,
        "summary": summary.as_dict(),
        "short_read": {
            "yield_model_holdout_top_quartile_yield_per_100": yield_model.metrics.get("top_quartile_yield_per_100"),
            "yield_model_holdout_baseline_yield_per_100": yield_model.metrics.get("baseline_yield_per_100"),
            "hard_decisive_per_100_rollouts": summary.hard_stats.get("decisive_per_100_rollouts"),
            "margin_decisive_per_100_rollouts": summary.margin_stats.get("decisive_per_100_rollouts"),
            "yield_decisive_per_100_rollouts": summary.yield_stats.get("decisive_per_100_rollouts"),
            "yield_minus_hard_decisive_per_100": summary.yield_minus_hard_decisive_per_100,
            "yield_minus_margin_decisive_per_100": summary.yield_minus_margin_decisive_per_100,
            "overlap_all_three": summary.overlap_all_three,
        },
        "notes": [
            "rev0046 trains a label-yield screen on historical audited counterfactual rows.",
            "The target is decisive labels per rollout, not raw branch margin.",
            "Hard, margin, and yield queues are compared on the same public pool and the same union-branched outcomes.",
            "No gameplay policy is promoted; this is a queueing/label-quality revision under C++ transition shadow checks.",
        ],
    }
    (DATA / "rev0046_yield_match_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
