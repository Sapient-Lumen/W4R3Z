from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Dict, Iterable, Mapping, Sequence

import numpy as np

from .action_counterfactual import ActionCounterfactualGameSpec
from .action_hard_racing import _hard_snapshots, _race_selected_snapshots
from .action_hard_frame import HardFrameSnapshot


MARGIN_SCREEN_FEATURES: tuple[str, ...] = (
    "action_count",
    "branched_action_count",
    "branched_subset",
    "screen_unique_votes",
    "screen_vote_entropy_proxy",
    "profile_spread",
    "ranker_spread",
    "screen_score",
    "starting_life_40",
    "starting_player",
)


@dataclass(frozen=True)
class MarginScreenModel:
    """Tiny public-feature model for prioritizing branch-label situations.

    This model is not a gameplay policy.  It is a queueing aid for the offline
    label generator.  It predicts whether a public decision frame is likely to
    produce a decisive counterfactual label, using only public-safe features and
    historical audited branch labels.
    """

    revision: str
    feature_names: tuple[str, ...]
    mean: tuple[float, ...]
    scale: tuple[float, ...]
    coef: tuple[float, ...]
    intercept: float
    train_rows: int
    holdout_rows: int
    metrics: Mapping[str, float]
    source_files: tuple[str, ...]

    def feature_vector(self, row: Mapping[str, object]) -> np.ndarray:
        vals = np.array([_as_float(row.get(name, 0.0)) for name in self.feature_names], dtype=np.float64)
        mean = np.array(self.mean, dtype=np.float64)
        scale = np.array(self.scale, dtype=np.float64)
        return (vals - mean) / scale

    def predict_margin(self, row: Mapping[str, object]) -> float:
        x = self.feature_vector(row)
        coef = np.array(self.coef, dtype=np.float64)
        return float(self.intercept + float(x @ coef))

    def predict_queue_score(self, row: Mapping[str, object]) -> float:
        pred = max(0.0, min(1.0, self.predict_margin(row)))
        public_score = max(0.0, min(1.0, _as_float(row.get("screen_score", 0.0))))
        action_bonus = min(1.0, max(0.0, (_as_float(row.get("action_count", 0.0)) - 4.0) / 16.0))
        return float(0.58 * pred + 0.27 * public_score + 0.15 * action_bonus)

    def as_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["feature_names"] = list(self.feature_names)
        d["mean"] = list(self.mean)
        d["scale"] = list(self.scale)
        d["coef"] = list(self.coef)
        d["source_files"] = list(self.source_files)
        return d

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "MarginScreenModel":
        return cls(
            revision=str(data.get("revision", "unknown")),
            feature_names=tuple(str(x) for x in data.get("feature_names", MARGIN_SCREEN_FEATURES)),
            mean=tuple(float(x) for x in data.get("mean", [0.0] * len(MARGIN_SCREEN_FEATURES))),
            scale=tuple(float(x) for x in data.get("scale", [1.0] * len(MARGIN_SCREEN_FEATURES))),
            coef=tuple(float(x) for x in data.get("coef", [0.0] * len(MARGIN_SCREEN_FEATURES))),
            intercept=float(data.get("intercept", 0.0)),
            train_rows=int(data.get("train_rows", 0)),
            holdout_rows=int(data.get("holdout_rows", 0)),
            metrics={str(k): float(v) for k, v in dict(data.get("metrics", {})).items()},
            source_files=tuple(str(x) for x in data.get("source_files", ())),
        )


