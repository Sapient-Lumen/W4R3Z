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
from .action_disagreement import _screen_votes, _vote_entropy_proxy
from .action_hybrid_selector import select_hybrid_action_indices
from .action_screen_compare import _method_compare_rows, _select_screened, _select_unscreened
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class MatchedHybridComparisonSummary:
    """Summary for matched unscreened/screened/hybrid selector audit.

    The audit samples public DecisionFrames where public-safe screeners disagree,
    branches the union of three selector budgets, and then compares which selector
    kept an empirically best action under the same branch rollout outcomes.  It
    is a label-budget audit, not a new promoted policy.
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
    hybrid_hits_union_best_rate: float
    unscreened_hits_union_best_rate: float
    screened_hits_union_best_rate: float
    screen_vote_hits_union_best_rate: float
    behavior_chosen_hits_union_best_rate: float
    mean_hybrid_lost_value_to_union_best: float
    mean_unscreened_lost_value_to_union_best: float
    mean_screened_lost_value_to_union_best: float
    mean_hybrid_minus_unscreened_best_score: float
    mean_hybrid_minus_screened_best_score: float
    hybrid_better_than_both_situations: int
    hybrid_worse_than_both_situations: int
    hybrid_tied_best_method_situations: int
    ranker_revision: str
    ranker_available_situations: int
    tool_status: Dict[str, object]
    mismatch_examples: tuple[Dict[str, object], ...]
    skipped_examples: tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _summary_from_methods(method_rows: Sequence[Mapping[str, object]], screen_rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    by_sit: dict[str, dict[str, Mapping[str, object]]] = {}
    for row in method_rows:
        by_sit.setdefault(str(row["situation_id"]), {})[str(row["method"])] = row

    methods = ("unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker")
    hits = {m: [] for m in methods}
    lost = {m: [] for m in methods}
    best_scores = {m: [] for m in methods}
    action_counts: list[int] = []
    union_counts: list[int] = []
    margins: list[float] = []
    behavior_hits: list[int] = []
    screen_vote_hits: list[int] = []
    hybrid_minus_unscreened: list[float] = []
    hybrid_minus_screened: list[float] = []
    hybrid_better_both = 0
    hybrid_worse_both = 0
    hybrid_tied_best = 0
    for sid, group in by_sit.items():
        if any(m not in group for m in methods):
            continue
        h = group["hybrid_vote_diverse_ranker"]
        u = group["unscreened_budget"]
        s = group["screened_vote_budget"]
        hv = float(h.get("method_best_mean_actor_score", 0.0))
        uv = float(u.get("method_best_mean_actor_score", 0.0))
        sv = float(s.get("method_best_mean_actor_score", 0.0))
        hybrid_minus_unscreened.append(hv - uv)
        hybrid_minus_screened.append(hv - sv)
        max_method = max(hv, uv, sv)
        min_method = min(hv, uv, sv)
        if hv > uv + 1e-9 and hv > sv + 1e-9:
            hybrid_better_both += 1
        if hv < uv - 1e-9 and hv < sv - 1e-9:
            hybrid_worse_both += 1
        if abs(hv - max_method) <= 1e-9:
            hybrid_tied_best += 1
        action_counts.append(int(h.get("action_count", 0)))
        union_counts.append(int(h.get("union_branched_action_count", 0)))
        margins.append(float(h.get("union_best_margin", 0.0)))
        behavior_hits.append(int(h.get("behavior_chosen_hits_union_best", 0)))
        screen_vote_hits.append(int(h.get("screen_vote_hits_union_best", 0)))
        for m in methods:
            row = group[m]
            hits[m].append(int(row.get("method_hits_union_best", 0)))
            lost[m].append(float(row.get("method_lost_value_to_union_best", 0.0)))
            best_scores[m].append(float(row.get("method_best_mean_actor_score", 0.0)))

    by_screen_sit: dict[str, list[int]] = {}
    for row in screen_rows:
        by_screen_sit.setdefault(str(row["situation_id"]), []).append(int(row.get("action_index", -1)))
    unique_votes = [len(set(v)) for v in by_screen_sit.values()]
    entropy = [_vote_entropy_proxy(tuple(v)) for v in by_screen_sit.values()]

    def mean(xs: Sequence[float | int]) -> float:
        return float(sum(float(x) for x in xs) / max(1, len(xs)))

    return {
        "situations": int(len(hybrid_minus_unscreened)),
        "mean_action_count": mean(action_counts),
        "mean_union_branched_count": mean(union_counts),
        "mean_unique_screen_votes": mean(unique_votes),
        "mean_vote_entropy_proxy": mean(entropy),
        "union_decisive_situations": int(sum(1 for m in margins if float(m) > 1e-9)),
        "mean_union_margin": mean(margins),
        "hybrid_hits_union_best_rate": mean(hits["hybrid_vote_diverse_ranker"]),
        "unscreened_hits_union_best_rate": mean(hits["unscreened_budget"]),
        "screened_hits_union_best_rate": mean(hits["screened_vote_budget"]),
        "screen_vote_hits_union_best_rate": mean(screen_vote_hits),
        "behavior_chosen_hits_union_best_rate": mean(behavior_hits),
        "mean_hybrid_lost_value_to_union_best": mean(lost["hybrid_vote_diverse_ranker"]),
        "mean_unscreened_lost_value_to_union_best": mean(lost["unscreened_budget"]),
        "mean_screened_lost_value_to_union_best": mean(lost["screened_vote_budget"]),
        "mean_hybrid_minus_unscreened_best_score": mean(hybrid_minus_unscreened),
        "mean_hybrid_minus_screened_best_score": mean(hybrid_minus_screened),
        "hybrid_better_than_both_situations": int(hybrid_better_both),
        "hybrid_worse_than_both_situations": int(hybrid_worse_both),
        "hybrid_tied_best_method_situations": int(hybrid_tied_best),
    }


def collect_matched_hybrid_comparison(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0040",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 2,
    max_situations: int = 14,
    max_actions_per_frame: int = 4,
    branch_action_budget: int | None = 4,
    branch_rollouts_per_action: int = 2,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 40040,
    ranker_revision: str = "rev0034",
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], MatchedHybridComparisonSummary]:
    """Compare unscreened, vote-priority, and hybrid branch selectors.

    All methods consume the same branch rollout outcomes for each sampled public
    situation.  The only thing being compared is which legal actions each method
    spent the branch budget on.
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
    ranker_available_situations = 0

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
            unscreened_idx, unscreened_reasons, uns_subset, uns_skip = _select_unscreened(
                frame,
                chosen_idx,
                max_actions_per_frame=int(max_actions_per_frame),
                branch_action_budget=int(branch_action_budget) if branch_action_budget is not None else None,
                rng=Random(int(budget_rng_seed) + sampled * 101 + step),
            )
            screened_idx, screened_reasons, scr_subset, scr_skip = _select_screened(
                frame,
                chosen_idx,
                unique_votes,
                max_actions_per_frame=int(max_actions_per_frame),
                branch_action_budget=int(branch_action_budget) if branch_action_budget is not None else None,
                rng=Random(int(budget_rng_seed) + sampled * 101 + step + 17),
            )
            hybrid_idx, hybrid_reasons, hyb_subset, hyb_skip, hybrid_meta = select_hybrid_action_indices(
                frame,
                chosen_idx,
                unique_votes,
                max_actions_per_frame=int(max_actions_per_frame),
                branch_action_budget=int(branch_action_budget) if branch_action_budget is not None else None,
                rng=Random(int(budget_rng_seed) + sampled * 101 + step + 31),
                ranker_revision=str(ranker_revision),
            )
            if hybrid_meta is not None and hybrid_meta.ranker_available:
                ranker_available_situations += 1
            if uns_skip or scr_skip or hyb_skip:
                skipped_high += 1
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            union_indices = tuple(sorted(set(unscreened_idx) | set(screened_idx) | set(hybrid_idx)))
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
                    branch_seed = 940000000 + sampled * 10000 + int(action_idx) * 100 + rollout
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
                        "branch_id": f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                        "behavior_game_id": spec.game_id,
                        "step": int(step),
                        "player": int(frame.player),
                        "action_index": int(action_idx),
                        "action_count": int(frame.action_count),
                        "union_branched_action_count": int(len(union_indices)),
                        "in_unscreened_budget": 1 if int(action_idx) in set(unscreened_idx) else 0,
                        "in_screened_vote_budget": 1 if int(action_idx) in set(screened_idx) else 0,
                        "in_hybrid_budget": 1 if int(action_idx) in set(hybrid_idx) else 0,
                        "hybrid_budget_reason": hybrid_reasons.get(int(action_idx), ""),
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
                    voted_indices=unique_votes,
                    selection_reasons=reasons,
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
    stats = _summary_from_methods(method_rows, screen_rows)
    summary = MatchedHybridComparisonSummary(
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
        mean_action_count=float(stats.get("mean_action_count", 0.0)),
        mean_union_branched_count=float(stats.get("mean_union_branched_count", 0.0)),
        mean_unique_screen_votes=float(stats.get("mean_unique_screen_votes", 0.0)),
        mean_vote_entropy_proxy=float(stats.get("mean_vote_entropy_proxy", 0.0)),
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
        mean_hybrid_minus_unscreened_best_score=float(stats.get("mean_hybrid_minus_unscreened_best_score", 0.0)),
        mean_hybrid_minus_screened_best_score=float(stats.get("mean_hybrid_minus_screened_best_score", 0.0)),
        hybrid_better_than_both_situations=int(stats.get("hybrid_better_than_both_situations", 0)),
        hybrid_worse_than_both_situations=int(stats.get("hybrid_worse_than_both_situations", 0)),
        hybrid_tied_best_method_situations=int(stats.get("hybrid_tied_best_method_situations", 0)),
        ranker_revision=str(ranker_revision),
        ranker_available_situations=int(ranker_available_situations),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return candidate_rows, method_rows, branch_rows, screen_rows, list(finalized_transitions), summary
