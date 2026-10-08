from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence, Tuple

from .action_features import action_feature_dict
from .action_budget import select_budgeted_action_indices
from .agents import MatchResult
from .cpp_transition import (
    TransitionMicroRecord,
    cpp_transition_signatures,
    cpp_transition_tool_status,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
)
from .decision import DecisionFrame, PublicDecisionAgent, apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import GameState, start_game
from .imitation import context_feature_dict
from .mulligan import MulliganPolicy
from .mulligan_ranker import make_mulligan_agent
from .public_agents import make_public_agent
from .reward_guard import reward_packet_from_state


@dataclass(frozen=True)
class ActionCounterfactualGameSpec:
    """One behavior game from which public decision frames may be branched.

    Counterfactual branching is an offline training/evaluation tool.  Agents do
    not see the hidden true state; the collector uses it only to create fair
    branches from an identical referee state.
    """

    game_id: str
    deck0_name: str
    deck1_name: str
    deck0: DeckVector
    deck1: DeckVector
    agent0: str
    agent1: str
    mulligan0: str | MulliganPolicy | None
    mulligan1: str | MulliganPolicy | None
    seed: int
    starting_player: int
    starting_life: int
    max_decisions: int = 420


@dataclass(frozen=True)
class ActionCounterfactualSummary:
    revision: str
    behavior_games: int
    behavior_decisions: int
    sampled_situations: int
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
    mean_best_minus_chosen: float
    behavior_chosen_best_rate: float
    decisive_situations: int
    tool_status: Dict[str, object]
    mismatch_examples: Tuple[Dict[str, object], ...]
    skipped_examples: Tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def score_for_actor(winner: int | None, actor: int) -> float:
    if winner is None:
        return 0.5
    return 1.0 if int(winner) == int(actor) else 0.0


def build_action_counterfactual_specs(
    strategies: Sequence[object],
    *,
    life_totals: Sequence[int] = (20, 40),
    base_seed: int = 3300000,
    max_decisions: int = 420,
    limit_games: int | None = 8,
) -> Tuple[ActionCounterfactualGameSpec, ...]:
    """Create a small panel of behavior games from StrategyBundle-like objects."""

    specs: list[ActionCounterfactualGameSpec] = []
    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                if limit_games is not None and len(specs) >= int(limit_games):
                    return tuple(specs)
                # Alternate starts; this is a sampler, not a full payoff table.
                starting_player = (i + j + int(life == 40)) % 2
                specs.append(
                    ActionCounterfactualGameSpec(
                        game_id=f"acf_g{k:04d}_life{life}_{left.strategy_id}_vs_{right.strategy_id}",
                        deck0_name=left.deck_name,
                        deck1_name=right.deck_name,
                        deck0=left.deck,
                        deck1=right.deck,
                        agent0=left.agent_name,
                        agent1=right.agent_name,
                        mulligan0=left.mulligan_policy,
                        mulligan1=right.mulligan_policy,
                        seed=base_seed + k,
                        starting_player=int(starting_player),
                        starting_life=int(life),
                        max_decisions=int(max_decisions),
                    )
                )
                k += 1
    return tuple(specs)


def _apply_and_collect_transition(
    state: GameState,
    frame: DecisionFrame,
    action_index: int,
    rng: Random,
    *,
    case_id: str,
    transition_rows: list[Dict[str, object]],
    records: list[TransitionMicroRecord],
    expected_sigs: list[str],
    row_indices: list[int],
) -> None:
    action = frame.legal_actions[action_index]
    pre_state = copy.deepcopy(state)
    pre_frame = str(pre_state.frame)
    pre_pending = "none" if pre_state.pending_choice is None else str(pre_state.pending_choice.kind)
    apply_decision_index(state, frame, action_index, rng)
    transported = with_jace_ultimate_shuffle_transport(pre_state, action, state)
    supported = is_supported_transition(pre_state, transported)
    row_index = len(transition_rows)
    if supported:
        records.append(transition_record_from_state_action(pre_state, transported, case_id))
        expected_sigs.append(state_signature(state))
        row_indices.append(row_index)
    transition_rows.append(
        {
            "case_id": case_id,
            "frame": pre_frame,
            "pending_choice_kind": pre_pending,
            "action": action.compact(),
            "supported_by_cpp": bool(supported),
            "skipped_reason": "" if supported else "unsupported_by_cpp_transition_microkernel",
            "cpp_match": "pending" if supported else "skipped",
        }
    )


