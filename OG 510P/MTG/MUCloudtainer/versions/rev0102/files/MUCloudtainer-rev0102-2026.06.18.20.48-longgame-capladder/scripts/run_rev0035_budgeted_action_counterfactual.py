from __future__ import annotations

import json
import sys
from pathlib import Path
from random import Random

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.action_counterfactual import build_action_counterfactual_specs, collect_action_counterfactuals
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.ranker_policy import LinearActionRankerModel, save_linear_ranker_model
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import outcome_ranker_probe_bundles, budgeted_counterfactual_action_ranker_bundles

REV = "rev0035"
DATA = ROOT / "data"
MODEL_PATH = DATA / "rev0035_counterfactual_action_ranker_model.json"


def _label_audit(candidate_rows: list[dict[str, object]]) -> dict[str, object]:
    df = pd.DataFrame(candidate_rows)
    if df.empty:
        return {"candidate_rows": 0}
    situations = df.groupby("situation_id")
    margins = situations["situation_best_margin"].first().astype(float)
    conf = situations["label_confidence_proxy"].first().astype(float)
    action_counts = situations["action_count"].first().astype(int)
    branched_counts = situations["branched_action_count"].first().astype(int)
    subset = situations["branched_subset"].first().astype(int)
    chosen_best = situations["behavior_chosen_is_best"].max().astype(int)
    decisive = margins > 1e-9
    reasons = df.get("budget_reason", pd.Series(dtype=str)).astype(str).value_counts().to_dict()
    return {
        "candidate_rows": int(len(df)),
        "situations": int(len(situations)),
        "mean_full_action_count": float(action_counts.mean()) if len(action_counts) else 0.0,
        "max_full_action_count": int(action_counts.max()) if len(action_counts) else 0,
        "mean_branched_action_count": float(branched_counts.mean()) if len(branched_counts) else 0.0,
        "max_branched_action_count": int(branched_counts.max()) if len(branched_counts) else 0,
        "subset_situations": int(subset.sum()),
        "full_menu_situations": int((subset == 0).sum()),
        "decisive_situations": int(decisive.sum()),
        "tie_situations": int((~decisive).sum()),
        "mean_margin": float(margins.mean()) if len(margins) else 0.0,
        "median_margin": float(margins.median()) if len(margins) else 0.0,
        "mean_label_confidence_proxy": float(conf.mean()) if len(conf) else 0.0,
        "confident_situations_ge_0_50": int((conf >= 0.50).sum()),
        "confident_situations_ge_0_75": int((conf >= 0.75).sum()),
        "behavior_chosen_best_rate": float(chosen_best.mean()) if len(chosen_best) else 0.0,
        "budget_reason_counts": {str(k): int(v) for k, v in reasons.items()},
    }


def _train_budgeted_counterfactual_ranker(candidate_rows: list[dict[str, object]]) -> dict[str, object]:
    df = pd.DataFrame(candidate_rows)
    features = list(action_ranker_feature_names())
    if df.empty:
        raise RuntimeError("no budgeted counterfactual candidate rows collected")
    situation_ids = sorted(df["situation_id"].astype(str).unique())
    rng = Random(35035)
    rng.shuffle(situation_ids)
    split = max(1, int(0.72 * len(situation_ids)))
    train_ids = set(situation_ids[:split])
    test_ids = set(situation_ids[split:] or situation_ids[:1])
    train = df[df["situation_id"].isin(train_ids)].copy()
    test = df[df["situation_id"].isin(test_ids)].copy()

    X_train = train[features].astype(float).to_numpy()
    y_train = train["mean_actor_score"].astype(float).to_numpy()
    subset_discount = np.where(train.get("branched_subset", 0).astype(int).to_numpy() == 1, 0.80, 1.00)
    sample_weight = (0.20 + train.get("label_confidence_proxy", 0.0).astype(float).to_numpy()) * subset_discount
    X_test = test[features].astype(float).to_numpy()
    y_test = test["mean_actor_score"].astype(float).to_numpy()

    model = Ridge(alpha=0.9, random_state=35035)
    model.fit(X_train, y_train, sample_weight=sample_weight)
    pred = model.predict(X_test)

    pred_rows = test.copy()
    pred_rows["prediction"] = pred
    top1 = []
    random_baseline = []
    mrrs = []
    top1_decisive = []
    top1_subset = []
    for _sid, g in pred_rows.groupby("situation_id"):
        g = g.sort_values("prediction", ascending=False).reset_index(drop=True)
        best_positions = [i for i, row in g.iterrows() if int(row["is_best_action"]) == 1]
        if not best_positions:
            continue
        hit = 1.0 if int(g.iloc[0]["is_best_action"]) == 1 else 0.0
        top1.append(hit)
        random_baseline.append(float(sum(g["is_best_action"].astype(int))) / max(1, len(g)))
        mrrs.append(1.0 / float(min(best_positions) + 1))
        if float(g.iloc[0].get("situation_best_margin", 0.0)) > 1e-9:
            top1_decisive.append(hit)
        if int(g.iloc[0].get("branched_subset", 0)) == 1:
            top1_subset.append(hit)

    ranker = LinearActionRankerModel(
        model_id="counterfactual_linear_ranker_rev0035",
        feature_names=tuple(features),
        coefficients=tuple(float(x) for x in model.coef_),
        intercept=float(model.intercept_),
        source_revision=REV,
        training_summary={
            "training_rows": int(len(train)),
            "test_rows": int(len(test)),
            "train_situations": int(len(train_ids)),
            "test_situations": int(len(test_ids)),
            "target": "mean_actor_score_from_budgeted_branched_public_rollouts",
            "ridge_alpha": 0.9,
            "sample_weight": "(0.20 + label_confidence_proxy) * subset_discount_0.80",
            "test_rmse": float(mean_squared_error(y_test, pred) ** 0.5) if len(test) else None,
            "test_r2": float(r2_score(y_test, pred)) if len(test) > 1 else None,
            "test_top1_best_action_accuracy": float(np.mean(top1)) if top1 else None,
            "test_top1_decisive_accuracy": float(np.mean(top1_decisive)) if top1_decisive else None,
            "test_top1_subset_accuracy": float(np.mean(top1_subset)) if top1_subset else None,
            "test_random_best_action_baseline": float(np.mean(random_baseline)) if random_baseline else None,
            "test_mrr": float(np.mean(mrrs)) if mrrs else None,
        },
    )
    save_linear_ranker_model(ranker, MODEL_PATH)
    coef_rows = [{"feature": f, "coefficient": float(c), "abs_coefficient": abs(float(c))} for f, c in zip(features, model.coef_)]
    coef_rows.sort(key=lambda r: r["abs_coefficient"], reverse=True)
    write_csv(DATA / "rev0035_counterfactual_action_ranker_coefficients.csv", coef_rows)
    return dict(ranker.training_summary or {})


