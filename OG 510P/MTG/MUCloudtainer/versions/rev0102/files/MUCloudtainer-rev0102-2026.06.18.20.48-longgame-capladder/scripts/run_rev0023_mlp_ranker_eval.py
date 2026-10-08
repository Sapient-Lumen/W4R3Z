from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.deckspace import DeckVector
from src.muc5.imitation import action_ranker_feature_names, collect_action_imitation_rows
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.ranker_policy import MLPActionRankerAgent, MLPActionRankerModel, save_mlp_ranker_model
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import mlp_ranker_probe_bundles

REV = "rev0023"
DATA = ROOT / "data"


def game_specs():
    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 30, 0, 0, 10, 0),
        DeckVector(40, 24, 4, 4, 8, 0),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 40, 0, 0, 20, 0),
        DeckVector(60, 36, 8, 8, 8, 0),
    ]
    agents = [
        make_public_agent("heuristic"),
        make_public_agent("counter_happy"),
        make_public_agent("threat_rush"),
        make_public_agent("patient"),
        make_public_agent("code_jace_lock_rev0013"),
        make_public_agent("code_overlord_clock_rev0013"),
        make_public_agent("code_force_conservative_rev0013"),
        make_public_agent("code_jace_ultimator_rev0020"),
        make_public_agent("ranker_blend_threat_rev0022"),
        make_public_agent("ranker_blend_counter_rev0022"),
    ]
    mulligans = [
        (POLICY_KEEP_ALWAYS, POLICY_KEEP_ALWAYS),
        (POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS),
        (POLICY_LAND_BAND_BUSINESS, POLICY_LAND_BAND),
        (POLICY_LAND_BAND, POLICY_LAND_BAND),
    ]
    specs = []
    for i in range(84):
        specs.append((
            decks[i % len(decks)],
            decks[(i * 5 + 1) % len(decks)],
            agents[i % len(agents)],
            agents[(i * 7 + 3) % len(agents)],
            i % 2,
            20 if i % 3 else 40,
            mulligans[i % len(mulligans)],
        ))
    return specs


def choice_metrics(df: pd.DataFrame, score_col: str) -> dict[str, float]:
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
            reciprocal += 1.0 / (pos + 1)
            correct += 1 if pos == 0 else 0
    return {
        "top1_accuracy": float(correct / total) if total else 0.0,
        "mean_reciprocal_rank": float(reciprocal / total) if total else 0.0,
        "random_slot_baseline_accuracy": float(sum(random_terms) / len(random_terms)) if random_terms else 0.0,
        "decisions": int(total),
    }


