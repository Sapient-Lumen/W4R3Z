from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Mapping, Sequence

from .action_schema import Action
from .imitation import action_ranker_feature_names, context_feature_dict
from .action_features import action_feature_dict
from .decision import DecisionFrame, PublicDecisionAgent


@dataclass(frozen=True)
class LinearActionRankerModel:
    """Frozen linear policy over public DecisionFrame/action features.

    This is deliberately small and boring.  The model is not an RL policy yet;
    it is an auditable listwise action scorer trained from public-policy traces.
    It exists to test the plumbing between supervised action-ranking data and
    tournament/promotion gates before we spend budget on PPO/CFR-style methods.
    """

    model_id: str
    feature_names: tuple[str, ...]
    coefficients: tuple[float, ...]
    intercept: float = 0.0
    source_revision: str = "rev0021"
    training_summary: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if len(self.feature_names) != len(self.coefficients):
            raise ValueError(f"feature/coefficient length mismatch: {len(self.feature_names)} vs {len(self.coefficients)}")

    def as_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "feature_names": list(self.feature_names),
            "coefficients": list(self.coefficients),
            "intercept": float(self.intercept),
            "source_revision": self.source_revision,
            "training_summary": dict(self.training_summary or {}),
        }

    def score_features(self, features: Mapping[str, float]) -> float:
        total = float(self.intercept)
        for name, coef in zip(self.feature_names, self.coefficients):
            total += float(coef) * float(features.get(name, 0.0))
        return total

    def score_action(self, frame: DecisionFrame, action: Action) -> float:
        features: dict[str, float] = {}
        features.update(context_feature_dict(frame.observation))
        features.update(action_feature_dict(action, frame.observation))
        return self.score_features(features)


@dataclass
class LinearActionRankerAgent:
    """Public-safe agent wrapper for a frozen linear action-ranker model."""

    model: LinearActionRankerModel
    name: str = "linear_ranker_rev0021"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = [(self.model.score_action(frame, action), rng.random(), idx) for idx, action in enumerate(frame.legal_actions)]
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_ranker_model_path() -> Path:
    return project_root() / "data" / "rev0021_linear_ranker_model.json"


def save_linear_ranker_model(model: LinearActionRankerModel, path: str | Path) -> None:
    Path(path).write_text(json.dumps(model.as_dict(), indent=2, sort_keys=True), encoding="utf-8")


def load_linear_ranker_model(path: str | Path) -> LinearActionRankerModel:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return LinearActionRankerModel(
        model_id=str(payload.get("model_id", "linear_ranker")),
        feature_names=tuple(str(x) for x in payload["feature_names"]),
        coefficients=tuple(float(x) for x in payload["coefficients"]),
        intercept=float(payload.get("intercept", 0.0)),
        source_revision=str(payload.get("source_revision", "unknown")),
        training_summary=payload.get("training_summary", {}),
    )


def load_default_linear_ranker_agent() -> LinearActionRankerAgent:
    path = default_ranker_model_path()
    if not path.exists():
        raise FileNotFoundError(f"default linear ranker model is missing: {path}")
    return LinearActionRankerAgent(load_linear_ranker_model(path))


# --- rev0025: outcome-weighted linear public action ranker ----------------

def default_outcome_ranker_model_path() -> Path:
    return project_root() / "data" / "rev0025_outcome_ranker_model.json"


def load_default_outcome_ranker_agent() -> LinearActionRankerAgent:
    path = default_outcome_ranker_model_path()
    if not path.exists():
        raise FileNotFoundError(f"default outcome-weighted ranker model is missing: {path}")
    return LinearActionRankerAgent(load_linear_ranker_model(path), name="outcome_linear_ranker_rev0025")


def load_default_blended_outcome_ranker_agent(profile: str, *, profile_weight: float = 0.05) -> "BlendedLinearRankerAgent":
    path = default_outcome_ranker_model_path()
    if not path.exists():
        raise FileNotFoundError(f"default outcome-weighted ranker model is missing: {path}")
    normalized = profile.strip().lower().replace("-", "_")
    return BlendedLinearRankerAgent(
        model=load_linear_ranker_model(path),
        profile=normalized,
        profile_weight=float(profile_weight),
        name=f"outcome_ranker_blend_{normalized}_rev0025",
    )



# --- rev0033+: action-counterfactual linear public action rankers ---------

