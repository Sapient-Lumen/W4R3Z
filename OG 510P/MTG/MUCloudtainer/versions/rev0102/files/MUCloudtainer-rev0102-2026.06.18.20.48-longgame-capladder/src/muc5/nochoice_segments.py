from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, List, Sequence

from .agents import MatchResult
from .decision import PublicDecisionAgent, apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import GameState, start_game
from .mulligan import MulliganAgent, MulliganPolicy


@dataclass(frozen=True)
class NoChoiceGameSummary:
    game_id: str
    decisions: int
    choice_frames: int
    forced_frames: int
    pass_only_frames: int
    forced_runs: int
    max_forced_run: int
    mean_forced_run: float
    estimated_segment_steps: int
    estimated_compression_ratio: float
    winner: str
    loss_reason: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class NoChoiceAggregateSummary:
    games: int
    decisions: int
    choice_frames: int
    forced_frames: int
    pass_only_frames: int
    forced_runs: int
    max_forced_run: int
    mean_forced_run: float
    forced_frame_rate: float
    pass_only_frame_rate: float
    estimated_segment_steps: int
    estimated_compression_ratio: float
    truncations: int

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _finish_run(run_len: int, runs: List[int]) -> int:
    if run_len > 0:
        runs.append(run_len)
    return 0


