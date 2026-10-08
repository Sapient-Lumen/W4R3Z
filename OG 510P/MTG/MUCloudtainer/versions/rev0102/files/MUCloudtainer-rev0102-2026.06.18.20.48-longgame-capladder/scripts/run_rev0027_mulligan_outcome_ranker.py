from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.mulligan_outcome_training import collect_outcome_weighted_mulligan_rows
from src.muc5.mulligan_ranker import (
    OUTCOME_MODEL_NAME,
    LinearMulliganRankerAgent,
    LinearMulliganRankerModel,
    load_mulligan_ranker_model,
    model_path_for_name,
    mulligan_ranker_feature_names,
    save_mulligan_ranker_model,
)
from src.muc5.payoff import aggregate_payoff_rows, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import learned_mulligan_gate_bundles, mulligan_outcome_gate_bundles

REV = "rev0027"
DATA = ROOT / "data"


def choice_metrics(df: pd.DataFrame, score_col: str, label_col: str, group_col: str) -> dict[str, float | int]:
    total = 0
    correct = 0
    reciprocal = 0.0
    random_terms = []
    for _, g in df.groupby(group_col, sort=False):
        total += 1
        ordered = g.sort_values(score_col, ascending=False).reset_index(drop=True)
        positions = ordered.index[ordered[label_col].astype(int) == 1].tolist()
        random_terms.append(1.0 / float(max(1, len(g))))
        if positions:
            pos = int(positions[0])
            correct += 1 if pos == 0 else 0
            reciprocal += 1.0 / float(pos + 1)
    return {
        "groups": int(total),
        "top1_accuracy": float(correct / total) if total else 0.0,
        "mean_reciprocal_rank": float(reciprocal / total) if total else 0.0,
        "random_slot_baseline_accuracy": float(sum(random_terms) / len(random_terms)) if random_terms else 0.0,
    }


def build_training_game_specs() -> list[tuple]:
    # Use the rev0024 same-shell policy panel as the behavior-policy source.
    # This intentionally includes deterministic rule mulligans and the previous
    # pseudo-oracle ranker, so rev0027 can learn from terminal outcomes rather
    # than only from hand-quality labels.
    strategies = learned_mulligan_gate_bundles(DATA / "seed_decks.json")
    # Keep the collection panel broad but not exhaustive: every behavior bundle
    # is tested against six stable opponents across both life totals and starts.
    opponent_indices = [0, 3, 4, 7, 8, 11]
    games: list[tuple] = []
    agent_cache = {b.agent_name: make_public_agent(b.agent_name) for b in strategies}
    for life in (20, 40):
        for i, left in enumerate(strategies):
            for j in opponent_indices:
                right = strategies[j]
                for starting_player in (0, 1):
                    games.append((
                        left.deck,
                        right.deck,
                        agent_cache[left.agent_name],
                        agent_cache[right.agent_name],
                        starting_player,
                        life,
                        (left.mulligan_policy, right.mulligan_policy),
                        left.strategy_id,
                        right.strategy_id,
                    ))
    return games