def counterfactual_ranker_model_path(revision: str = "rev0033") -> Path:
    """Return the JSON model path for an action-counterfactual ranker revision.

    rev0033 introduced the first branch-rollout action ranker.  rev0034+ reuse
    the same public feature/action contract, so the loader should not have to be
    copy-pasted every time a new counterfactual label budget is generated.
    """

    normalized = str(revision).strip().lower()
    if not normalized.startswith("rev"):
        normalized = "rev" + normalized
    return project_root() / "data" / f"{normalized}_counterfactual_action_ranker_model.json"


def default_counterfactual_ranker_model_path() -> Path:
    return counterfactual_ranker_model_path("rev0033")


def load_counterfactual_ranker_agent(revision: str = "rev0033", *, name: str | None = None) -> LinearActionRankerAgent:
    path = counterfactual_ranker_model_path(revision)
    if not path.exists():
        raise FileNotFoundError(f"counterfactual action ranker model is missing: {path}")
    normalized = str(revision).strip().lower()
    if not normalized.startswith("rev"):
        normalized = "rev" + normalized
    return LinearActionRankerAgent(
        load_linear_ranker_model(path),
        name=name or f"counterfactual_linear_ranker_{normalized}",
    )


def load_default_counterfactual_ranker_agent() -> LinearActionRankerAgent:
    return load_counterfactual_ranker_agent("rev0033", name="counterfactual_linear_ranker_rev0033")


def load_blended_counterfactual_ranker_agent(
    revision: str = "rev0033",
    profile: str = "threat_rush",
    *,
    profile_weight: float = 0.05,
    name: str | None = None,
) -> "BlendedLinearRankerAgent":
    path = counterfactual_ranker_model_path(revision)
    if not path.exists():
        raise FileNotFoundError(f"counterfactual action ranker model is missing: {path}")
    normalized_profile = profile.strip().lower().replace("-", "_")
    normalized_rev = str(revision).strip().lower()
    if not normalized_rev.startswith("rev"):
        normalized_rev = "rev" + normalized_rev
    return BlendedLinearRankerAgent(
        model=load_linear_ranker_model(path),
        profile=normalized_profile,
        profile_weight=float(profile_weight),
        name=name or f"counterfactual_ranker_blend_{normalized_profile}_{normalized_rev}",
    )



