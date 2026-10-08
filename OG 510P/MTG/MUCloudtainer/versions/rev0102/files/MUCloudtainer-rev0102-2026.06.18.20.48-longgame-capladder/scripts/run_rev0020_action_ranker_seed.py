from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from src.muc5.code_policy import make_code_policy_agent
from src.muc5.deckspace import DeckVector
from src.muc5.imitation import action_ranker_feature_names, collect_action_imitation_rows
from src.muc5.public_agents import make_public_agent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REV = "rev0020"


def game_specs():
    decks = [
        DeckVector(40, 22, 8, 6, 3, 1),
        DeckVector(40, 20, 4, 8, 5, 3),
        DeckVector(40, 30, 0, 0, 10, 0),
        DeckVector(60, 30, 10, 8, 8, 4),
        DeckVector(60, 34, 4, 12, 5, 5),
        DeckVector(60, 40, 0, 0, 20, 0),
    ]
    agents = [
        make_public_agent("heuristic"),
        make_public_agent("counter_happy"),
        make_public_agent("threat_rush"),
        make_public_agent("patient"),
        make_code_policy_agent("code_jace_ultimator_rev0020"),
        make_code_policy_agent("code_overlord_clock_rev0013"),
    ]
    mulligans = [("keep_always", "keep_always"), ("land_band", "land_band_business"), ("land_band_business", "land_band")]
    specs = []
    for i in range(48):
        specs.append((
            decks[i % len(decks)],
            decks[(i * 2 + 1) % len(decks)],
            agents[i % len(agents)],
            agents[(i * 3 + 2) % len(agents)],
            i % 2,
            20 if i % 3 else 40,
            mulligans[i % len(mulligans)],
        ))
    return specs


def train_ranker(df: pd.DataFrame, feature_cols: list[str]) -> tuple[dict[str, object], pd.DataFrame]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss, roc_auc_score

    train_mask = (df["game_index"].astype(int) % 5) != 0
    train = df[train_mask].copy()
    test = df[~train_mask].copy()
    X_train = train[feature_cols].astype(float).to_numpy()
    y_train = train["chosen"].astype(int).to_numpy()
    X_test = test[feature_cols].astype(float).to_numpy()
    y_test = test["chosen"].astype(int).to_numpy()
    model = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear", random_state=2020)
    model.fit(X_train, y_train)
    test_probs = model.predict_proba(X_test)[:, 1]
    test = test.assign(pred_prob=test_probs)
    grouped = test.groupby("decision_id", sort=False)
    correct = 0
    total = 0
    reciprocal = 0.0
    for _, g in grouped:
        total += 1
        ordered = g.sort_values("pred_prob", ascending=False).reset_index(drop=True)
        chosen_positions = ordered.index[ordered["chosen"].astype(int) == 1].tolist()
        if chosen_positions:
            pos = chosen_positions[0]
            reciprocal += 1.0 / (pos + 1)
            if pos == 0:
                correct += 1
    coefs = pd.DataFrame({"feature": feature_cols, "coef": model.coef_[0]}).assign(abs_coef=lambda x: x["coef"].abs()).sort_values("abs_coef", ascending=False)
    metrics: dict[str, object] = {
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_decisions": int(train["decision_id"].nunique()),
        "test_decisions": int(test["decision_id"].nunique()),
        "test_top1_accuracy": float(correct / total) if total else 0.0,
        "test_mean_reciprocal_rank": float(reciprocal / total) if total else 0.0,
        "test_log_loss": float(log_loss(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "test_roc_auc": float(roc_auc_score(y_test, test_probs)) if len(set(y_test.tolist())) > 1 else None,
        "random_slot_baseline_accuracy": float((1.0 / test.groupby("decision_id")["action_count"].first()).mean()) if total else 0.0,
    }
    return metrics, coefs


def main() -> None:
    DATA.mkdir(exist_ok=True)
    rows, collection = collect_action_imitation_rows(game_specs(), seed_base=2020000, max_decisions=320)
    dataset_path = DATA / f"{REV}_action_ranker_dataset.csv"
    pd.DataFrame(rows).to_csv(dataset_path, index=False)
    df = pd.DataFrame(rows)
    feature_cols = list(action_ranker_feature_names())
    try:
        metrics, coefs = train_ranker(df, feature_cols)
    except Exception as exc:
        metrics = {"train_failed": True, "error": repr(exc)}
        coefs = pd.DataFrame(columns=["feature", "coef", "abs_coef"])
    coefs.head(80).to_csv(DATA / f"{REV}_action_ranker_coefficients.csv", index=False)
    summary = {
        "revision": REV,
        "collection": collection.as_dict(),
        "feature_count": len(feature_cols),
        "feature_names": feature_cols,
        "ranker_metrics": metrics,
        "top_coefficients": coefs.head(20).to_dict(orient="records"),
    }
    (DATA / f"{REV}_action_ranker_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
