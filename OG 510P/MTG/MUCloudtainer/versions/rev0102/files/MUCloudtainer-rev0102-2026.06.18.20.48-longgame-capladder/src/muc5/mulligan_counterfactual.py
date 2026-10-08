from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from .action_schema import Action
from .cards import CARD_ORDER
from .mulligan import MULLIGAN_KEEP, MULLIGAN_TAKE, MulliganAgent, MulliganObservation
from .mulligan_ranker import (
    OUTCOME_MODEL_NAME,
    LinearMulliganRankerAgent,
    load_mulligan_ranker_model,
    make_training_observation,
    model_path_for_name,
    mulligan_ranker_feature_names,
    mulligan_ranker_feature_vector,
)

COUNTERFACTUAL_MODEL_NAME = "mulligan_counterfactual_ranker_rev0029"
COUNTERFACTUAL_MODEL_FILENAME = "rev0029_counterfactual_mulligan_model.json"
REPEATED_COUNTERFACTUAL_MODEL_NAME = "mulligan_repeated_counterfactual_ranker_rev0030"
REPEATED_COUNTERFACTUAL_MODEL_FILENAME = "rev0030_repeated_counterfactual_mulligan_model.json"


def counterfactual_model_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / COUNTERFACTUAL_MODEL_FILENAME


def repeated_counterfactual_model_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / REPEATED_COUNTERFACTUAL_MODEL_FILENAME


@dataclass(frozen=True)
class CounterfactualMulliganModel:
    """Linear first-look value model trained from keep-vs-mulligan branches.

    The target is ``mulligan_score - keep_score`` for the same first seven-card
    look.  Positive predictions mean the model believes taking the first
    mulligan is better; negative predictions mean keeping is better.  The model
    is intentionally first-look only.  Subsequent keep/take decisions and bottom
    choices are delegated to a normal mulligan agent.
    """

    model_id: str
    feature_names: Tuple[str, ...]
    delta_weights: Tuple[float, ...]
    delta_intercept: float
    source_revision: str
    fallback_mulligan: str
    training_summary: Mapping[str, object]

    def predict_mulligan_minus_keep(self, obs: MulliganObservation) -> float:
        xs = mulligan_ranker_feature_vector(obs, None, self.feature_names)
        return float(self.delta_intercept + sum(w * x for w, x in zip(self.delta_weights, xs)))

    def to_json(self) -> Dict[str, object]:
        return {
            "schema": "muc5.counterfactual_mulligan.v1",
            "model_id": self.model_id,
            "feature_names": list(self.feature_names),
            "delta_weights": list(self.delta_weights),
            "delta_intercept": float(self.delta_intercept),
            "source_revision": self.source_revision,
            "fallback_mulligan": self.fallback_mulligan,
            "training_summary": dict(self.training_summary),
        }

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> "CounterfactualMulliganModel":
        if payload.get("schema") != "muc5.counterfactual_mulligan.v1":
            raise ValueError(f"unexpected counterfactual mulligan schema {payload.get('schema')!r}")
        feature_names = tuple(str(x) for x in payload["feature_names"])  # type: ignore[index]
        delta_weights = tuple(float(x) for x in payload["delta_weights"])  # type: ignore[index]
        if len(feature_names) != len(delta_weights):
            raise ValueError("counterfactual mulligan feature/weight length mismatch")
        return cls(
            model_id=str(payload["model_id"]),
            feature_names=feature_names,
            delta_weights=delta_weights,
            delta_intercept=float(payload["delta_intercept"]),
            source_revision=str(payload.get("source_revision", "unknown")),
            fallback_mulligan=str(payload.get("fallback_mulligan", OUTCOME_MODEL_NAME)),
            training_summary=payload.get("training_summary", {}),  # type: ignore[arg-type]
        )


def save_counterfactual_mulligan_model(model: CounterfactualMulliganModel, path: str | Path | None = None) -> None:
    p = Path(path) if path is not None else counterfactual_model_path()
    p.write_text(json.dumps(model.to_json(), indent=2, sort_keys=True), encoding="utf-8")