def play_public_game_with_nochoice_audit(
    deck0: DeckVector,
    deck1: DeckVector,
    agent0: PublicDecisionAgent,
    agent1: PublicDecisionAgent,
    *,
    game_id: str,
    seed: int,
    transition_seed: int | None = None,
    agent_seed: int | None = None,
    starting_player: int = 0,
    starting_life: int = 20,
    max_decisions: int = 500,
    mulligan_agents: tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
) -> tuple[GameState, MatchResult, NoChoiceGameSummary]:
    """Play one public game and measure forced-action runs.

    A forced frame is any DecisionFrame with exactly one legal action.  This is
    *not* automatically safe to batch semantically, but long runs of such frames
    are the next place to look for a C++ no-choice segment kernel.
    """

    transition_rng = Random(seed if transition_seed is None else int(transition_seed))
    agent_rng = Random(seed + 1000003 if agent_seed is None else int(agent_seed))
    state = start_game(
        deck0,
        deck1,
        seed=seed,
        starting_player=starting_player,
        starting_life=starting_life,
        mulligan_agents=mulligan_agents,
        record_log=False,
    )
    agents = [agent0, agent1]
    decisions = 0
    choice_frames = 0
    forced_frames = 0
    pass_only_frames = 0
    forced_run = 0
    forced_runs: List[int] = []
    for decisions in range(1, max_decisions + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        if frame.action_count == 1:
            forced_frames += 1
            forced_run += 1
            if frame.legal_actions[0].kind == "PASS":
                pass_only_frames += 1
        else:
            choice_frames += 1
            forced_run = _finish_run(forced_run, forced_runs)
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        apply_decision_index(state, frame, action_index, transition_rng)
    forced_run = _finish_run(forced_run, forced_runs)
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    result = MatchResult(state.winner, state.loss_reason, decisions, len(state.log))
    estimated_segment_steps = choice_frames + len(forced_runs)
    summary = NoChoiceGameSummary(
        game_id=game_id,
        decisions=int(decisions),
        choice_frames=int(choice_frames),
        forced_frames=int(forced_frames),
        pass_only_frames=int(pass_only_frames),
        forced_runs=int(len(forced_runs)),
        max_forced_run=int(max(forced_runs) if forced_runs else 0),
        mean_forced_run=float(sum(forced_runs) / len(forced_runs)) if forced_runs else 0.0,
        estimated_segment_steps=int(estimated_segment_steps),
        estimated_compression_ratio=float(decisions / max(1, estimated_segment_steps)),
        winner="None" if result.winner is None else str(result.winner),
        loss_reason=result.loss_reason,
    )
    return state, result, summary


def aggregate_nochoice_summaries(rows: Sequence[NoChoiceGameSummary]) -> NoChoiceAggregateSummary:
    games = len(rows)
    decisions = sum(r.decisions for r in rows)
    choice_frames = sum(r.choice_frames for r in rows)
    forced_frames = sum(r.forced_frames for r in rows)
    pass_only_frames = sum(r.pass_only_frames for r in rows)
    forced_runs = sum(r.forced_runs for r in rows)
    estimated_segment_steps = sum(r.estimated_segment_steps for r in rows)
    weighted_run_total = sum(r.mean_forced_run * r.forced_runs for r in rows)
    return NoChoiceAggregateSummary(
        games=int(games),
        decisions=int(decisions),
        choice_frames=int(choice_frames),
        forced_frames=int(forced_frames),
        pass_only_frames=int(pass_only_frames),
        forced_runs=int(forced_runs),
        max_forced_run=int(max((r.max_forced_run for r in rows), default=0)),
        mean_forced_run=float(weighted_run_total / forced_runs) if forced_runs else 0.0,
        forced_frame_rate=float(forced_frames / max(1, decisions)),
        pass_only_frame_rate=float(pass_only_frames / max(1, decisions)),
        estimated_segment_steps=int(estimated_segment_steps),
        estimated_compression_ratio=float(decisions / max(1, estimated_segment_steps)),
        truncations=int(sum(1 for r in rows if r.loss_reason == "max_decisions_reached")),
    )

# --------------------------- rev0030 segment fingerprints ---------------------------

from .replay import state_fingerprint


@dataclass(frozen=True)
class NoChoiceSegmentFingerprintRow:
    game_id: str
    segment_index: int
    start_step: int
    end_step: int
    length: int
    player_sequence: str
    action_sequence: str
    all_pass: bool
    start_frame: str
    end_frame: str
    start_fingerprint: str
    end_fingerprint: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class NoChoiceSegmentFingerprintSummary:
    games: int
    segments: int
    total_forced_actions: int
    max_segment_length: int
    mean_segment_length: float
    all_pass_segments: int
    all_pass_rate: float
    estimated_decision_compression_ratio: float
    truncations: int

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def play_public_game_with_nochoice_fingerprints(
    deck0: DeckVector,
    deck1: DeckVector,
    agent0: PublicDecisionAgent,
    agent1: PublicDecisionAgent,
    *,
    game_id: str,
    seed: int,
    transition_seed: int | None = None,
    agent_seed: int | None = None,
    starting_player: int = 0,
    starting_life: int = 20,
    max_decisions: int = 500,
    mulligan_agents: tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
) -> tuple[GameState, MatchResult, NoChoiceGameSummary, tuple[NoChoiceSegmentFingerprintRow, ...]]:
    """Play a public game and emit start/end fingerprints for forced-action runs.

    This is a measurement seam for a future C++ no-choice-segment kernel.  It
    does not make C++ authoritative.  The important artifact is the segment
    transcript: start fingerprint, forced action sequence, and end fingerprint.
    """

    transition_rng = Random(seed if transition_seed is None else int(transition_seed))
    agent_rng = Random(seed + 1000003 if agent_seed is None else int(agent_seed))
    state = start_game(
        deck0,
        deck1,
        seed=seed,
        starting_player=starting_player,
        starting_life=starting_life,
        mulligan_agents=mulligan_agents,
        record_log=False,
    )
    agents = [agent0, agent1]
    decisions = 0
    choice_frames = 0
    forced_frames = 0
    pass_only_frames = 0
    forced_runs: List[int] = []
    segment_rows: List[NoChoiceSegmentFingerprintRow] = []
    active_start_step: int | None = None
    active_start_fingerprint = ""
    active_start_frame = ""
    active_actions: List[str] = []
    active_players: List[str] = []

    def finish_segment(end_step: int) -> None:
        nonlocal active_start_step, active_start_fingerprint, active_start_frame, active_actions, active_players
        if active_start_step is None:
            return
        forced_runs.append(len(active_actions))
        segment_rows.append(
            NoChoiceSegmentFingerprintRow(
                game_id=game_id,
                segment_index=len(segment_rows),
                start_step=int(active_start_step),
                end_step=int(end_step),
                length=len(active_actions),
                player_sequence="|".join(active_players),
                action_sequence=" || ".join(active_actions),
                all_pass=all(a == "PASS" for a in active_actions),
                start_frame=active_start_frame,
                end_frame=str(state.frame),
                start_fingerprint=active_start_fingerprint,
                end_fingerprint=state_fingerprint(state),
            )
        )
        active_start_step = None
        active_start_fingerprint = ""
        active_start_frame = ""
        active_actions = []
        active_players = []

    for decisions in range(1, max_decisions + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        if frame.action_count == 1:
            forced_frames += 1
            if active_start_step is None:
                active_start_step = decisions
                active_start_fingerprint = state_fingerprint(state)
                active_start_frame = str(state.frame)
            action = frame.legal_actions[0]
            active_actions.append(action.compact())
            active_players.append(str(frame.player))
            if action.kind == "PASS":
                pass_only_frames += 1
        else:
            choice_frames += 1
            finish_segment(decisions - 1)
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        apply_decision_index(state, frame, action_index, transition_rng)
    finish_segment(decisions)
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    result = MatchResult(state.winner, state.loss_reason, decisions, len(state.log))
    estimated_segment_steps = choice_frames + len(segment_rows)
    game_summary = NoChoiceGameSummary(
        game_id=game_id,
        decisions=int(decisions),
        choice_frames=int(choice_frames),
        forced_frames=int(forced_frames),
        pass_only_frames=int(pass_only_frames),
        forced_runs=int(len(segment_rows)),
        max_forced_run=int(max((r.length for r in segment_rows), default=0)),
        mean_forced_run=float(sum(r.length for r in segment_rows) / len(segment_rows)) if segment_rows else 0.0,
        estimated_segment_steps=int(estimated_segment_steps),
        estimated_compression_ratio=float(decisions / max(1, estimated_segment_steps)),
        winner="None" if result.winner is None else str(result.winner),
        loss_reason=result.loss_reason,
    )
    return state, result, game_summary, tuple(segment_rows)


def aggregate_nochoice_fingerprint_rows(
    game_summaries: Sequence[NoChoiceGameSummary],
    segment_rows: Sequence[NoChoiceSegmentFingerprintRow],
) -> NoChoiceSegmentFingerprintSummary:
    games = len(game_summaries)
    total_forced = sum(int(r.length) for r in segment_rows)
    estimated_steps = sum(int(g.choice_frames) for g in game_summaries) + len(segment_rows)
    decisions = sum(int(g.decisions) for g in game_summaries)
    return NoChoiceSegmentFingerprintSummary(
        games=int(games),
        segments=int(len(segment_rows)),
        total_forced_actions=int(total_forced),
        max_segment_length=int(max((r.length for r in segment_rows), default=0)),
        mean_segment_length=float(total_forced / max(1, len(segment_rows))),
        all_pass_segments=int(sum(1 for r in segment_rows if r.all_pass)),
        all_pass_rate=float(sum(1 for r in segment_rows if r.all_pass) / max(1, len(segment_rows))),
        estimated_decision_compression_ratio=float(decisions / max(1, estimated_steps)),
        truncations=int(sum(1 for g in game_summaries if g.loss_reason == "max_decisions_reached")),
    )
