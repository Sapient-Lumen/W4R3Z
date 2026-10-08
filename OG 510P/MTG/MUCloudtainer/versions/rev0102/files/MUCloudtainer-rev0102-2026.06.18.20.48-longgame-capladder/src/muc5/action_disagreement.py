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
from .action_features import action_feature_dict
from .cpp_transition import TransitionMicroRecord, cpp_transition_tool_status
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .engine import GameState, start_game
from .imitation import context_feature_dict
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent


@dataclass(frozen=True)
class DisagreementScreenedCounterfactualSummary:
    """Summary for rev0038 disagreement-screened gameplay labels.

    The goal is not merely more rows.  Action-counterfactual learning is useful
    only when sampled public situations contain real alternatives.  This screen
    watches a panel of public-safe policies vote on a DecisionFrame and branches
    only frames where those policies disagree.  The branch labels are still
    produced by the offline referee; policies never see hidden state.
    """

    revision: str
    behavior_games: int
    behavior_decisions: int
    screen_frames_seen: int
    screen_frames_with_choices: int
    screen_frames_with_disagreement: int
    sampled_situations: int
    skipped_no_disagreement: int
    skipped_high_action_frames: int
    full_menu_situations: int
    budgeted_situations: int
    candidate_actions: int
    branch_games: int
    branch_rollouts_per_action: int
    branch_terminal_games: int
    branch_truncations: int
    cpp_checked_transitions: int
    cpp_skipped_transitions: int
    cpp_mismatches: int
    mean_action_count: float
    mean_unique_screen_votes: float
    mean_vote_entropy_proxy: float
    decisive_situations: int
    behavior_chosen_best_rate: float
    mean_best_minus_chosen: float
    mean_label_confidence_proxy: float
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


def _vote_entropy_proxy(votes: Sequence[int]) -> float:
    """Return a tiny normalized disagreement proxy in [0, 1].

    It is not Shannon entropy; it is a cheap bounded proxy: 0 when all voters
    choose the same action and approaches 1 as votes spread across actions.
    """

    if not votes:
        return 0.0
    counts = Counter(int(v) for v in votes)
    if len(counts) <= 1:
        return 0.0
    most = max(counts.values())
    return float(1.0 - most / max(1, len(votes)))


def _screen_votes(
    frame,
    screeners: Mapping[str, PublicDecisionAgent],
    *,
    seed: int,
) -> tuple[list[Dict[str, object]], tuple[int, ...], float]:
    rows: list[Dict[str, object]] = []
    votes: list[int] = []
    for name, agent in screeners.items():
        rng = Random(int(seed) + _stable_seed(name))
        idx = int(agent.choose_action_index(frame, rng))
        if idx < 0 or idx >= frame.action_count:
            raise ValueError(f"screening agent {name} chose illegal action index {idx}/{frame.action_count}")
        votes.append(idx)
        rows.append({
            "screener": str(name),
            "action_index": int(idx),
            "action": frame.legal_actions[idx].compact(),
        })
    return rows, tuple(sorted(set(votes))), _vote_entropy_proxy(votes)


def _select_with_votes(
    frame,
    *,
    chosen_idx: int,
    voted_indices: Sequence[int],
    max_actions_per_frame: int,
    sample_high_action_frames: bool,
    branch_action_budget: int | None,
    rng: Random,
) -> tuple[tuple[int, ...], dict[int, str], bool, bool]:
    """Return selected action indices, reasons, subset flag, skipped-high flag."""

    if frame.action_count <= int(max_actions_per_frame):
        idxs = tuple(range(frame.action_count))
        return idxs, {i: "full_menu_within_max_actions" for i in idxs}, False, False

    if not sample_high_action_frames or branch_action_budget is None:
        return tuple(), {}, False, True

    budget = max(2, int(branch_action_budget))
    base = select_budgeted_action_indices(frame, int(chosen_idx), budget=budget, rng=rng)
    reasons: dict[int, str] = dict(base.reasons)
    priority: list[int] = []

    def add(idx: int, reason: str) -> None:
        if idx < 0 or idx >= frame.action_count:
            return
        if idx not in priority:
            priority.append(idx)
        if idx not in reasons:
            reasons[idx] = reason
        elif reason not in reasons[idx]:
            reasons[idx] = f"{reasons[idx]}+{reason}"

    add(int(chosen_idx), "behavior_chosen")
    for idx in voted_indices:
        add(int(idx), "screen_vote")
    for idx in base.indices:
        add(int(idx), reasons.get(int(idx), "budget_diverse"))

    selected = tuple(sorted(priority[:budget]))
    return selected, {i: reasons.get(i, "selected") for i in selected}, True, len(selected) <= 1


