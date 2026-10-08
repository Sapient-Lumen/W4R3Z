from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence

from .action_counterfactual import ActionCounterfactualGameSpec
from .action_hard_frame import HardFrameSnapshot
from .action_hard_racing import _hard_snapshots, _race_selected_snapshots
from .action_margin_screen import MarginScreenModel, select_margin_screen_snapshots, snapshot_public_feature_row


@dataclass(frozen=True)
class QueueMethodStats:
    method: str
    selected_situations: int
    branched_situations: int
    high_action_selected: int
    decisive_situations: int
    branch_rollouts: int
    decisive_per_100_rollouts: float
    mean_situation_best_margin: float
    mean_label_confidence_proxy: float
    mean_behavior_chosen_best: float
    mean_action_count: float
    mean_queue_score: float

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MarginVsHardQueueSummary:
    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    candidate_frames_seen: int
    pool_rows: int
    hard_selected: int
    margin_selected: int
    union_selected: int
    overlap_selected: int
    hard_only_selected: int
    margin_only_selected: int
    branch_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    hard_stats: Mapping[str, object]
    margin_stats: Mapping[str, object]
    margin_minus_hard_decisive_per_100: float
    margin_minus_hard_mean_margin: float
    margin_minus_hard_mean_confidence: float
    margin_queue_beats_hard_on_unique_decisive: int
    hard_queue_beats_margin_on_unique_decisive: int
    ranker_revision: str
    tool_status: Mapping[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _mean(xs: Sequence[float | int]) -> float:
    return float(sum(float(x) for x in xs) / max(1, len(xs)))


def select_hard_screen_snapshots(
    snapshots: Sequence[HardFrameSnapshot],
    *,
    max_situations: int,
    max_per_behavior_game: int = 2,
) -> tuple[list[HardFrameSnapshot], list[dict[str, object]]]:
    """Select frames by the pre-model public hard-frame score.

    This is the matched baseline for margin-screen experiments.  It uses the
    same per-behavior-game cap as the margin selector so a single weird game
    cannot monopolize the label budget.
    """

    scored: list[tuple[float, HardFrameSnapshot, dict[str, object]]] = []
    for snap in snapshots:
        row = snapshot_public_feature_row(snap)
        score = float(snap.screen_score)
        d = dict(row)
        d.update({
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "hard_screen_score": score,
            "base_screen_score": score,
            "screen_reason": snap.reason,
        })
        scored.append((score, snap, d))
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
        dd["hard_screen_rank"] = int(len(selected) + 1)
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
            dd["hard_screen_rank"] = int(len(selected) + 1)
            selected.append(snap)
            rows.append(dd)
            if len(selected) >= int(max_situations):
                break
    return selected, rows


def _union_snapshots(*groups: Sequence[HardFrameSnapshot]) -> list[HardFrameSnapshot]:
    by_id: dict[str, HardFrameSnapshot] = {}
    for group in groups:
        for snap in group:
            by_id.setdefault(snap.situation_seed_id, snap)
    # Stable ordering: preserve baseline hardness first, then id fallback.
    return sorted(by_id.values(), key=lambda s: (-s.screen_score, -s.action_count, s.situation_seed_id))


def _pool_rows(
    pool: Sequence[HardFrameSnapshot],
    hard_rows: Sequence[Mapping[str, object]],
    margin_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    hard_by_id = {str(r["source_candidate_id"]): r for r in hard_rows}
    margin_by_id = {str(r["source_candidate_id"]): r for r in margin_rows}
    out: list[dict[str, object]] = []
    for snap in pool:
        sid = snap.situation_seed_id
        row = snapshot_public_feature_row(snap)
        hr = hard_by_id.get(sid, {})
        mr = margin_by_id.get(sid, {})
        row.update({
            "source_candidate_id": sid,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "hard_selected": int(bool(hr)),
            "margin_selected": int(bool(mr)),
            "hard_screen_rank": int(hr.get("hard_screen_rank", 0) or 0),
            "margin_screen_rank": int(mr.get("margin_screen_rank", 0) or 0),
            "hard_screen_score": float(hr.get("hard_screen_score", snap.screen_score)),
            "margin_screen_score": float(mr.get("margin_screen_score", 0.0) or 0.0),
            "margin_predicted_margin": float(mr.get("predicted_margin", 0.0) or 0.0),
            "screen_reason": snap.reason,
        })
        out.append(row)
    return out


def _method_rows(
    *,
    method: str,
    selected: Sequence[HardFrameSnapshot],
    selected_rows: Sequence[Mapping[str, object]],
    candidate_rows: Sequence[Mapping[str, object]],
    pool_score_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    selected_by_source = {str(r["source_candidate_id"]): r for r in selected_rows}
    pool_by_source = {str(r["source_candidate_id"]): r for r in pool_score_rows}
    candidates_by_sit: dict[str, list[Mapping[str, object]]] = {}
    for row in candidate_rows:
        candidates_by_sit.setdefault(str(row["situation_id"]), []).append(row)
    out: list[dict[str, object]] = []
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
            "queue_score": float(pool_row.get("margin_screen_score" if method == "margin_screen" else "hard_screen_score", snap.screen_score) or 0.0),
            "hard_selected": int(pool_row.get("hard_selected", 0) or 0),
            "margin_selected": int(pool_row.get("margin_selected", 0) or 0),
            "selected_by_both": int((pool_row.get("hard_selected", 0) or 0) and (pool_row.get("margin_selected", 0) or 0)),
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
        high_action_selected=int(sum(1 for r in rows if int(r.get("action_count", 0) or 0) >= 5)),
        decisive_situations=decisive,
        branch_rollouts=rollouts,
        decisive_per_100_rollouts=float(100.0 * decisive / max(1, rollouts)),
        mean_situation_best_margin=_mean([float(r.get("situation_best_margin", 0.0) or 0.0) for r in branched]),
        mean_label_confidence_proxy=_mean([float(r.get("label_confidence_proxy", 0.0) or 0.0) for r in branched]),
        mean_behavior_chosen_best=_mean([int(r.get("behavior_chosen_is_best", 0) or 0) for r in branched]),
        mean_action_count=_mean([int(r.get("action_count", 0) or 0) for r in rows]),
        mean_queue_score=_mean([float(r.get("queue_score", 0.0) or 0.0) for r in rows]),
    )


def collect_margin_vs_hard_queue_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    model: MarginScreenModel,
    revision: str = "rev0045",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 1,
    max_behavior_frames: int = 220,
    candidate_pool_situations: int = 34,
    selected_situations: int = 10,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 5,
    branch_max_decisions: int = 420,
    budget_rng_seed: int = 45045,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 4,
    adaptive_stop_margin: float = 0.40,
    adaptive_target_confidence: float = 0.55,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], MarginVsHardQueueSummary]:
    """Matched comparison of baseline hard-frame queue vs margin-screen queue.

    The two selectors see the same public candidate pool.  We branch only the
    union of their selected situations and then score each selector from the
    same branch results.  This isolates queue quality from branch rollout noise.
    """

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
    hard_selected, hard_rank_rows = select_hard_screen_snapshots(
        pool,
        max_situations=selected_situations,
        max_per_behavior_game=max_per_behavior_game,
    )
    margin_selected, margin_rank_rows = select_margin_screen_snapshots(
        pool,
        model,
        max_situations=selected_situations,
        max_per_behavior_game=max_per_behavior_game,
    )
    pool_rows = _pool_rows(pool, hard_rank_rows, margin_rank_rows)
    union = _union_snapshots(hard_selected, margin_selected)
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
    hard_method_rows = _method_rows(
        method="hard_screen",
        selected=hard_selected,
        selected_rows=selected_rows,
        candidate_rows=candidate_rows,
        pool_score_rows=pool_rows,
    )
    margin_method_rows = _method_rows(
        method="margin_screen",
        selected=margin_selected,
        selected_rows=selected_rows,
        candidate_rows=candidate_rows,
        pool_score_rows=pool_rows,
    )
    method_rows = hard_method_rows + margin_method_rows
    hard_stats = _stats("hard_screen", hard_method_rows)
    margin_stats = _stats("margin_screen", margin_method_rows)
    hard_ids = {s.situation_seed_id for s in hard_selected}
    margin_ids = {s.situation_seed_id for s in margin_selected}

    hard_unique_decisive = sum(1 for r in hard_method_rows if str(r["source_candidate_id"]) not in margin_ids and int(r.get("decisive", 0) or 0))
    margin_unique_decisive = sum(1 for r in margin_method_rows if str(r["source_candidate_id"]) not in hard_ids and int(r.get("decisive", 0) or 0))
    summary = MarginVsHardQueueSummary(
        revision=revision,
        behavior_games=int(len(specs)),
        behavior_decisions=int(stats.get("behavior_decisions", 0)),
        choice_frames_seen=int(stats.get("choice_frames_seen", 0)),
        candidate_frames_seen=int(stats.get("candidate_frames_seen", 0)),
        pool_rows=int(len(pool_rows)),
        hard_selected=int(len(hard_selected)),
        margin_selected=int(len(margin_selected)),
        union_selected=int(len(union)),
        overlap_selected=int(len(hard_ids & margin_ids)),
        hard_only_selected=int(len(hard_ids - margin_ids)),
        margin_only_selected=int(len(margin_ids - hard_ids)),
        branch_games=int(len(branch_rows)),
        branch_truncations=int(race_summary.branch_truncations),
        cpp_checked_transitions=int(race_summary.cpp_checked_transitions),
        cpp_skipped_transitions=int(race_summary.cpp_skipped_transitions),
        cpp_mismatches=int(race_summary.cpp_mismatches),
        hard_stats=hard_stats.as_dict(),
        margin_stats=margin_stats.as_dict(),
        margin_minus_hard_decisive_per_100=float(margin_stats.decisive_per_100_rollouts - hard_stats.decisive_per_100_rollouts),
        margin_minus_hard_mean_margin=float(margin_stats.mean_situation_best_margin - hard_stats.mean_situation_best_margin),
        margin_minus_hard_mean_confidence=float(margin_stats.mean_label_confidence_proxy - hard_stats.mean_label_confidence_proxy),
        margin_queue_beats_hard_on_unique_decisive=int(margin_unique_decisive > hard_unique_decisive),
        hard_queue_beats_margin_on_unique_decisive=int(hard_unique_decisive > margin_unique_decisive),
        ranker_revision=str(ranker_revision),
        tool_status=race_summary.tool_status,
        mismatch_examples=race_summary.mismatch_examples,
        skipped_examples=race_summary.skipped_examples,
    )
    return pool_rows, hard_rank_rows, margin_rank_rows, selected_rows, method_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, summary
