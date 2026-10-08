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

from src.muc5.action_counterfactual import build_action_counterfactual_specs
from src.muc5.action_disagreement import collect_disagreement_screened_counterfactuals
from src.muc5.cpp_rollout import finalize_cpp_shadow_rollout, prepare_cpp_shadow_rollout, strategy_pair_specs
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.mulligan_ranker import make_mulligan_agent
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.ranker_policy import LinearActionRankerModel, save_linear_ranker_model
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import outcome_ranker_probe_bundles, disagreement_counterfactual_action_ranker_bundles

REV = "rev0038"
DATA = ROOT / "data"
MODEL_PATH = DATA / "rev0038_counterfactual_action_ranker_model.json"


def _label_audit(candidate_rows: list[dict[str, object]], screen_rows: list[dict[str, object]]) -> dict[str, object]:
    df = pd.DataFrame(candidate_rows)
    if df.empty:
        return {"candidate_rows": 0, "screen_rows": len(screen_rows)}
    situations = df.groupby("situation_id")
    margins = situations["situation_best_margin"].first().astype(float)
    conf = situations["label_confidence_proxy"].first().astype(float)
    action_counts = situations["action_count"].first().astype(int)
    branched_counts = situations["branched_action_count"].first().astype(int)
    subset = situations["branched_subset"].first().astype(int)
    unique_votes = situations["screen_unique_votes"].first().astype(int)
    entropy = situations["screen_vote_entropy_proxy"].first().astype(float)
    chosen_best = situations["behavior_chosen_is_best"].max().astype(int)
    voted_best = situations.apply(lambda g: int(((g["screen_voted_action"].astype(int) == 1) & (g["is_best_action"].astype(int) == 1)).any()))
    decisive = margins > 1e-9
    reasons = df.get("budget_reason", pd.Series(dtype=str)).astype(str).value_counts().to_dict()
    screen_df = pd.DataFrame(screen_rows)
    screener_counts = screen_df["screener"].value_counts().to_dict() if not screen_df.empty else {}
    return {
        "candidate_rows": int(len(df)),
        "screen_rows": int(len(screen_rows)),
        "situations": int(len(situations)),
        "decisive_situations": int(decisive.sum()),
        "tie_situations": int((~decisive).sum()),
        "mean_margin": float(margins.mean()) if len(margins) else 0.0,
        "median_margin": float(margins.median()) if len(margins) else 0.0,
        "mean_label_confidence_proxy": float(conf.mean()) if len(conf) else 0.0,
        "confident_situations_ge_0_50": int((conf >= 0.50).sum()),
        "confident_situations_ge_0_75": int((conf >= 0.75).sum()),
        "behavior_chosen_best_rate": float(chosen_best.mean()) if len(chosen_best) else 0.0,
        "screen_voted_best_rate": float(voted_best.mean()) if len(voted_best) else 0.0,
        "mean_full_action_count": float(action_counts.mean()) if len(action_counts) else 0.0,
        "max_full_action_count": int(action_counts.max()) if len(action_counts) else 0,
        "mean_branched_action_count": float(branched_counts.mean()) if len(branched_counts) else 0.0,
        "max_branched_action_count": int(branched_counts.max()) if len(branched_counts) else 0,
        "subset_situations": int(subset.sum()),
        "full_menu_situations": int((subset == 0).sum()),
        "mean_unique_screen_votes": float(unique_votes.mean()) if len(unique_votes) else 0.0,
        "mean_vote_entropy_proxy": float(entropy.mean()) if len(entropy) else 0.0,
        "budget_reason_counts": {str(k): int(v) for k, v in reasons.items()},
        "screener_vote_counts": {str(k): int(v) for k, v in screener_counts.items()},
    }


