from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.outcome_training import collect_outcome_weighted_action_rows
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.ranker_policy import LinearActionRankerModel, save_linear_ranker_model
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import outcome_ranker_probe_bundles

REV = "rev0025"
DATA = ROOT / "data"


def game_specs():
    """Public training games for outcome-weighted behavior cloning.

    This panel intentionally contains multiple policy families. Outcome weighting
    should bias the learner toward actions from successful trajectories, not just
    toward the most common behavior-policy personality.
    """

    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 24, 4, 4, 8, 0),
        DeckVector(40, 18, 6, 10, 4, 2),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 36, 8, 8, 8, 0),
        DeckVector(60, 40, 0, 0, 20, 0),
    ]
    agents = [
        make_public_agent("heuristic"),
        make_public_agent("counter_happy"),
        make_public_agent("threat_rush"),
        make_public_agent("patient"),
        make_public_agent("code_jace_lock_rev0013"),
        make_public_agent("code_overlord_clock_rev0013"),
        make_public_agent("code_force_conservative_rev0013"),
        make_public_agent("mlp_ranker_blend_threat_rev0023"),
    ]
    mulligans = [
        (POLICY_KEEP_ALWAYS, POLICY_KEEP_ALWAYS),
        (POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS),
        (POLICY_LAND_BAND_BUSINESS, POLICY_LAND_BAND),
        ("mulligan_ranker_rev0024", POLICY_LAND_BAND_BUSINESS),
        (POLICY_LAND_BAND, "mulligan_ranker_rev0024"),
    ]
    specs = []
    for i in range(112):
        specs.append((
            decks[i % len(decks)],
            decks[(i * 5 + 2) % len(decks)],
            agents[i % len(agents)],
            agents[(i * 7 + 3) % len(agents)],
            i % 2,
            20 if i % 4 else 40,
            mulligans[i % len(mulligans)],
        ))
    return specs


def choice_metrics(df: pd.DataFrame, score_col: str) -> dict[str, float | int]:
    correct = 0
    total = 0
    reciprocal = 0.0
    random_terms = []
    for _, g in df.groupby("decision_id", sort=False):
        total += 1
        random_terms.append(1.0 / float(g["action_count"].iloc[0]))
        ordered = g.sort_values(score_col, ascending=False).reset_index(drop=True)
        chosen_positions = ordered.index[ordered["chosen"].astype(int) == 1].tolist()
        if chosen_positions:
            pos = int(chosen_positions[0])
            correct += 1 if pos == 0 else 0
            reciprocal += 1.0 / float(pos + 1)
    return {
        "decisions": int(total),
        "top1_accuracy": float(correct / total) if total else 0.0,
        "mean_reciprocal_rank": float(reciprocal / total) if total else 0.0,
        "random_slot_baseline_accuracy": float(sum(random_terms) / len(random_terms)) if random_terms else 0.0,
    }