@dataclass(frozen=True)
class MarginScreenAuditSummary:
    revision: str
    source_situation_rows: int
    train_rows: int
    holdout_rows: int
    holdout_rmse: float
    holdout_mae: float
    holdout_top_quartile_decisive_rate: float
    holdout_baseline_decisive_rate: float
    holdout_top_quartile_mean_margin: float
    holdout_baseline_mean_margin: float
    selected_pool_size: int
    selected_situations: int
    margin_selected_mean_predicted_margin: float
    margin_selected_mean_queue_score: float
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    decisive_situations: int
    decisive_per_100_rollouts: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _as_float(x: object) -> float:
    try:
        if x is None:
            return 0.0
        if isinstance(x, str) and not x.strip():
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def _first_per_situation(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    out: list[dict[str, object]] = []
    for row in rows:
        sid = str(row.get("situation_id", ""))
        if not sid or sid in seen:
            continue
        if "situation_best_margin" not in row:
            continue
        seen.add(sid)
        out.append(dict(row))
    return out


def load_historical_margin_rows(paths: Sequence[Path | str]) -> list[dict[str, object]]:
    all_rows: list[dict[str, object]] = []
    for path_like in paths:
        path = Path(path_like)
        if not path.exists():
            continue
        try:
            with path.open(newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            for row in _first_per_situation(rows):
                # Fill missing public-screen features so older datasets can help
                # without pretending they had modern screen telemetry.
                row.setdefault("branched_action_count", row.get("action_count", 0))
                row.setdefault("branched_subset", 0)
                row.setdefault("screen_unique_votes", 0)
                row.setdefault("screen_vote_entropy_proxy", 0.0)
                row.setdefault("profile_spread", 0.0)
                row.setdefault("ranker_spread", 0.0)
                row.setdefault("screen_score", 0.0)
                row.setdefault("starting_life_40", 1 if int(_as_float(row.get("starting_life", 20))) == 40 else 0)
                all_rows.append(row)
        except Exception:
            continue
    return all_rows


def _row_to_features(row: Mapping[str, object]) -> list[float]:
    d = dict(row)
    d["starting_life_40"] = 1.0 if int(_as_float(d.get("starting_life", 20))) == 40 else _as_float(d.get("starting_life_40", 0))
    return [_as_float(d.get(name, 0.0)) for name in MARGIN_SCREEN_FEATURES]


def train_margin_screen_model(
    rows: Sequence[Mapping[str, object]],
    *,
    revision: str = "rev0044",
    source_files: Sequence[str] = (),
    seed: int = 44044,
    holdout_fraction: float = 0.30,
    l2: float = 0.15,
) -> tuple[MarginScreenModel, list[dict[str, object]]]:
    if len(rows) < 8:
        raise ValueError(f"Need at least 8 historical margin rows, got {len(rows)}")
    rng = Random(int(seed))
    idxs = list(range(len(rows)))
    rng.shuffle(idxs)
    holdout_n = max(2, min(len(rows) // 2, int(round(len(rows) * float(holdout_fraction)))))
    holdout_idx = set(idxs[:holdout_n])
    train = [rows[i] for i in range(len(rows)) if i not in holdout_idx]
    holdout = [rows[i] for i in range(len(rows)) if i in holdout_idx]

    X = np.array([_row_to_features(r) for r in train], dtype=np.float64)
    y = np.array([_as_float(r.get("situation_best_margin", 0.0)) for r in train], dtype=np.float64)
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale < 1e-9] = 1.0
    Xs = (X - mean) / scale
    Xa = np.column_stack([np.ones(len(Xs)), Xs])
    penalty = np.eye(Xa.shape[1]) * float(l2)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(Xa.T @ Xa + penalty) @ Xa.T @ y

    model = MarginScreenModel(
        revision=str(revision),
        feature_names=MARGIN_SCREEN_FEATURES,
        mean=tuple(float(x) for x in mean),
        scale=tuple(float(x) for x in scale),
        coef=tuple(float(x) for x in beta[1:]),
        intercept=float(beta[0]),
        train_rows=len(train),
        holdout_rows=len(holdout),
        metrics={},
        source_files=tuple(str(x) for x in source_files),
    )
    eval_rows = evaluate_margin_screen_model(model, holdout)
    metrics = _metrics_from_eval(eval_rows)
    model = MarginScreenModel(
        revision=model.revision,
        feature_names=model.feature_names,
        mean=model.mean,
        scale=model.scale,
        coef=model.coef,
        intercept=model.intercept,
        train_rows=model.train_rows,
        holdout_rows=model.holdout_rows,
        metrics=metrics,
        source_files=model.source_files,
    )
    return model, eval_rows


def evaluate_margin_screen_model(model: MarginScreenModel, rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for r in rows:
        pred = model.predict_margin(r)
        actual = _as_float(r.get("situation_best_margin", 0.0))
        out.append({
            "situation_id": str(r.get("situation_id", "")),
            "source_revision": str(r.get("revision", "")),
            "actual_margin": float(actual),
            "predicted_margin": float(pred),
            "predicted_queue_score": float(model.predict_queue_score(r)),
            "decisive": 1 if actual > 1e-9 else 0,
            "label_confidence_proxy": _as_float(r.get("label_confidence_proxy", 0.0)),
            "action_count": int(_as_float(r.get("action_count", 0))),
        })
    return out


def _metrics_from_eval(eval_rows: Sequence[Mapping[str, object]]) -> dict[str, float]:
    if not eval_rows:
        return {}
    err = [float(r["predicted_margin"]) - float(r["actual_margin"]) for r in eval_rows]
    rmse = float((sum(e * e for e in err) / max(1, len(err))) ** 0.5)
    mae = float(sum(abs(e) for e in err) / max(1, len(err)))
    ordered = sorted(eval_rows, key=lambda r: float(r["predicted_queue_score"]), reverse=True)
    top_n = max(1, len(ordered) // 4)
    top = ordered[:top_n]
    decisive_rate = lambda xs: float(sum(int(r["decisive"]) for r in xs) / max(1, len(xs)))
    mean_margin = lambda xs: float(sum(float(r["actual_margin"]) for r in xs) / max(1, len(xs)))
    return {
        "rmse": rmse,
        "mae": mae,
        "top_quartile_decisive_rate": decisive_rate(top),
        "baseline_decisive_rate": decisive_rate(eval_rows),
        "top_quartile_mean_margin": mean_margin(top),
        "baseline_mean_margin": mean_margin(eval_rows),
    }


def save_margin_screen_model(model: MarginScreenModel, path: Path | str) -> None:
    Path(path).write_text(json.dumps(model.as_dict(), indent=2))


def load_margin_screen_model(path: Path | str) -> MarginScreenModel:
    return MarginScreenModel.from_dict(json.loads(Path(path).read_text()))


def snapshot_public_feature_row(snap: HardFrameSnapshot) -> dict[str, object]:
    return {
        "action_count": int(snap.action_count),
        "branched_action_count": int(snap.action_count),
        "branched_subset": 0,
        "screen_unique_votes": int(len(snap.unique_votes)),
        "screen_vote_entropy_proxy": float(snap.vote_entropy_proxy),
        "profile_spread": float(snap.profile_spread),
        "ranker_spread": float(snap.ranker_spread),
        "screen_score": float(snap.screen_score),
        "starting_life": int(snap.spec.starting_life),
        "starting_life_40": 1 if int(snap.spec.starting_life) == 40 else 0,
        "starting_player": int(snap.spec.starting_player),
    }


def select_margin_screen_snapshots(
    snapshots: Sequence[HardFrameSnapshot],
    model: MarginScreenModel,
    *,
    max_situations: int,
    max_per_behavior_game: int = 2,
) -> tuple[list[HardFrameSnapshot], list[dict[str, object]]]:
    scored: list[tuple[float, HardFrameSnapshot, dict[str, object]]] = []
    for snap in snapshots:
        row = snapshot_public_feature_row(snap)
        pred = float(model.predict_margin(row))
        q = float(model.predict_queue_score(row))
        score = float(q)
        d = dict(row)
        d.update({
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "predicted_margin": pred,
            "margin_queue_score": q,
            "base_screen_score": float(snap.screen_score),
            "screen_reason": snap.reason,
        })
        scored.append((score, snap, d))
    ordered = sorted(scored, key=lambda item: (-item[0], -item[1].action_count, -item[1].vote_entropy_proxy, item[1].situation_seed_id))
    selected: list[HardFrameSnapshot] = []
    rows: list[dict[str, object]] = []
    per_game: dict[str, int] = {}
    cap = max(1, int(max_per_behavior_game))
    for rank, (score, snap, d) in enumerate(ordered):
        gid = str(snap.spec.game_id)
        if per_game.get(gid, 0) >= cap:
            continue
        dd = dict(d)
        dd["margin_screen_rank"] = int(len(selected) + 1)
        dd["margin_screen_score"] = float(score)
        selected.append(snap)
        rows.append(dd)
        per_game[gid] = per_game.get(gid, 0) + 1
        if len(selected) >= int(max_situations):
            break
    if len(selected) < int(max_situations):
        seen = {s.situation_seed_id for s in selected}
        for score, snap, d in ordered:
            if snap.situation_seed_id in seen:
                continue
            dd = dict(d)
            dd["margin_screen_rank"] = int(len(selected) + 1)
            dd["margin_screen_score"] = float(score)
            selected.append(snap)
            rows.append(dd)
            if len(selected) >= int(max_situations):
                break
    return selected, rows


def collect_margin_screened_online_racing(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    model: MarginScreenModel,
    revision: str = "rev0044",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 2,
    max_behavior_frames: int = 220,
    candidate_pool_situations: int = 32,
    selected_situations: int = 10,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 5,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 44044,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 4,
    adaptive_stop_margin: float = 0.40,
    adaptive_target_confidence: float = 0.55,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], HardFrameOnlineRacingSummary]:
    from .action_hard_racing import HardFrameOnlineRacingSummary

    pool, _unused, stats = _hard_snapshots(
        specs,
        revision=revision,
        screen_agent_names=screen_agent_names,
        min_unique_screen_votes=min_unique_screen_votes,
        max_behavior_frames=max_behavior_frames,
        high_action_threshold=high_action_threshold,
        ranker_revision=ranker_revision,
        max_situations=int(candidate_pool_situations),
        max_per_behavior_game=max_per_behavior_game,
    )
    selected, margin_rows = select_margin_screen_snapshots(
        pool,
        model,
        max_situations=selected_situations,
        max_per_behavior_game=max_per_behavior_game,
    )
    selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, summary = _race_selected_snapshots(
        selected,
        stats,
        revision=revision,
        behavior_games=len(specs),
        high_action_threshold=high_action_threshold,
        max_actions_per_frame=max_actions_per_frame,
        branch_action_budget=branch_action_budget,
        branch_max_decisions=branch_max_decisions,
        budget_rng_seed=budget_rng_seed,
        ranker_revision=ranker_revision,
        base_rollouts_per_action=base_rollouts_per_action,
        max_extra_rollouts_per_situation=max_extra_rollouts_per_situation,
        adaptive_stop_margin=adaptive_stop_margin,
        adaptive_target_confidence=adaptive_target_confidence,
    )
    by_source = {str(r["source_candidate_id"]): r for r in margin_rows}
    for rows in (selected_rows, candidate_rows):
        for r in rows:
            mr = by_source.get(str(r.get("source_candidate_id", "")))
            if mr:
                r["margin_predicted_margin"] = float(mr.get("predicted_margin", 0.0))
                r["margin_screen_score"] = float(mr.get("margin_screen_score", 0.0))
                r["margin_screen_rank"] = int(mr.get("margin_screen_rank", 0))
    return margin_rows, selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, summary
