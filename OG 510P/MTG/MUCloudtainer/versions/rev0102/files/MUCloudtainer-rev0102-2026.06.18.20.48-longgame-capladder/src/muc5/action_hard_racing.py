from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence

from .action_counterfactual import ActionCounterfactualGameSpec, _finalize_cpp_rows
from .action_disagreement import _screen_votes
from .action_features import action_feature_dict
from .action_hard_frame import (
    HardFrameSnapshot,
    _profile_score_spread,
    _ranker_score_spread,
    hard_frame_screen_score,
)
from .action_hybrid_selector import select_hybrid_action_indices
from .action_racing import _allocation_priority, _branch_action_once, _stdev
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class HardFrameOnlineRacingSummary:
    """Summary for the online hard-frame adaptive/racing label collector.

    rev0043 combines rev0041's public hard-frame queue with rev0036's live
    branch-allocation idea.  Unlike rev0042's audit over a pre-generated branch
    matrix, this collector spends branch rollouts online: every selected action
    gets a base sample, then extra samples are allocated to current top
    contenders until the margin/confidence heuristic says to stop or the budget
    is exhausted.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    candidate_frames_seen: int
    frames_with_disagreement: int
    selected_situations: int
    high_action_selected: int
    subset_situations: int
    candidate_actions: int
    branch_games: int
    base_rollouts_per_action: int
    max_extra_rollouts_per_situation: int
    adaptive_extra_rollouts: int
    early_stops: int
    branch_terminal_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    mean_action_count: float
    mean_branched_action_count: float
    mean_rollouts_per_action: float
    decisive_situations: int
    decisive_per_100_rollouts: float
    mean_best_minus_chosen: float
    behavior_chosen_best_rate: float
    mean_label_confidence_proxy: float
    mean_selected_screen_score: float
    mean_vote_entropy_proxy: float
    mean_profile_spread: float
    mean_ranker_spread: float
    ranker_revision: str
    ranker_available_frames_seen: int
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _mean(xs: Sequence[float | int]) -> float:
    return float(sum(float(x) for x in xs) / max(1, len(xs)))


def _hard_snapshots(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str,
    screen_agent_names: Sequence[str],
    min_unique_screen_votes: int,
    max_behavior_frames: int,
    high_action_threshold: int,
    ranker_revision: str,
    max_situations: int,
    max_per_behavior_game: int,
) -> tuple[list[HardFrameSnapshot], list[Dict[str, object]], Dict[str, int]]:
    """Collect public-only hard-frame snapshots without running branch games."""

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

    ordered = sorted(snapshots, key=lambda s: (-s.screen_score, -s.action_count, -s.vote_entropy_proxy, s.situation_seed_id))
    selected: list[HardFrameSnapshot] = []
    per_game: dict[str, int] = {}
    cap = max(1, int(max_per_behavior_game))
    for snap in ordered:
        gid = str(snap.spec.game_id)
        if per_game.get(gid, 0) >= cap:
            continue
        selected.append(snap)
        per_game[gid] = per_game.get(gid, 0) + 1
        if len(selected) >= int(max_situations):
            break
    if len(selected) < int(max_situations):
        seen = {s.situation_seed_id for s in selected}
        for snap in ordered:
            if snap.situation_seed_id in seen:
                continue
            selected.append(snap)
            if len(selected) >= int(max_situations):
                break

    # Store vote rows only for selected frames in the caller.  The global rows
    # here are not stable until situation_ids are assigned, so return stats only.
    stats = {
        "behavior_decisions": int(behavior_decisions),
        "choice_frames_seen": int(choice_seen),
        "candidate_frames_seen": int(candidate_frames_seen),
        "frames_with_disagreement": int(frames_with_disagreement),
        "ranker_available_frames": int(ranker_available_frames),
    }
    return selected, [], stats




def _race_selected_snapshots(
    selected_snaps: Sequence[HardFrameSnapshot],
    stats: Mapping[str, int],
    *,
    revision: str,
    behavior_games: int,
    high_action_threshold: int,
    max_actions_per_frame: int,
    branch_action_budget: int,
    branch_max_decisions: int,
    budget_rng_seed: int,
    ranker_revision: str,
    base_rollouts_per_action: int,
    max_extra_rollouts_per_situation: int,
    adaptive_stop_margin: float,
    adaptive_target_confidence: float,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], HardFrameOnlineRacingSummary]:
    """Run online branch racing over already-selected hard-frame snapshots.

    This refactor keeps public hard-frame selection separate from expensive
    offline branch labeling.  It lets rev0044 and later selectors rerank a
    public-safe candidate pool without duplicating the branch/racing/C++ shadow
    machinery.
    """
    selected_rows: list[Dict[str, object]] = []
    candidate_rows: list[Dict[str, object]] = []
    branch_rows: list[Dict[str, object]] = []
    allocation_rows: list[Dict[str, object]] = []
    screen_rows: list[Dict[str, object]] = []
    transition_rows: list[Dict[str, object]] = []
    records: list[TransitionMicroRecord] = []
    expected_sigs: list[str] = []
    row_indices: list[int] = []

    agent_cache: dict[str, PublicDecisionAgent] = {}

    def agent(name: str) -> PublicDecisionAgent:
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    branch_terminal = 0
    branch_trunc = 0
    adaptive_extra = 0
    early_stops = 0
    subset_situations = 0
    total_rollouts = 0

    for sampled, snap in enumerate(selected_snaps):
        spec = snap.spec
        frame = snap.frame
        chosen_idx = int(snap.chosen_idx)
        selected_idx, selection_reasons, is_subset, skipped, meta = select_hybrid_action_indices(
            frame,
            chosen_idx,
            snap.unique_votes,
            max_actions_per_frame=int(max_actions_per_frame),
            branch_action_budget=int(branch_action_budget),
            rng=Random(int(budget_rng_seed) + sampled * 101 + snap.step),
            ranker_revision=str(ranker_revision),
        )
        if skipped or len(selected_idx) <= 1:
            continue
        if is_subset:
            subset_situations += 1
        situation_id = f"{revision}_s{sampled:04d}_{spec.game_id}_step{snap.step:04d}"
        selected_rows.append({
            "revision": revision,
            "situation_id": situation_id,
            "source_candidate_id": snap.situation_seed_id,
            "behavior_game_id": spec.game_id,
            "step": int(snap.step),
            "player": int(frame.player),
            "action_count": int(frame.action_count),
            "branched_action_count": int(len(selected_idx)),
            "branched_subset": int(is_subset),
            "behavior_chosen_index": int(chosen_idx),
            "behavior_chosen_action": frame.legal_actions[chosen_idx].compact(),
            "screen_unique_votes": int(len(snap.unique_votes)),
            "screen_vote_entropy_proxy": float(snap.vote_entropy_proxy),
            "profile_spread": float(snap.profile_spread),
            "ranker_spread": float(snap.ranker_spread),
            "screen_score": float(snap.screen_score),
            "high_action_bonus": float(snap.high_action_bonus),
            "screen_reason": snap.reason,
            "ranker_available_for_selector": int(bool(meta and meta.ranker_available)),
            "starting_life": int(spec.starting_life),
            "starting_player": int(spec.starting_player),
            "agent0": spec.agent0,
            "agent1": spec.agent1,
            "mulligan0": str(spec.mulligan0),
            "mulligan1": str(spec.mulligan1),
        })
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

        agents = (agent(spec.agent0), agent(spec.agent1))
        ctx = context_feature_dict(frame.observation)
        scores_by_action: dict[int, list[float]] = {int(i): [] for i in selected_idx}
        metas_by_action: dict[int, list[Dict[str, object]]] = {int(i): [] for i in selected_idx}

        # Base rollout for every selected action.
        for action_idx in selected_idx:
            for _ in range(int(base_rollouts_per_action)):
                rollout = len(metas_by_action[int(action_idx)])
                score, meta_row = _branch_action_once(
                    pre_branch_state=snap.state,
                    frame_action_strings=frame.legal_action_strings,
                    action_idx=int(action_idx),
                    rollout=int(rollout),
                    situation_id=situation_id,
                    agents=agents,
                    actor=int(frame.player),
                    branch_max_decisions=int(branch_max_decisions),
                    transition_rows=transition_rows,
                    records=records,
                    expected_sigs=expected_sigs,
                    row_indices=row_indices,
                )
                scores_by_action[int(action_idx)].append(float(score))
                metas_by_action[int(action_idx)].append(meta_row)
                total_rollouts += 1
                if str(meta_row.get("winner")) == "None":
                    branch_trunc += 1
                else:
                    branch_terminal += 1
                allocation_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "phase": "base",
                    "action_index": int(action_idx),
                    "rollout": int(rollout),
                    "score": float(score),
                    "pre_extra_margin": 0.0,
                    "pre_extra_uncertainty": 0.0,
                    "pre_extra_confidence": 0.0,
                })

        stopped_early = False
        extra_used = 0
        while extra_used < int(max_extra_rollouts_per_situation):
            top, runner, margin, uncertainty, confidence = _allocation_priority(scores_by_action, rng=Random(int(budget_rng_seed) + sampled * 977 + extra_used))
            if runner is not None and margin >= float(adaptive_stop_margin) and confidence >= float(adaptive_target_confidence):
                stopped_early = True
                break
            # Spend on the action with fewer samples among the top pair, with a
            # bias toward the current top if tied.  This is online: no unseen
            # future rollouts are generated or inspected.
            options = [top] if runner is None else [top, runner]
            options = sorted(options, key=lambda i: (len(scores_by_action[int(i)]), 0 if int(i) == top else 1))
            action_idx = int(options[0])
            rollout = len(metas_by_action[action_idx])
            score, meta_row = _branch_action_once(
                pre_branch_state=snap.state,
                frame_action_strings=frame.legal_action_strings,
                action_idx=action_idx,
                rollout=int(rollout),
                situation_id=situation_id,
                agents=agents,
                actor=int(frame.player),
                branch_max_decisions=int(branch_max_decisions),
                transition_rows=transition_rows,
                records=records,
                expected_sigs=expected_sigs,
                row_indices=row_indices,
            )
            scores_by_action[action_idx].append(float(score))
            metas_by_action[action_idx].append(meta_row)
            adaptive_extra += 1
            extra_used += 1
            total_rollouts += 1
            if str(meta_row.get("winner")) == "None":
                branch_trunc += 1
            else:
                branch_terminal += 1
            allocation_rows.append({
                "revision": revision,
                "situation_id": situation_id,
                "phase": "adaptive",
                "action_index": int(action_idx),
                "rollout": int(rollout),
                "score": float(score),
                "pre_extra_margin": float(margin),
                "pre_extra_uncertainty": float(uncertainty),
                "pre_extra_confidence": float(confidence),
            })
        if stopped_early:
            early_stops += 1

        means = {i: _mean(vals) for i, vals in scores_by_action.items()}
        stdevs = {i: _stdev(vals) for i, vals in scores_by_action.items()}
        rollouts = {i: len(vals) for i, vals in scores_by_action.items()}
        best_score = max(means.values()) if means else 0.0
        chosen_score = float(means.get(chosen_idx, 0.0))
        sorted_means = sorted(means.values(), reverse=True)
        second_best = float(sorted_means[1]) if len(sorted_means) > 1 else float(best_score)
        margin = float(best_score - second_best)
        mean_stdev = _mean(tuple(stdevs.values()))
        mean_rollouts = _mean(tuple(rollouts.values()))
        confidence = float(margin / (margin + mean_stdev + (0.25 / max(1.0, mean_rollouts ** 0.5)) + 1e-9))
        best_indices = {i for i, score in means.items() if abs(float(score) - float(best_score)) <= 1e-9}

        for action_idx in selected_idx:
            action = frame.legal_actions[int(action_idx)]
            for m in metas_by_action[int(action_idx)]:
                branch_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "branch_id": m["branch_id"],
                    "behavior_game_id": spec.game_id,
                    "step": int(snap.step),
                    "player": int(frame.player),
                    "action_index": int(action_idx),
                    "action_count": int(frame.action_count),
                    "branched_action_count": int(len(selected_idx)),
                    "branched_subset": int(is_subset),
                    "budget_reason": selection_reasons.get(int(action_idx), ""),
                    "behavior_chosen": 1 if int(action_idx) == chosen_idx else 0,
                    "screen_voted_action": 1 if int(action_idx) in set(snap.unique_votes) else 0,
                    "rollout": int(m["rollout"]),
                    "action": action.compact(),
                    "actor_score": float(m["actor_score"]),
                    "winner": m["winner"],
                    "loss_reason": m["loss_reason"],
                    "branch_decisions": int(m["branch_decisions"]),
                    "turn_number": int(m["turn_number"]),
                    "starting_life": int(spec.starting_life),
                    "starting_player": int(spec.starting_player),
                    "allocation": "adaptive" if int(m["rollout"]) >= int(base_rollouts_per_action) else "base",
                })
            feats: dict[str, float] = {}
            feats.update(ctx)
            feats.update(action_feature_dict(action, frame.observation))
            row: Dict[str, object] = {
                "revision": revision,
                "situation_id": situation_id,
                "source_candidate_id": snap.situation_seed_id,
                "behavior_game_id": spec.game_id,
                "step": int(snap.step),
                "player": int(frame.player),
                "action_index": int(action_idx),
                "action_count": int(frame.action_count),
                "branched_action_count": int(len(selected_idx)),
                "branched_subset": int(is_subset),
                "budget_reason": selection_reasons.get(int(action_idx), ""),
                "action": action.compact(),
                "behavior_chosen": 1 if int(action_idx) == chosen_idx else 0,
                "screen_voted_action": 1 if int(action_idx) in set(snap.unique_votes) else 0,
                "branch_rollouts": int(rollouts[int(action_idx)]),
                "base_rollouts_per_action": int(base_rollouts_per_action),
                "adaptive_extra_rollouts_for_action": int(max(0, rollouts[int(action_idx)] - int(base_rollouts_per_action))),
                "total_adaptive_extra_rollouts": int(extra_used),
                "adaptive_stopped_early": int(stopped_early),
                "mean_actor_score": float(means[int(action_idx)]),
                "actor_score_stdev": float(stdevs.get(int(action_idx), 0.0)),
                "best_mean_actor_score": float(best_score),
                "second_best_mean_actor_score": float(second_best),
                "chosen_mean_actor_score": float(chosen_score),
                "value_gap_to_best": float(best_score - means[int(action_idx)]),
                "situation_best_margin": float(margin),
                "label_confidence_proxy": float(confidence),
                "is_best_action": 1 if int(action_idx) in best_indices else 0,
                "behavior_chosen_is_best": 1 if chosen_idx in best_indices else 0,
                "screen_score": float(snap.screen_score),
                "screen_reason": snap.reason,
                "screen_unique_votes": int(len(snap.unique_votes)),
                "screen_vote_entropy_proxy": float(snap.vote_entropy_proxy),
                "profile_spread": float(snap.profile_spread),
                "ranker_spread": float(snap.ranker_spread),
                "starting_life": int(spec.starting_life),
                "starting_player": int(spec.starting_player),
                "agent0": spec.agent0,
                "agent1": spec.agent1,
                "mulligan0": str(spec.mulligan0),
                "mulligan1": str(spec.mulligan1),
            }
            row.update(feats)
            candidate_rows.append(row)

    cpp_mismatches, finalized = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    skipped_rows = [r for r in finalized if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized if r.get("cpp_match") is False]
    by_situation: dict[str, list[Mapping[str, object]]] = {}
    for row in candidate_rows:
        by_situation.setdefault(str(row["situation_id"]), []).append(row)
    action_counts = [int(rows[0]["action_count"]) for rows in by_situation.values() if rows]
    branched_counts = [int(rows[0]["branched_action_count"]) for rows in by_situation.values() if rows]
    margins = [float(rows[0]["situation_best_margin"]) for rows in by_situation.values() if rows]
    confidences = [float(rows[0]["label_confidence_proxy"]) for rows in by_situation.values() if rows]
    screen_scores = [float(r.get("screen_score", 0.0)) for r in selected_rows]
    vote_entropy = [float(r.get("screen_vote_entropy_proxy", 0.0)) for r in selected_rows]
    profile_spread = [float(r.get("profile_spread", 0.0)) for r in selected_rows]
    ranker_spread = [float(r.get("ranker_spread", 0.0)) for r in selected_rows]
    regrets: list[float] = []
    chosen_best = 0
    for rows in by_situation.values():
        chosen = [r for r in rows if int(r["behavior_chosen"]) == 1]
        if chosen:
            regrets.append(float(chosen[0]["best_mean_actor_score"]) - float(chosen[0]["chosen_mean_actor_score"]))
            chosen_best += int(chosen[0]["behavior_chosen_is_best"])
    decisive = int(sum(1 for x in margins if float(x) > 1e-9))
    summary = HardFrameOnlineRacingSummary(
        revision=revision,
        behavior_games=int(behavior_games),
        behavior_decisions=int(stats.get("behavior_decisions", 0)),
        choice_frames_seen=int(stats.get("choice_frames_seen", 0)),
        candidate_frames_seen=int(stats.get("candidate_frames_seen", 0)),
        frames_with_disagreement=int(stats.get("frames_with_disagreement", 0)),
        selected_situations=int(len(by_situation)),
        high_action_selected=int(sum(1 for r in selected_rows if int(r.get("action_count", 0)) >= int(high_action_threshold))),
        subset_situations=int(subset_situations),
        candidate_actions=int(len(candidate_rows)),
        branch_games=int(len(branch_rows)),
        base_rollouts_per_action=int(base_rollouts_per_action),
        max_extra_rollouts_per_situation=int(max_extra_rollouts_per_situation),
        adaptive_extra_rollouts=int(adaptive_extra),
        early_stops=int(early_stops),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_trunc),
        cpp_checked_transitions=int(sum(1 for r in finalized if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=_mean(action_counts),
        mean_branched_action_count=_mean(branched_counts),
        mean_rollouts_per_action=float(total_rollouts / max(1, len(candidate_rows))),
        decisive_situations=int(decisive),
        decisive_per_100_rollouts=float(100.0 * decisive / max(1, total_rollouts)),
        mean_best_minus_chosen=_mean(regrets),
        behavior_chosen_best_rate=float(chosen_best / max(1, len(by_situation))),
        mean_label_confidence_proxy=_mean(confidences),
        mean_selected_screen_score=_mean(screen_scores),
        mean_vote_entropy_proxy=_mean(vote_entropy),
        mean_profile_spread=_mean(profile_spread),
        mean_ranker_spread=_mean(ranker_spread),
        ranker_revision=str(ranker_revision),
        ranker_available_frames_seen=int(stats.get("ranker_available_frames", 0)),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return selected_rows, candidate_rows, branch_rows, allocation_rows, screen_rows, list(finalized), summary
def collect_hard_frame_online_racing(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0043",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 2,
    max_behavior_frames: int = 220,
    max_situations: int = 12,
    high_action_threshold: int = 5,
    max_actions_per_frame: int = 3,
    branch_action_budget: int = 5,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 43043,
    ranker_revision: str = "rev0034",
    max_per_behavior_game: int = 2,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 8,
    adaptive_stop_margin: float = 0.50,
    adaptive_target_confidence: float = 0.62,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], HardFrameOnlineRacingSummary]:
    """Collect hard-frame action counterfactual labels with online racing.

    Public-only screeners choose hard frames.  A hybrid disagreement/diversity/
    ranker-prior selector chooses a branch subset.  Then branch rollouts are
    allocated online rather than generated as a full fixed matrix.
    """

    selected_snaps, _unused, stats = _hard_snapshots(
        specs,
        revision=revision,
        screen_agent_names=screen_agent_names,
        min_unique_screen_votes=min_unique_screen_votes,
        max_behavior_frames=max_behavior_frames,
        high_action_threshold=high_action_threshold,
        ranker_revision=ranker_revision,
        max_situations=max_situations,
        max_per_behavior_game=max_per_behavior_game,
    )

    return _race_selected_snapshots(
        selected_snaps,
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
