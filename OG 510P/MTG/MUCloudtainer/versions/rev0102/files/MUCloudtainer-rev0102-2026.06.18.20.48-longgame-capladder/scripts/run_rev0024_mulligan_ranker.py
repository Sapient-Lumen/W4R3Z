from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cpp_trace import check_public_traces_with_cpp
from src.muc5.mulligan_ranker import (
    MODEL_NAME,
    LinearMulliganRankerModel,
    LinearMulliganRankerAgent,
    generate_mulligan_training_rows,
    load_mulligan_ranker_model,
    mulligan_ranker_feature_names,
    save_mulligan_ranker_model,
)
from src.muc5.payoff import aggregate_payoff_rows, load_seed_decks, write_csv
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows, strategy_standings
from src.muc5.public_agents import make_public_agent
from src.muc5.public_payoff import build_public_payoff_rows
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import learned_mulligan_gate_bundles

REV = "rev0024"
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


def train_model(seed_decks_path: Path) -> tuple[LinearMulliganRankerModel, dict[str, object], pd.DataFrame, pd.DataFrame]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

    decks = load_seed_decks(seed_decks_path)
    deck_counts_list = [d.counts() for d in decks.values()]
    keep_rows, bottom_rows = generate_mulligan_training_rows(deck_counts_list, samples_per_deck_life=180, seed=240240)
    keep_df = pd.DataFrame(keep_rows)
    bottom_df = pd.DataFrame(bottom_rows)
    features = list(mulligan_ranker_feature_names())

    keep_train_mask = (keep_df["sample"].astype(int) % 5) != 0
    bottom_train_mask = (bottom_df["sample"].astype(int) % 5) != 0
    keep_train = keep_df[keep_train_mask]
    keep_test = keep_df[~keep_train_mask]
    bottom_train = bottom_df[bottom_train_mask]
    bottom_test = bottom_df[~bottom_train_mask]

    keep_clf = LogisticRegression(max_iter=220, C=1.0, solver="liblinear", random_state=24024)
    bottom_clf = LogisticRegression(max_iter=220, C=1.0, solver="liblinear", random_state=24025)
    keep_clf.fit(keep_train[features].astype(float).to_numpy(), keep_train["label_keep"].astype(int).to_numpy())
    bottom_clf.fit(bottom_train[features].astype(float).to_numpy(), bottom_train["label_bottom"].astype(int).to_numpy())

    keep_prob = keep_clf.predict_proba(keep_test[features].astype(float).to_numpy())[:, 1]
    keep_pred = (keep_prob >= 0.5).astype(int)
    bottom_prob = bottom_clf.predict_proba(bottom_test[features].astype(float).to_numpy())[:, 1]
    bottom_eval = bottom_test.assign(pred_prob=bottom_prob)
    bottom_metrics = choice_metrics(bottom_eval, "pred_prob", "label_bottom", "example_id")

    metrics: dict[str, object] = {
        "keep_train_rows": int(len(keep_train)),
        "keep_test_rows": int(len(keep_test)),
        "bottom_train_rows": int(len(bottom_train)),
        "bottom_test_rows": int(len(bottom_test)),
        "feature_count": int(len(features)),
        "keep_accuracy": float(accuracy_score(keep_test["label_keep"].astype(int), keep_pred)),
        "keep_log_loss": float(log_loss(keep_test["label_keep"].astype(int), keep_prob)),
        "keep_roc_auc": float(roc_auc_score(keep_test["label_keep"].astype(int), keep_prob)),
        "bottom_top1_accuracy": bottom_metrics["top1_accuracy"],
        "bottom_mrr": bottom_metrics["mean_reciprocal_rank"],
        "bottom_random_slot_baseline_accuracy": bottom_metrics["random_slot_baseline_accuracy"],
        "bottom_groups": bottom_metrics["groups"],
        "deck_count": int(len(deck_counts_list)),
        "samples_per_deck_life": 180,
        "label_source": "rev0024_pseudo_oracle_opening_hand_quality",
    }
    model = LinearMulliganRankerModel(
        model_id="linear_mulligan_ranker_rev0024_logreg",
        feature_names=tuple(features),
        keep_weights=tuple(float(x) for x in keep_clf.coef_.ravel()),
        keep_intercept=float(keep_clf.intercept_.ravel()[0]),
        bottom_weights=tuple(float(x) for x in bottom_clf.coef_.ravel()),
        bottom_intercept=float(bottom_clf.intercept_.ravel()[0]),
        source_revision=REV,
        training_summary=metrics,
    )
    return model, metrics, keep_df, bottom_df


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
    # Include learned-vs-baseline cases in both life-total regimes.
    return [
        (0, 3, 20, 0),
        (3, 0, 40, 1),
        (4, 7, 20, 1),
        (7, 4, 40, 0),
        (8, 11, 20, 0),
        (11, 8, 40, 1),
        (3, 7, 20, 0),
        (7, 11, 40, 1),
    ]