def train_mlp_ranker(df: pd.DataFrame, feature_cols: list[str]) -> tuple[MLPActionRankerModel, dict[str, object], pd.DataFrame]:
    from sklearn.metrics import log_loss, roc_auc_score
    from sklearn.neural_network import MLPClassifier

    train_mask = (df["game_index"].astype(int) % 5) != 0
    train = df[train_mask].copy()
    test = df[~train_mask].copy()
    X_train = train[feature_cols].astype(float).to_numpy()
    y_train = train["chosen"].astype(int).to_numpy()
    X_test = test[feature_cols].astype(float).to_numpy()
    y_test = test["chosen"].astype(int).to_numpy()
    clf = MLPClassifier(
        hidden_layer_sizes=(32,),
        activation="relu",
        solver="adam",
        alpha=0.0005,
        batch_size=512,
        learning_rate_init=0.003,
        max_iter=120,
        early_stopping=True,
        n_iter_no_change=8,
        validation_fraction=0.12,
        random_state=23023,
    )
    clf.fit(X_train, y_train)
    test_probs = clf.predict_proba(X_test)[:, 1]
    test = test.assign(pred_prob=test_probs)
    choice = choice_metrics(test, "pred_prob")
    metrics: dict[str, object] = {
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_decisions": int(train["decision_id"].nunique()),
        "test_decisions": int(test["decision_id"].nunique()),
        "n_iter": int(clf.n_iter_),
        "loss": float(clf.loss_),
        "test_top1_accuracy": choice["top1_accuracy"],
        "test_mean_reciprocal_rank": choice["mean_reciprocal_rank"],
        "random_slot_baseline_accuracy": choice["random_slot_baseline_accuracy"],
        "test_log_loss": float(log_loss(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "test_roc_auc": float(roc_auc_score(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "hidden_size": int(clf.coefs_[0].shape[1]),
    }
    model = MLPActionRankerModel(
        model_id="mlp_ranker_rev0023_sklearn_mlp32",
        feature_names=tuple(feature_cols),
        hidden_weights=tuple(tuple(float(v) for v in row) for row in clf.coefs_[0]),
        hidden_bias=tuple(float(v) for v in clf.intercepts_[0]),
        output_weights=tuple(float(v) for v in clf.coefs_[1].ravel()),
        output_bias=float(clf.intercepts_[1].ravel()[0]),
        activation="relu",
        source_revision=REV,
        training_summary=metrics,
    )
    # Simple feature influence proxy: sum absolute first-layer weights.
    importance = pd.DataFrame({
        "feature": feature_cols,
        "abs_hidden_weight_sum": [float(sum(abs(v) for v in row)) for row in clf.coefs_[0]],
    }).sort_values("abs_hidden_weight_sum", ascending=False)
    return model, metrics, importance


def lint_mlp_agent(model: MLPActionRankerModel) -> dict[str, object]:
    from random import Random
    from src.muc5.decision import build_decision_frame
    from src.muc5.engine import start_game

    deck = DeckVector(40, 22, 8, 6, 3, 1)
    state = start_game(deck, deck, seed=2302301, starting_life=20, record_log=False)
    frame = build_decision_frame(state)
    agent = MLPActionRankerAgent(model)
    idx = agent.choose_action_index(frame, Random(9))
    return {"ok": 0 <= idx < frame.action_count, "action_count": frame.action_count, "chosen_index": int(idx), "chosen_action": frame.legal_actions[idx].compact()}


def trace_specs(strategies):
    return [
        (0, 3, 20, 0),
        (1, 4, 20, 1),
        (2, 5, 40, 0),
        (3, 6, 40, 1),
        (4, 7, 20, 0),
        (5, 0, 40, 1),
        (6, 2, 20, 1),
        (7, 1, 40, 0),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    feature_cols = list(action_ranker_feature_names())
    rows, collection = collect_action_imitation_rows(game_specs(), seed_base=2302300, max_decisions=360)
    df = pd.DataFrame(rows)
    df.to_csv(DATA / f"{REV}_mlp_ranker_training_dataset.csv", index=False)
    model, metrics, importance = train_mlp_ranker(df, feature_cols)
    save_mlp_ranker_model(model, DATA / f"{REV}_mlp_ranker_model.json")
    importance.head(100).to_csv(DATA / f"{REV}_mlp_ranker_feature_importance.csv", index=False)
    lint = lint_mlp_agent(model)
    if not lint["ok"]:
        raise SystemExit(f"MLP ranker lint failed: {lint}")

    strategies = mlp_ranker_probe_bundles(DATA / "seed_decks.json")
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2303000, max_decisions=560)
    write_csv(DATA / f"{REV}_mlp_ranker_games.csv", rows)
    aggregate = aggregate_payoff_rows(rows)
    write_csv(DATA / f"{REV}_mlp_ranker_aggregate.csv", aggregate)
    standings = strategy_standings(rows)
    write_csv(DATA / f"{REV}_mlp_ranker_standings.csv", standings)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / f"{REV}_mlp_ranker_pairwise.csv", pairwise)
    write_csv(DATA / f"{REV}_mlp_ranker_stat_standings.csv", stat_stand)
    stat_gate = audit_statistical_gate(rows, stat_stand, pairwise, min_raw_rows=len(rows), max_truncation_rate=0.12)

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
            seed=2304000 + t,
            transition_seed=2305000 + t,
            agent_seed=2306000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=560,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_mlp_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_mlp_ranker_replay_traces.jsonl")
    (DATA / f"{REV}_mlp_ranker_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / f"{REV}_mlp_ranker_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / f"{REV}_mlp_ranker_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")
    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    mlp_ids = [s.strategy_id for s in strategies if s.agent_name.startswith("mlp_")]
    summary = {
        "revision": REV,
        "collection": collection.as_dict(),
        "feature_count": len(feature_cols),
        "training_metrics": metrics,
        "ranker_lint": lint,
        "strategy_count": len(strategies),
        "mlp_strategy_ids": mlp_ids,
        "games": len(rows),
        "aggregate_rows": len(aggregate),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "top_standings": standings[:8],
        "top_stat_standings": stat_stand[:8],
    }
    (DATA / f"{REV}_mlp_ranker_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
