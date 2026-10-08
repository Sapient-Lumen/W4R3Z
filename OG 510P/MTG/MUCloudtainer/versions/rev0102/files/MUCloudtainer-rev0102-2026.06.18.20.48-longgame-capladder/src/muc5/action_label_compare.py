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
from .action_racing import _allocation_priority, _stdev, _branch_action_once
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import GameState, start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class MatchedActionLabelComparisonSummary:
    """Summary for fixed-vs-adaptive action-counterfactual labels.

    rev0037 measures a subtle but important question: does adaptive/racing label
    allocation change labels on the same public situations, and how many branch
    rollouts does it save/spend relative to fixed equal rollouts per action?
    This is a label-audit object, not a strategic-strength claim.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    sampled_situations: int
    candidate_actions: int
    branch_games: int
    fixed_rollouts_per_action: int
    adaptive_base_rollouts_per_action: int
    adaptive_max_extra_rollouts_per_situation: int
    fixed_total_rollouts: int
    adaptive_total_rollouts: int
    rollout_delta_adaptive_minus_fixed: int
    adaptive_early_stops: int
    full_menu_situations: int
    budgeted_situations: int
    skipped_high_action_frames: int
    fixed_decisive_situations: int
    adaptive_decisive_situations: int
    best_set_agreement_rate: float
    chosen_best_agreement_rate: float
    fixed_behavior_chosen_best_rate: float
    adaptive_behavior_chosen_best_rate: float
    mean_fixed_margin: float
    mean_adaptive_margin: float
    mean_abs_best_score_delta: float
    branch_terminal_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _score_for_method(
    scores_by_action: Mapping[int, Sequence[float]],
    *,
    chosen_idx: int,
    method: str,
    fixed_rollouts_per_action: int,
    adaptive_base_rollouts_per_action: int,
    adaptive_max_extra_rollouts_per_situation: int,
    adaptive_stop_margin: float,
    adaptive_target_confidence: float,
    rng: Random,
) -> tuple[dict[int, list[float]], dict[str, object]]:
    """Return action-score samples visible to one label-allocation method."""

    if method == "fixed_equal":
        selected = {int(i): list(vals[: int(fixed_rollouts_per_action)]) for i, vals in scores_by_action.items()}
        return selected, {"adaptive_extra_rollouts": 0, "adaptive_stopped_early": False}

    if method != "adaptive_race":
        raise ValueError(f"unknown label method {method!r}")

    selected = {int(i): list(vals[: int(adaptive_base_rollouts_per_action)]) for i, vals in scores_by_action.items()}
    next_slot = {int(i): int(adaptive_base_rollouts_per_action) for i in scores_by_action}
    extra_used = 0
    stopped = False
    while extra_used < int(adaptive_max_extra_rollouts_per_situation):
        top_idx, second_idx, margin, _uncertainty, confidence = _allocation_priority(selected, rng=rng)
        if second_idx is None:
            stopped = True
            break
        min_contender_rollouts = min(len(selected[top_idx]), len(selected[second_idx]))
        if min_contender_rollouts >= 2 and (margin >= float(adaptive_stop_margin) or confidence >= float(adaptive_target_confidence)):
            stopped = True
            break
        if len(selected[top_idx]) <= len(selected[second_idx]):
            target = top_idx
        else:
            target = second_idx
        if next_slot[target] >= len(scores_by_action[target]):
            # No precomputed rollout left for this contender. Try the runner-up;
            # if that is exhausted too, stop.  This keeps the comparator honest
            # about its finite label budget.
            alt = second_idx if target == top_idx else top_idx
            if next_slot[alt] >= len(scores_by_action[alt]):
                stopped = True
                break
            target = alt
        selected[target].append(float(scores_by_action[target][next_slot[target]]))
        next_slot[target] += 1
        extra_used += 1
    return selected, {"adaptive_extra_rollouts": int(extra_used), "adaptive_stopped_early": bool(stopped)}


def _method_rows(
    *,
    method: str,
    situation_id: str,
    frame,
    selected_indices: Sequence[int],
    chosen_idx: int,
    sampled_scores: Mapping[int, Sequence[float]],
    action_count: int,
    branched_subset: bool,
    selection_reasons: Mapping[int, str],
    ctx: Mapping[str, float],
    spec: ActionCounterfactualGameSpec,
    step: int,
    method_meta: Mapping[str, object],
) -> tuple[list[Dict[str, object]], Dict[str, object]]:
    means = {int(i): sum(map(float, vals)) / max(1, len(vals)) for i, vals in sampled_scores.items()}
    stdevs = {int(i): _stdev(tuple(map(float, vals))) for i, vals in sampled_scores.items()}
    best = max(means.values()) if means else 0.0
    sorted_means = sorted(means.values(), reverse=True)
    second_best = sorted_means[1] if len(sorted_means) > 1 else best
    margin = float(best - second_best)
    best_indices = {i for i, v in means.items() if abs(float(v) - best) < 1e-9}
    # Reuse the same rough confidence heuristic as the adaptive allocator.
    _top, _second, _m, _uncertainty, confidence = _allocation_priority(sampled_scores, rng=Random(370370 + len(situation_id)))
    chosen_score = float(means.get(int(chosen_idx), 0.0))
    rows: list[Dict[str, object]] = []
    for action_idx in selected_indices:
        action = frame.legal_actions[int(action_idx)]
        feats: dict[str, float] = {}
        feats.update(ctx)
        feats.update(action_feature_dict(action, frame.observation))
        row: Dict[str, object] = {
            "method": method,
            "situation_id": situation_id,
            "behavior_game_id": spec.game_id,
            "step": int(step),
            "player": int(frame.player),
            "action_index": int(action_idx),
            "action_count": int(action_count),
            "branched_action_count": int(len(selected_indices)),
            "branched_subset": int(bool(branched_subset)),
            "budget_reason": selection_reasons.get(int(action_idx), ""),
            "action": action.compact(),
            "behavior_chosen": 1 if int(action_idx) == int(chosen_idx) else 0,
            "branch_rollouts": int(len(sampled_scores[int(action_idx)])),
            "mean_actor_score": float(means[int(action_idx)]),
            "actor_score_stdev": float(stdevs.get(int(action_idx), 0.0)),
            "best_mean_actor_score": float(best),
            "second_best_mean_actor_score": float(second_best),
            "chosen_mean_actor_score": float(chosen_score),
            "value_gap_to_best": float(best - means[int(action_idx)]),
            "situation_best_margin": float(margin),
            "label_confidence_proxy": float(confidence),
            "is_best_action": 1 if int(action_idx) in best_indices else 0,
            "behavior_chosen_is_best": 1 if int(chosen_idx) in best_indices else 0,
            "adaptive_extra_rollouts": int(method_meta.get("adaptive_extra_rollouts", 0)),
            "adaptive_stopped_early": int(bool(method_meta.get("adaptive_stopped_early", False))),
            "starting_life": int(spec.starting_life),
            "starting_player": int(spec.starting_player),
            "agent0": spec.agent0,
            "agent1": spec.agent1,
            "mulligan0": str(spec.mulligan0),
            "mulligan1": str(spec.mulligan1),
        }
        row.update(feats)
        rows.append(row)
    sit = {
        "situation_id": situation_id,
        "method": method,
        "best_actions": "|".join(str(i) for i in sorted(best_indices)),
        "behavior_chosen_is_best": 1 if int(chosen_idx) in best_indices else 0,
        "best_mean_actor_score": float(best),
        "chosen_mean_actor_score": float(chosen_score),
        "situation_best_margin": float(margin),
        "label_confidence_proxy": float(confidence),
        "total_rollouts": int(sum(len(sampled_scores[int(i)]) for i in selected_indices)),
        "adaptive_extra_rollouts": int(method_meta.get("adaptive_extra_rollouts", 0)),
        "adaptive_stopped_early": int(bool(method_meta.get("adaptive_stopped_early", False))),
        "action_count": int(action_count),
        "branched_action_count": int(len(selected_indices)),
        "branched_subset": int(bool(branched_subset)),
    }
    return rows, sit


def collect_matched_action_label_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0037",
    max_situations: int = 12,
    max_actions_per_frame: int = 3,
    sample_high_action_frames: bool = True,
    branch_action_budget: int | None = 5,
    budget_rng_seed: int = 37037,
    fixed_rollouts_per_action: int = 3,
    adaptive_base_rollouts_per_action: int = 1,
    adaptive_max_extra_rollouts_per_situation: int | None = None,
    adaptive_stop_margin: float = 0.50,
    adaptive_target_confidence: float = 0.62,
    branch_max_decisions: int = 320,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], MatchedActionLabelComparisonSummary]:
    """Collect fixed-vs-adaptive labels on the same public situations.

    A full branch-outcome matrix is generated once for each sampled situation.
    Fixed and adaptive labelers then consume different prefixes/subsets of that
    same matrix.  This avoids a common audit mistake: comparing two labelers on
    different public states or under different hidden branch worlds.
    """

    method_candidate_rows: list[Dict[str, object]] = []
    branch_rows: list[Dict[str, object]] = []
    situation_rows: list[Dict[str, object]] = []
    comparison_rows: list[Dict[str, object]] = []
    transition_rows: list[Dict[str, object]] = []
    records: list[TransitionMicroRecord] = []
    expected_sigs: list[str] = []
    row_indices: list[int] = []

    max_precomputed_rollouts = int(fixed_rollouts_per_action)
    adaptive_max_extra = int(adaptive_max_extra_rollouts_per_situation) if adaptive_max_extra_rollouts_per_situation is not None else None
    skipped_high = 0
    full_menu_situations = 0
    budgeted_situations = 0
    behavior_decisions = 0
    branch_terminal = 0
    branch_truncations = 0
    sampled = 0
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
        if sampled >= int(max_situations):
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
            if sampled >= int(max_situations) or state.winner is not None:
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
                selector_rng = Random(int(budget_rng_seed) + int(spec_i) * 1000003 + int(step) * 9176 + int(sampled))
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
                situation_id = f"mlcmp_s{sampled:04d}_{spec.game_id}_step{step:04d}"
                pre_branch_state = copy.deepcopy(state)
                frame_action_strings = tuple(frame.legal_action_strings)
                ctx = context_feature_dict(frame.observation)
                scores_by_action: dict[int, list[float]] = {int(i): [] for i in selected_indices}
                # Precompute the branch matrix once. Both label allocators consume it.
                for action_idx in selected_indices:
                    for rollout in range(max_precomputed_rollouts):
                        score, meta = _branch_action_once(
                            pre_branch_state=pre_branch_state,
                            frame_action_strings=frame_action_strings,
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
                        if str(meta.get("winner")) == "None":
                            branch_truncations += 1
                        else:
                            branch_terminal += 1
                        branch_rows.append({
                            "revision": revision,
                            "situation_id": situation_id,
                            "action_index": int(action_idx),
                            "rollout": int(rollout),
                            "action": frame.legal_actions[int(action_idx)].compact(),
                            "actor_score": float(score),
                            "winner": meta["winner"],
                            "loss_reason": meta["loss_reason"],
                            "branch_decisions": int(meta["branch_decisions"]),
                            "turn_number": int(meta["turn_number"]),
                            "behavior_chosen": 1 if int(action_idx) == chosen_idx else 0,
                            "action_count": int(frame.action_count),
                            "branched_action_count": int(len(selected_indices)),
                            "branched_subset": int(branched_subset),
                            "budget_reason": selection_reasons.get(int(action_idx), ""),
                        })

                if adaptive_max_extra is None:
                    adaptive_extra_budget = max(0, len(selected_indices) * (int(fixed_rollouts_per_action) - int(adaptive_base_rollouts_per_action)))
                else:
                    adaptive_extra_budget = int(adaptive_max_extra)
                method_payloads: dict[str, tuple[dict[int, list[float]], dict[str, object]]] = {}
                method_payloads["fixed_equal"] = _score_for_method(
                    scores_by_action,
                    chosen_idx=chosen_idx,
                    method="fixed_equal",
                    fixed_rollouts_per_action=int(fixed_rollouts_per_action),
                    adaptive_base_rollouts_per_action=int(adaptive_base_rollouts_per_action),
                    adaptive_max_extra_rollouts_per_situation=int(adaptive_extra_budget),
                    adaptive_stop_margin=float(adaptive_stop_margin),
                    adaptive_target_confidence=float(adaptive_target_confidence),
                    rng=Random(int(budget_rng_seed) + sampled),
                )
                method_payloads["adaptive_race"] = _score_for_method(
                    scores_by_action,
                    chosen_idx=chosen_idx,
                    method="adaptive_race",
                    fixed_rollouts_per_action=int(fixed_rollouts_per_action),
                    adaptive_base_rollouts_per_action=int(adaptive_base_rollouts_per_action),
                    adaptive_max_extra_rollouts_per_situation=int(adaptive_extra_budget),
                    adaptive_stop_margin=float(adaptive_stop_margin),
                    adaptive_target_confidence=float(adaptive_target_confidence),
                    rng=Random(int(budget_rng_seed) + 991 * sampled),
                )

                per_method_sits: dict[str, Dict[str, object]] = {}
                for method, (samples, meta) in method_payloads.items():
                    rows, sit = _method_rows(
                        method=method,
                        situation_id=situation_id,
                        frame=frame,
                        selected_indices=selected_indices,
                        chosen_idx=chosen_idx,
                        sampled_scores=samples,
                        action_count=int(frame.action_count),
                        branched_subset=branched_subset,
                        selection_reasons=selection_reasons,
                        ctx=ctx,
                        spec=spec,
                        step=int(step),
                        method_meta=meta,
                    )
                    method_candidate_rows.extend(rows)
                    situation_rows.append(sit)
                    per_method_sits[method] = sit

                fixed = per_method_sits["fixed_equal"]
                adaptive = per_method_sits["adaptive_race"]
                comparison_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "behavior_game_id": spec.game_id,
                    "step": int(step),
                    "action_count": int(frame.action_count),
                    "branched_action_count": int(len(selected_indices)),
                    "branched_subset": int(branched_subset),
                    "fixed_best_actions": fixed["best_actions"],
                    "adaptive_best_actions": adaptive["best_actions"],
                    "best_set_agrees": 1 if fixed["best_actions"] == adaptive["best_actions"] else 0,
                    "fixed_behavior_chosen_is_best": int(fixed["behavior_chosen_is_best"]),
                    "adaptive_behavior_chosen_is_best": int(adaptive["behavior_chosen_is_best"]),
                    "chosen_best_agrees": 1 if int(fixed["behavior_chosen_is_best"]) == int(adaptive["behavior_chosen_is_best"]) else 0,
                    "fixed_best_mean_actor_score": float(fixed["best_mean_actor_score"]),
                    "adaptive_best_mean_actor_score": float(adaptive["best_mean_actor_score"]),
                    "fixed_margin": float(fixed["situation_best_margin"]),
                    "adaptive_margin": float(adaptive["situation_best_margin"]),
                    "fixed_total_rollouts": int(fixed["total_rollouts"]),
                    "adaptive_total_rollouts": int(adaptive["total_rollouts"]),
                    "rollout_delta_adaptive_minus_fixed": int(adaptive["total_rollouts"]) - int(fixed["total_rollouts"]),
                    "adaptive_extra_rollouts": int(adaptive["adaptive_extra_rollouts"]),
                    "adaptive_stopped_early": int(adaptive["adaptive_stopped_early"]),
                })
                sampled += 1

            apply_decision_index(state, frame, chosen_idx, transition_rng)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    fixed_sits = [r for r in situation_rows if r["method"] == "fixed_equal"]
    adaptive_sits = [r for r in situation_rows if r["method"] == "adaptive_race"]
    fixed_decisive = sum(1 for r in fixed_sits if float(r["situation_best_margin"]) > 1e-9)
    adaptive_decisive = sum(1 for r in adaptive_sits if float(r["situation_best_margin"]) > 1e-9)
    fixed_rollouts = sum(int(r["total_rollouts"]) for r in fixed_sits)
    adaptive_rollouts = sum(int(r["total_rollouts"]) for r in adaptive_sits)
    summary = MatchedActionLabelComparisonSummary(
        revision=revision,
        behavior_games=len(specs),
        behavior_decisions=int(behavior_decisions),
        sampled_situations=int(sampled),
        candidate_actions=int(len(method_candidate_rows)),
        branch_games=int(len(branch_rows)),
        fixed_rollouts_per_action=int(fixed_rollouts_per_action),
        adaptive_base_rollouts_per_action=int(adaptive_base_rollouts_per_action),
        adaptive_max_extra_rollouts_per_situation=int(adaptive_max_extra if adaptive_max_extra is not None else -1),
        fixed_total_rollouts=int(fixed_rollouts),
        adaptive_total_rollouts=int(adaptive_rollouts),
        rollout_delta_adaptive_minus_fixed=int(adaptive_rollouts - fixed_rollouts),
        adaptive_early_stops=sum(int(r["adaptive_stopped_early"]) for r in adaptive_sits),
        full_menu_situations=int(full_menu_situations),
        budgeted_situations=int(budgeted_situations),
        skipped_high_action_frames=int(skipped_high),
        fixed_decisive_situations=int(fixed_decisive),
        adaptive_decisive_situations=int(adaptive_decisive),
        best_set_agreement_rate=sum(int(r["best_set_agrees"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        chosen_best_agreement_rate=sum(int(r["chosen_best_agrees"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        fixed_behavior_chosen_best_rate=sum(int(r["fixed_behavior_chosen_is_best"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        adaptive_behavior_chosen_best_rate=sum(int(r["adaptive_behavior_chosen_is_best"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        mean_fixed_margin=sum(float(r["fixed_margin"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        mean_adaptive_margin=sum(float(r["adaptive_margin"]) for r in comparison_rows) / max(1, len(comparison_rows)),
        mean_abs_best_score_delta=sum(abs(float(r["adaptive_best_mean_actor_score"]) - float(r["fixed_best_mean_actor_score"])) for r in comparison_rows) / max(1, len(comparison_rows)),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_truncations),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return method_candidate_rows, branch_rows, comparison_rows, list(finalized_transitions), summary