def _record_replay_samples(eval_specs, count: int = 8):
    agent_cache = {}
    mulligan_cache = {}

    def agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mull(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    sample_indices = [0, 1, 2, 3, max(0, len(eval_specs)//2 - 1), len(eval_specs)//2, len(eval_specs)-2, len(eval_specs)-1]
    replay_traces = []
    replay_results = []
    seen = set()
    for idx in sample_indices[:count + 4]:
        if idx in seen or idx < 0 or idx >= len(eval_specs):
            continue
        seen.add(idx)
        spec = eval_specs[idx]
        trace = record_public_decision_trace(
            spec.deck0,
            spec.deck1,
            agent(spec.agent0),
            agent(spec.agent1),
            seed=int(spec.seed),
            transition_seed=int(spec.seed),
            agent_seed=int(spec.seed) + 1000003,
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            max_decisions=int(spec.max_decisions),
            mulligan_agents=(mull(spec.mulligan0), mull(spec.mulligan1)),
        )
        replay_traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
        if len(replay_traces) >= count:
            break
    return replay_traces, replay_results


def main() -> None:
    DATA.mkdir(exist_ok=True)

    behavior_strategies = outcome_ranker_probe_bundles(DATA / "seed_decks.json")[:6]
    cf_specs = build_action_counterfactual_specs(
        behavior_strategies,
        life_totals=(20, 40),
        base_seed=3500000,
        max_decisions=430,
        limit_games=12,
    )
    candidate_rows, branch_rows, transition_rows, cf_summary = collect_action_counterfactuals(
        cf_specs,
        revision=REV,
        max_situations=26,
        max_actions_per_frame=3,
        sample_high_action_frames=True,
        branch_action_budget=6,
        budget_rng_seed=35035,
        branch_rollouts_per_action=2,
        branch_max_decisions=320,
    )
    label_audit = _label_audit(candidate_rows)
    train_summary = _train_budgeted_counterfactual_ranker(candidate_rows)

    strategies = budgeted_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")[:6]
    eval_specs = strategy_pair_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=3535000,
        max_decisions=440,
    )
    prepared = prepare_cpp_shadow_rollout(eval_specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    game_rows = list(prepared.game_rows)
    aggregate = aggregate_payoff_rows(game_rows)
    standings = strategy_standings(game_rows)
    stat_standings = statistical_standings(game_rows, min_games_for_claim=24)
    pairwise = pairwise_stat_rows(game_rows, min_games_for_claim=4)

    replay_traces, replay_results = _record_replay_samples(eval_specs, count=8)
    promotion = audit_promotion_rows(
        game_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=120, min_replay_traces=6, max_truncation_rate=0.25),
    )
    stat_gate = audit_statistical_gate(game_rows, stat_standings, pairwise, min_raw_rows=120, max_truncation_rate=0.25)

    write_csv(DATA / "rev0035_action_counterfactual_candidates.csv", candidate_rows)
    write_csv(DATA / "rev0035_action_counterfactual_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0035_action_counterfactual_cpp_transitions.csv", transition_rows)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_games.csv", game_rows)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_aggregate.csv", aggregate)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_standings.csv", standings)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_pairwise.csv", pairwise)
    write_csv(DATA / "rev0035_budgeted_counterfactual_ranker_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])
    write_trace_jsonl(replay_traces, DATA / "rev0035_budgeted_counterfactual_ranker_replay_traces.jsonl")
    (DATA / "rev0035_budgeted_counterfactual_ranker_replay_results.json").write_text(json.dumps(replay_results, indent=2), encoding="utf-8")

    payload = {
        "revision": REV,
        "codename": "budgetedactioncf-searchgate",
        "counterfactual_collection": cf_summary.as_dict(),
        "label_audit": label_audit,
        "training_summary": train_summary,
        "payoff_games": len(game_rows),
        "aggregate_rows": len(aggregate),
        "promotion_gate": promotion.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": sum(1 for r in replay_results if r.get("passed")),
        "truncations": sum(1 for r in game_rows if int(r.get("is_truncation", 0)) == 1),
        "artifacts": {
            "candidates": "data/rev0035_action_counterfactual_candidates.csv",
            "branch_games": "data/rev0035_action_counterfactual_branch_games.csv",
            "model": "data/rev0035_counterfactual_action_ranker_model.json",
            "payoff_games": "data/rev0035_budgeted_counterfactual_ranker_games.csv",
            "cpp_transitions": "data/rev0035_budgeted_counterfactual_ranker_cpp_transitions.csv",
        },
    }
    (DATA / "rev0035_budgeted_action_counterfactual_summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