def load_counterfactual_mulligan_model(path: str | Path | None = None) -> CounterfactualMulliganModel:
    p = Path(path) if path is not None else counterfactual_model_path()
    return CounterfactualMulliganModel.from_json(json.loads(p.read_text(encoding="utf-8")))


@dataclass
class CounterfactualFirstLookMulliganAgent:
    """Use paired branch value only for the first keep/take decision.

    Later London-mulligan decisions are delegated to ``fallback`` so this model
    does not pretend to have learned bottom-card choice values from first-look
    branch data.
    """

    model: CounterfactualMulliganModel
    fallback: MulliganAgent
    name: str = COUNTERFACTUAL_MODEL_NAME
    threshold: float = 0.0

    def choose_mulligan_action(self, obs: MulliganObservation, legal: Sequence[Action], rng: Random) -> Action:
        if obs.stage == "keep_or_mulligan" and int(obs.mulligans_taken) == 0:
            if MULLIGAN_TAKE not in legal:
                return MULLIGAN_KEEP
            delta = self.model.predict_mulligan_minus_keep(obs)
            return MULLIGAN_TAKE if delta > self.threshold else MULLIGAN_KEEP
        return self.fallback.choose_mulligan_action(obs, legal, rng)


def load_counterfactual_mulligan_agent(path: str | Path | None = None, *, name: str = COUNTERFACTUAL_MODEL_NAME) -> CounterfactualFirstLookMulliganAgent:
    model = load_counterfactual_mulligan_model(path)
    # Avoid importing the factory here; use the stable rev0027 model directly to
    # keep this module acyclic and make the delegation explicit.
    fallback_model = load_mulligan_ranker_model(model_path_for_name(model.fallback_mulligan))
    fallback = LinearMulliganRankerAgent(fallback_model, name=model.fallback_mulligan)
    return CounterfactualFirstLookMulliganAgent(model=model, fallback=fallback, name=name)


def load_repeated_counterfactual_mulligan_agent(path: str | Path | None = None) -> CounterfactualFirstLookMulliganAgent:
    return load_counterfactual_mulligan_agent(path or repeated_counterfactual_model_path(), name=REPEATED_COUNTERFACTUAL_MODEL_NAME)


