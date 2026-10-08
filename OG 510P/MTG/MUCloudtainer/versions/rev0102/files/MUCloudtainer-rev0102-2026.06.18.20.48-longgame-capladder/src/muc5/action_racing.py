from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence

from .action_budget import select_budgeted_action_indices
from .action_counterfactual import (
    ActionCounterfactualGameSpec,
    _apply_and_collect_transition,
    _finalize_cpp_rows,
    _rollout_branch,
)
from .action_features import action_feature_dict
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import GameState, start_game
from .imitation import context_feature_dict
from .mulligan import MulliganPolicy
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class AdaptiveActionCounterfactualSummary:
    """Summary for adaptive/racing action-counterfactual labels.

    rev0036 moves from a fixed rollouts-per-action labeler to a tiny racing
    labeler.  Every sampled legal action still gets a base rollout, but extra
    rollouts are spent on the current top contenders when the best-vs-second
    gap remains small.  The summary keeps the allocation visible because these
    are offline labels, not a proof of full-game optimality.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    sampled_situations: int
    skipped_high_action_frames: int
    full_menu_situations: int
    budgeted_situations: int
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
    mean_best_minus_chosen: float
    behavior_chosen_best_rate: float
    decisive_situations: int
    mean_label_confidence_proxy: float
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _stdev(vals: Sequence[float]) -> float:
    if len(vals) <= 1:
        return 0.0
    mean = sum(float(v) for v in vals) / float(len(vals))
    return (sum((float(v) - mean) ** 2 for v in vals) / float(len(vals) - 1)) ** 0.5


def _branch_action_once(
    *,
    pre_branch_state: GameState,
    frame_action_strings: Sequence[str],
    action_idx: int,
    rollout: int,
    situation_id: str,
    agents: Sequence[PublicDecisionAgent],
    actor: int,
    branch_max_decisions: int,
    transition_rows: list[Dict[str, object]],
    records: list[TransitionMicroRecord],
    expected_sigs: list[str],
    row_indices: list[int],
) -> tuple[float, Dict[str, object]]:
    """Apply one counterfactual first action and roll the branch out."""

    branch_state = copy.deepcopy(pre_branch_state)
    branch_frame = build_decision_frame(branch_state)
    if tuple(branch_frame.legal_action_strings) != tuple(frame_action_strings):
        raise ValueError(f"{situation_id}: branch legal menu drift before action")
    stable = sum((i + 1) * ord(ch) for i, ch in enumerate(str(situation_id)))
    branch_seed = 936000000 + (stable + int(action_idx) * 1009 + int(rollout) * 9176) % 100000000
    branch_rng = Random(int(branch_seed))
    first_action = branch_frame.legal_actions[action_idx]
    _apply_and_collect_transition(
        branch_state,
        branch_frame,
        action_idx,
        branch_rng,
        case_id=f"{situation_id}_a{action_idx:02d}_r{rollout:02d}_first_{first_action.kind}",
        transition_rows=transition_rows,
        records=records,
        expected_sigs=expected_sigs,
        row_indices=row_indices,
    )
    score, result, branch_decisions, turn_number = _rollout_branch(
        branch_state,
        agents,
        actor=actor,
        branch_seed=int(branch_seed) + 37,
        max_decisions=int(branch_max_decisions),
        case_prefix=f"{situation_id}_a{action_idx:02d}_r{rollout:02d}",
        transition_rows=transition_rows,
        records=records,
        expected_sigs=expected_sigs,
        row_indices=row_indices,
    )
    meta = {
        "branch_id": f"{situation_id}_a{action_idx:02d}_r{rollout:02d}",
        "rollout": int(rollout),
        "actor_score": float(score),
        "winner": "None" if result.winner is None else int(result.winner),
        "loss_reason": result.loss_reason,
        "branch_decisions": int(branch_decisions),
        "turn_number": int(turn_number),
    }
    return float(score), meta


def _allocation_priority(scores_by_action: Mapping[int, Sequence[float]], *, rng: Random) -> tuple[int, int | None, float, float, float]:
    """Pick the current top contender and its challenger.

    Returns top action, second action, margin, pseudo uncertainty, and confidence.
    The uncertainty intentionally includes a pseudo-count term so a one-rollout
    tie still asks for more evidence instead of falsely looking certain.
    """

    stats = []
    for idx, vals in scores_by_action.items():
        n = max(1, len(vals))
        mean = sum(float(v) for v in vals) / float(n)
        sd = _stdev(vals)
        # Binary-ish bounded rewards: use a conservative pseudo standard error
        # until real samples are present.
        stderr = max(sd / (n ** 0.5), 0.25 / (n ** 0.5))
        stats.append((mean, -stderr, rng.random(), int(idx), n, stderr))
    stats.sort(reverse=True)
    top = stats[0]
    second = stats[1] if len(stats) > 1 else None
    if second is None:
        return int(top[3]), None, 1.0, float(top[5]), 1.0
    margin = float(top[0] - second[0])
    uncertainty = float(top[5] + second[5])
    confidence = float(margin / (margin + uncertainty + 1e-9))
    return int(top[3]), int(second[3]), margin, uncertainty, confidence


def collect_adaptive_action_counterfactuals(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0036",
    max_situations: int = 24,
    max_actions_per_frame: int = 4,
    sample_high_action_frames: bool = True,
    branch_action_budget: int | None = 6,
    budget_rng_seed: int = 36036,
    base_rollouts_per_action: int = 1,
    max_extra_rollouts_per_situation: int = 6,
    adaptive_stop_margin: float = 0.50,
    adaptive_target_confidence: float = 0.62,
    branch_max_decisions: int = 320,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], AdaptiveActionCounterfactualSummary]:
    """Collect action-counterfactual labels with adaptive branch allocation.

    All selected actions receive ``base_rollouts_per_action`` rollouts.  Extra
    rollouts are then assigned to the top two empirical contenders until the
    margin looks decisive or the per-situation extra budget is exhausted.
    """

    candidate_rows: list[Dict[str, object]] = []
    branch_rows: list[Dict[str, object]] = []
    transition_rows: list[Dict[str, object]] = []
    records: list[TransitionMicroRecord] = []
    expected_sigs: list[str] = []
    row_indices: list[int] = []

    skipped_high = 0
    full_menu_situations = 0
    budgeted_situations = 0
    behavior_decisions = 0
    situation_count = 0
    adaptive_extra = 0
    early_stops = 0
    branch_terminal = 0
    branch_truncations = 0
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

    for spec_i, spec in enumerate(specs):
        if situation_count >= int(max_situations):
            break
        transition_rng = Random(int(spec.seed))
        agent_rng = Random(int(spec.seed) + 1000003)
        state = start_game(
            spec.deck0,
            spec.deck1,
            seed=int(spec.seed),
            starting_player=int(spec.starting_player),
            starting_life=int(spec.starting_life),
            mulligan_agents=(mulligan(spec.mulligan0), mulligan(spec.mulligan1)),
            record_log=False,
        )
        agents = [agent(spec.agent0), agent(spec.agent1)]
        for step in range(1, int(spec.max_decisions) + 1):
            if situation_count >= int(max_situations) or state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"behavior policy chose illegal action index {chosen_idx}/{frame.action_count}")
            behavior_decisions += 1

            selected_indices: tuple[int, ...] = tuple()
            selection_reasons: dict[int, str] = {}
            branched_subset = False
            if frame.action_count > 1 and frame.action_count <= int(max_actions_per_frame):
                selected_indices = tuple(range(frame.action_count))
                selection_reasons = {i: "full_menu_within_max_actions" for i in selected_indices}
                full_menu_situations += 1
            elif frame.action_count > int(max_actions_per_frame) and sample_high_action_frames and branch_action_budget is not None:
                selector_rng = Random(int(budget_rng_seed) + int(spec_i) * 1000003 + int(step) * 9176 + int(situation_count))
                selection = select_budgeted_action_indices(frame, chosen_idx, budget=int(branch_action_budget), rng=selector_rng)
                selected_indices = tuple(selection.indices)
                selection_reasons = dict(selection.reasons)
                branched_subset = bool(selection.is_subset)
                if len(selected_indices) > 1:
                    budgeted_situations += 1
                else:
                    skipped_high += 1
            elif frame.action_count > int(max_actions_per_frame):
                skipped_high += 1

            if len(selected_indices) > 1:
                situation_id = f"arace_s{situation_count:04d}_{spec.game_id}_step{step:04d}"
                actor = int(frame.player)
                pre_branch_state = copy.deepcopy(state)
                ctx = context_feature_dict(frame.observation)
                frame_action_strings = tuple(frame.legal_action_strings)
                scores_by_action: dict[int, list[float]] = {int(i): [] for i in selected_indices}
                rollout_meta_by_action: dict[int, list[Dict[str, object]]] = {int(i): [] for i in selected_indices}
                allocation_rows: list[Dict[str, object]] = []
                allocation_rng = Random(int(budget_rng_seed) + 17 * situation_count)

                rollout_counter = 0
                for action_idx in selected_indices:
                    for _ in range(int(base_rollouts_per_action)):
                        score, meta = _branch_action_once(
                            pre_branch_state=pre_branch_state,
                            frame_action_strings=frame_action_strings,
                            action_idx=int(action_idx),
                            rollout=rollout_counter,
                            situation_id=situation_id,
                            agents=agents,
                            actor=actor,
                            branch_max_decisions=int(branch_max_decisions),
                            transition_rows=transition_rows,
                            records=records,
                            expected_sigs=expected_sigs,
                            row_indices=row_indices,
                        )
                        rollout_counter += 1
                        scores_by_action[int(action_idx)].append(float(score))
                        rollout_meta_by_action[int(action_idx)].append(meta)
                        if str(meta.get("winner")) == "None":
                            branch_truncations += 1
                        else:
                            branch_terminal += 1
                        allocation_rows.append({"phase": "base", "action_index": int(action_idx), "rollout": int(meta["rollout"]), "score": float(score)})

                extra_used = 0
                stopped_early = False
                while extra_used < int(max_extra_rollouts_per_situation):
                    top_idx, second_idx, margin, uncertainty, confidence = _allocation_priority(scores_by_action, rng=allocation_rng)
                    if second_idx is None:
                        stopped_early = True
                        break
                    min_contender_rollouts = min(len(scores_by_action[top_idx]), len(scores_by_action[second_idx]))
                    if min_contender_rollouts >= 2 and (margin >= float(adaptive_stop_margin) or confidence >= float(adaptive_target_confidence)):
                        stopped_early = True
                        break
                    # Prefer the less-sampled of the top two.  If tied, sample
                    # the empirical leader first to confirm it, then challenger.
                    if len(scores_by_action[top_idx]) <= len(scores_by_action[second_idx]):
                        chosen_for_extra = top_idx
                    else:
                        chosen_for_extra = second_idx
                    score, meta = _branch_action_once(
                        pre_branch_state=pre_branch_state,
                        frame_action_strings=frame_action_strings,
                        action_idx=int(chosen_for_extra),
                        rollout=rollout_counter,
                        situation_id=situation_id,
                        agents=agents,
                        actor=actor,
                        branch_max_decisions=int(branch_max_decisions),
                        transition_rows=transition_rows,
                        records=records,
                        expected_sigs=expected_sigs,
                        row_indices=row_indices,
                    )
                    rollout_counter += 1
                    extra_used += 1
                    adaptive_extra += 1
                    scores_by_action[int(chosen_for_extra)].append(float(score))
                    rollout_meta_by_action[int(chosen_for_extra)].append(meta)
                    if str(meta.get("winner")) == "None":
                        branch_truncations += 1
                    else:
                        branch_terminal += 1
                    allocation_rows.append({
                        "phase": "adaptive",
                        "action_index": int(chosen_for_extra),
                        "rollout": int(meta["rollout"]),
                        "score": float(score),
                        "pre_extra_margin": float(margin),
                        "pre_extra_uncertainty": float(uncertainty),
                        "pre_extra_confidence": float(confidence),
                    })
                if stopped_early:
                    early_stops += 1

                means = {i: sum(vals) / max(1, len(vals)) for i, vals in scores_by_action.items()}
                stdevs = {i: _stdev(vals) for i, vals in scores_by_action.items()}
                rollouts = {i: len(vals) for i, vals in scores_by_action.items()}
                best = max(means.values()) if means else 0.0
                chosen_score = float(means.get(chosen_idx, 0.0))
                sorted_means = sorted(means.values(), reverse=True)
                second_best = float(sorted_means[1]) if len(sorted_means) > 1 else float(best)
                situation_margin = float(best - second_best)
                mean_stdev = float(sum(stdevs.values()) / max(1, len(stdevs)))
                # Includes a rollouts factor so repeated samples are more trusted
                # than one lucky decisive branch.
                mean_rollouts = float(sum(rollouts.values()) / max(1, len(rollouts)))
                confidence = float(situation_margin / (situation_margin + mean_stdev + (0.25 / max(1.0, mean_rollouts ** 0.5)) + 1e-9))
                best_indices = {i for i, v in means.items() if abs(v - best) <= 1e-9}

                for action_idx in selected_indices:
                    action = frame.legal_actions[action_idx]
                    for meta in rollout_meta_by_action[int(action_idx)]:
                        branch_rows.append({
                            "revision": revision,
                            "situation_id": situation_id,
                            "branch_id": meta["branch_id"],
                            "behavior_game_id": spec.game_id,
                            "step": int(step),
                            "player": actor,
                            "action_index": int(action_idx),
                            "action_count": int(frame.action_count),
                            "branched_action_count": int(len(selected_indices)),
                            "branched_subset": int(branched_subset),
                            "budget_reason": selection_reasons.get(int(action_idx), ""),
                            "behavior_chosen": 1 if int(action_idx) == chosen_idx else 0,
                            "rollout": int(meta["rollout"]),
                            "action": action.compact(),
                            "actor_score": float(meta["actor_score"]),
                            "winner": meta["winner"],
                            "loss_reason": meta["loss_reason"],
                            "branch_decisions": int(meta["branch_decisions"]),
                            "turn_number": int(meta["turn_number"]),
                            "starting_life": int(spec.starting_life),
                            "starting_player": int(spec.starting_player),
                            "agent0": spec.agent0,
                            "agent1": spec.agent1,
                            "mulligan0": str(spec.mulligan0),
                            "mulligan1": str(spec.mulligan1),
                            "allocation": "adaptive" if int(meta["rollout"]) >= int(base_rollouts_per_action) * len(selected_indices) else "base",
                        })
                    feats: dict[str, float] = {}
                    feats.update(ctx)
                    feats.update(action_feature_dict(action, frame.observation))
                    row: Dict[str, object] = {
                        "revision": revision,
                        "situation_id": situation_id,
                        "behavior_game_id": spec.game_id,
                        "step": int(step),
                        "player": actor,
                        "action_index": int(action_idx),
                        "action_count": int(frame.action_count),
                        "branched_action_count": int(len(selected_indices)),
                        "branched_subset": int(branched_subset),
                        "budget_reason": selection_reasons.get(int(action_idx), ""),
                        "action": action.compact(),
                        "behavior_chosen": 1 if int(action_idx) == chosen_idx else 0,
                        "branch_rollouts": int(rollouts[int(action_idx)]),
                        "base_rollouts_per_action": int(base_rollouts_per_action),
                        "adaptive_extra_rollouts_for_action": int(max(0, rollouts[int(action_idx)] - int(base_rollouts_per_action))),
                        "total_adaptive_extra_rollouts": int(extra_used),
                        "adaptive_stopped_early": int(stopped_early),
                        "mean_actor_score": float(means[int(action_idx)]),
                        "actor_score_stdev": float(stdevs.get(int(action_idx), 0.0)),
                        "best_mean_actor_score": float(best),
                        "second_best_mean_actor_score": float(second_best),
                        "chosen_mean_actor_score": float(chosen_score),
                        "value_gap_to_best": float(best - means[int(action_idx)]),
                        "situation_best_margin": float(situation_margin),
                        "label_confidence_proxy": float(confidence),
                        "is_best_action": 1 if int(action_idx) in best_indices else 0,
                        "behavior_chosen_is_best": 1 if chosen_idx in best_indices else 0,
                        "starting_life": int(spec.starting_life),
                        "starting_player": int(spec.starting_player),
                        "agent0": spec.agent0,
                        "agent1": spec.agent1,
                        "mulligan0": str(spec.mulligan0),
                        "mulligan1": str(spec.mulligan1),
                    }
                    row.update(feats)
                    candidate_rows.append(row)
                situation_count += 1

            apply_decision_index(state, frame, chosen_idx, transition_rng)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    by_situation: dict[str, list[Mapping[str, object]]] = {}
    for row in candidate_rows:
        by_situation.setdefault(str(row["situation_id"]), []).append(row)
    action_counts = [int(rows[0]["action_count"]) for rows in by_situation.values() if rows]
    branched_counts = [int(rows[0]["branched_action_count"]) for rows in by_situation.values() if rows]
    regrets = []
    chosen_best = 0
    decisive = 0
    confidences = []
    for rows in by_situation.values():
        chosen = [r for r in rows if int(r["behavior_chosen"]) == 1]
        if chosen:
            regrets.append(float(chosen[0]["best_mean_actor_score"]) - float(chosen[0]["chosen_mean_actor_score"]))
            chosen_best += int(chosen[0]["behavior_chosen_is_best"])
        margins = [float(r["situation_best_margin"]) for r in rows[:1]]
        conf = [float(r["label_confidence_proxy"]) for r in rows[:1]]
        confidences.extend(conf)
        if margins and margins[0] > 1e-9:
            decisive += 1
    total_rollouts = sum(int(r.get("branch_rollouts", 0)) for r in candidate_rows)
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    summary = AdaptiveActionCounterfactualSummary(
        revision=revision,
        behavior_games=len(specs),
        behavior_decisions=int(behavior_decisions),
        sampled_situations=int(situation_count),
        skipped_high_action_frames=int(skipped_high),
        full_menu_situations=int(full_menu_situations),
        budgeted_situations=int(budgeted_situations),
        candidate_actions=int(len(candidate_rows)),
        branch_games=int(len(branch_rows)),
        base_rollouts_per_action=int(base_rollouts_per_action),
        max_extra_rollouts_per_situation=int(max_extra_rollouts_per_situation),
        adaptive_extra_rollouts=int(adaptive_extra),
        early_stops=int(early_stops),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_truncations),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=float(sum(action_counts) / max(1, len(action_counts))),
        mean_branched_action_count=float(sum(branched_counts) / max(1, len(branched_counts))),
        mean_rollouts_per_action=float(total_rollouts / max(1, len(candidate_rows))),
        mean_best_minus_chosen=float(sum(regrets) / max(1, len(regrets))),
        behavior_chosen_best_rate=float(chosen_best / max(1, len(by_situation))),
        decisive_situations=int(decisive),
        mean_label_confidence_proxy=float(sum(confidences) / max(1, len(confidences))),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return candidate_rows, branch_rows, list(finalized_transitions), summary
