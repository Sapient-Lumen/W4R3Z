from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence

from .action_counterfactual import (
    ActionCounterfactualGameSpec,
    _apply_and_collect_transition,
    _finalize_cpp_rows,
    _rollout_branch,
)
from .action_disagreement import _screen_votes
from .action_hybrid_selector import select_hybrid_action_indices
from .action_screen_compare import _method_compare_rows, _select_screened, _select_unscreened
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import DecisionFrame, PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import GameState, start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import PublicProfileAgent, make_public_agent
from .ranker_policy import counterfactual_ranker_model_path, load_linear_ranker_model


@dataclass(frozen=True)
class HardFrameSnapshot:
    """A public decision frame selected for expensive branch labeling.

    The snapshot stores a hidden true-state copy only inside the offline labeler.
    It is never passed to gameplay agents.  The point is to prioritize frames
    where a branch budget might matter: many legal actions, public-policy
    disagreement, profile-score spread, and/or ranker-prior spread.
    """

    situation_seed_id: str
    spec: ActionCounterfactualGameSpec
    spec_index: int
    step: int
    state: GameState
    frame: DecisionFrame
    chosen_idx: int
    vote_rows: tuple[Dict[str, object], ...]
    unique_votes: tuple[int, ...]
    vote_entropy_proxy: float
    action_count: int
    profile_spread: float
    ranker_spread: float
    screen_score: float
    high_action_bonus: float
    reason: str


