from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence, Tuple

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
from .decision import apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import start_game
from .mulligan_ranker import make_mulligan_agent
from .payoff import StrategyBundle
from .public_agents import make_public_agent
from .reward_guard import reward_packet_from_state

REWARD_CONVENTION = "draw_half_reporting_terminal_only_training"
PUBLIC_INTERFACE = "public_decision_frame"


@dataclass(frozen=True)
class CppShadowGameSpec:
    """One public-strategy game to run under Python semantics and C++ shadow checks."""

    game_id: str
    strategy0: str
    strategy1: str
    deck0_name: str
    deck1_name: str
    deck0: DeckVector
    deck1: DeckVector
    agent0: str
    agent1: str
    mulligan0: str
    mulligan1: str
    seed: int
    starting_player: int
    starting_life: int
    max_decisions: int = 500
    simulator_revision: str = "rev0026"


@dataclass(frozen=True)
class CppShadowTransitionRow:
    game_id: str
    step: int
    player: int
    frame: str
    main_phase: str
    pending_choice_kind: str
    stack_depth: int
    action_kind: str
    action: str
    supported_by_cpp: bool
    skipped_reason: str
    cpp_match: bool | None
    case_id: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PreparedCppShadowRollout:
    """Live rollout records after Python has applied semantics, before C++ batch."""

    revision: str
    game_rows: Tuple[Dict[str, object], ...]
    records: Tuple[TransitionMicroRecord, ...]
    expected_signatures: Tuple[str, ...]
    record_row_indices: Tuple[int, ...]
    transition_rows: Tuple[CppShadowTransitionRow, ...]
    python_errors: Tuple[str, ...]

    @property
    def games(self) -> int:
        return len(self.game_rows)

    @property
    def events(self) -> int:
        return len(self.transition_rows)

    @property
    def supported_events(self) -> int:
        return len(self.records)