def _summarize_candidate_rows(rows: Sequence[Mapping[str, object]]) -> dict[str, float | int]:
    by_situation: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        by_situation.setdefault(str(row["situation_id"]), []).append(row)
    decisive = 0
    chosen_best = 0
    regrets: list[float] = []
    margins: list[float] = []
    conf: list[float] = []
    action_counts: list[int] = []
    unique_votes: list[int] = []
    entropy: list[float] = []
    for sit_rows in by_situation.values():
        if not sit_rows:
            continue
        first = sit_rows[0]
        action_counts.append(int(first.get("action_count", 0)))
        unique_votes.append(int(first.get("screen_unique_votes", 0)))
        entropy.append(float(first.get("screen_vote_entropy_proxy", 0.0)))
        margins.append(float(first.get("situation_best_margin", 0.0)))
        conf.append(float(first.get("label_confidence_proxy", 0.0)))
        if float(first.get("situation_best_margin", 0.0)) > 1e-9:
            decisive += 1
        chosen = [r for r in sit_rows if int(r.get("behavior_chosen", 0)) == 1]
        if chosen:
            chosen_best += int(chosen[0].get("behavior_chosen_is_best", 0))
            regrets.append(float(chosen[0].get("best_mean_actor_score", 0.0)) - float(chosen[0].get("chosen_mean_actor_score", 0.0)))
    n = max(1, len(by_situation))
    return {
        "situations": int(len(by_situation)),
        "decisive_situations": int(decisive),
        "behavior_chosen_best_rate": float(chosen_best / n),
        "mean_best_minus_chosen": float(sum(regrets) / max(1, len(regrets))),
        "mean_action_count": float(sum(action_counts) / max(1, len(action_counts))),
        "mean_unique_screen_votes": float(sum(unique_votes) / max(1, len(unique_votes))),
        "mean_vote_entropy_proxy": float(sum(entropy) / max(1, len(entropy))),
        "mean_label_confidence_proxy": float(sum(conf) / max(1, len(conf))),
    }