@dataclass(frozen=True)
class HardFrameSelectorSummary:
    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    candidate_frames_seen: int
    frames_with_disagreement: int
    selected_situations: int
    high_action_selected: int
    subset_situations: int
    union_candidate_actions: int
    branch_games: int
    branch_rollouts_per_action: int
    branch_terminal_games: int
    branch_truncations: int
    method_rows: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    mean_action_count: float
    mean_selected_screen_score: float
    mean_vote_entropy_proxy: float
    mean_profile_spread: float
    mean_ranker_spread: float
    union_decisive_situations: int
    mean_union_margin: float
    hybrid_hits_union_best_rate: float
    unscreened_hits_union_best_rate: float
    screened_hits_union_best_rate: float
    screen_vote_hits_union_best_rate: float
    behavior_chosen_hits_union_best_rate: float
    mean_hybrid_lost_value_to_union_best: float
    mean_unscreened_lost_value_to_union_best: float
    mean_screened_lost_value_to_union_best: float
    hybrid_better_than_both_situations: int
    hybrid_worse_than_both_situations: int
    ranker_revision: str
    ranker_available_frames_seen: int
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _normalize_spread(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    vals = [float(v) for v in values]
    return float(max(vals) - min(vals))


def _profile_score_spread(frame: DecisionFrame, profiles: Sequence[str] = ("counter_happy", "threat_rush", "patient")) -> float:
    """Cheap public-safe disagreement proxy from readable profile scorers."""

    if frame.action_count <= 1:
        return 0.0
    spreads: list[float] = []
    for name in profiles:
        try:
            agent = PublicProfileAgent(str(name))
            scores = [float(agent.score_action(frame.observation, a)) for a in frame.legal_actions]
            spreads.append(_normalize_spread(scores))
        except Exception:
            continue
    if not spreads:
        return 0.0
    # Compress arbitrary score units into [0, 1-ish] while preserving ordering.
    raw = sum(spreads) / float(len(spreads))
    return float(raw / (abs(raw) + 10.0)) if raw != 0 else 0.0


def _ranker_score_spread(frame: DecisionFrame, revision: str) -> tuple[float, bool]:
    """Cheap public-safe spread from a previous counterfactual ranker if present."""

    try:
        path = counterfactual_ranker_model_path(str(revision))
        if not path.exists():
            return 0.0, False
        model = load_linear_ranker_model(path)
        scores = [float(model.score_action(frame, a)) for a in frame.legal_actions]
        raw = _normalize_spread(scores)
        return (float(raw / (abs(raw) + 1.0)) if raw != 0 else 0.0), True
    except Exception:
        return 0.0, False


def hard_frame_screen_score(
    *,
    action_count: int,
    unique_votes: int,
    vote_entropy_proxy: float,
    profile_spread: float,
    ranker_spread: float,
    high_action_threshold: int = 5,
) -> tuple[float, float, str]:
    """Score a frame for expensive branch labeling.

    This is intentionally public-feature-only.  It does not inspect the hidden
    true state or branch outcomes.  The score is a queueing heuristic for the
    offline labeler, not a game-playing policy.
    """

    action_component = min(1.0, max(0.0, (float(action_count) - 1.0) / 14.0))
    high_action_bonus = 1.0 if int(action_count) >= int(high_action_threshold) else 0.0
    vote_component = min(1.0, max(0.0, float(vote_entropy_proxy)))
    unique_component = min(1.0, max(0.0, (float(unique_votes) - 1.0) / 4.0))
    profile_component = min(1.0, max(0.0, float(profile_spread)))
    ranker_component = min(1.0, max(0.0, float(ranker_spread)))
    score = (
        0.20 * action_component
        + 0.20 * high_action_bonus
        + 0.25 * vote_component
        + 0.15 * unique_component
        + 0.12 * profile_component
        + 0.08 * ranker_component
    )
    reasons = []
    if high_action_bonus:
        reasons.append("high_action")
    if vote_component > 0:
        reasons.append("public_disagreement")
    if profile_component >= 0.20:
        reasons.append("profile_spread")
    if ranker_component >= 0.10:
        reasons.append("ranker_spread")
    if not reasons:
        reasons.append("low_signal_choice")
    return float(score), float(high_action_bonus), "+".join(reasons)


def _summary_from_methods(method_rows: Sequence[Mapping[str, object]], selected_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_sit: dict[str, dict[str, Mapping[str, object]]] = {}
    for row in method_rows:
        by_sit.setdefault(str(row["situation_id"]), {})[str(row["method"])] = row

    methods = ("unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker")
    hits = {m: [] for m in methods}
    lost = {m: [] for m in methods}
    margins: list[float] = []
    action_counts: list[int] = []
    vote_entropy: list[float] = []
    profile_spread: list[float] = []
    ranker_spread: list[float] = []
    screen_scores: list[float] = []
    behavior_hits: list[int] = []
    screen_vote_hits: list[int] = []
    hybrid_better_both = 0
    hybrid_worse_both = 0

    selected_by_sid = {str(r["situation_id"]): r for r in selected_rows}
    for sid, group in by_sit.items():
        if any(m not in group for m in methods):
            continue
        h = group["hybrid_vote_diverse_ranker"]
        u = group["unscreened_budget"]
        s = group["screened_vote_budget"]
        hv = float(h.get("method_best_mean_actor_score", 0.0))
        uv = float(u.get("method_best_mean_actor_score", 0.0))
        sv = float(s.get("method_best_mean_actor_score", 0.0))
        if hv > uv + 1e-9 and hv > sv + 1e-9:
            hybrid_better_both += 1
        if hv < uv - 1e-9 and hv < sv - 1e-9:
            hybrid_worse_both += 1
        margins.append(float(h.get("union_best_margin", 0.0)))
        action_counts.append(int(h.get("action_count", 0)))
        behavior_hits.append(int(h.get("behavior_chosen_hits_union_best", 0)))
        screen_vote_hits.append(int(h.get("screen_vote_hits_union_best", 0)))
        for m in methods:
            hits[m].append(int(group[m].get("method_hits_union_best", 0)))
            lost[m].append(float(group[m].get("method_lost_value_to_union_best", 0.0)))
        sr = selected_by_sid.get(sid, {})
        vote_entropy.append(float(sr.get("screen_vote_entropy_proxy", 0.0)))
        profile_spread.append(float(sr.get("profile_spread", 0.0)))
        ranker_spread.append(float(sr.get("ranker_spread", 0.0)))
        screen_scores.append(float(sr.get("screen_score", 0.0)))

    def mean(xs: Sequence[float | int]) -> float:
        return float(sum(float(x) for x in xs) / max(1, len(xs)))

    return {
        "situations": len(by_sit),
        "mean_action_count": mean(action_counts),
        "mean_selected_screen_score": mean(screen_scores),
        "mean_vote_entropy_proxy": mean(vote_entropy),
        "mean_profile_spread": mean(profile_spread),
        "mean_ranker_spread": mean(ranker_spread),
        "union_decisive_situations": int(sum(1 for x in margins if float(x) > 1e-9)),
        "mean_union_margin": mean(margins),
        "hybrid_hits_union_best_rate": mean(hits["hybrid_vote_diverse_ranker"]),
        "unscreened_hits_union_best_rate": mean(hits["unscreened_budget"]),
        "screened_hits_union_best_rate": mean(hits["screened_vote_budget"]),
        "screen_vote_hits_union_best_rate": mean(screen_vote_hits),
        "behavior_chosen_hits_union_best_rate": mean(behavior_hits),
        "mean_hybrid_lost_value_to_union_best": mean(lost["hybrid_vote_diverse_ranker"]),
        "mean_unscreened_lost_value_to_union_best": mean(lost["unscreened_budget"]),
        "mean_screened_lost_value_to_union_best": mean(lost["screened_vote_budget"]),
        "hybrid_better_than_both_situations": hybrid_better_both,
        "hybrid_worse_than_both_situations": hybrid_worse_both,
    }


def collect_hard_frame_hybrid_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0041",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 2,
    max_behavior_frames: int = 140,
    max_situations: int = 12,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 5,
    branch_rollouts_per_action: int = 2,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 41041,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], HardFrameSelectorSummary]:
    """Screen hard public frames, then compare branch-budget selectors.

    Unlike rev0040's one-pass collector, this function first builds a small
    public-only priority queue of candidate frames, then branches the highest
    scoring frames.  ``max_behavior_frames`` is applied per behavior game so one
    long match cannot monopolize the queue.  It is designed to find
    high-action/high-disagreement frames where selector budget may actually bind.
    """

    selected_frame_rows: list[Dict[str, object]] = []
    candidate_rows: list[Dict[str, object]] = []
    method_rows: list[Dict[str, object]] = []
    branch_rows: list[Dict[str, object]] = []
    screen_rows: list[Dict[str, object]] = []
    transition_rows: list[Dict[str, object]] = []
    records: list[TransitionMicroRecord] = []
    expected_sigs: list[str] = []
    row_indices: list[int] = []

    agent_cache: dict[str, PublicDecisionAgent] = {}
    mulligan_cache: dict[str, object] = {}

    def agent(name: str) -> PublicDecisionAgent:
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def mulligan(name: object) -> object:
        key = str(name)
        if key not in mulligan_cache:
            mulligan_cache[key] = make_mulligan_agent(name)
        return mulligan_cache[key]

    screeners = {str(name): agent(str(name)) for name in screen_agent_names}
    behavior_decisions = 0
    choice_seen = 0
    candidate_frames_seen = 0
    frames_with_disagreement = 0
    ranker_available_frames = 0
    snapshots: list[HardFrameSnapshot] = []

    for spec_i, spec in enumerate(specs):
        frames_this_spec = 0
        transition_rng = Random(int(spec.seed))
        agent_rng = Random(int(spec.seed) + 1000003)
        agents = (agent(spec.agent0), agent(spec.agent1))
        state = start_game(
            spec.deck0,
            spec.deck1,
            seed=int(spec.seed),
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            mulligan_agents=(mulligan(spec.mulligan0), mulligan(spec.mulligan1)),
            record_log=False,
        )
        for step in range(1, int(spec.max_decisions) + 1):
            if state.winner is not None or frames_this_spec >= int(max_behavior_frames):
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"behavior policy chose illegal action index {chosen_idx}/{frame.action_count}")
            behavior_decisions += 1
            frames_this_spec += 1
            if frame.action_count > 1:
                choice_seen += 1
                vote_rows, unique_votes, entropy = _screen_votes(frame, screeners, seed=int(spec.seed) + step * 9176 + spec_i)
                prof_spread = _profile_score_spread(frame)
                rank_spread, rank_avail = _ranker_score_spread(frame, str(ranker_revision))
                if rank_avail:
                    ranker_available_frames += 1
                score, high_bonus, reason = hard_frame_screen_score(
                    action_count=int(frame.action_count),
                    unique_votes=len(unique_votes),
                    vote_entropy_proxy=float(entropy),
                    profile_spread=float(prof_spread),
                    ranker_spread=float(rank_spread),
                    high_action_threshold=int(high_action_threshold),
                )
                if len(unique_votes) >= int(min_unique_screen_votes):
                    frames_with_disagreement += 1
                    candidate_frames_seen += 1
                    snapshots.append(
                        HardFrameSnapshot(
                            situation_seed_id=f"{revision}_cand{candidate_frames_seen:04d}_{spec.game_id}_step{step:04d}",
                            spec=spec,
                            spec_index=int(spec_i),
                            step=int(step),
                            state=copy.deepcopy(state),
                            frame=frame,
                            chosen_idx=int(chosen_idx),
                            vote_rows=tuple(vote_rows),
                            unique_votes=tuple(unique_votes),
                            vote_entropy_proxy=float(entropy),
                            action_count=int(frame.action_count),
                            profile_spread=float(prof_spread),
                            ranker_spread=float(rank_spread),
                            screen_score=float(score),
                            high_action_bonus=float(high_bonus),
                            reason=reason,
                        )
                    )
            apply_decision_index(state, frame, chosen_idx, transition_rng)

    # Prefer high-score frames, then high-action frames, but cap how many frames
    # one behavior game can contribute.  rev0041 first pass showed that a naive
    # top-k queue can overfit one long Jace/Overlord game and produce many
    # superficially hard but outcome-tied labels.
    ordered_snapshots = sorted(
        snapshots,
        key=lambda s: (-s.screen_score, -s.action_count, -s.vote_entropy_proxy, s.situation_seed_id),
    )
    selected: list[HardFrameSnapshot] = []
    per_game: dict[str, int] = {}
    cap = max(1, int(max_per_behavior_game))
    for snap in ordered_snapshots:
        gid = str(snap.spec.game_id)
        if per_game.get(gid, 0) >= cap:
            continue
        selected.append(snap)
        per_game[gid] = per_game.get(gid, 0) + 1
        if len(selected) >= int(max_situations):
            break
    if len(selected) < int(max_situations):
        seen = {s.situation_seed_id for s in selected}
        for snap in ordered_snapshots:
            if snap.situation_seed_id in seen:
                continue
            selected.append(snap)
            if len(selected) >= int(max_situations):
                break
    snapshots = selected

    branch_terminal = 0
    branch_trunc = 0
    subset_situations = 0

    for sampled, snap in enumerate(snapshots):
        spec = snap.spec
        frame = snap.frame
        chosen_idx = int(snap.chosen_idx)
        unscreened_idx, unscreened_reasons, _uns_subset, uns_skip = _select_unscreened(
            frame,
            chosen_idx,
            max_actions_per_frame=int(max_actions_per_frame),
            branch_action_budget=int(branch_action_budget),
            rng=Random(int(budget_rng_seed) + sampled * 101 + snap.step),
        )
        screened_idx, screened_reasons, _scr_subset, scr_skip = _select_screened(
            frame,
            chosen_idx,
            snap.unique_votes,
            max_actions_per_frame=int(max_actions_per_frame),
            branch_action_budget=int(branch_action_budget),
            rng=Random(int(budget_rng_seed) + sampled * 101 + snap.step + 17),
        )
        hybrid_idx, hybrid_reasons, hyb_subset, hyb_skip, _hybrid_meta = select_hybrid_action_indices(
            frame,
            chosen_idx,
            snap.unique_votes,
            max_actions_per_frame=int(max_actions_per_frame),
            branch_action_budget=int(branch_action_budget),
            rng=Random(int(budget_rng_seed) + sampled * 101 + snap.step + 31),
            ranker_revision=str(ranker_revision),
        )
        if uns_skip or scr_skip or hyb_skip:
            continue
        union_indices = tuple(sorted(set(unscreened_idx) | set(screened_idx) | set(hybrid_idx)))
        if len(union_indices) <= 1:
            continue
        if frame.action_count > int(max_actions_per_frame):
            subset_situations += 1
        situation_id = f"{revision}_s{sampled:04d}_{spec.game_id}_step{snap.step:04d}"
        selected_row = {
            "revision": revision,
            "situation_id": situation_id,
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": spec.game_id,
            "step": int(snap.step),
            "player": int(frame.player),
            "action_count": int(frame.action_count),
            "union_branched_action_count": int(len(union_indices)),
            "behavior_chosen_index": int(chosen_idx),
            "behavior_chosen_action": frame.legal_actions[chosen_idx].compact(),
            "screen_unique_votes": int(len(snap.unique_votes)),
            "screen_vote_entropy_proxy": float(snap.vote_entropy_proxy),
            "profile_spread": float(snap.profile_spread),
            "ranker_spread": float(snap.ranker_spread),
            "screen_score": float(snap.screen_score),
            "high_action_bonus": float(snap.high_action_bonus),
            "screen_reason": snap.reason,
            "starting_life": int(spec.starting_life),
            "starting_player": int(spec.starting_player),
            "agent0": spec.agent0,
            "agent1": spec.agent1,
            "mulligan0": str(spec.mulligan0),
            "mulligan1": str(spec.mulligan1),
        }
        selected_frame_rows.append(selected_row)
        for vr in snap.vote_rows:
            screen_rows.append({
                "revision": revision,
                "situation_id": situation_id,
                "source_candidate_id": snap.situation_seed_id,
                "behavior_game_id": spec.game_id,
                "step": int(snap.step),
                "player": int(frame.player),
                "action_count": int(frame.action_count),
                "behavior_chosen_index": int(chosen_idx),
                "behavior_chosen_action": frame.legal_actions[chosen_idx].compact(),
                "screen_unique_votes": int(len(snap.unique_votes)),
                "screen_vote_entropy_proxy": float(snap.vote_entropy_proxy),
                "screen_score": float(snap.screen_score),
                **vr,
            })

        ctx = context_feature_dict(frame.observation)
        scores_by_action = {int(i): [] for i in union_indices}
        agents = (agent(spec.agent0), agent(spec.agent1))
        for action_idx in union_indices:
            for rollout in range(int(branch_rollouts_per_action)):
                branch_state = copy.deepcopy(snap.state)
                branch_frame = build_decision_frame(branch_state)
                if branch_frame.legal_action_strings != frame.legal_action_strings:
                    raise ValueError(f"{situation_id}: branch legal menu drift before action")
                branch_seed = 941000000 + sampled * 10000 + int(action_idx) * 100 + rollout
                branch_rng = Random(branch_seed)
                action = frame.legal_actions[int(action_idx)]
                _apply_and_collect_transition(
                    branch_state,
                    branch_frame,
                    int(action_idx),
                    branch_rng,
                    case_id=f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}_first_{action.kind}",
                    transition_rows=transition_rows,
                    records=records,
                    expected_sigs=expected_sigs,
                    row_indices=row_indices,
                )
                score, result, branch_decisions, turn_number = _rollout_branch(
                    branch_state,
                    agents,
                    actor=int(frame.player),
                    branch_seed=branch_seed + 43,
                    max_decisions=int(branch_max_decisions),
                    case_prefix=f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                    transition_rows=transition_rows,
                    records=records,
                    expected_sigs=expected_sigs,
                    row_indices=row_indices,
                )
                scores_by_action[int(action_idx)].append(float(score))
                if result.winner is None:
                    branch_trunc += 1
                else:
                    branch_terminal += 1
                branch_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "source_candidate_id": snap.situation_seed_id,
                    "branch_id": f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                    "behavior_game_id": spec.game_id,
                    "step": int(snap.step),
                    "player": int(frame.player),
                    "action_index": int(action_idx),
                    "action_count": int(frame.action_count),
                    "union_branched_action_count": int(len(union_indices)),
                    "in_unscreened_budget": 1 if int(action_idx) in set(unscreened_idx) else 0,
                    "in_screened_vote_budget": 1 if int(action_idx) in set(screened_idx) else 0,
                    "in_hybrid_budget": 1 if int(action_idx) in set(hybrid_idx) else 0,
                    "hybrid_budget_reason": hybrid_reasons.get(int(action_idx), ""),
                    "behavior_chosen": 1 if int(action_idx) == int(chosen_idx) else 0,
                    "screen_voted_action": 1 if int(action_idx) in set(snap.unique_votes) else 0,
                    "rollout": int(rollout),
                    "action": action.compact(),
                    "actor_score": float(score),
                    "winner": "None" if result.winner is None else int(result.winner),
                    "loss_reason": result.loss_reason,
                    "branch_decisions": int(branch_decisions),
                    "turn_number": int(turn_number),
                    "starting_life": int(spec.starting_life),
                    "starting_player": int(spec.starting_player),
                })
        for method, idxs, reasons in (
            ("unscreened_budget", unscreened_idx, unscreened_reasons),
            ("screened_vote_budget", screened_idx, screened_reasons),
            ("hybrid_vote_diverse_ranker", hybrid_idx, hybrid_reasons),
        ):
            rows, sit = _method_compare_rows(
                situation_id=situation_id,
                method=method,
                frame=frame,
                selected_indices=idxs,
                union_indices=union_indices,
                scores_by_action=scores_by_action,
                chosen_idx=chosen_idx,
                voted_indices=snap.unique_votes,
                selection_reasons=reasons,
                ctx=ctx,
                spec=spec,
                step=snap.step,
            )
            for row in rows:
                row.update({
                    "screen_score": float(snap.screen_score),
                    "screen_reason": snap.reason,
                    "profile_spread": float(snap.profile_spread),
                    "ranker_spread": float(snap.ranker_spread),
                    "high_action_bonus": float(snap.high_action_bonus),
                })
            sit.update({
                "screen_score": float(snap.screen_score),
                "screen_reason": snap.reason,
                "profile_spread": float(snap.profile_spread),
                "ranker_spread": float(snap.ranker_spread),
                "high_action_bonus": float(snap.high_action_bonus),
            })
            candidate_rows.extend(rows)
            method_rows.append(sit)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    stats = _summary_from_methods(method_rows, selected_frame_rows)
    summary = HardFrameSelectorSummary(
        revision=str(revision),
        behavior_games=int(len(specs)),
        behavior_decisions=int(behavior_decisions),
        choice_frames_seen=int(choice_seen),
        candidate_frames_seen=int(candidate_frames_seen),
        frames_with_disagreement=int(frames_with_disagreement),
        selected_situations=int(len(selected_frame_rows)),
        high_action_selected=int(sum(1 for r in selected_frame_rows if int(r.get("action_count", 0)) >= int(high_action_threshold))),
        subset_situations=int(subset_situations),
        union_candidate_actions=int(len({(r.get("situation_id"), r.get("action_index")) for r in candidate_rows})),
        branch_games=int(len(branch_rows)),
        branch_rollouts_per_action=int(branch_rollouts_per_action),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_trunc),
        method_rows=int(len(method_rows)),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=float(stats.get("mean_action_count", 0.0)),
        mean_selected_screen_score=float(stats.get("mean_selected_screen_score", 0.0)),
        mean_vote_entropy_proxy=float(stats.get("mean_vote_entropy_proxy", 0.0)),
        mean_profile_spread=float(stats.get("mean_profile_spread", 0.0)),
        mean_ranker_spread=float(stats.get("mean_ranker_spread", 0.0)),
        union_decisive_situations=int(stats.get("union_decisive_situations", 0)),
        mean_union_margin=float(stats.get("mean_union_margin", 0.0)),
        hybrid_hits_union_best_rate=float(stats.get("hybrid_hits_union_best_rate", 0.0)),
        unscreened_hits_union_best_rate=float(stats.get("unscreened_hits_union_best_rate", 0.0)),
        screened_hits_union_best_rate=float(stats.get("screened_hits_union_best_rate", 0.0)),
        screen_vote_hits_union_best_rate=float(stats.get("screen_vote_hits_union_best_rate", 0.0)),
        behavior_chosen_hits_union_best_rate=float(stats.get("behavior_chosen_hits_union_best_rate", 0.0)),
        mean_hybrid_lost_value_to_union_best=float(stats.get("mean_hybrid_lost_value_to_union_best", 0.0)),
        mean_unscreened_lost_value_to_union_best=float(stats.get("mean_unscreened_lost_value_to_union_best", 0.0)),
        mean_screened_lost_value_to_union_best=float(stats.get("mean_screened_lost_value_to_union_best", 0.0)),
        hybrid_better_than_both_situations=int(stats.get("hybrid_better_than_both_situations", 0)),
        hybrid_worse_than_both_situations=int(stats.get("hybrid_worse_than_both_situations", 0)),
        ranker_revision=str(ranker_revision),
        ranker_available_frames_seen=int(ranker_available_frames),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return selected_frame_rows, candidate_rows, method_rows, branch_rows, screen_rows, list(finalized_transitions), summary