def train_linear_action_ranker_from_candidate_rows(
    candidate_rows: Sequence[Mapping[str, object]],
    *,
    model_id: str,
    source_revision: str,
    seed: int = 47047,
    train_fraction: float = 0.72,
    ridge_alpha: float = 0.75,
    target_column: str = "mean_actor_score",
    sample_weight_mode: str = "confidence_subset_vote",
) -> tuple[LinearActionRankerModel, dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    """Train a tiny JSON-backed linear public action ranker from branch labels.

    Several rev0033+ scripts used near-identical local Ridge-training blocks.
    rev0047 pulls the common part into the ranker module so future label
    collectors can differ in *how labels are generated* without copy-pasting the
    model/export path.  The function accepts already-public feature rows: it
    never touches GameState and never creates hidden-information features.

    Returns ``(model, metrics, coefficient_rows, prediction_rows)``.
    """

    if not candidate_rows:
        raise ValueError("no candidate rows supplied for action-ranker training")

    # Local imports keep importing this module cheap for normal gameplay agents.
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_squared_error, r2_score

    df = pd.DataFrame([dict(r) for r in candidate_rows]).replace([np.inf, -np.inf], np.nan)
    features = list(action_ranker_feature_names())
    missing = [name for name in features if name not in df.columns]
    for name in missing:
        df[name] = 0.0
    for name in features + [target_column, "label_confidence_proxy", "branched_subset", "branch_rollouts", "screen_unique_votes", "situation_best_margin", "is_best_action"]:
        if name in df.columns:
            df[name] = pd.to_numeric(df[name], errors="coerce").fillna(0.0)
    if target_column not in df.columns:
        raise ValueError(f"candidate rows are missing target column {target_column!r}")
    if "situation_id" not in df.columns:
        raise ValueError("candidate rows must include situation_id for groupwise splitting")

    situation_ids = sorted(df["situation_id"].astype(str).unique())
    if not situation_ids:
        raise ValueError("candidate rows contain no situations")
    rng = Random(int(seed))
    rng.shuffle(situation_ids)
    split = max(1, int(float(train_fraction) * len(situation_ids)))
    if split >= len(situation_ids) and len(situation_ids) > 1:
        split = len(situation_ids) - 1
    train_ids = set(situation_ids[:split])
    test_ids = set(situation_ids[split:] or situation_ids[:1])
    train = df[df["situation_id"].astype(str).isin(train_ids)].copy()
    test = df[df["situation_id"].astype(str).isin(test_ids)].copy()

    X_train = train[features].astype(float).to_numpy()
    y_train = train[target_column].astype(float).to_numpy()
    X_test = test[features].astype(float).to_numpy()
    y_test = test[target_column].astype(float).to_numpy()

    if sample_weight_mode == "none":
        sample_weight = None
        sample_weight_desc = "none"
    else:
        conf = train["label_confidence_proxy"].astype(float).to_numpy() if "label_confidence_proxy" in train.columns else np.zeros(len(train))
        subset_vals = train["branched_subset"].astype(float).to_numpy() if "branched_subset" in train.columns else np.zeros(len(train))
        subset_discount = np.where(subset_vals == 1, 0.84, 1.00)
        rollouts = np.maximum(1.0, train["branch_rollouts"].astype(float).to_numpy() if "branch_rollouts" in train.columns else np.ones(len(train)))
        rollout_bonus = np.minimum(1.25, 1.0 + 0.03 * np.maximum(0.0, rollouts - 1.0))
        vote_bonus = 1.0 + 0.06 * np.maximum(0.0, (train["screen_unique_votes"].astype(float).to_numpy() if "screen_unique_votes" in train.columns else np.ones(len(train))) - 1.0)
        decisive_bonus = np.where((train["situation_best_margin"].astype(float).to_numpy() if "situation_best_margin" in train.columns else np.zeros(len(train))) > 1e-9, 1.10, 0.90)
        sample_weight = (0.18 + conf) * subset_discount * rollout_bonus * vote_bonus * decisive_bonus
        sample_weight_desc = "(0.18 + label_confidence_proxy) * subset_discount_0.84 * rollout_bonus<=1.25 * vote_bonus * decisive_bonus"

    model_fit = Ridge(alpha=float(ridge_alpha), random_state=int(seed))
    model_fit.fit(X_train, y_train, sample_weight=sample_weight)
    pred = model_fit.predict(X_test) if len(test) else np.array([])

    pred_rows = test.copy()
    if len(test):
        pred_rows["prediction"] = pred
    else:
        pred_rows["prediction"] = []

    top1: list[float] = []
    decisive_top1: list[float] = []
    confident_top1: list[float] = []
    random_best: list[float] = []
    mrrs: list[float] = []
    for _sid, g0 in pred_rows.groupby("situation_id"):
        g = g0.sort_values("prediction", ascending=False).reset_index(drop=True)
        best_positions = [i for i, row in g.iterrows() if int(row.get("is_best_action", 0)) == 1]
        if not best_positions:
            continue
        hit = 1.0 if int(g.iloc[0].get("is_best_action", 0)) == 1 else 0.0
        top1.append(hit)
        random_best.append(float(sum(g.get("is_best_action", 0).astype(int))) / max(1, len(g)))
        mrrs.append(1.0 / float(min(best_positions) + 1))
        if float(g.iloc[0].get("situation_best_margin", 0.0)) > 1e-9:
            decisive_top1.append(hit)
        if float(g.iloc[0].get("label_confidence_proxy", 0.0)) >= 0.50:
            confident_top1.append(hit)

    metrics: dict[str, object] = {
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_situations": int(len(train_ids)),
        "test_situations": int(len(test_ids)),
        "target": str(target_column),
        "ridge_alpha": float(ridge_alpha),
        "sample_weight_mode": str(sample_weight_mode),
        "sample_weight": sample_weight_desc,
        "test_rmse": float(mean_squared_error(y_test, pred) ** 0.5) if len(test) else None,
        "test_r2": float(r2_score(y_test, pred)) if len(test) > 1 else None,
        "test_top1_best_action_accuracy": float(np.mean(top1)) if top1 else None,
        "test_top1_decisive_accuracy": float(np.mean(decisive_top1)) if decisive_top1 else None,
        "test_top1_confident_accuracy": float(np.mean(confident_top1)) if confident_top1 else None,
        "test_random_best_action_baseline": float(np.mean(random_best)) if random_best else None,
        "test_mrr": float(np.mean(mrrs)) if mrrs else None,
    }
    model = LinearActionRankerModel(
        model_id=str(model_id),
        feature_names=tuple(features),
        coefficients=tuple(float(x) for x in model_fit.coef_),
        intercept=float(model_fit.intercept_),
        source_revision=str(source_revision),
        training_summary=metrics,
    )
    coef_rows = [{"feature": f, "coefficient": float(c), "abs_coefficient": abs(float(c))} for f, c in zip(features, model_fit.coef_)]
    coef_rows.sort(key=lambda r: r["abs_coefficient"], reverse=True)
    return model, metrics, coef_rows, pred_rows.to_dict(orient="records")

def load_default_blended_counterfactual_ranker_agent(profile: str, *, profile_weight: float = 0.05) -> "BlendedLinearRankerAgent":
    return load_blended_counterfactual_ranker_agent(
        "rev0033",
        profile,
        profile_weight=profile_weight,
        name=f"counterfactual_ranker_blend_{profile.strip().lower().replace('-', '_')}_rev0033",
    )

def zero_linear_ranker_model(model_id: str = "zero_linear_ranker") -> LinearActionRankerModel:
    names = action_ranker_feature_names()
    return LinearActionRankerModel(model_id=model_id, feature_names=names, coefficients=tuple(0.0 for _ in names))

@dataclass
class BlendedLinearRankerAgent:
    """Public-safe ranker plus a tiny readable profile prior.

    The rev0021 ranker is an imitation model trained from weak public/code
    policies.  rev0022 adds deliberately small blend variants so we can test a
    question before heavier RL: does a learned action-ranker become more useful
    when combined with an interpretable style prior, or does the prior simply
    drown out the model?

    The profile scorer still receives only the public observation and the legal
    action.  It never sees GameState.
    """

    model: LinearActionRankerModel
    profile: str
    profile_weight: float = 0.08
    ranker_weight: float = 1.0
    name: str = "ranker_blend_rev0022"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        # Local import avoids a module-import cycle: public_agents imports this
        # module only from its factory path.
        from .public_agents import PublicProfileAgent

        prior = PublicProfileAgent(self.profile)
        scored = []
        for idx, action in enumerate(frame.legal_actions):
            ranker_score = self.model.score_action(frame, action)
            profile_score = prior.score_action(frame.observation, action)
            score = self.ranker_weight * ranker_score + self.profile_weight * profile_score
            scored.append((score, rng.random(), idx))
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]


