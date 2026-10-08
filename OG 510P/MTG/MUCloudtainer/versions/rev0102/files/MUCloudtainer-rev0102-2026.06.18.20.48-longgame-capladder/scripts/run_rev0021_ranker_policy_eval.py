from __future__ import annotations

import json
import sys
from pathlib import Path
from random import Random

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.code_policy import make_code_policy_agent
from src.muc5.deckspace import DeckVector
from src.muc5.decision import build_decision_frame
from src.muc5.engine import start_game
from src.muc5.imitation import action_ranker_feature_names, collect_action_imitation_rows
from src.muc5.mulligan import POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from src.muc5.payoff import StrategyBundle, aggregate_payoff_rows, load_seed_decks, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.ranker_policy import LinearActionRankerAgent, LinearActionRankerModel, save_linear_ranker_model
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings

REV = "rev0021"
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
        make_code_policy_agent("code_jace_lock_rev0013"),
        make_code_policy_agent("code_overlord_clock_rev0013"),
        make_code_policy_agent("code_force_conservative_rev0013"),
        make_code_policy_agent("code_jace_ultimator_rev0020"),
    ]
    mulligans = [
        (POLICY_KEEP_ALWAYS, POLICY_KEEP_ALWAYS),
        (POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS),
        (POLICY_LAND_BAND_BUSINESS, POLICY_LAND_BAND),
        (POLICY_LAND_BAND, POLICY_LAND_BAND),
    ]
    specs = []
    for i in range(72):
        specs.append((
            decks[i % len(decks)],
            decks[(i * 3 + 1) % len(decks)],
            agents[i % len(agents)],
            agents[(i * 5 + 2) % len(agents)],
            i % 2,
            20 if i % 4 else 40,
            mulligans[i % len(mulligans)],
        ))
    return specs