@dataclass(frozen=True)
class CppShadowRolloutSummary:
    revision: str
    games: int
    events: int
    supported_events: int
    skipped_events: int
    mismatches: int
    python_errors: int
    support_rate: float
    cpp_match_rate_on_supported: float
    terminal_games: int
    truncations: int
    total_decisions: int
    tool_status: Dict[str, object]
    unsupported_examples: Tuple[Dict[str, object], ...]
    mismatch_examples: Tuple[Dict[str, object], ...]
    python_error_examples: Tuple[str, ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _pending_kind(state) -> str:
    return "none" if state.pending_choice is None else str(state.pending_choice.kind)


def _score_for_player(result: MatchResult, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def _row_from_finished_state(spec: CppShadowGameSpec, state, result: MatchResult) -> Dict[str, object]:
    p0_packet = reward_packet_from_state(state, 0)
    p1_packet = reward_packet_from_state(state, 1)
    return {
        "simulator_revision": spec.simulator_revision,
        "strategy0": spec.strategy0,
        "strategy1": spec.strategy1,
        "deck0": spec.deck0_name,
        "deck1": spec.deck1_name,
        "agent0": spec.agent0,
        "agent1": spec.agent1,
        "mulligan0": spec.mulligan0,
        "mulligan1": spec.mulligan1,
        "starting_life": int(spec.starting_life),
        "starting_player": int(spec.starting_player),
        "seed": int(spec.seed),
        "transition_seed": int(spec.seed),
        "agent_seed": int(spec.seed) + 1000003,
        "winner": "None" if result.winner is None else str(result.winner),
        "p0_score": _score_for_player(result, 0),
        "p1_score": _score_for_player(result, 1),
        "p0_terminal_win": 1.0 if result.winner == 0 else 0.0,
        "p1_terminal_win": 1.0 if result.winner == 1 else 0.0,
        "is_nonterminal_draw": result.winner is None,
        "is_truncation": result.loss_reason == "max_decisions_reached",
        "loss_reason": result.loss_reason,
        "decisions": int(result.decisions),
        "log_events": int(result.log_events),
        "turn_number": int(state.turn_number),
        "reward_convention": REWARD_CONVENTION,
        "interface": PUBLIC_INTERFACE,
        "p0_terminal_only_score": "None" if p0_packet.terminal_only_score is None else p0_packet.terminal_only_score,
        "p1_terminal_only_score": "None" if p1_packet.terminal_only_score is None else p1_packet.terminal_only_score,
        "cpp_shadow_game_id": spec.game_id,
    }


def strategy_pair_specs(
    strategies: Sequence[StrategyBundle],
    *,
    simulator_revision: str = "rev0026",
    life_totals: Sequence[int] = (20, 40),
    reps: int = 1,
    base_seed: int = 26000,
    max_decisions: int = 500,
) -> Tuple[CppShadowGameSpec, ...]:
    """Create a small ordered payoff grid as C++ shadow rollout specs."""

    specs: list[CppShadowGameSpec] = []
    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                for starting_player in (0, 1):
                    for rep in range(reps):
                        specs.append(
                            CppShadowGameSpec(
                                game_id=f"g{k:05d}_life{life}_sp{starting_player}_{left.strategy_id}_vs_{right.strategy_id}_r{rep}",
                                strategy0=left.strategy_id,
                                strategy1=right.strategy_id,
                                deck0_name=left.deck_name,
                                deck1_name=right.deck_name,
                                deck0=left.deck,
                                deck1=right.deck,
                                agent0=left.agent_name,
                                agent1=right.agent_name,
                                mulligan0=str(left.mulligan_policy),
                                mulligan1=str(right.mulligan_policy),
                                seed=base_seed + k,
                                starting_player=int(starting_player),
                                starting_life=int(life),
                                max_decisions=int(max_decisions),
                                simulator_revision=simulator_revision,
                            )
                        )
                        k += 1
    return tuple(specs)


def run_cpp_shadow_outcome_rows(
    specs: Sequence[CppShadowGameSpec],
    *,
    revision: str = "rev0026",
) -> tuple[Tuple[Dict[str, object], ...], Tuple[str, ...]]:
    """Run CppShadowGameSpec games without building per-transition C++ records.

    This is the population-scale path: it preserves the exact public-agent,
    mulligan, RNG, and terminal-row semantics used by
    ``prepare_cpp_shadow_rollout`` but skips the deep-copy/transition-record work
    that dominates long empirical-game runs.  Pair it with a smaller sampled
    ``prepare_cpp_shadow_rollout`` call when C++ parity evidence is still needed.
    """

    game_rows: list[Dict[str, object]] = []
    python_errors: list[str] = []
    agent_cache: Dict[str, object] = {}

    def cached_agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    for spec in specs:
        try:
            transition_rng = Random(int(spec.seed))
            agent_rng = Random(int(spec.seed) + 1000003)
            state = start_game(
                spec.deck0,
                spec.deck1,
                seed=int(spec.seed),
                starting_player=int(spec.starting_player),
                starting_life=int(spec.starting_life),
                mulligan_agents=(make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1)),
                record_log=False,
            )
            agents = [cached_agent(spec.agent0), cached_agent(spec.agent1)]
            decisions = 0
            for step in range(1, int(spec.max_decisions) + 1):
                if state.winner is not None:
                    break
                frame = build_decision_frame(state)
                if frame.action_count <= 0:
                    break
                action_index = agents[frame.player].choose_action_index(frame, agent_rng)  # type: ignore[attr-defined]
                if action_index < 0 or action_index >= frame.action_count:
                    python_errors.append(f"{spec.game_id} step {step}: illegal action index {action_index}/{frame.action_count}")
                    break
                apply_decision_index(state, frame, action_index, transition_rng)
                decisions = int(step)
            if state.winner is None:
                state.frame = "GAME_OVER"
                state.loss_reason = "max_decisions_reached"
            result = MatchResult(state.winner, state.loss_reason, int(decisions), len(state.log))
            row = _row_from_finished_state(spec, state, result)
            row["outcome_runner_revision"] = revision
            row["cpp_shadow_game_id"] = spec.game_id
            game_rows.append(row)
        except Exception as exc:  # pragma: no cover - diagnostics path
            python_errors.append(f"{spec.game_id}: exception {type(exc).__name__}: {exc}")

    return tuple(game_rows), tuple(python_errors)


def sample_sequence_evenly(items: Sequence[CppShadowGameSpec], *, max_items: int) -> tuple[CppShadowGameSpec, ...]:
    """Return a deterministic chronology-spanning sample from a sequence."""

    if max_items <= 0 or len(items) <= int(max_items):
        return tuple(items)
    n = len(items)
    selected_indices = sorted({round(i * (n - 1) / (int(max_items) - 1)) for i in range(int(max_items))})
    return tuple(items[i] for i in selected_indices)


def prepare_cpp_shadow_rollout(specs: Sequence[CppShadowGameSpec], *, revision: str = "rev0026") -> PreparedCppShadowRollout:
    """Run public games in Python and prepare one batched C++ parity check.

    This is the rev0026 batch-rollout sketch.  It is not yet a C++ tournament
    engine: Python still chooses agents, enforces hidden-information observations,
    and applies the authoritative transition.  C++ receives a batch of the exact
    one-action transitions that occurred and must reproduce Python's SIGv2 after
    each action.  The API avoids writing large JSON traces for every smoke run.
    """

    records: list[TransitionMicroRecord] = []
    expected: list[str] = []
    row_indices: list[int] = []
    transition_rows: list[CppShadowTransitionRow] = []
    game_rows: list[Dict[str, object]] = []
    python_errors: list[str] = []
    agent_cache: Dict[str, object] = {}

    def cached_agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    for spec in specs:
        try:
            transition_rng = Random(int(spec.seed))
            agent_rng = Random(int(spec.seed) + 1000003)
            state = start_game(
                spec.deck0,
                spec.deck1,
                seed=int(spec.seed),
                starting_player=int(spec.starting_player),
                starting_life=int(spec.starting_life),
                mulligan_agents=(make_mulligan_agent(spec.mulligan0), make_mulligan_agent(spec.mulligan1)),
                record_log=False,
            )
            agents = [cached_agent(spec.agent0), cached_agent(spec.agent1)]
            decisions = 0
            for step in range(1, int(spec.max_decisions) + 1):
                if state.winner is not None:
                    break
                frame = build_decision_frame(state)
                if frame.action_count <= 0:
                    break
                action_index = agents[frame.player].choose_action_index(frame, agent_rng)  # type: ignore[attr-defined]
                if action_index < 0 or action_index >= frame.action_count:
                    python_errors.append(f"{spec.game_id} step {step}: illegal action index {action_index}/{frame.action_count}")
                    break
                action = frame.legal_actions[action_index]
                pre_state = copy.deepcopy(state)
                pre_frame = str(state.frame)
                pre_main_phase = str(state.main_phase)
                pre_pending_kind = _pending_kind(state)
                pre_stack_depth = len(state.stack)
                case_id = f"{spec.game_id}_step{step}_{pre_frame}_{pre_pending_kind}_{action.kind}"
                apply_decision_index(state, frame, action_index, transition_rng)
                decisions = int(step)
                transported = with_jace_ultimate_shuffle_transport(pre_state, action, state)
                supported = is_supported_transition(pre_state, transported)
                skipped_reason = "" if supported else "unsupported_by_cpp_transition_microkernel"
                row_index = len(transition_rows)
                if supported:
                    records.append(transition_record_from_state_action(pre_state, transported, case_id))
                    expected.append(state_signature(state))
                    row_indices.append(row_index)
                transition_rows.append(
                    CppShadowTransitionRow(
                        game_id=spec.game_id,
                        step=int(decisions),
                        player=int(frame.player),
                        frame=pre_frame,
                        main_phase=pre_main_phase,
                        pending_choice_kind=pre_pending_kind,
                        stack_depth=int(pre_stack_depth),
                        action_kind=str(action.kind),
                        action=action.compact(),
                        supported_by_cpp=bool(supported),
                        skipped_reason=skipped_reason,
                        cpp_match=None,
                        case_id=case_id,
                    )
                )
            if state.winner is None:
                state.frame = "GAME_OVER"
                state.loss_reason = "max_decisions_reached"
            result = MatchResult(state.winner, state.loss_reason, int(decisions), len(state.log))
            game_rows.append(_row_from_finished_state(spec, state, result))
        except Exception as exc:  # pragma: no cover - diagnostics path
            python_errors.append(f"{spec.game_id}: exception {type(exc).__name__}: {exc}")

    return PreparedCppShadowRollout(
        revision=revision,
        game_rows=tuple(game_rows),
        records=tuple(records),
        expected_signatures=tuple(expected),
        record_row_indices=tuple(row_indices),
        transition_rows=tuple(transition_rows),
        python_errors=tuple(python_errors),
    )


def sample_prepared_cpp_shadow_rollout(prepared: PreparedCppShadowRollout, *, max_records: int) -> PreparedCppShadowRollout:
    """Return an evenly spaced C++ shadow sample while preserving all game rows.

    Long population runs can generate far more transition micro-records than are
    useful to re-check on every linked revision.  This helper keeps outcome rows
    intact, selects a deterministic chronology-spanning sample of supported C++
    records, and rewrites record-row indices so ``finalize_cpp_shadow_rollout``
    can evaluate the sample without shipping the full raw transition table.
    Callers should separately report ``len(prepared.transition_rows)`` when they
    need the raw generated transition count.
    """

    if max_records <= 0 or len(prepared.records) <= int(max_records):
        return prepared
    n = len(prepared.records)
    selected_indices = sorted({round(i * (n - 1) / (int(max_records) - 1)) for i in range(int(max_records))})
    selected_records = []
    selected_expected = []
    selected_rows = []
    selected_row_indices = []
    for record_index in selected_indices:
        old_row_index = prepared.record_row_indices[record_index]
        selected_records.append(prepared.records[record_index])
        selected_expected.append(prepared.expected_signatures[record_index])
        selected_row_indices.append(len(selected_rows))
        selected_rows.append(prepared.transition_rows[old_row_index])
    return PreparedCppShadowRollout(
        revision=prepared.revision,
        game_rows=prepared.game_rows,
        records=tuple(selected_records),
        expected_signatures=tuple(selected_expected),
        record_row_indices=tuple(selected_row_indices),
        transition_rows=tuple(selected_rows),
        python_errors=prepared.python_errors,
    )


def finalize_cpp_shadow_rollout(prepared: PreparedCppShadowRollout) -> tuple[CppShadowRolloutSummary, list[CppShadowTransitionRow]]:
    """Run one batched C++ transition check for a prepared live rollout."""

    rows = list(prepared.transition_rows)
    mismatches = 0
    mismatch_examples: list[Dict[str, object]] = []
    if prepared.records:
        actual = cpp_transition_signatures(prepared.records)
        for record_idx, (got, want) in enumerate(zip(actual, prepared.expected_signatures)):
            row_index = prepared.record_row_indices[record_idx]
            old = rows[row_index]
            ok = got == want
            if not ok:
                mismatches += 1
                if len(mismatch_examples) < 10:
                    mismatch_examples.append({"case_id": old.case_id, "game_id": old.game_id, "step": old.step, "action": old.action, "expected": want, "actual": got})
            rows[row_index] = CppShadowTransitionRow(
                game_id=old.game_id,
                step=old.step,
                player=old.player,
                frame=old.frame,
                main_phase=old.main_phase,
                pending_choice_kind=old.pending_choice_kind,
                stack_depth=old.stack_depth,
                action_kind=old.action_kind,
                action=old.action,
                supported_by_cpp=old.supported_by_cpp,
                skipped_reason=old.skipped_reason,
                cpp_match=ok,
                case_id=old.case_id,
            )

    events = len(rows)
    supported = sum(1 for r in rows if r.supported_by_cpp)
    skipped = events - supported
    match_rate = 1.0 if supported == 0 else (supported - mismatches) / supported
    terminal_games = sum(1 for r in prepared.game_rows if str(r.get("winner")) != "None")
    truncations = sum(1 for r in prepared.game_rows if str(r.get("is_truncation")).lower() in {"true", "1"})
    total_decisions = sum(int(r.get("decisions", 0)) for r in prepared.game_rows)
    summary = CppShadowRolloutSummary(
        revision=prepared.revision,
        games=len(prepared.game_rows),
        events=events,
        supported_events=supported,
        skipped_events=skipped,
        mismatches=mismatches,
        python_errors=len(prepared.python_errors),
        support_rate=0.0 if events == 0 else supported / events,
        cpp_match_rate_on_supported=match_rate,
        terminal_games=terminal_games,
        truncations=truncations,
        total_decisions=total_decisions,
        tool_status=cpp_transition_tool_status().as_dict(),
        unsupported_examples=tuple(r.as_dict() for r in rows if not r.supported_by_cpp)[:10],
        mismatch_examples=tuple(mismatch_examples),
        python_error_examples=tuple(prepared.python_errors[:10]),
    )
    return summary, rows


__all__ = [
    "CppShadowGameSpec",
    "CppShadowTransitionRow",
    "PreparedCppShadowRollout",
    "CppShadowRolloutSummary",
    "finalize_cpp_shadow_rollout",
    "prepare_cpp_shadow_rollout",
    "run_cpp_shadow_outcome_rows",
    "sample_prepared_cpp_shadow_rollout",
    "sample_sequence_evenly",
    "strategy_pair_specs",
]