def load_default_blended_ranker_agent(profile: str, *, profile_weight: float = 0.08) -> BlendedLinearRankerAgent:
    model = load_linear_ranker_model(default_ranker_model_path())
    normalized = profile.strip().lower().replace("-", "_")
    return BlendedLinearRankerAgent(
        model=model,
        profile=normalized,
        profile_weight=float(profile_weight),
        name=f"ranker_blend_{normalized}_rev0022",
    )


# --- rev0023: tiny non-linear public action-ranker ------------------------

@dataclass(frozen=True)
class MLPActionRankerModel:
    """Frozen one-hidden-layer MLP action scorer over public features.

    This is intentionally small and JSON-backed.  It is not a security boundary
    and not an RL policy; it is an auditable non-linear action ranker that keeps
    the same public DecisionFrame/action-feature contract as the rev0021 linear
    model.  The final output is a logit, which is sufficient for ranking legal
    actions within a frame.
    """

    model_id: str
    feature_names: tuple[str, ...]
    hidden_weights: tuple[tuple[float, ...], ...]  # feature x hidden
    hidden_bias: tuple[float, ...]
    output_weights: tuple[float, ...]              # hidden
    output_bias: float
    activation: str = "relu"
    source_revision: str = "rev0023"
    training_summary: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        hidden = len(self.hidden_bias)
        if len(self.output_weights) != hidden:
            raise ValueError("output weight length must equal hidden size")
        if len(self.hidden_weights) != len(self.feature_names):
            raise ValueError("hidden weight row count must equal feature count")
        for row in self.hidden_weights:
            if len(row) != hidden:
                raise ValueError("all hidden weight rows must equal hidden size")

    @property
    def hidden_size(self) -> int:
        return len(self.hidden_bias)

    def as_dict(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "feature_names": list(self.feature_names),
            "hidden_weights": [list(row) for row in self.hidden_weights],
            "hidden_bias": list(self.hidden_bias),
            "output_weights": list(self.output_weights),
            "output_bias": float(self.output_bias),
            "activation": self.activation,
            "source_revision": self.source_revision,
            "training_summary": dict(self.training_summary or {}),
        }

    def _activate(self, x: float) -> float:
        if self.activation == "relu":
            return x if x > 0.0 else 0.0
        if self.activation == "tanh":
            import math
            return math.tanh(x)
        if self.activation == "identity":
            return x
        raise ValueError(f"unsupported MLP activation {self.activation!r}")

    def score_features(self, features: Mapping[str, float]) -> float:
        hidden_vals = [float(b) for b in self.hidden_bias]
        for i, name in enumerate(self.feature_names):
            x = float(features.get(name, 0.0))
            if x == 0.0:
                continue
            row = self.hidden_weights[i]
            for h, w in enumerate(row):
                hidden_vals[h] += x * float(w)
        hidden_vals = [self._activate(x) for x in hidden_vals]
        total = float(self.output_bias)
        for h, w in enumerate(self.output_weights):
            total += hidden_vals[h] * float(w)
        return total

    def score_action(self, frame: DecisionFrame, action: Action) -> float:
        features: dict[str, float] = {}
        features.update(context_feature_dict(frame.observation))
        features.update(action_feature_dict(action, frame.observation))
        return self.score_features(features)