def _train_disagreement_ranker(candidate_rows: list[dict[str, object]]) -> dict[str, object]:
    df = pd.DataFrame(candidate_rows)
    if df.empty:
        raise RuntimeError("no disagreement-screened candidate rows collected")
    features = list(action_ranker_feature_names())
    situation_ids = sorted(df["situation_id"].astype(str).unique())
    rng = Random(38038)
    rng.shuffle(situation_ids)
    split = max(1, int(0.70 * len(situation_ids)))
    train_ids = set(situation_ids[:split])
    test_ids = set(situation_ids[split:] or situation_ids[:1])
    train = df[df["situation_id"].isin(train_ids)].copy()
    test = df[df["situation_id"].isin(test_ids)].copy()
    X_train = train[features].astype(float).to_numpy()
    y_train = train["mean_actor_score"].astype(float).to_numpy()
    X_test = test[features].astype(float).to_numpy()
    y_test = test["mean_actor_score"].astype(float).to_numpy()

    subset_discount = np.where(train.get("branched_subset", 0).astype(int).to_numpy() == 1, 0.82, 1.00)
    vote_bonus = 1.0 + 0.10 * np.maximum(0.0, train.get("screen_unique_votes", 1).astype(float).to_numpy() - 1.0)
    conf = train.get("label_confidence_proxy", 0.0).astype(float).to_numpy()
    sample_weight = (0.20 + conf) * subset_discount * vote_bonus

    model = Ridge(alpha=0.75, random_state=38038)
    model.fit(X_train, y_train, sample_weight=sample_weight)
    pred = model.predict(X_test)
    pred_rows = test.copy()
    pred_rows["prediction"] = pred
    top1 = []
    decisive_top1 = []
    confident_top1 = []
    random_baseline = []
    mrrs = []
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
            decisive_top1.append(hit)
        if float(g.iloc[0].get("label_confidence_proxy", 0.0)) >= 0.50:
            confident_top1.append(hit)

    ranker = LinearActionRankerModel(
        model_id="counterfactual_linear_ranker_rev0038",
        feature_names=tuple(features),
        coefficients=tuple(float(x) for x in model.coef_),
        intercept=float(model.intercept_),
        source_revision=REV,
        training_summary={
            "training_rows": int(len(train)),
            "test_rows": int(len(test)),
            "train_situations": int(len(train_ids)),
            "test_situations": int(len(test_ids)),
            "target": "mean_actor_score_from_disagreement_screened_public_action_counterfactual_rollouts",
            "ridge_alpha": 0.75,
            "sample_weight": "(0.20 + label_confidence_proxy) * subset_discount_0.82 * (1 + 0.10 * extra_screen_votes)",
            "test_rmse": float(mean_squared_error(y_test, pred) ** 0.5) if len(test) else None,
            "test_r2": float(r2_score(y_test, pred)) if len(test) > 1 else None,
            "test_top1_best_action_accuracy": float(np.mean(top1)) if top1 else None,
            "test_top1_decisive_accuracy": float(np.mean(decisive_top1)) if decisive_top1 else None,
            "test_top1_confident_accuracy": float(np.mean(confident_top1)) if confident_top1 else None,
            "test_random_best_action_baseline": float(np.mean(random_baseline)) if random_baseline else None,
            "test_mrr": float(np.mean(mrrs)) if mrrs else None,
        },
    )
    save_linear_ranker_model(ranker, MODEL_PATH)
    coef_rows = [{"feature": f, "coefficient": float(c), "abs_coefficient": abs(float(c))} for f, c in zip(features, model.coef_)]
    coef_rows.sort(key=lambda r: r["abs_coefficient"], reverse=True)
    write_csv(DATA / "rev0038_counterfactual_action_ranker_coefficients.csv", coef_rows)
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

    if not eval_specs:
        return [], []
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
        base_seed=3800000,
        max_decisions=430,
        limit_games=12,
    )
    candidate_rows, branch_rows, screen_rows, transition_rows, cf_summary = collect_disagreement_screened_counterfactuals(
        cf_specs,
        revision=REV,
        max_situations=14,
        max_actions_per_frame=4,
        sample_high_action_frames=True,
        branch_action_budget=6,
        branch_rollouts_per_action=2,
        branch_max_decisions=320,
        min_unique_screen_votes=2,
        budget_rng_seed=38038,
    )
    label_audit = _label_audit(candidate_rows, screen_rows)
    train_summary = _train_disagreement_ranker(candidate_rows)

    strategies = disagreement_counterfactual_action_ranker_bundles(DATA / "seed_decks.json")[:6]
    eval_specs = strategy_pair_specs(
        strategies,
        simulator_revision=REV,
        life_totals=(20, 40),
        reps=1,
        base_seed=3838000,
        max_decisions=820,
    )
    prepared = prepare_cpp_shadow_rollout(eval_specs, revision=REV)
    cpp_summary, cpp_transition_rows = finalize_cpp_shadow_rollout(prepared)
    games = [dict(row) for row in prepared.game_rows]
    for row in games:
        row.setdefault("simulator_revision", REV)
        row.setdefault("interface", "public_decision_frame")
        row.setdefault("reward_convention", "draw_half_reporting_terminal_only_training")
    aggregate = aggregate_payoff_rows(games)
    standings = strategy_standings(games)
    stat_standings = statistical_standings(games)
    pairwise = pairwise_stat_rows(games, min_games_for_claim=4)

    replay_traces, replay_results = _record_replay_samples(eval_specs, count=8)
    write_trace_jsonl(replay_traces, DATA / "rev0038_disagreement_counterfactual_ranker_replay_traces.jsonl")
    (DATA / "rev0038_disagreement_counterfactual_ranker_replay_results.json").write_text(json.dumps(replay_results, indent=2))
    replay_passed = sum(1 for r in replay_results if r.get("passed"))
    promo = audit_promotion_rows(
        games,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=60, min_replay_traces=6, max_truncation_rate=0.30),
    )
    stat_gate = audit_statistical_gate(games, stat_standings, pairwise, min_raw_rows=60, max_truncation_rate=0.30)

    write_csv(DATA / "rev0038_disagreement_action_counterfactual_candidates.csv", candidate_rows)
    write_csv(DATA / "rev0038_disagreement_action_counterfactual_branch_games.csv", branch_rows)
    write_csv(DATA / "rev0038_disagreement_action_counterfactual_screen_votes.csv", screen_rows)
    write_csv(DATA / "rev0038_disagreement_action_counterfactual_cpp_transitions.csv", transition_rows)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_games.csv", games)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_aggregate.csv", aggregate)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_standings.csv", standings)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_stat_standings.csv", stat_standings)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_pairwise.csv", pairwise)
    write_csv(DATA / "rev0038_disagreement_counterfactual_ranker_cpp_transitions.csv", [r.as_dict() for r in cpp_transition_rows])

    summary = {
        "revision": REV,
        "codename": "disagreescreen-labelquality",
        "counterfactual_summary": cf_summary.as_dict(),
        "label_audit": label_audit,
        "training_summary": train_summary,
        "payoff_games": len(games),
        "aggregate_rows": len(aggregate),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_samples": len(replay_results),
        "replay_passed": int(replay_passed),
        "cpp_shadow_summary": cpp_summary.as_dict(),
        "truncations": int(sum(1 for r in games if r.get("is_truncation"))),
        "priority_after_rev0038": [
            "compare disagreement-screened labels against unscreened/adaptive labels on matched situations",
            "increase decisive branch labels by spending rollouts where public policies genuinely disagree",
            "use C++ segment gates for branch-heavy data collection once no-choice segments become a bottleneck",
            "run larger MAP-Elites/meta-rank panels only on nontruncated promoted tables",
            "develop search targets for unchosen gameplay actions after label confidence improves",
        ],
        "notes": [
            "Disagreement screening is a label-budget heuristic, not a strategic claim.",
            "Screening votes come from public-safe policies receiving only DecisionFrames.",
            "Offline branch labels use hidden true state only inside the referee labeler; agents do not see it.",
        ],
    }
    (DATA / "rev0038_disagreement_screened_counterfactual_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