def _counts_from_row(row: Mapping[str, object], prefix: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for card in CARD_ORDER:
        value = int(float(row.get(f"{prefix}_{card}", 0) or 0))
        if value > 0:
            out[card] = value
    return out


def counterfactual_training_rows_from_pairs(
    pair_rows: Iterable[Mapping[str, object]],
    deck_counts_by_name: Mapping[str, Mapping[str, int]],
) -> list[dict[str, object]]:
    """Turn rev0028 paired branch rows into first-look regression examples."""

    features = list(mulligan_ranker_feature_names())
    out: list[dict[str, object]] = []
    for idx, row in enumerate(pair_rows):
        deck_name = str(row["deck0"])
        deck_counts = {card: int(deck_counts_by_name[deck_name].get(card, 0) or 0) for card in CARD_ORDER}
        hand = _counts_from_row(row, "initial_hand")
        life = int(row.get("starting_life", 20) or 20)
        obs = make_training_observation(
            player=0,
            stage="keep_or_mulligan",
            hand=hand,
            deck_counts=deck_counts,
            starting_life=life,
            mulligans_taken=0,
        )
        fd = dict(zip(features, mulligan_ranker_feature_vector(obs)))
        keep_score = float(row.get("keep_score", 0.5) or 0.5)
        mull_score = float(row.get("mulligan_score", 0.5) or 0.5)
        delta = mull_score - keep_score
        out.append({
            "example_id": idx,
            "pair_id": str(row.get("pair_id", idx)),
            "deck0": deck_name,
            "starting_life": life,
            "starting_player": int(row.get("starting_player", 0) or 0),
            "keep_score": keep_score,
            "mulligan_score": mull_score,
            "mulligan_minus_keep": delta,
            "better_branch": "mulligan" if delta > 0 else ("keep" if delta < 0 else "tie"),
            "non_tie": 1 if abs(delta) > 1e-12 else 0,
            # Larger absolute deltas should matter more; ties are still retained
            # with tiny weight so feature summaries remain complete.
            "sample_weight": max(0.05, abs(delta)) if abs(delta) > 1e-12 else 0.05,
            **fd,
        })
    return out


def train_counterfactual_mulligan_model(training_rows: Sequence[Mapping[str, object]]) -> tuple[CounterfactualMulliganModel, dict[str, object]]:
    """Fit a tiny ridge model to paired keep-vs-mulligan deltas."""

    if len(training_rows) < 8:
        raise ValueError("need at least 8 counterfactual rows")
    import numpy as np
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    features = list(mulligan_ranker_feature_names())
    X = np.asarray([[float(r.get(f, 0.0) or 0.0) for f in features] for r in training_rows], dtype=float)
    y = np.asarray([float(r.get("mulligan_minus_keep", 0.0) or 0.0) for r in training_rows], dtype=float)
    w = np.asarray([float(r.get("sample_weight", 1.0) or 1.0) for r in training_rows], dtype=float)
    idx = np.arange(len(training_rows))
    test_mask = (idx % 4) == 0
    train_mask = ~test_mask
    if len(set(np.sign(y[train_mask]))) < 2 and np.any(y[train_mask] == 0):
        pass
    model = Ridge(alpha=1.35, fit_intercept=True, random_state=29029)
    model.fit(X[train_mask], y[train_mask], sample_weight=w[train_mask])
    pred = model.predict(X)
    test_pred = pred[test_mask]
    test_y = y[test_mask]
    nontie = np.abs(test_y) > 1e-12
    if np.any(nontie):
        sign_acc = float(np.mean(np.sign(test_pred[nontie]) == np.sign(test_y[nontie])))
    else:
        sign_acc = float("nan")
    # Conservative decision accuracy: choosing KEEP on predicted delta <= 0.
    decision_correct = np.where(np.abs(test_y) <= 1e-12, 1.0, (np.sign(test_pred) == np.sign(test_y)).astype(float))
    metrics: dict[str, object] = {
        "rows": int(len(training_rows)),
        "train_rows": int(train_mask.sum()),
        "test_rows": int(test_mask.sum()),
        "feature_count": int(len(features)),
        "tie_rows": int(np.sum(np.abs(y) <= 1e-12)),
        "keep_better_rows": int(np.sum(y < 0)),
        "mulligan_better_rows": int(np.sum(y > 0)),
        "mean_delta": float(np.mean(y)),
        "mean_abs_delta": float(np.mean(np.abs(y))),
        "test_mae": float(mean_absolute_error(test_y, test_pred)),
        "test_rmse": float(math.sqrt(mean_squared_error(test_y, test_pred))),
        "test_r2": float(r2_score(test_y, test_pred)) if len(test_y) > 1 else float("nan"),
        "test_non_tie_sign_accuracy": sign_acc,
        "test_decision_accuracy_ties_count_as_correct": float(np.mean(decision_correct)) if len(decision_correct) else 0.0,
        "label_source": "same_opening_hand_keep_vs_mulligan_branch_delta",
        "fallback_mulligan": OUTCOME_MODEL_NAME,
        "model_note": "first-look keep/take value only; bottom and later mulligans delegate to rev0027 outcome ranker",
    }
    out_model = CounterfactualMulliganModel(
        model_id="ridge_firstlook_counterfactual_mulligan_rev0029",
        feature_names=tuple(features),
        delta_weights=tuple(float(x) for x in model.coef_.ravel()),
        delta_intercept=float(model.intercept_),
        source_revision="rev0029",
        fallback_mulligan=OUTCOME_MODEL_NAME,
        training_summary=metrics,
    )
    return out_model, metrics