@dataclass
class MLPActionRankerAgent:
    """Public-safe agent wrapper for a frozen JSON MLP ranker."""

    model: MLPActionRankerModel
    name: str = "mlp_ranker_rev0023"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        scored = [(self.model.score_action(frame, action), rng.random(), idx) for idx, action in enumerate(frame.legal_actions)]
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]


@dataclass
class BlendedMLPRankerAgent:
    """MLP ranker plus a tiny readable public-profile prior."""

    model: MLPActionRankerModel
    profile: str
    profile_weight: float = 0.06
    ranker_weight: float = 1.0
    name: str = "mlp_ranker_blend_rev0023"

    def choose_action_index(self, frame: DecisionFrame, rng: Random) -> int:
        if frame.action_count <= 0:
            raise ValueError("no legal actions")
        from .public_agents import PublicProfileAgent

        prior = PublicProfileAgent(self.profile)
        scored = []
        for idx, action in enumerate(frame.legal_actions):
            score = self.ranker_weight * self.model.score_action(frame, action)
            score += self.profile_weight * prior.score_action(frame.observation, action)
            scored.append((score, rng.random(), idx))
        scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
        return scored[0][2]


def default_mlp_ranker_model_path() -> Path:
    return project_root() / "data" / "rev0023_mlp_ranker_model.json"


def save_mlp_ranker_model(model: MLPActionRankerModel, path: str | Path) -> None:
    Path(path).write_text(json.dumps(model.as_dict(), indent=2, sort_keys=True), encoding="utf-8")


def load_mlp_ranker_model(path: str | Path) -> MLPActionRankerModel:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return MLPActionRankerModel(
        model_id=str(payload.get("model_id", "mlp_ranker")),
        feature_names=tuple(str(x) for x in payload["feature_names"]),
        hidden_weights=tuple(tuple(float(v) for v in row) for row in payload["hidden_weights"]),
        hidden_bias=tuple(float(x) for x in payload["hidden_bias"]),
        output_weights=tuple(float(x) for x in payload["output_weights"]),
        output_bias=float(payload["output_bias"]),
        activation=str(payload.get("activation", "relu")),
        source_revision=str(payload.get("source_revision", "unknown")),
        training_summary=payload.get("training_summary", {}),
    )


def load_default_mlp_ranker_agent() -> MLPActionRankerAgent:
    path = default_mlp_ranker_model_path()
    if not path.exists():
        raise FileNotFoundError(f"default MLP ranker model is missing: {path}")
    return MLPActionRankerAgent(load_mlp_ranker_model(path))


def load_default_blended_mlp_ranker_agent(profile: str, *, profile_weight: float = 0.06) -> BlendedMLPRankerAgent:
    model = load_mlp_ranker_model(default_mlp_ranker_model_path())
    normalized = profile.strip().lower().replace("-", "_")
    return BlendedMLPRankerAgent(
        model=model,
        profile=normalized,
        profile_weight=float(profile_weight),
        name=f"mlp_ranker_blend_{normalized}_rev0023",
    )
