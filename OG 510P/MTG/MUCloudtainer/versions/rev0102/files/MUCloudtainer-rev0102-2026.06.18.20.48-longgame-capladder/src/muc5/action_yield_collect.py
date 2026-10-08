from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Sequence

from .action_counterfactual import ActionCounterfactualGameSpec
from .action_hard_racing import _hard_snapshots, _race_selected_snapshots, HardFrameOnlineRacingSummary
from .action_margin_screen import snapshot_public_feature_row
from .action_yield_screen import YieldScreenModel, select_yield_screen_snapshots


@dataclass(frozen=True)
class YieldScreenOnlineCollectionSummary:
    """Summary for a yield-screened online branch-label collection.

    rev0047 separates the *yield queue* from the rev0046 matched queue audit.
    The matched audit remains useful for comparing selectors; this collector is
    the production-shaped label path: use the best current public queueing model,
    then spend branch rollout budget with the existing online/adaptive racer.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    candidate_frames_seen: int
    pool_rows: int
    yield_selected: int
    branch_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    decisive_situations: int
    decisive_per_100_rollouts: float
    mean_action_count: float
    mean_branched_action_count: float
    mean_rollouts_per_action: float
    mean_label_confidence_proxy: float
    behavior_chosen_best_rate: float
    mean_best_minus_chosen: float
    yield_model_revision: str
    hard_race_summary: Mapping[str, object]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _pool_rows(pool, yield_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    by_id = {str(r.get("source_candidate_id", "")): r for r in yield_rows}
    out: list[dict[str, object]] = []
    for snap in pool:
        yr = by_id.get(snap.situation_seed_id, {})
        row = snapshot_public_feature_row(snap)
        row.update({
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": snap.spec.game_id,
            "step": int(snap.step),
            "yield_selected": int(bool(yr)),
            "yield_screen_rank": int(yr.get("yield_screen_rank", 0) or 0),
            "yield_screen_score": float(yr.get("yield_screen_score", 0.0) or 0.0),
            "yield_predicted_yield_per_100": float(yr.get("predicted_yield_per_100", 0.0) or 0.0),
            "base_screen_score": float(snap.screen_score),
            "screen_reason": snap.reason,
        })
        out.append(row)
    return out


def collect_yield_screen_online_counterfactuals(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    yield_model: YieldScreenModel,
    revision: str = "rev0047",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 1,
    max_behavior_frames: int = 260,
    candidate_pool_situations: int = 60,
    selected_situations: int = 16,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 6,
    branch_max_decisions: int = 420,
    budget_rng_seed: int = 47047,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 6,
    adaptive_stop_margin: float = 0.42,
    adaptive_target_confidence: float = 0.58,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], YieldScreenOnlineCollectionSummary]:
    """Collect action-counterfactual labels from the yield-screen queue.

    This function is intentionally a small orchestration layer over existing
    public-hard-frame and C++-shadowed racing machinery.  It adds no new hidden
    features: frame selection is public-only, and hidden state is used only by
    the offline branch-label referee.
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
    selected, yield_rank_rows = select_yield_screen_snapshots(
        pool,
        yield_model,
        max_situations=int(selected_situations),
        max_per_behavior_game=max_per_behavior_game,
    )
    pool_out = _pool_rows(pool, yield_rank_rows)
    selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, race_summary = _race_selected_snapshots(
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
    summary = YieldScreenOnlineCollectionSummary(
        revision=revision,
        behavior_games=int(len(specs)),
        behavior_decisions=int(stats.get("behavior_decisions", 0)),
        choice_frames_seen=int(stats.get("choice_frames_seen", 0)),
        candidate_frames_seen=int(stats.get("candidate_frames_seen", 0)),
        pool_rows=int(len(pool_out)),
        yield_selected=int(len(selected)),
        branch_games=int(race_summary.branch_games),
        branch_truncations=int(race_summary.branch_truncations),
        cpp_checked_transitions=int(race_summary.cpp_checked_transitions),
        cpp_skipped_transitions=int(race_summary.cpp_skipped_transitions),
        cpp_mismatches=int(race_summary.cpp_mismatches),
        decisive_situations=int(race_summary.decisive_situations),
        decisive_per_100_rollouts=float(race_summary.decisive_per_100_rollouts),
        mean_action_count=float(race_summary.mean_action_count),
        mean_branched_action_count=float(race_summary.mean_branched_action_count),
        mean_rollouts_per_action=float(race_summary.mean_rollouts_per_action),
        mean_label_confidence_proxy=float(race_summary.mean_label_confidence_proxy),
        behavior_chosen_best_rate=float(race_summary.behavior_chosen_best_rate),
        mean_best_minus_chosen=float(race_summary.mean_best_minus_chosen),
        yield_model_revision=str(yield_model.revision),
        hard_race_summary=race_summary.as_dict(),
    )
    return pool_out, yield_rank_rows, selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, cpp_rows, summary