def _rollout_branch(
    state: GameState,
    agents: Sequence[PublicDecisionAgent],
    *,
    actor: int,
    branch_seed: int,
    max_decisions: int,
    case_prefix: str,
    transition_rows: list[Dict[str, object]],
    records: list[TransitionMicroRecord],
    expected_sigs: list[str],
    row_indices: list[int],
) -> tuple[float, MatchResult, int, int]:
    """Roll from an already-branched state to terminal/truncation."""

    transition_rng = Random(int(branch_seed))
    agent_rng = Random(int(branch_seed) + 1000003)
    decisions = 0
    for decisions in range(1, int(max_decisions) + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        if action_index < 0 or action_index >= frame.action_count:
            raise ValueError(f"branch policy chose illegal action index {action_index}/{frame.action_count}")
        _apply_and_collect_transition(
            state,
            frame,
            action_index,
            transition_rng,
            case_id=f"{case_prefix}_roll{decisions:04d}_{frame.player}_{frame.legal_actions[action_index].kind}",
            transition_rows=transition_rows,
            records=records,
            expected_sigs=expected_sigs,
            row_indices=row_indices,
        )
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    result = MatchResult(state.winner, state.loss_reason, int(decisions), len(state.log))
    return score_for_actor(result.winner, actor), result, int(decisions), int(state.turn_number)


def _finalize_cpp_rows(
    transition_rows: list[Dict[str, object]],
    records: Sequence[TransitionMicroRecord],
    expected_sigs: Sequence[str],
    row_indices: Sequence[int],
) -> tuple[int, tuple[Dict[str, object], ...]]:
    mismatches = 0
    if records:
        actual = cpp_transition_signatures(records)
        for idx, (got, want) in enumerate(zip(actual, expected_sigs)):
            row_idx = int(row_indices[idx])
            ok = got == want
            transition_rows[row_idx]["cpp_match"] = bool(ok)
            transition_rows[row_idx]["expected_signature"] = want
            transition_rows[row_idx]["cpp_signature"] = got
            if not ok:
                mismatches += 1
    return mismatches, tuple(transition_rows)


def collect_action_counterfactuals(
    specs: Sequence[ActionCounterfactualGameSpec],
    *,
    revision: str = "rev0033",
    max_situations: int = 18,
    max_actions_per_frame: int = 8,
    branch_rollouts_per_action: int = 2,
    branch_max_decisions: int = 260,
    sample_high_action_frames: bool = False,
    branch_action_budget: int | None = None,
    budget_rng_seed: int = 7331,
) -> tuple[list[Dict[str, object]], list[Dict[str, object]], list[Dict[str, object]], ActionCounterfactualSummary]:
    """Collect counterfactual values for unchosen legal gameplay actions.

    A behavior game supplies public DecisionFrames.  For sampled frames with a
    manageable number of legal actions, each legal action is branched from an
    identical true referee state and rolled out with public agents.  The output
    rows are labels for action-rankers/search targets; they are not exposed to an
    agent during play.
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
        if situation_count >= max_situations:
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
            if situation_count >= max_situations or state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            chosen_idx = int(agents[frame.player].choose_action_index(frame, agent_rng))
            if chosen_idx < 0 or chosen_idx >= frame.action_count:
                raise ValueError(f"behavior policy chose illegal action index {chosen_idx}/{frame.action_count}")
            behavior_decisions += 1
            # Sample only true choices.  Small menus can be fully branched.
            # Large menus can optionally be handled through a recorded budgeted
            # subset; labels from those frames are explicitly marked as subset
            # labels and should not be treated as proving full-menu optimality.
            selected_indices: tuple[int, ...] = tuple()
            selection_reasons: dict[int, str] = {}
            branched_subset = False
            if frame.action_count > 1 and frame.action_count <= int(max_actions_per_frame):
                selected_indices = tuple(range(frame.action_count))
                selection_reasons = {i: "full_menu_within_max_actions" for i in selected_indices}
                full_menu_situations += 1
            elif frame.action_count > int(max_actions_per_frame) and sample_high_action_frames and branch_action_budget is not None:
                selector_rng = Random(int(budget_rng_seed) + int(spec_i) * 1000003 + int(step) * 9176 + int(situation_count))
                selection = select_budgeted_action_indices(
                    frame,
                    chosen_idx,
                    budget=int(branch_action_budget),
                    rng=selector_rng,
                )
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
                situation_id = f"acf_s{situation_count:04d}_{spec.game_id}_step{step:04d}"
                actor = int(frame.player)
                pre_branch_state = copy.deepcopy(state)
                rollout_scores_by_action: dict[int, list[float]] = {i: [] for i in selected_indices}
                branch_meta: dict[int, list[Dict[str, object]]] = {i: [] for i in selected_indices}
                ctx = context_feature_dict(frame.observation)
                for action_idx in selected_indices:
                    action = frame.legal_actions[action_idx]
                    for rollout in range(int(branch_rollouts_per_action)):
                        branch_state = copy.deepcopy(pre_branch_state)
                        branch_frame = build_decision_frame(branch_state)
                        if branch_frame.legal_action_strings != frame.legal_action_strings:
                            raise ValueError(f"{situation_id}: branch legal menu drift before action")
                        branch_seed = 910000000 + situation_count * 10000 + action_idx * 100 + rollout
                        branch_rng = Random(branch_seed)
                        # First counterfactual action, then policy rollout.
                        _apply_and_collect_transition(
                            branch_state,
                            branch_frame,
                            action_idx,
                            branch_rng,
                            case_id=f"{situation_id}_a{action_idx:02d}_r{rollout:02d}_first_{action.kind}",
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
                            case_prefix=f"{situation_id}_a{action_idx:02d}_r{rollout:02d}",
                            transition_rows=transition_rows,
                            records=records,
                            expected_sigs=expected_sigs,
                            row_indices=row_indices,
                        )
                        rollout_scores_by_action[action_idx].append(float(score))
                        if result.winner is None:
                            branch_truncations += 1
                        else:
                            branch_terminal += 1
                        meta = {
                            "revision": revision,
                            "situation_id": situation_id,
                            "branch_id": f"{situation_id}_a{action_idx:02d}_r{rollout:02d}",
                            "behavior_game_id": spec.game_id,
                            "step": int(step),
                            "player": actor,
                            "action_index": int(action_idx),
                            "action_count": int(frame.action_count),
                            "branched_action_count": int(len(selected_indices)),
                            "branched_subset": int(branched_subset),
                            "budget_reason": selection_reasons.get(action_idx, ""),
                            "behavior_chosen": 1 if action_idx == chosen_idx else 0,
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
                        }
                        branch_rows.append(meta)
                        branch_meta[action_idx].append(meta)
                means = {i: sum(vals) / max(1, len(vals)) for i, vals in rollout_scores_by_action.items()}
                stdevs = {}
                for i, vals in rollout_scores_by_action.items():
                    mean = means[i]
                    if len(vals) <= 1:
                        stdevs[i] = 0.0
                    else:
                        stdevs[i] = (sum((float(v) - mean) ** 2 for v in vals) / float(len(vals) - 1)) ** 0.5
                best = max(means.values()) if means else 0.0
                chosen_score = float(means.get(chosen_idx, 0.0))
                sorted_means = sorted(means.values(), reverse=True)
                second_best = float(sorted_means[1]) if len(sorted_means) > 1 else float(best)
                situation_margin = float(best - second_best)
                # A cheap bounded confidence proxy: higher when the best action's
                # empirical margin clears the branch-rollout noise.  This is not
                # a statistical proof; it is a label-budget diagnostic used by
                # scripts to avoid over-reading tiny rollout samples.
                mean_stdev = float(sum(stdevs.values()) / max(1, len(stdevs)))
                label_confidence_proxy = float(situation_margin / (situation_margin + mean_stdev + 1e-9))
                best_indices = {i for i, v in means.items() if abs(v - best) <= 1e-9}
                for action_idx in selected_indices:
                    action = frame.legal_actions[action_idx]
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
                        "budget_reason": selection_reasons.get(action_idx, ""),
                        "action": action.compact(),
                        "behavior_chosen": 1 if action_idx == chosen_idx else 0,
                        "branch_rollouts": int(branch_rollouts_per_action),
                        "mean_actor_score": float(means[action_idx]),
                        "actor_score_stdev": float(stdevs.get(action_idx, 0.0)),
                        "best_mean_actor_score": float(best),
                        "second_best_mean_actor_score": float(second_best),
                        "chosen_mean_actor_score": float(chosen_score),
                        "value_gap_to_best": float(best - means[action_idx]),
                        "situation_best_margin": float(situation_margin),
                        "label_confidence_proxy": float(label_confidence_proxy),
                        "is_best_action": 1 if action_idx in best_indices else 0,
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

            # Continue the behavior game along the actual behavior-policy path.
            apply_decision_index(state, frame, chosen_idx, transition_rng)

    cpp_mismatches, finalized_transitions = _finalize_cpp_rows(transition_rows, records, expected_sigs, row_indices)
    candidate_actions = len(candidate_rows)
    by_situation: dict[str, list[Mapping[str, object]]] = {}
    for row in candidate_rows:
        by_situation.setdefault(str(row["situation_id"]), []).append(row)
    action_counts = [int(rows[0]["action_count"]) for rows in by_situation.values() if rows]
    regrets = []
    chosen_best = 0
    decisive = 0
    for rows in by_situation.values():
        chosen = [r for r in rows if int(r["behavior_chosen"]) == 1]
        if chosen:
            regrets.append(float(chosen[0]["best_mean_actor_score"]) - float(chosen[0]["chosen_mean_actor_score"]))
            chosen_best += int(chosen[0]["behavior_chosen_is_best"])
        scores = sorted({float(r["mean_actor_score"]) for r in rows})
        if len(scores) > 1 and scores[-1] - scores[0] > 1e-9:
            decisive += 1
    skipped_rows = [r for r in finalized_transitions if r.get("supported_by_cpp") is False]
    mismatch_rows = [r for r in finalized_transitions if r.get("cpp_match") is False]
    summary = ActionCounterfactualSummary(
        revision=revision,
        behavior_games=len(specs),
        behavior_decisions=int(behavior_decisions),
        sampled_situations=int(situation_count),
        skipped_high_action_frames=int(skipped_high),
        full_menu_situations=int(full_menu_situations),
        budgeted_situations=int(budgeted_situations),
        candidate_actions=int(candidate_actions),
        branch_games=int(len(branch_rows)),
        branch_rollouts_per_action=int(branch_rollouts_per_action),
        branch_terminal_games=int(branch_terminal),
        branch_truncations=int(branch_truncations),
        cpp_checked_transitions=int(sum(1 for r in finalized_transitions if r.get("supported_by_cpp") is True)),
        cpp_skipped_transitions=int(len(skipped_rows)),
        cpp_mismatches=int(cpp_mismatches),
        mean_action_count=float(sum(action_counts) / max(1, len(action_counts))),
        mean_best_minus_chosen=float(sum(regrets) / max(1, len(regrets))),
        behavior_chosen_best_rate=float(chosen_best / max(1, len(by_situation))),
        decisive_situations=int(decisive),
        tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(dict(r) for r in mismatch_rows[:5]),
        skipped_examples=tuple(dict(r) for r in skipped_rows[:5]),
    )
    return candidate_rows, branch_rows, list(finalized_transitions), summary
