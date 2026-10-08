from __future__ import annotations

import copy
from collections import Counter
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
from .action_disagreement import _screen_votes, _vote_entropy_proxy
from .action_features import action_feature_dict
from .action_racing import _stdev
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class MatchedScreenComparisonSummary:
    """Summary for rev0039 matched unscreened-vs-screened action-label audit.

    The collector uses the same behavior games, the same sampled public
    DecisionFrames, and the same branch rollout outcomes.  It then asks whether
    an unscreened budget selector and a disagreement-aware selector would keep
    different candidate actions and whether either selector loses value relative
    to the union of branched actions.  This is a label-budget audit, not a
    policy-strength claim.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    choice_frames_seen: int
    frames_with_disagreement: int
    sampled_situations: int
    skipped_no_disagreement: int
    skipped_high_action_frames: int
    full_menu_situations: int
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
    mean_union_branched_count: float
    mean_unique_screen_votes: float
    mean_vote_entropy_proxy: float
    union_decisive_situations: int
    mean_union_margin: float
    mean_screened_minus_unscreened_best_score: float
    screened_better_situations: int
    unscreened_better_situations: int
    tied_method_situations: int
    screened_hits_union_best_rate: float
    unscreened_hits_union_best_rate: float
    screened_vote_hits_union_best_rate: float
    behavior_chosen_hits_union_best_rate: float
    mean_screened_lost_value_to_union_best: float
    mean_unscreened_lost_value_to_union_best: float
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _stable_seed(name: str) -> int:
    total = 0
    for i, ch in enumerate(str(name), start=1):
        total += i * ord(ch)
    return total


def _select_unscreened(frame, chosen_idx: int, *, max_actions_per_frame: int, branch_action_budget: int | None, rng: Random):
    if frame.action_count <= int(max_actions_per_frame):
        idxs = tuple(range(frame.action_count))
        return idxs, {i: "full_menu_within_max_actions" for i in idxs}, False, False
    if branch_action_budget is None:
        return tuple(), {}, False, True
    sel = select_budgeted_action_indices(frame, int(chosen_idx), budget=int(branch_action_budget), rng=rng)
    return tuple(sel.indices), dict(sel.reasons), True, len(sel.indices) <= 1


def _select_screened(frame, chosen_idx: int, voted_indices: Sequence[int], *, max_actions_per_frame: int, branch_action_budget: int | None, rng: Random):
    if frame.action_count <= int(max_actions_per_frame):
        idxs = tuple(range(frame.action_count))
        return idxs, {i: "full_menu_within_max_actions" for i in idxs}, False, False
    if branch_action_budget is None:
        return tuple(), {}, False, True
    base = select_budgeted_action_indices(frame, int(chosen_idx), budget=int(branch_action_budget), rng=rng)
    budget = max(2, int(branch_action_budget))
    priority: list[int] = []
    reasons: dict[int, str] = dict(base.reasons)

    def add(idx: int, reason: str) -> None:
        if idx < 0 or idx >= frame.action_count:
            return
        if idx not in priority:
            priority.append(idx)
        old = reasons.get(idx, "")
        if not old:
            reasons[idx] = reason
        elif reason not in old:
            reasons[idx] = f"{old}+{reason}"

    add(int(chosen_idx), "behavior_chosen")
    for idx in voted_indices:
        add(int(idx), "screen_vote")
    for idx in base.indices:
        add(int(idx), reasons.get(int(idx), "budget_diverse"))
    idxs = tuple(sorted(priority[:budget]))
    return idxs, {i: reasons.get(i, "selected") for i in idxs}, True, len(idxs) <= 1


def _method_compare_rows(
    *,
    situation_id: str,
    method: str,
    frame,
    selected_indices: Sequence[int],
    union_indices: Sequence[int],
    scores_by_action: Mapping[int, Sequence[float]],
    chosen_idx: int,
    voted_indices: Sequence[int],
    selection_reasons: Mapping[int, str],
    ctx: Mapping[str, float],
    spec: ActionCounterfactualGameSpec,
    step: int,
) -> tuple[list[Dict[str, object]], Dict[str, object]]:
    means = {int(i): sum(map(float, vals)) / max(1, len(vals)) for i, vals in scores_by_action.items()}
    stdevs = {int(i): _stdev(tuple(map(float, vals))) for i, vals in scores_by_action.items()}
    union_best = max((means[int(i)] for i in union_indices), default=0.0)
    sorted_union = sorted((means[int(i)] for i in union_indices), reverse=True)
    union_second = sorted_union[1] if len(sorted_union) > 1 else union_best
    union_margin = float(union_best - union_second)
    method_best = max((means[int(i)] for i in selected_indices), default=0.0)
    method_best_indices = {int(i) for i in selected_indices if abs(float(means[int(i)]) - method_best) <= 1e-9}
    union_best_indices = {int(i) for i in union_indices if abs(float(means[int(i)]) - union_best) <= 1e-9}
    voted_set = {int(v) for v in voted_indices}
    chosen_score = float(means.get(int(chosen_idx), 0.0))
    mean_stdev = float(sum(stdevs.values()) / max(1, len(stdevs)))
    confidence = float(union_margin / (union_margin + mean_stdev + 1e-9))
    rows: list[Dict[str, object]] = []
    for idx in selected_indices:
        action = frame.legal_actions[int(idx)]
        feats: dict[str, float] = {}
        feats.update(ctx)
        feats.update(action_feature_dict(action, frame.observation))
        row: Dict[str, object] = {
            "method": method,
            "situation_id": situation_id,
            "behavior_game_id": spec.game_id,
            "step": int(step),
            "player": int(frame.player),
            "action_index": int(idx),
            "action_count": int(frame.action_count),
            "union_branched_action_count": int(len(union_indices)),
            "method_branched_action_count": int(len(selected_indices)),
            "budget_reason": selection_reasons.get(int(idx), ""),
            "action": action.compact(),
            "behavior_chosen": 1 if int(idx) == int(chosen_idx) else 0,
            "screen_voted_action": 1 if int(idx) in voted_set else 0,
            "branch_rollouts": int(len(scores_by_action[int(idx)])),
            "mean_actor_score": float(means[int(idx)]),
            "actor_score_stdev": float(stdevs.get(int(idx), 0.0)),
            "method_best_mean_actor_score": float(method_best),
            "union_best_mean_actor_score": float(union_best),
            "union_second_best_mean_actor_score": float(union_second),
            "chosen_mean_actor_score": float(chosen_score),
            "value_gap_to_union_best": float(union_best - means[int(idx)]),
            "method_lost_value_to_union_best": float(union_best - method_best),
            "union_best_margin": float(union_margin),
            "label_confidence_proxy": float(confidence),
            "is_method_best_action": 1 if int(idx) in method_best_indices else 0,
            "is_union_best_action": 1 if int(idx) in union_best_indices else 0,
            "method_hits_union_best": 1 if bool(method_best_indices & union_best_indices) else 0,
            "behavior_chosen_hits_union_best": 1 if int(chosen_idx) in union_best_indices else 0,
            "screen_vote_hits_union_best": 1 if bool(voted_set & union_best_indices) else 0,
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
        "method_best_actions": "|".join(str(i) for i in sorted(method_best_indices)),
        "union_best_actions": "|".join(str(i) for i in sorted(union_best_indices)),
        "method_hits_union_best": 1 if bool(method_best_indices & union_best_indices) else 0,
        "method_best_mean_actor_score": float(method_best),
        "union_best_mean_actor_score": float(union_best),
        "method_lost_value_to_union_best": float(union_best - method_best),
        "union_best_margin": float(union_margin),
        "label_confidence_proxy": float(confidence),
        "behavior_chosen_hits_union_best": 1 if int(chosen_idx) in union_best_indices else 0,
        "screen_vote_hits_union_best": 1 if bool(voted_set & union_best_indices) else 0,
        "action_count": int(frame.action_count),
        "union_branched_action_count": int(len(union_indices)),
        "method_branched_action_count": int(len(selected_indices)),
    }
    return rows, sit


def _summary_from_method_rows(rows: Sequence[Mapping[str, object]], screen_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_sit_method: dict[tuple[str, str], Mapping[str, object]] = {}
    by_sit: dict[str, dict[str, Mapping[str, object]]] = {}
    for r in rows:
        key = (str(r["situation_id"]), str(r["method"]))
        if key not in by_sit_method:
            by_sit_method[key] = r
            by_sit.setdefault(str(r["situation_id"]), {})[str(r["method"])] = r
    screened_minus: list[float] = []
    screened_better = 0
    unscreened_better = 0
    tied = 0
    screened_hits = []
    unscreened_hits = []
    screened_lost = []
    unscreened_lost = []
    margins = []
    action_counts = []
    union_counts = []
    behavior_hits = []
    screen_vote_hits = []
    for _sid, methods in by_sit.items():
        s = methods.get("screened_vote_budget")
        u = methods.get("unscreened_budget")
        if not s or not u:
            continue
        sv = float(s.get("method_best_mean_actor_score", 0.0))
        uv = float(u.get("method_best_mean_actor_score", 0.0))
        diff = sv - uv
        screened_minus.append(diff)
        if diff > 1e-9:
            screened_better += 1
        elif diff < -1e-9:
            unscreened_better += 1
        else:
            tied += 1
        screened_hits.append(int(s.get("method_hits_union_best", 0)))
        unscreened_hits.append(int(u.get("method_hits_union_best", 0)))
        screened_lost.append(float(s.get("method_lost_value_to_union_best", 0.0)))
        unscreened_lost.append(float(u.get("method_lost_value_to_union_best", 0.0)))
        margins.append(float(s.get("union_best_margin", 0.0)))
        action_counts.append(int(s.get("action_count", 0)))
        union_counts.append(int(s.get("union_branched_action_count", 0)))
        behavior_hits.append(int(s.get("behavior_chosen_hits_union_best", 0)))
        screen_vote_hits.append(int(s.get("screen_vote_hits_union_best", 0)))
    screen_df_count = len(screen_rows)
    unique_votes = []
    entropy = []
    by_screen_sit: dict[str, list[Mapping[str, object]]] = {}
    for row in screen_rows:
        by_screen_sit.setdefault(str(row["situation_id"]), []).append(row)
    for sit_rows in by_screen_sit.values():
        votes = [int(r.get("action_index", -1)) for r in sit_rows]
        unique_votes.append(len(set(votes)))
        entropy.append(_vote_entropy_proxy(votes))
    n = max(1, len(screened_minus))
    return {
        "situations": int(len(screened_minus)),
        "screen_rows": int(screen_df_count),
        "mean_screened_minus_unscreened_best_score": float(sum(screened_minus) / n),
        "screened_better_situations": int(screened_better),
        "unscreened_better_situations": int(unscreened_better),
        "tied_method_situations": int(tied),
        "screened_hits_union_best_rate": float(sum(screened_hits) / max(1, len(screened_hits))),
        "unscreened_hits_union_best_rate": float(sum(unscreened_hits) / max(1, len(unscreened_hits))),
        "screened_vote_hits_union_best_rate": float(sum(screen_vote_hits) / max(1, len(screen_vote_hits))),
        "behavior_chosen_hits_union_best_rate": float(sum(behavior_hits) / max(1, len(behavior_hits))),
        "mean_screened_lost_value_to_union_best": float(sum(screened_lost) / max(1, len(screened_lost))),
        "mean_unscreened_lost_value_to_union_best": float(sum(unscreened_lost) / max(1, len(unscreened_lost))),
        "union_decisive_situations": int(sum(1 for m in margins if m > 1e-9)),
        "mean_union_margin": float(sum(margins) / max(1, len(margins))),
        "mean_action_count": float(sum(action_counts) / max(1, len(action_counts))),
        "mean_union_branched_count": float(sum(union_counts) / max(1, len(union_counts))),
        "mean_unique_screen_votes": float(sum(unique_votes) / max(1, len(unique_votes))),
        "mean_vote_entropy_proxy": float(sum(entropy) / max(1, len(entropy))),
    }


def collect_matched_screen_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0039",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
        "counterfactual_ranker_blend_threat_rev0038",
    ),
    min_unique_screen_votes: int = 2,
    max_situations: int = 14,
    max_actions_per_frame: int = 4,
    branch_action_budget: int = 6,
    branch_rollouts_per_action: int = 2,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 39039,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], MatchedScreenComparisonSummary]:
    """Compare screened and unscreened label selectors on matched branch outcomes.

    The collector samples public frames where several public-safe policies vote
    for different actions.  For each frame, it branches the union of an
    unscreened budget subset and a screen-vote-aware budget subset.  Since both
    methods consume the same branch outcomes, their differences are due to label
    selection, not rollout noise.
    """

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
    frames_with_disagreement = 0
    skipped_no_disagreement = 0
    skipped_high = 0
    sampled = 0
    full_menu = 0
    subset = 0
    branch_terminal = 0
    branch_trunc = 0

    for spec_i, spec in enumerate(specs):
        if sampled >= int(max_situations):
            break
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
            if state.winner is not None or sampled >= int(max_situations):
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            behavior_decisions += 1
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"behavior agent chose illegal action index {chosen_idx}/{frame.action_count}")
            if frame.action_count <= 1:
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            choice_seen += 1
            vote_rows, unique_votes, entropy = _screen_votes(frame, screeners, seed=int(spec.seed) + step * 9176 + spec_i)
            if len(unique_votes) < int(min_unique_screen_votes):
                skipped_no_disagreement += 1
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            frames_with_disagreement += 1
            pre_branch_state = copy.deepcopy(state)
            budget_rng = Random(int(budget_rng_seed) + sampled * 101 + step)
            unscreened_idx, unscreened_reasons, uns_subset, uns_skip = _select_unscreened(
                frame,
                chosen_idx,
                max_actions_per_frame=int(max_actions_per_frame),
                branch_action_budget=int(branch_action_budget),
                rng=budget_rng,
            )
            screened_idx, screened_reasons, scr_subset, scr_skip = _select_screened(
                frame,
                chosen_idx,
                unique_votes,
                max_actions_per_frame=int(max_actions_per_frame),
                branch_action_budget=int(branch_action_budget),
                rng=Random(int(budget_rng_seed) + sampled * 101 + step + 17),
            )
            if uns_skip or scr_skip:
                skipped_high += 1
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            union_indices = tuple(sorted(set(unscreened_idx) | set(screened_idx)))
            if len(union_indices) <= 1:
                skipped_high += 1
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            if frame.action_count <= int(max_actions_per_frame):
                full_menu += 1
            else:
                subset += 1
            situation_id = f"{revision}_s{sampled:04d}_{spec.game_id}_step{step:04d}"
            for vr in vote_rows:
                screen_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "behavior_game_id": spec.game_id,
                    "step": int(step),
                    "player": int(frame.player),
                    "action_count": int(frame.action_count),
                    "behavior_chosen_index": int(chosen_idx),
                    "behavior_chosen_action": frame.legal_actions[chosen_idx].compact(),
                    "screen_unique_votes": int(len(unique_votes)),
                    "screen_vote_entropy_proxy": float(entropy),
                    **vr,
                })
            ctx = context_feature_dict(frame.observation)
            scores_by_action = {int(i): [] for i in union_indices}
            for action_idx in union_indices:
                for rollout in range(int(branch_rollouts_per_action)):
                    branch_state = copy.deepcopy(pre_branch_state)
                    branch_frame = build_decision_frame(branch_state)
                    if branch_frame.legal_action_strings != frame.legal_action_strings:
                        raise ValueError(f"{situation_id}: branch legal menu drift before action")
                    branch_seed = 939000000 + sampled * 10000 + int(action_idx) * 100 + rollout
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
                        branch_seed=branch_seed + 41,
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
                        "branch_id": f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                        "behavior_game_id": spec.game_id,
                        "step": int(step),
                        "player": int(frame.player),
                        "action_index": int(action_idx),
                        "action_count": int(frame.action_count),
                        "union_branched_action_count": int(len(union_indices)),
                        "in_unscreened_budget": 1 if int(action_idx) in set(unscreened_idx) else 0,
                        "in_screened_vote_budget": 1 if int(action_idx) in set(screened_idx) else 0,
                        "behavior_chosen": 1 if int(action_idx) == int(chosen_idx) else 0,
                        "screen_voted_action": 1 if int(action_idx) in set(unique_votes) else 0,
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
            rows, sit = _method_compare_rows(
                situation_id=situation_id,
                method="unscreened_budget",
                frame=frame,
                selected_indices=unscreened_idx,
                union_indices=union_indices,
                scores_by_action=scores_by_action,
                chosen_idx=chosen_idx,
                voted_indices=unique_votes,
                selection_reasons=unscreened_reasons,
                ctx=ctx,
                spec=spec,
                step=step,
            )
            candidate_rows.extend(rows)
            method_rows.append(sit)
            rows, sit = _method_compare_rows(
                situation_id=situation_id,
                method="screened_vote_budget",
                frame=frame,
                selected_indices=screened_idx,
                union_indices=union_indices,
                scores_by_action=scores_by_action,
                chosen_idx=chosen_idx,
                voted_indices=unique_votes,
                selection_reasons=screened_reasons,
                ctx=ctx,
                spec=spec,
                step=step,
            )
            candidate_rows.extend(rows)
            method_rows.append(sit)
            sampled += 1
            apply_decision_index(state, frame, chosen_idx, transition_rng)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    method_stats = _summary_from_method_rows(method_rows, screen_rows)
    summary = MatchedScreenComparisonSummary(
        revision=revision,
        behavior_games=len(specs),
        behavior_decisions=int(behavior_decisions),
        choice_frames_seen=int(choice_seen),
        frames_with_disagreement=int(frames_with_disagreement),
        sampled_situations=int(sampled),
        skipped_no_disagreement=int(skipped_no_disagreement),
        skipped_high_action_frames=int(skipped_high),
        full_menu_situations=int(full_menu),
        subset_situations=int(subset),
        union_candidate_actions=int(len({(r.get('situation_id'), r.get('action_index')) for r in candidate_rows})),
        branch_games=int(len(branch_rows)),
        branch_rollouts_per_action=int(branch_rollouts_per_action),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_trunc),
        method_rows=int(len(method_rows)),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=float(method_stats.get("mean_action_count", 0.0)),
        mean_union_branched_count=float(method_stats.get("mean_union_branched_count", 0.0)),
        mean_unique_screen_votes=float(method_stats.get("mean_unique_screen_votes", 0.0)),
        mean_vote_entropy_proxy=float(method_stats.get("mean_vote_entropy_proxy", 0.0)),
        union_decisive_situations=int(method_stats.get("union_decisive_situations", 0)),
        mean_union_margin=float(method_stats.get("mean_union_margin", 0.0)),
        mean_screened_minus_unscreened_best_score=float(method_stats.get("mean_screened_minus_unscreened_best_score", 0.0)),
        screened_better_situations=int(method_stats.get("screened_better_situations", 0)),
        unscreened_better_situations=int(method_stats.get("unscreened_better_situations", 0)),
        tied_method_situations=int(method_stats.get("tied_method_situations", 0)),
        screened_hits_union_best_rate=float(method_stats.get("screened_hits_union_best_rate", 0.0)),
        unscreened_hits_union_best_rate=float(method_stats.get("unscreened_hits_union_best_rate", 0.0)),
        screened_vote_hits_union_best_rate=float(method_stats.get("screened_vote_hits_union_best_rate", 0.0)),
        behavior_chosen_hits_union_best_rate=float(method_stats.get("behavior_chosen_hits_union_best_rate", 0.0)),
        mean_screened_lost_value_to_union_best=float(method_stats.get("mean_screened_lost_value_to_union_best", 0.0)),
        mean_unscreened_lost_value_to_union_best=float(method_stats.get("mean_unscreened_lost_value_to_union_best", 0.0)),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return candidate_rows, method_rows, branch_rows, screen_rows, list(finalized_transitions), summary