def train_outcome_ranker(df: pd.DataFrame, feature_cols: list[str]) -> tuple[LinearActionRankerModel, dict[str, object], pd.DataFrame]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss, roc_auc_score

    usable = df[df["outcome_weight"].astype(float) > 0.0].copy()
    train_mask = (usable["game_index"].astype(int) % 5) != 0
    train = usable[train_mask].copy()
    test = usable[~train_mask].copy()
    X_train = train[feature_cols].astype(float).to_numpy()
    y_train = train["chosen"].astype(int).to_numpy()
    w_train = train["outcome_weight"].astype(float).to_numpy()
    X_test = test[feature_cols].astype(float).to_numpy()
    y_test = test["chosen"].astype(int).to_numpy()
    clf = LogisticRegression(
        max_iter=260,
        C=0.75,
        solver="liblinear",
        random_state=25025,
    )
    clf.fit(X_train, y_train, sample_weight=w_train)
    test_probs = clf.predict_proba(X_test)[:, 1]
    eval_df = test.assign(pred_prob=test_probs)
    choice = choice_metrics(eval_df, "pred_prob")
    metrics: dict[str, object] = {
        "label_source": "terminal_outcome_weighted_behavior_cloning",
        "weighting_rule": "win=1.0 loss=0.15 truncation=0.0",
        "raw_rows": int(len(df)),
        "usable_weighted_rows": int(len(usable)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "raw_decisions": int(df["decision_id"].nunique()),
        "usable_decisions": int(usable["decision_id"].nunique()),
        "train_decisions": int(train["decision_id"].nunique()),
        "test_decisions": int(test["decision_id"].nunique()),
        "feature_count": int(len(feature_cols)),
        "total_train_weight": float(w_train.sum()),
        "test_top1_accuracy": choice["top1_accuracy"],
        "test_mean_reciprocal_rank": choice["mean_reciprocal_rank"],
        "random_slot_baseline_accuracy": choice["random_slot_baseline_accuracy"],
        "test_log_loss_unweighted": float(log_loss(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "test_roc_auc_unweighted": float(roc_auc_score(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
    }
    model = LinearActionRankerModel(
        model_id="outcome_linear_ranker_rev0025_logreg_weighted",
        feature_names=tuple(feature_cols),
        coefficients=tuple(float(x) for x in clf.coef_.ravel()),
        intercept=float(clf.intercept_.ravel()[0]),
        source_revision=REV,
        training_summary=metrics,
    )
    importance = pd.DataFrame({
        "feature": feature_cols,
        "abs_coefficient": [float(abs(x)) for x in clf.coef_.ravel()],
        "coefficient": [float(x) for x in clf.coef_.ravel()],
    }).sort_values("abs_coefficient", ascending=False)
    return model, metrics, importance


def lint_outcome_agent() -> dict[str, object]:
    from random import Random
    from src.muc5.decision import build_decision_frame
    from src.muc5.engine import start_game

    deck = DeckVector(40, 22, 8, 6, 3, 1)
    state = start_game(deck, deck, seed=2502501, starting_life=20, record_log=False)
    frame = build_decision_frame(state)
    agent = make_public_agent("outcome_linear_ranker_rev0025")
    idx = agent.choose_action_index(frame, Random(25))
    return {"ok": 0 <= idx < frame.action_count, "action_count": frame.action_count, "chosen_index": int(idx), "chosen_action": frame.legal_actions[idx].compact()}


def trace_specs(strategies):
    return [
        (0, 3, 20, 0),
        (1, 4, 20, 1),
        (2, 5, 40, 0),
        (3, 6, 40, 1),
        (0, 7, 20, 1),
        (1, 6, 40, 0),
        (2, 4, 20, 0),
        (7, 0, 40, 1),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    feature_cols = list(action_ranker_feature_names())
    rows, collection = collect_outcome_weighted_action_rows(game_specs(), seed_base=2502500, max_decisions=520)
    df = pd.DataFrame(rows)
    df.to_csv(DATA / f"{REV}_outcome_ranker_training_dataset.csv", index=False)
    model, metrics, importance = train_outcome_ranker(df, feature_cols)
    save_linear_ranker_model(model, DATA / f"{REV}_outcome_ranker_model.json")
    importance.head(100).to_csv(DATA / f"{REV}_outcome_ranker_feature_importance.csv", index=False)
    lint = lint_outcome_agent()
    if not lint["ok"]:
        raise SystemExit(f"outcome ranker lint failed: {lint}")

    strategies = outcome_ranker_probe_bundles(DATA / "seed_decks.json")
    payoff_rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2503000, max_decisions=600)
    write_csv(DATA / f"{REV}_outcome_ranker_games.csv", payoff_rows)
    aggregate = aggregate_payoff_rows(payoff_rows)
    write_csv(DATA / f"{REV}_outcome_ranker_aggregate.csv", aggregate)
    standings = strategy_standings(payoff_rows)
    write_csv(DATA / f"{REV}_outcome_ranker_standings.csv", standings)
    pairwise = pairwise_stat_rows(payoff_rows, min_games_for_claim=4)
    stat_stand = statistical_standings(payoff_rows, min_games_for_claim=24)
    write_csv(DATA / f"{REV}_outcome_ranker_pairwise.csv", pairwise)
    write_csv(DATA / f"{REV}_outcome_ranker_stat_standings.csv", stat_stand)
    stat_gate = audit_statistical_gate(payoff_rows, stat_stand, pairwise, min_raw_rows=len(payoff_rows), max_truncation_rate=0.12)

    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(trace_specs(strategies)):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=2504000 + t,
            transition_seed=2505000 + t,
            agent_seed=2506000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=600,
            mulligan_agents=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_outcome_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_outcome_ranker_replay_traces.jsonl")
    (DATA / f"{REV}_outcome_ranker_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / f"{REV}_outcome_ranker_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / f"{REV}_outcome_ranker_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        payoff_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(payoff_rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    outcome_ids = [s.strategy_id for s in strategies if s.agent_name.startswith("outcome_")]
    summary = {
        "revision": REV,
        "collection": collection.as_dict(),
        "feature_count": len(feature_cols),
        "training_metrics": metrics,
        "ranker_lint": lint,
        "strategy_count": len(strategies),
        "outcome_strategy_ids": outcome_ids,
        "games": len(payoff_rows),
        "aggregate_rows": len(aggregate),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "top_standings": standings[:8],
        "top_stat_standings": stat_stand[:8],
        "important_features_top10": importance.head(10).to_dict(orient="records"),
    }
    (DATA / f"{REV}_outcome_ranker_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