def collect_disagreement_screened_counterfactuals(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0038",
    screen_agent_names: Sequence[str] = (
        "counter_happy",
        "threat_rush",
        "patient",
        "code_jace_lock_rev0013",
        "outcome_ranker_blend_counter_rev0025",
    ),
    min_unique_screen_votes: int = 2,
    max_situations: int = 18,
    max_actions_per_frame: int = 4,
    sample_high_action_frames: bool = True,
    branch_action_budget: int | None = 6,
    branch_rollouts_per_action: int = 3,
    branch_max_decisions: int = 320,
    budget_rng_seed: int = 38038,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], DisagreementScreenedCounterfactualSummary]:
    """Collect action-counterfactual labels from frames where public policies disagree.

    This is a label-quality screen, not a stronger player.  It biases the offline
    branch budget toward frames where several public-safe policies pick different
    legal actions.  That tends to avoid spending branch rollouts on boring
    forced/pass-equivalent frames.  Branches are still checked against the C++
    transition shadow path, and Python remains semantic authority.
    """

    candidate_rows: list[Dict[str, object]] = []
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
    screen_seen = 0
    screen_choice_frames = 0
    screen_disagree = 0
    sampled = 0
    skipped_no_disagreement = 0
    skipped_high = 0
    full_menu = 0
    budgeted = 0
    branch_terminal = 0
    branch_truncations = 0

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
            screen_seen += 1

            if frame.action_count > 1:
                screen_choice_frames += 1
                vote_rows, unique_votes, entropy = _screen_votes(
                    frame,
                    screeners,
                    seed=int(spec.seed) + int(step) * 1009 + int(frame.player) * 991,
                )
                if len(unique_votes) >= int(min_unique_screen_votes):
                    screen_disagree += 1
                else:
                    skipped_no_disagreement += 1
            else:
                vote_rows, unique_votes, entropy = [], tuple(), 0.0
                skipped_no_disagreement += 1

            # Continue behavior path if the screen says this frame is boring.
            if frame.action_count <= 1 or len(unique_votes) < int(min_unique_screen_votes):
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue

            selector_rng = Random(int(budget_rng_seed) + int(spec_i) * 1000003 + int(step) * 9176 + int(sampled))
            selected_indices, selection_reasons, branched_subset, skipped_hi = _select_with_votes(
                frame,
                chosen_idx=chosen_idx,
                voted_indices=unique_votes,
                max_actions_per_frame=int(max_actions_per_frame),
                sample_high_action_frames=bool(sample_high_action_frames),
                branch_action_budget=branch_action_budget,
                rng=selector_rng,
            )
            if skipped_hi or len(selected_indices) <= 1:
                skipped_high += 1
                apply_decision_index(state, frame, chosen_idx, transition_rng)
                continue
            if branched_subset:
                budgeted += 1
            else:
                full_menu += 1

            situation_id = f"dacf_s{sampled:04d}_{spec.game_id}_step{step:04d}"
            actor = int(frame.player)
            pre_branch_state = copy.deepcopy(state)
            ctx = context_feature_dict(frame.observation)
            scores_by_action: dict[int, list[float]] = {int(i): [] for i in selected_indices}
            for vr in vote_rows:
                screen_rows.append({
                    "revision": revision,
                    "situation_id": situation_id,
                    "behavior_game_id": spec.game_id,
                    "step": int(step),
                    "player": actor,
                    "action_count": int(frame.action_count),
                    "behavior_chosen_index": int(chosen_idx),
                    "behavior_chosen_action": frame.legal_actions[chosen_idx].compact(),
                    "screen_unique_votes": int(len(unique_votes)),
                    "screen_vote_entropy_proxy": float(entropy),
                    **vr,
                })

            for action_idx in selected_indices:
                for rollout in range(int(branch_rollouts_per_action)):
                    branch_state = copy.deepcopy(pre_branch_state)
                    branch_frame = build_decision_frame(branch_state)
                    if branch_frame.legal_action_strings != frame.legal_action_strings:
                        raise ValueError(f"{situation_id}: branch legal menu drift before action")
                    branch_seed = 938000000 + sampled * 10000 + int(action_idx) * 100 + rollout
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
                        actor=actor,
                        branch_seed=branch_seed + 37,
                        max_decisions=int(branch_max_decisions),
                        case_prefix=f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                        transition_rows=transition_rows,
                        records=records,
                        expected_sigs=expected_sigs,
                        row_indices=row_indices,
                    )
                    scores_by_action[int(action_idx)].append(float(score))
                    if result.winner is None:
                        branch_truncations += 1
                    else:
                        branch_terminal += 1
                    branch_rows.append({
                        "revision": revision,
                        "situation_id": situation_id,
                        "branch_id": f"{situation_id}_a{int(action_idx):02d}_r{rollout:02d}",
                        "behavior_game_id": spec.game_id,
                        "step": int(step),
                        "player": actor,
                        "action_index": int(action_idx),
                        "action_count": int(frame.action_count),
                        "branched_action_count": int(len(selected_indices)),
                        "branched_subset": int(branched_subset),
                        "budget_reason": selection_reasons.get(int(action_idx), ""),
                        "behavior_chosen": 1 if int(action_idx) == int(chosen_idx) else 0,
                        "rollout": int(rollout),
                        "action": action.compact(),
                        "actor_score": float(score),
                        "winner": "None" if result.winner is None else int(result.winner),
                        "loss_reason": result.loss_reason,
                        "branch_decisions": int(branch_decisions),
                        "turn_number": int(turn_number),
                        "starting_life": int(spec.starting_life),
                        "starting_player": int(spec.starting_player),
                        "agent0": spec.agent0,
                        "agent1": spec.agent1,
                        "mulligan0": str(spec.mulligan0),
                        "mulligan1": str(spec.mulligan1),
                    })

            means = {i: sum(vals) / max(1, len(vals)) for i, vals in scores_by_action.items()}
            stdevs: dict[int, float] = {}
            for i, vals in scores_by_action.items():
                mean = means[i]
                if len(vals) <= 1:
                    stdevs[i] = 0.0
                else:
                    stdevs[i] = (sum((float(v) - mean) ** 2 for v in vals) / float(len(vals) - 1)) ** 0.5
            best = max(means.values()) if means else 0.0
            sorted_means = sorted(means.values(), reverse=True)
            second_best = float(sorted_means[1]) if len(sorted_means) > 1 else float(best)
            margin = float(best - second_best)
            mean_stdev = float(sum(stdevs.values()) / max(1, len(stdevs)))
            confidence = float(margin / (margin + mean_stdev + 1e-9))
            chosen_score = float(means.get(int(chosen_idx), 0.0))
            best_indices = {i for i, v in means.items() if abs(float(v) - best) <= 1e-9}
            voted_action_set = set(int(v) for v in unique_votes)
            for action_idx in selected_indices:
                action = frame.legal_actions[int(action_idx)]
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
                    "behavior_chosen": 1 if int(action_idx) == int(chosen_idx) else 0,
                    "screen_voted_action": 1 if int(action_idx) in voted_action_set else 0,
                    "screen_unique_votes": int(len(unique_votes)),
                    "screen_vote_entropy_proxy": float(entropy),
                    "screen_vote_actions": "|".join(str(v) for v in unique_votes),
                    "branch_rollouts": int(branch_rollouts_per_action),
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
                    "starting_life": int(spec.starting_life),
                    "starting_player": int(spec.starting_player),
                    "agent0": spec.agent0,
                    "agent1": spec.agent1,
                    "mulligan0": str(spec.mulligan0),
                    "mulligan1": str(spec.mulligan1),
                }
                row.update(feats)
                candidate_rows.append(row)
            sampled += 1
            apply_decision_index(state, frame, chosen_idx, transition_rng)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    row_stats = _summarize_candidate_rows(candidate_rows)
    summary = DisagreementScreenedCounterfactualSummary(
        revision=revision,
        behavior_games=len(specs),
        behavior_decisions=int(behavior_decisions),
        screen_frames_seen=int(screen_seen),
        screen_frames_with_choices=int(screen_choice_frames),
        screen_frames_with_disagreement=int(screen_disagree),
        sampled_situations=int(sampled),
        skipped_no_disagreement=int(skipped_no_disagreement),
        skipped_high_action_frames=int(skipped_high),
        full_menu_situations=int(full_menu),
        budgeted_situations=int(budgeted),
        candidate_actions=int(len(candidate_rows)),
        branch_games=int(len(branch_rows)),
        branch_rollouts_per_action=int(branch_rollouts_per_action),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_truncations),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=float(row_stats.get("mean_action_count", 0.0)),
        mean_unique_screen_votes=float(row_stats.get("mean_unique_screen_votes", 0.0)),
        mean_vote_entropy_proxy=float(row_stats.get("mean_vote_entropy_proxy", 0.0)),
        decisive_situations=int(row_stats.get("decisive_situations", 0)),
        behavior_chosen_best_rate=float(row_stats.get("behavior_chosen_best_rate", 0.0)),
        mean_best_minus_chosen=float(row_stats.get("mean_best_minus_chosen", 0.0)),
        mean_label_confidence_proxy=float(row_stats.get("mean_label_confidence_proxy", 0.0)),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return candidate_rows, branch_rows, screen_rows, list(finalized_transitions), summary