def train_model() -> tuple[LinearMulliganRankerModel, dict[str, object], pd.DataFrame, pd.DataFrame, dict[str, object]]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

    games = build_training_game_specs()
    keep_rows, bottom_rows, collection = collect_outcome_weighted_mulligan_rows(games, seed_base=2702700, max_decisions=560)
    keep_df = pd.DataFrame(keep_rows)
    bottom_df = pd.DataFrame(bottom_rows)
    features = list(mulligan_ranker_feature_names())

    if keep_df.empty or bottom_df.empty:
        raise RuntimeError("mulligan outcome collection produced empty training tables")
    if keep_df["label_keep"].nunique() < 2:
        raise RuntimeError("keep/take outcome table needs both keep and take labels")
    if bottom_df["label_bottom"].nunique() < 2:
        raise RuntimeError("bottom outcome table needs both positive and negative labels")

    keep_train_mask = (keep_df["game_index"].astype(int) % 5) != 0
    bottom_train_mask = (bottom_df["game_index"].astype(int) % 5) != 0
    keep_train = keep_df[keep_train_mask].copy()
    keep_test = keep_df[~keep_train_mask].copy()
    bottom_train = bottom_df[bottom_train_mask].copy()
    bottom_test = bottom_df[~bottom_train_mask].copy()

    # LogisticRegression accepts sample_weight. Keep the floor tiny but nonzero
    # for terminal losing choices because they still help define the legal-action
    # surface; truncations remain zero-weight teachers.
    keep_weight = keep_train["outcome_weight"].astype(float).to_numpy()
    bottom_weight = bottom_train["outcome_weight"].astype(float).to_numpy()
    if keep_weight.sum() <= 0 or bottom_weight.sum() <= 0:
        raise RuntimeError("outcome mulligan weights are all zero")

    keep_clf = LogisticRegression(max_iter=260, C=0.9, solver="liblinear", random_state=27027)
    bottom_clf = LogisticRegression(max_iter=260, C=0.9, solver="liblinear", random_state=27028)
    keep_clf.fit(keep_train[features].astype(float).to_numpy(), keep_train["label_keep"].astype(int).to_numpy(), sample_weight=keep_weight)
    bottom_clf.fit(bottom_train[features].astype(float).to_numpy(), bottom_train["label_bottom"].astype(int).to_numpy(), sample_weight=bottom_weight)

    keep_prob = keep_clf.predict_proba(keep_test[features].astype(float).to_numpy())[:, 1]
    keep_pred = (keep_prob >= 0.5).astype(int)
    bottom_prob = bottom_clf.predict_proba(bottom_test[features].astype(float).to_numpy())[:, 1]
    bottom_eval = bottom_test.assign(pred_prob=bottom_prob)
    bottom_metrics = choice_metrics(bottom_eval, "pred_prob", "label_bottom", "example_id")
    try:
        keep_auc = float(roc_auc_score(keep_test["label_keep"].astype(int), keep_prob))
    except ValueError:
        keep_auc = float("nan")

    metrics: dict[str, object] = {
        "collection": collection.as_dict(),
        "keep_train_rows": int(len(keep_train)),
        "keep_test_rows": int(len(keep_test)),
        "bottom_train_rows": int(len(bottom_train)),
        "bottom_test_rows": int(len(bottom_test)),
        "feature_count": int(len(features)),
        "keep_accuracy": float(accuracy_score(keep_test["label_keep"].astype(int), keep_pred)),
        "keep_log_loss": float(log_loss(keep_test["label_keep"].astype(int), keep_prob)),
        "keep_roc_auc": keep_auc,
        "bottom_top1_accuracy": bottom_metrics["top1_accuracy"],
        "bottom_mrr": bottom_metrics["mean_reciprocal_rank"],
        "bottom_random_slot_baseline_accuracy": bottom_metrics["random_slot_baseline_accuracy"],
        "bottom_groups": bottom_metrics["groups"],
        "label_source": "rev0027_terminal_outcome_weighted_behavior_mulligans",
        "behavior_panel_games": len(games),
    }
    model = LinearMulliganRankerModel(
        model_id="linear_mulligan_outcome_ranker_rev0027_logreg",
        feature_names=tuple(features),
        keep_weights=tuple(float(x) for x in keep_clf.coef_.ravel()),
        keep_intercept=float(keep_clf.intercept_.ravel()[0]),
        bottom_weights=tuple(float(x) for x in bottom_clf.coef_.ravel()),
        bottom_intercept=float(bottom_clf.intercept_.ravel()[0]),
        source_revision=REV,
        training_summary=metrics,
    )
    return model, metrics, keep_df, bottom_df, collection.as_dict()


def same_shell_policy_summary(rows):
    scores = defaultdict(list)
    terminal_wins = defaultdict(list)
    for row in rows:
        for side in (0, 1):
            strategy = str(row[f"strategy{side}"])
            shell, suffix = strategy.rsplit("_", 1)
            scores[(shell, suffix)].append(float(row[f"p{side}_score"]))
            terminal_wins[(shell, suffix)].append(float(row[f"p{side}_terminal_win"]))
    out = []
    for (shell, suffix), vals in sorted(scores.items()):
        wins = terminal_wins[(shell, suffix)]
        out.append({
            "shell": shell,
            "policy_suffix": suffix,
            "games": len(vals),
            "mean_score_draw_half": sum(vals) / len(vals) if vals else 0.0,
            "terminal_win_rate": sum(wins) / len(wins) if wins else 0.0,
        })
    out.sort(key=lambda r: (r["shell"], -r["mean_score_draw_half"], r["policy_suffix"]))
    return out