def train_ranker(df: pd.DataFrame, feature_cols: list[str]) -> tuple[LinearActionRankerModel, dict[str, object], pd.DataFrame]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss, roc_auc_score

    train_mask = (df["game_index"].astype(int) % 5) != 0
    train = df[train_mask].copy()
    test = df[~train_mask].copy()
    X_train = train[feature_cols].astype(float).to_numpy()
    y_train = train["chosen"].astype(int).to_numpy()
    X_test = test[feature_cols].astype(float).to_numpy()
    y_test = test["chosen"].astype(int).to_numpy()
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear", random_state=2021)
    clf.fit(X_train, y_train)
    test_probs = clf.predict_proba(X_test)[:, 1]
    test = test.assign(pred_prob=test_probs)
    grouped = test.groupby("decision_id", sort=False)
    correct = 0
    total = 0
    reciprocal = 0.0
    random_baseline_terms = []
    for _, g in grouped:
        total += 1
        random_baseline_terms.append(1.0 / float(g["action_count"].iloc[0]))
        ordered = g.sort_values("pred_prob", ascending=False).reset_index(drop=True)
        chosen_positions = ordered.index[ordered["chosen"].astype(int) == 1].tolist()
        if chosen_positions:
            pos = int(chosen_positions[0])
            reciprocal += 1.0 / (pos + 1)
            correct += 1 if pos == 0 else 0
    metrics: dict[str, object] = {
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_decisions": int(train["decision_id"].nunique()),
        "test_decisions": int(test["decision_id"].nunique()),
        "test_top1_accuracy": float(correct / total) if total else 0.0,
        "test_mean_reciprocal_rank": float(reciprocal / total) if total else 0.0,
        "random_slot_baseline_accuracy": float(sum(random_baseline_terms) / len(random_baseline_terms)) if random_baseline_terms else 0.0,
        "test_log_loss": float(log_loss(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "test_roc_auc": float(roc_auc_score(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
    }
    coefs = pd.DataFrame({"feature": feature_cols, "coef": clf.coef_[0]}).assign(abs_coef=lambda x: x["coef"].abs()).sort_values("abs_coef", ascending=False)
    model = LinearActionRankerModel(
        model_id="linear_ranker_rev0021_logreg",
        feature_names=tuple(feature_cols),
        coefficients=tuple(float(x) for x in clf.coef_[0]),
        intercept=float(clf.intercept_[0]),
        source_revision=REV,
        training_summary=metrics,
    )
    return model, metrics, coefs


def strategy_population(decks_path: Path) -> list[StrategyBundle]:
    decks = load_seed_decks(decks_path)
    return [
        StrategyBundle("ranker_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "linear_ranker_rev0021", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("ranker_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "linear_ranker_rev0021", POLICY_LAND_BAND),
        StrategyBundle("ranker_jace60", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "linear_ranker_rev0021", POLICY_KEEP_ALWAYS),
        StrategyBundle("pub_fjace", "forty_force_jace_pressure", decks["forty_force_jace_pressure"], "heuristic", POLICY_LAND_BAND),
        StrategyBundle("pub_counter_wall", "sixty_counterwall_jace", decks["sixty_counterwall_jace"], "counter_happy", POLICY_LAND_BAND_BUSINESS),
        StrategyBundle("pub_threat_overlord", "forty_overlord_impending", decks["forty_overlord_impending"], "threat_rush", POLICY_LAND_BAND),
        StrategyBundle("code_jace", "sixty_no_overlord_jace_only", decks["sixty_no_overlord_jace_only"], "code_jace_lock_rev0013", POLICY_KEEP_ALWAYS),
        StrategyBundle("code_clock", "forty_overlord_impending", decks["forty_overlord_impending"], "code_overlord_clock_rev0013", POLICY_LAND_BAND),
    ]


def lint_ranker_agent(model: LinearActionRankerModel, decks_path: Path) -> dict[str, object]:
    decks = load_seed_decks(decks_path)
    agent = LinearActionRankerAgent(model)
    rng = Random(2021)
    errors: list[str] = []
    frames_checked = 0
    for i, deck_name in enumerate(["forty_force_jace_pressure", "forty_overlord_impending", "sixty_no_overlord_jace_only"]):
        state = start_game(decks[deck_name], decks[deck_name], seed=91210 + i, starting_life=20 if i else 40, record_log=False)
        frame = build_decision_frame(state)
        frames_checked += 1
        idx = agent.choose_action_index(frame, rng)
        if not 0 <= idx < frame.action_count:
            errors.append(f"frame {i}: index {idx} outside {frame.action_count}")
    return {"ok": not errors, "frames_checked": frames_checked, "errors": errors}


def main() -> None:
    DATA.mkdir(exist_ok=True)
    feature_cols = list(action_ranker_feature_names())
    rows, collection = collect_action_imitation_rows(game_specs(), seed_base=2021000, max_decisions=340)
    df = pd.DataFrame(rows)
    dataset_path = DATA / f"{REV}_ranker_training_dataset.csv"
    df.to_csv(dataset_path, index=False)
    model, metrics, coefs = train_ranker(df, feature_cols)
    save_linear_ranker_model(model, DATA / f"{REV}_linear_ranker_model.json")
    coefs.head(100).to_csv(DATA / f"{REV}_linear_ranker_coefficients.csv", index=False)
    lint = lint_ranker_agent(model, DATA / "seed_decks.json")
    if not lint["ok"]:
        raise SystemExit(f"ranker lint failed: {lint}")

    strategies = strategy_population(DATA / "seed_decks.json")
    payoff_rows = build_public_payoff_rows(strategies, simulator_revision=REV, base_seed=212100, max_decisions=520)
    write_csv(DATA / f"{REV}_ranker_policy_games.csv", payoff_rows)
    aggregate = aggregate_payoff_rows(payoff_rows)
    write_csv(DATA / f"{REV}_ranker_policy_aggregate.csv", aggregate)
    standings = strategy_standings(payoff_rows)
    write_csv(DATA / f"{REV}_ranker_policy_standings.csv", standings)
    stat_stand = statistical_standings(payoff_rows, min_games_for_claim=24)
    pairwise = pairwise_stat_rows(payoff_rows, min_games_for_claim=4)
    write_csv(DATA / f"{REV}_ranker_policy_stat_standings.csv", stat_stand)
    write_csv(DATA / f"{REV}_ranker_policy_pairwise.csv", pairwise)
    stat_gate = audit_statistical_gate(payoff_rows, stat_stand, pairwise, min_raw_rows=len(payoff_rows), max_truncation_rate=0.10)

    sample_specs = [(0, 3, 20, 0), (1, 4, 20, 1), (2, 6, 40, 0), (6, 0, 40, 1), (4, 1, 20, 0), (7, 2, 40, 1), (0, 7, 20, 1), (2, 5, 40, 0)]
    traces = []
    replay_results = []
    for t, (i, j, life, starting_player) in enumerate(sample_specs):
        left = strategies[i]
        right = strategies[j]
        trace = record_public_decision_trace(
            left.deck,
            right.deck,
            make_public_agent(left.agent_name),
            make_public_agent(right.agent_name),
            seed=312100 + t,
            transition_seed=412100 + t,
            agent_seed=512100 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=520,
            mulligan_policies=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"{REV}_ranker_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / f"{REV}_ranker_policy_replay_traces.jsonl")
    (DATA / f"{REV}_ranker_policy_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    promo = audit_promotion_rows(
        payoff_rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(payoff_rows), min_replay_traces=len(replay_results), max_truncation_rate=0.10),
    )

    ranker_strategy_rows = [r for r in stat_stand if "linear_ranker_rev0021" in str(r.get("agents", ""))]
    summary = {
        "revision": REV,
        "collection": collection.as_dict(),
        "feature_count": len(feature_cols),
        "training_metrics": metrics,
        "ranker_lint": lint,
        "payoff_games": len(payoff_rows),
        "strategies": len(strategies),
        "aggregate_rows": len(aggregate),
        "ranker_strategy_count": len(ranker_strategy_rows),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "top_standings": standings[:8],
        "top_stat_standings": stat_stand[:8],
        "ranker_stat_rows": ranker_strategy_rows,
        "top_coefficients": coefs.head(20).to_dict(orient="records"),
    }
    (DATA / f"{REV}_ranker_policy_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or metrics["test_top1_accuracy"] <= metrics["random_slot_baseline_accuracy"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