def main() -> None:
    DATA.mkdir(exist_ok=True)
    model, metrics, keep_df, bottom_df = train_model(DATA / "seed_decks.json")
    save_mulligan_ranker_model(model, DATA / "rev0024_mulligan_ranker_model.json")
    keep_df.to_csv(DATA / "rev0024_mulligan_ranker_keep_training.csv", index=False)
    bottom_df.to_csv(DATA / "rev0024_mulligan_ranker_bottom_training.csv", index=False)

    # Basic agent lint from a loaded JSON model.
    loaded = load_mulligan_ranker_model(DATA / "rev0024_mulligan_ranker_model.json")
    agent = LinearMulliganRankerAgent(loaded)
    lint = {
        "model_name": MODEL_NAME,
        "loaded_model_id": loaded.model_id,
        "feature_count": len(loaded.feature_names),
        "agent_name": agent.name,
        "keep_accuracy": metrics["keep_accuracy"],
        "bottom_top1_accuracy": metrics["bottom_top1_accuracy"],
    }

    strategies = learned_mulligan_gate_bundles(DATA / "seed_decks.json")
    rows = build_public_payoff_rows(strategies, simulator_revision=REV, reps=1, base_seed=2403000, max_decisions=560)
    write_csv(DATA / "rev0024_learned_mulligan_games.csv", rows)
    aggregate = aggregate_payoff_rows(rows)
    write_csv(DATA / "rev0024_learned_mulligan_aggregate.csv", aggregate)
    standings = strategy_standings(rows)
    write_csv(DATA / "rev0024_learned_mulligan_standings.csv", standings)
    shell_summary = same_shell_policy_summary(rows)
    write_csv(DATA / "rev0024_learned_mulligan_same_shell.csv", shell_summary)
    pairwise = pairwise_stat_rows(rows, min_games_for_claim=4)
    stat_stand = statistical_standings(rows, min_games_for_claim=24)
    write_csv(DATA / "rev0024_learned_mulligan_pairwise.csv", pairwise)
    write_csv(DATA / "rev0024_learned_mulligan_stat_standings.csv", stat_stand)
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
            seed=2404000 + t,
            transition_seed=2405000 + t,
            agent_seed=2406000 + t,
            starting_player=starting_player,
            starting_life=life,
            max_decisions=560,
            mulligan_agents=(left.mulligan_policy, right.mulligan_policy),
        )
        trace["trace_id"] = f"rev0024_learned_mulligan_trace_{t:03d}"
        traces.append(trace)
        replay_results.append(replay_public_decision_trace(trace).as_dict())
    write_trace_jsonl(traces, DATA / "rev0024_learned_mulligan_replay_traces.jsonl")
    (DATA / "rev0024_learned_mulligan_replay_results.json").write_text(json.dumps(replay_results, indent=2, sort_keys=True), encoding="utf-8")
    cpp_summary, cpp_rows = check_public_traces_with_cpp(traces, revision=REV)
    write_csv(DATA / "rev0024_learned_mulligan_cpp_trace_rows.csv", [r.as_dict() for r in cpp_rows])
    (DATA / "rev0024_learned_mulligan_cpp_trace_summary.json").write_text(json.dumps(cpp_summary.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    promo = audit_promotion_rows(
        rows,
        replay_results=replay_results,
        config=PromotionGateConfig(simulator_revision=REV, min_rows=len(rows), max_truncation_rate=0.12, min_replay_traces=len(traces)),
    )
    summary = {
        "revision": REV,
        "strategy_count": len(strategies),
        "games": len(rows),
        "aggregate_rows": len(aggregate),
        "mulligan_policies": sorted({str(s.mulligan_policy) for s in strategies}),
        "training_metrics": metrics,
        "lint": lint,
        "promotion_gate": promo.as_dict(),
        "statistical_gate": stat_gate.as_dict(),
        "cpp_trace_summary": cpp_summary.as_dict(),
        "replay_passed": sum(1 for r in replay_results if r.get("passed") is True),
        "replay_count": len(replay_results),
        "top_standings": standings[:8],
        "same_shell_policy_summary": shell_summary,
    }
    (DATA / "rev0024_learned_mulligan_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not promo.passed or not stat_gate.passed or cpp_summary.mismatches != 0 or cpp_summary.skipped_events != 0 or cpp_summary.python_replay_errors != 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
