from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Dict, Iterable, Mapping, Sequence

import numpy as np

from .action_counterfactual import ActionCounterfactualGameSpec
from .action_hard_frame import HardFrameSnapshot
from .action_hard_racing import _hard_snapshots, _race_selected_snapshots
from .action_margin_compare import _union_snapshots, select_hard_screen_snapshots
from .action_margin_screen import MarginScreenModel, select_margin_screen_snapshots, snapshot_public_feature_row


YIELD_SCREEN_FEATURES: tuple[str, ...] = (
    "action_count",
    "screen_unique_votes",
    "screen_vote_entropy_proxy",
    "profile_spread",
    "ranker_spread",
    "screen_score",
    "starting_life_40",
    "starting_player",
)


def _as_float(x: object) -> float:
    try:
        if x is None:
            return 0.0
        if isinstance(x, str) and not x.strip():
            return 0.0
        return float(x)
    except Exception:
        return 0.0


def _mean(xs: Sequence[float | int]) -> float:
    return float(sum(float(x) for x in xs) / max(1, len(xs)))


@dataclass(frozen=True)
class YieldScreenModel:
    """Tiny public-feature model for prioritizing high-yield branch labels.

    The target is not raw branch margin.  It is decisive labels per rollout, so
    a frame with one decisive label in a small branch budget is preferred over a
    visually interesting frame that consumes many rollouts and ties.  This is a
    queueing model for offline label generation, not a gameplay policy.
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

    def predict_yield_per_100(self, row: Mapping[str, object]) -> float:
        x = self.feature_vector(row)
        coef = np.array(self.coef, dtype=np.float64)
        return float(self.intercept + float(x @ coef))

    def predict_queue_score(self, row: Mapping[str, object]) -> float:
        # Most smoke historical yields are between 0 and 5 decisive labels per
        # 100 rollouts.  Normalize gently but keep public-hardness features as a
        # backstop so a noisy linear prediction cannot select only tiny menus.
        pred_norm = max(0.0, min(1.0, self.predict_yield_per_100(row) / 5.0))
        public_score = max(0.0, min(1.0, _as_float(row.get("screen_score", 0.0))))
        vote = max(0.0, min(1.0, _as_float(row.get("screen_vote_entropy_proxy", 0.0))))
        action_bonus = min(1.0, max(0.0, (_as_float(row.get("action_count", 0.0)) - 4.0) / 16.0))
        return float(0.58 * pred_norm + 0.22 * public_score + 0.12 * vote + 0.08 * action_bonus)

    def as_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["feature_names"] = list(self.feature_names)
        d["mean"] = list(self.mean)
        d["scale"] = list(self.scale)
        d["coef"] = list(self.coef)
        d["source_files"] = list(self.source_files)
        return d

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "YieldScreenModel":
        return cls(
            revision=str(data.get("revision", "unknown")),
            feature_names=tuple(str(x) for x in data.get("feature_names", YIELD_SCREEN_FEATURES)),
            mean=tuple(float(x) for x in data.get("mean", [0.0] * len(YIELD_SCREEN_FEATURES))),
            scale=tuple(float(x) for x in data.get("scale", [1.0] * len(YIELD_SCREEN_FEATURES))),
            coef=tuple(float(x) for x in data.get("coef", [0.0] * len(YIELD_SCREEN_FEATURES))),
            intercept=float(data.get("intercept", 0.0)),
            train_rows=int(data.get("train_rows", 0)),
            holdout_rows=int(data.get("holdout_rows", 0)),
            metrics={str(k): float(v) for k, v in dict(data.get("metrics", {})).items()},
            source_files=tuple(str(x) for x in data.get("source_files", ())),
        )


@dataclass(frozen=True)
class QueueMethodStats:
    method: str
    selected_situations: int
    branched_situations: int
    decisive_situations: int
    branch_rollouts: int
    decisive_per_100_rollouts: float
    mean_situation_best_margin: float
    mean_label_confidence_proxy: float
    mean_action_count: float
    mean_queue_score: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class YieldQueueComparisonSummary:
    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    candidate_frames_seen: int
    pool_rows: int
    hard_selected: int
    margin_selected: int
    yield_selected: int
    union_selected: int
    overlap_all_three: int
    branch_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    hard_stats: Mapping[str, object]
    margin_stats: Mapping[str, object]
    yield_stats: Mapping[str, object]
    yield_minus_hard_decisive_per_100: float
    yield_minus_margin_decisive_per_100: float
    yield_unique_decisive: int
    hard_unique_decisive: int
    margin_unique_decisive: int
    yield_model_revision: str
    margin_model_revision: str
    tool_status: Mapping[str, object]
    mismatch_examples: tuple[dict[str, object], ...]
    skipped_examples: tuple[dict[str, object], ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _aggregate_candidate_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    by_sid: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        sid = str(row.get("situation_id", ""))
        if not sid or "situation_best_margin" not in row:
            continue
        by_sid.setdefault(sid, []).append(row)
    out: list[dict[str, object]] = []
    for sid, group in by_sid.items():
        first = dict(group[0])
        total_rollouts = int(sum(int(_as_float(r.get("branch_rollouts", 0))) for r in group))
        margin = float(_as_float(first.get("situation_best_margin", 0.0)))
        decisive = 1 if margin > 1e-9 else 0
        first.setdefault("screen_unique_votes", first.get("screen_unique_votes", 0))
        first.setdefault("screen_vote_entropy_proxy", first.get("screen_vote_entropy_proxy", 0.0))
        first.setdefault("profile_spread", first.get("profile_spread", 0.0))
        first.setdefault("ranker_spread", first.get("ranker_spread", 0.0))
        first.setdefault("screen_score", first.get("screen_score", 0.0))
        first.setdefault("starting_life_40", 1 if int(_as_float(first.get("starting_life", 20))) == 40 else 0)
        first["situation_id"] = sid
        first["candidate_action_rows"] = int(len(group))
        first["total_branch_rollouts"] = int(total_rollouts)
        first["decisive"] = int(decisive)
        first["label_yield_per_100_rollouts"] = float(100.0 * decisive / max(1, total_rollouts))
        out.append(first)
    return out


def load_historical_yield_rows(paths: Sequence[Path | str]) -> list[dict[str, object]]:
    all_rows: list[dict[str, object]] = []
    for path_like in paths:
        path = Path(path_like)
        if not path.exists():
            continue
        try:
            with path.open(newline="") as f:
                rows = list(csv.DictReader(f))
            for row in _aggregate_candidate_rows(rows):
                row["source_file"] = path.name
                all_rows.append(row)
        except Exception:
            continue
    return all_rows


def _row_to_features(row: Mapping[str, object]) -> list[float]:
    d = dict(row)
    d["starting_life_40"] = 1.0 if int(_as_float(d.get("starting_life", 20))) == 40 else _as_float(d.get("starting_life_40", 0))
    return [_as_float(d.get(name, 0.0)) for name in YIELD_SCREEN_FEATURES]


def train_yield_screen_model(
    rows: Sequence[Mapping[str, object]],
    *,
    revision: str = "rev0046",
    source_files: Sequence[str] = (),
    seed: int = 46046,
    holdout_fraction: float = 0.30,
    l2: float = 0.35,
) -> tuple[YieldScreenModel, list[dict[str, object]]]:
    if len(rows) < 8:
        raise ValueError(f"Need at least 8 historical yield rows, got {len(rows)}")
    rng = Random(int(seed))
    idxs = list(range(len(rows)))
    rng.shuffle(idxs)
    holdout_n = max(2, min(len(rows) // 2, int(round(len(rows) * float(holdout_fraction)))))
    holdout_idx = set(idxs[:holdout_n])
    train = [rows[i] for i in range(len(rows)) if i not in holdout_idx]
    holdout = [rows[i] for i in range(len(rows)) if i in holdout_idx]

    X = np.array([_row_to_features(r) for r in train], dtype=np.float64)
    y = np.array([_as_float(r.get("label_yield_per_100_rollouts", 0.0)) for r in train], dtype=np.float64)
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale < 1e-9] = 1.0
    Xs = (X - mean) / scale
    Xa = np.column_stack([np.ones(len(Xs)), Xs])
    penalty = np.eye(Xa.shape[1]) * float(l2)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(Xa.T @ Xa + penalty) @ Xa.T @ y
    model0 = YieldScreenModel(
        revision=revision,
        feature_names=YIELD_SCREEN_FEATURES,
        mean=tuple(float(x) for x in mean),
        scale=tuple(float(x) for x in scale),
        coef=tuple(float(x) for x in beta[1:]),
        intercept=float(beta[0]),
        train_rows=len(train),
        holdout_rows=len(holdout),
        metrics={},
        source_files=tuple(str(x) for x in source_files),
    )
    eval_rows = evaluate_yield_screen_model(model0, holdout)
    metrics = _metrics_from_eval(eval_rows)
    model = YieldScreenModel(
        revision=model0.revision,
        feature_names=model0.feature_names,
        mean=model0.mean,
        scale=model0.scale,
        coef=model0.coef,
        intercept=model0.intercept,
        train_rows=model0.train_rows,
        holdout_rows=model0.holdout_rows,
        metrics=metrics,
        source_files=model0.source_files,
    )
    return model, eval_rows


def evaluate_yield_screen_model(model: YieldScreenModel, rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        actual = float(_as_float(row.get("label_yield_per_100_rollouts", 0.0)))
        out.append({
            "situation_id": str(row.get("situation_id", "")),
            "source_file": str(row.get("source_file", "")),
            "actual_yield_per_100": actual,
            "predicted_yield_per_100": float(model.predict_yield_per_100(row)),
            "predicted_queue_score": float(model.predict_queue_score(row)),
            "decisive": int(_as_float(row.get("decisive", 0)) > 0),
            "total_branch_rollouts": int(_as_float(row.get("total_branch_rollouts", 0))),
            "situation_best_margin": float(_as_float(row.get("situation_best_margin", 0.0))),
            "action_count": int(_as_float(row.get("action_count", 0))),
        })
    return out


def _metrics_from_eval(rows: Sequence[Mapping[str, object]]) -> dict[str, float]:
    if not rows:
        return {}
    err = [float(r["predicted_yield_per_100"]) - float(r["actual_yield_per_100"]) for r in rows]
    rmse = float((sum(e * e for e in err) / max(1, len(err))) ** 0.5)
    mae = float(sum(abs(e) for e in err) / max(1, len(err)))
    ordered = sorted(rows, key=lambda r: float(r["predicted_queue_score"]), reverse=True)
    top_n = max(1, len(ordered) // 4)
    top = ordered[:top_n]
    decisive_rate = lambda xs: float(sum(int(r["decisive"]) for r in xs) / max(1, len(xs)))
    yield_mean = lambda xs: float(sum(float(r["actual_yield_per_100"]) for r in xs) / max(1, len(xs)))
    return {
        "rmse": rmse,
        "mae": mae,
        "top_quartile_decisive_rate": decisive_rate(top),
        "baseline_decisive_rate": decisive_rate(rows),
        "top_quartile_yield_per_100": yield_mean(top),
        "baseline_yield_per_100": yield_mean(rows),
    }


def save_yield_screen_model(model: YieldScreenModel, path: Path | str) -> None:
    Path(path).write_text(json.dumps(model.as_dict(), indent=2))


def load_yield_screen_model(path: Path | str) -> YieldScreenModel:
    return YieldScreenModel.from_dict(json.loads(Path(path).read_text()))


def select_yield_screen_snapshots(
    snapshots: Sequence[HardFrameSnapshot],
    model: YieldScreenModel,
    *,
    max_situations: int,
    max_per_behavior_game: int = 2,
) -> tuple[list[HardFrameSnapshot], list[dict[str, object]]]:
    scored: list[tuple[float, HardFrameSnapshot, dict[str, object]]] = []
    for snap in snapshots:
        row = snapshot_public_feature_row(snap)
        pred = float(model.predict_yield_per_100(row))
        q = float(model.predict_queue_score(row))
        d = dict(row)
        d.update({
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "predicted_yield_per_100": pred,
            "yield_queue_score": q,
            "base_screen_score": float(snap.screen_score),
            "screen_reason": snap.reason,
        })
        scored.append((q, snap, d))
    ordered = sorted(scored, key=lambda item: (-item[0], -item[1].action_count, -item[1].vote_entropy_proxy, item[1].situation_seed_id))
    selected: list[HardFrameSnapshot] = []
    rows: list[dict[str, object]] = []
    per_game: dict[str, int] = {}
    cap = max(1, int(max_per_behavior_game))
    for score, snap, d in ordered:
        gid = str(snap.spec.game_id)
        if per_game.get(gid, 0) >= cap:
            continue
        dd = dict(d)
        dd["yield_screen_rank"] = int(len(selected) + 1)
        dd["yield_screen_score"] = float(score)
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
            dd["yield_screen_rank"] = int(len(selected) + 1)
            dd["yield_screen_score"] = float(score)
            selected.append(snap)
            rows.append(dd)
            if len(selected) >= int(max_situations):
                break
    return selected, rows


def _pool_rows(
    pool: Sequence[HardFrameSnapshot],
    hard_rows: Sequence[Mapping[str, object]],
    margin_rows: Sequence[Mapping[str, object]],
    yield_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    hard_by_id = {str(r["source_candidate_id"]): r for r in hard_rows}
    margin_by_id = {str(r["source_candidate_id"]): r for r in margin_rows}
    yield_by_id = {str(r["source_candidate_id"]): r for r in yield_rows}
    out: list[dict[str, object]] = []
    for snap in pool:
        sid = snap.situation_seed_id
        row = snapshot_public_feature_row(snap)
        hr = hard_by_id.get(sid, {})
        mr = margin_by_id.get(sid, {})
        yr = yield_by_id.get(sid, {})
        row.update({
            "source_candidate_id": sid,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "hard_selected": int(bool(hr)),
            "margin_selected": int(bool(mr)),
            "yield_selected": int(bool(yr)),
            "hard_screen_rank": int(hr.get("hard_screen_rank", 0) or 0),
            "margin_screen_rank": int(mr.get("margin_screen_rank", 0) or 0),
            "yield_screen_rank": int(yr.get("yield_screen_rank", 0) or 0),
            "hard_screen_score": float(hr.get("hard_screen_score", snap.screen_score) or 0.0),
            "margin_screen_score": float(mr.get("margin_screen_score", 0.0) or 0.0),
            "yield_screen_score": float(yr.get("yield_screen_score", 0.0) or 0.0),
            "margin_predicted_margin": float(mr.get("predicted_margin", 0.0) or 0.0),
            "yield_predicted_yield_per_100": float(yr.get("predicted_yield_per_100", 0.0) or 0.0),
        })
        out.append(row)
    return out


def _method_rows(
    *,
    method: str,
    selected: Sequence[HardFrameSnapshot],
    selected_rows: Sequence[Mapping[str, object]],
    candidate_rows: Sequence[Mapping[str, object]],
    pool_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    selected_by_source = {str(r["source_candidate_id"]): r for r in selected_rows}
    pool_by_source = {str(r["source_candidate_id"]): r for r in pool_rows}
    candidates_by_sit: dict[str, list[Mapping[str, object]]] = {}
    for row in candidate_rows:
        candidates_by_sit.setdefault(str(row["situation_id"]), []).append(row)
    out: list[dict[str, object]] = []
    score_field = {
        "hard_screen": "hard_screen_score",
        "margin_screen": "margin_screen_score",
        "yield_screen": "yield_screen_score",
    }.get(method, "screen_score")
    for rank, snap in enumerate(selected, start=1):
        src = snap.situation_seed_id
        sr = selected_by_source.get(src, {})
        sid = str(sr.get("situation_id", ""))
        cand = candidates_by_sit.get(sid, []) if sid else []
        first = cand[0] if cand else {}
        rollouts = int(sum(int(r.get("branch_rollouts", 0) or 0) for r in cand)) if cand else 0
        pool_row = pool_by_source.get(src, {})
        decisive = int(float(first.get("situation_best_margin", 0.0) or 0.0) > 1e-9)
        out.append({
            "method": method,
            "method_rank": int(rank),
            "source_candidate_id": src,
            "situation_id": sid,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "branched": int(bool(cand)),
            "action_count": int(first.get("action_count", snap.action_count) or snap.action_count),
            "branched_action_count": int(first.get("branched_action_count", 0) or 0),
            "branch_rollouts": int(rollouts),
            "situation_best_margin": float(first.get("situation_best_margin", 0.0) or 0.0),
            "label_confidence_proxy": float(first.get("label_confidence_proxy", 0.0) or 0.0),
            "decisive": decisive,
            "behavior_chosen_is_best": int(first.get("behavior_chosen_is_best", 0) or 0),
            "best_mean_actor_score": float(first.get("best_mean_actor_score", 0.0) or 0.0),
            "chosen_mean_actor_score": float(first.get("chosen_mean_actor_score", 0.0) or 0.0),
            "queue_score": float(pool_row.get(score_field, snap.screen_score) or 0.0),
            "hard_selected": int(pool_row.get("hard_selected", 0) or 0),
            "margin_selected": int(pool_row.get("margin_selected", 0) or 0),
            "yield_selected": int(pool_row.get("yield_selected", 0) or 0),
            "selected_by_all_three": int((pool_row.get("hard_selected", 0) or 0) and (pool_row.get("margin_selected", 0) or 0) and (pool_row.get("yield_selected", 0) or 0)),
        })
    return out


def _stats(method: str, rows: Sequence[Mapping[str, object]]) -> QueueMethodStats:
    branched = [r for r in rows if int(r.get("branched", 0) or 0)]
    rollouts = int(sum(int(r.get("branch_rollouts", 0) or 0) for r in branched))
    decisive = int(sum(int(r.get("decisive", 0) or 0) for r in branched))
    return QueueMethodStats(
        method=method,
        selected_situations=int(len(rows)),
        branched_situations=int(len(branched)),
        decisive_situations=decisive,
        branch_rollouts=rollouts,
        decisive_per_100_rollouts=float(100.0 * decisive / max(1, rollouts)),
        mean_situation_best_margin=_mean([float(r.get("situation_best_margin", 0.0) or 0.0) for r in branched]),
        mean_label_confidence_proxy=_mean([float(r.get("label_confidence_proxy", 0.0) or 0.0) for r in branched]),
        mean_action_count=_mean([int(r.get("action_count", 0) or 0) for r in rows]),
        mean_queue_score=_mean([float(r.get("queue_score", 0.0) or 0.0) for r in rows]),
    )


def collect_yield_vs_hard_margin_queue_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    yield_model: YieldScreenModel,
    margin_model: MarginScreenModel,
    revision: str = "rev0046",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 1,
    max_behavior_frames: int = 220,
    candidate_pool_situations: int = 36,
    selected_situations: int = 10,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 5,
    branch_max_decisions: int = 420,
    budget_rng_seed: int = 46046,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 4,
    adaptive_stop_margin: float = 0.40,
    adaptive_target_confidence: float = 0.55,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], YieldQueueComparisonSummary]:
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
    hard_selected, hard_rank_rows = select_hard_screen_snapshots(pool, max_situations=selected_situations, max_per_behavior_game=max_per_behavior_game)
    margin_selected, margin_rank_rows = select_margin_screen_snapshots(pool, margin_model, max_situations=selected_situations, max_per_behavior_game=max_per_behavior_game)
    yield_selected, yield_rank_rows = select_yield_screen_snapshots(pool, yield_model, max_situations=selected_situations, max_per_behavior_game=max_per_behavior_game)
    pool_rows = _pool_rows(pool, hard_rank_rows, margin_rank_rows, yield_rank_rows)
    union = _union_snapshots(hard_selected, margin_selected, yield_selected)
    selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, race_summary = _race_selected_snapshots(
        union,
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
    hard_method_rows = _method_rows(method="hard_screen", selected=hard_selected, selected_rows=selected_rows, candidate_rows=candidate_rows, pool_rows=pool_rows)
    margin_method_rows = _method_rows(method="margin_screen", selected=margin_selected, selected_rows=selected_rows, candidate_rows=candidate_rows, pool_rows=pool_rows)
    yield_method_rows = _method_rows(method="yield_screen", selected=yield_selected, selected_rows=selected_rows, candidate_rows=candidate_rows, pool_rows=pool_rows)
    method_rows = hard_method_rows + margin_method_rows + yield_method_rows
    hard_stats = _stats("hard_screen", hard_method_rows)
    margin_stats = _stats("margin_screen", margin_method_rows)
    yield_stats = _stats("yield_screen", yield_method_rows)
    hard_ids = {s.situation_seed_id for s in hard_selected}
    margin_ids = {s.situation_seed_id for s in margin_selected}
    yield_ids = {s.situation_seed_id for s in yield_selected}

    def unique_decisive(rows: Sequence[Mapping[str, object]], other_ids: set[str]) -> int:
        return int(sum(1 for r in rows if str(r["source_candidate_id"]) not in other_ids and int(r.get("decisive", 0) or 0)))

    summary = YieldQueueComparisonSummary(
        revision=revision,
        behavior_games=int(len(specs)),
        behavior_decisions=int(stats.get("behavior_decisions", 0)),
        choice_frames_seen=int(stats.get("choice_frames_seen", 0)),
        candidate_frames_seen=int(stats.get("candidate_frames_seen", 0)),
        pool_rows=int(len(pool_rows)),
        hard_selected=int(len(hard_selected)),
        margin_selected=int(len(margin_selected)),
        yield_selected=int(len(yield_selected)),
        union_selected=int(len(union)),
        overlap_all_three=int(len(hard_ids & margin_ids & yield_ids)),
        branch_games=int(len(branch_rows)),
        branch_truncations=int(race_summary.branch_truncations),
        cpp_checked_transitions=int(race_summary.cpp_checked_transitions),
        cpp_skipped_transitions=int(race_summary.cpp_skipped_transitions),
        cpp_mismatches=int(race_summary.cpp_mismatches),
        hard_stats=hard_stats.as_dict(),
        margin_stats=margin_stats.as_dict(),
        yield_stats=yield_stats.as_dict(),
        yield_minus_hard_decisive_per_100=float(yield_stats.decisive_per_100_rollouts - hard_stats.decisive_per_100_rollouts),
        yield_minus_margin_decisive_per_100=float(yield_stats.decisive_per_100_rollouts - margin_stats.decisive_per_100_rollouts),
        yield_unique_decisive=unique_decisive(yield_method_rows, hard_ids | margin_ids),
        hard_unique_decisive=unique_decisive(hard_method_rows, margin_ids | yield_ids),
        margin_unique_decisive=unique_decisive(margin_method_rows, hard_ids | yield_ids),
        yield_model_revision=yield_model.revision,
        margin_model_revision=margin_model.revision,
        tool_status=race_summary.tool_status,
        mismatch_examples=race_summary.mismatch_examples,
        skipped_examples=race_summary.skipped_examples,
    )
    return pool_rows, hard_rank_rows, margin_rank_rows, yield_rank_rows, selected_rows, method_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, summary