def trace_specs(strategies):
    # Ensure each shell has at least one outcome-vs-baseline replay trace.
    name_to_idx = {s.strategy_id: i for i, s in enumerate(strategies)}
    pairs = [
        ("fjace_code_outcome", "fjace_code_business", 20, 0),
        ("fjace_code_outcome", "fjace_code_pseudo", 40, 1),
        ("overlord_threat_outcome", "overlord_threat_band", 20, 1),
        ("overlord_threat_outcome", "overlord_threat_pseudo", 40, 0),
        ("wall_counter_outcome", "wall_counter_business", 20, 0),
        ("wall_counter_outcome", "wall_counter_pseudo", 40, 1),
        ("fjace_code_outcome", "wall_counter_outcome", 20, 0),
        ("overlord_threat_outcome", "fjace_code_outcome", 40, 1),
    ]
    return [(name_to_idx[a], name_to_idx[b], life, start) for a, b, life, start in pairs]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    model, metrics, keep_df, bottom_df, collection = train_model()
    save_mulligan_ranker_model(model, model_path_for_name(OUTCOME_MODEL_NAME))
    keep_df.to_csv(DATA / "rev0027_mulligan_outcome_keep_training.csv", index=False)
    bottom_df.to_csv(DATA / "rev0027_mulligan_outcome_bottom_training.csv", index=False)

    # Lint the fresh JSON model through the public factory path.
    loaded = load_mulligan_ranker_model(model_path_for_name(OUTCOME_MODEL_NAME))
    lint_agent = LinearMulliganRankerAgent(loaded, name=OUTCOME_MODEL_NAME)
    lint = {
        "agent_name": lint_agent.name,
        "model_id": loaded.model_id,
        "feature_count": len(loaded.feature_names),
        "keep_accuracy": metrics["keep_accuracy"],
        "bottom_top1_accuracy": metrics["bottom_top1_accuracy"],
        "bottom_random_slot_baseline_accuracy": metrics["bottom_random_slot_baseline_accuracy"],
    }

    strategies = mulligan_outcome_gate_bundles(DATA / "seed_decks.json")
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2703000, max_decisions=560)
    write_csv(DATA / "rev0027_mulligan_outcome_games.csv", rows)
    aggregate = aggregate_payoff_rows(rows)
    write_csv(DATA / "rev0027_mulligan_outcome_aggregate.csv", aggregate)
    standings = strategy_standings(rows)
    write_csv(DATA / "rev0027_mulligan_outcome_standings.csv", standings)
    shell_summary = same_shell_policy_summary(rows)
    write_csv(DATA / "rev0027_mulligan_outcome_same_shell.csv", shell_summary)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / "rev0027_mulligan_outcome_pairwise.csv", pairwise)
    write_csv(DATA / "rev0027_mulligan_outcome_stat_standings.csv", stat_stand)
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
            seed=2704000 + t,
            transition_seed=2705000 + t,
            agent_seed=2706000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=560,
            mulligan_agents=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"rev0027_mulligan_outcome_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / "rev0027_mulligan_outcome_replay_traces.jsonl")
    (DATA / "rev0027_mulligan_outcome_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / "rev0027_mulligan_outcome_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / "rev0027_mulligan_outcome_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    summary = {
        "revision": REV,
        "codename": "mulliganoutcome-cachedpregame",
        "training_metrics": metrics,
        "collection": collection,
        "lint": lint,
        "strategy_count": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(aggregate),
        "same_shell_rows": len(shell_summary),
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "replay_count": len(traces),
        "replay_passed": sum(1 for r in replay_results if r.get("passed")),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "public_payoff_refactor": {
            "mulligan_agent_cache": True,
            "reason": "avoid reloading JSON-backed mulligan ranker once per game",
        },
    }
    (DATA / "rev0027_mulligan_outcome_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
