from __future__ import annotations

import copy
import shutil
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from random import Random
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from .agents import MatchResult
from .cpp_transition import (
    TransitionMicroRecord,
    project_root,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
    is_supported_transition,
    cpp_transition_tool_status,
)
from .decision import apply_decision_index, build_decision_frame
from .engine import start_game
from .mulligan_ranker import make_mulligan_agent
from .payoff import StrategyBundle
from .public_agents import make_public_agent
from .reward_guard import reward_packet_from_state

REWARD_CONVENTION = "draw_half_reporting_terminal_only_training"
PUBLIC_INTERFACE = "public_decision_frame"


@dataclass(frozen=True)
class CppSegmentToolStatus:
    gpp: str | None
    source_exists: bool
    binary_exists: bool
    usable: bool
    error: str | None = None

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CppNoChoiceSegmentSpec:
    game_id: str
    strategy0: str
    strategy1: str
    deck0_name: str
    deck1_name: str
    deck0: object
    deck1: object
    agent0: str
    agent1: str
    mulligan0: str
    mulligan1: str
    seed: int
    starting_player: int
    starting_life: int
    max_decisions: int = 600
    simulator_revision: str = "rev0031"


@dataclass(frozen=True)
class PreparedSegmentRecord:
    segment_id: str
    record: TransitionMicroRecord

    def to_tsv(self) -> str:
        return f"{self.segment_id}\t{self.record.to_tsv()}"


@dataclass(frozen=True)
class CppNoChoiceSegmentRow:
    game_id: str
    segment_id: str
    segment_index: int
    start_step: int
    end_step: int
    length: int
    player_sequence: str
    action_sequence: str
    all_pass: bool
    start_signature: str
    expected_end_signature: str
    cpp_end_signature: str | None
    cpp_match: bool | None
    supported_events: int
    skipped_events: int
    skipped_reason: str

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CppNoChoiceGameRow:
    simulator_revision: str
    game_id: str
    strategy0: str
    strategy1: str
    deck0: str
    deck1: str
    agent0: str
    agent1: str
    mulligan0: str
    mulligan1: str
    starting_life: int
    starting_player: int
    seed: int
    transition_seed: int
    agent_seed: int
    winner: str
    p0_score: float
    p1_score: float
    p0_terminal_win: float
    p1_terminal_win: float
    is_nonterminal_draw: bool
    is_truncation: bool
    loss_reason: str
    decisions: int
    segments: int
    forced_actions: int
    choice_frames: int
    cpp_checked_segments: int
    cpp_segment_mismatches: int
    log_events: int
    turn_number: int
    reward_convention: str
    interface: str
    p0_terminal_only_score: object
    p1_terminal_only_score: object

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CppNoChoiceSegmentSummary:
    revision: str
    games: int
    decisions: int
    segments: int
    checked_segments: int
    forced_actions: int
    supported_events: int
    skipped_events: int
    cpp_segment_mismatches: int
    cpp_match_rate_on_checked_segments: float
    max_segment_length: int
    mean_segment_length: float
    all_pass_segments: int
    all_pass_rate: float
    estimated_decision_compression_ratio: float
    terminal_games: int
    truncations: int
    tool_status: Dict[str, object]
    transition_tool_status: Dict[str, object]
    mismatch_examples: Tuple[Dict[str, object], ...]
    skipped_examples: Tuple[Dict[str, object], ...]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def segment_source_path() -> Path:
    return project_root() / "cpp" / "muc5_transition_segment.cpp"


def segment_binary_path() -> Path:
    return project_root() / "build" / "muc5_transition_segment"


def build_segment_binary(*, force: bool = False) -> Path:
    src = segment_source_path()
    out = segment_binary_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    gpp = shutil.which("g++")
    if not gpp:
        raise RuntimeError("g++ not available in this cloudtainer")
    if not src.exists():
        raise RuntimeError(f"C++ segment source missing: {src}")
    if force or not out.exists() or src.stat().st_mtime > out.stat().st_mtime:
        subprocess.run(
            [gpp, "-O3", "-std=c++17", str(src), "-o", str(out)],
            cwd=str(project_root()),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    return out


def cpp_segment_tool_status(*, try_build: bool = True) -> CppSegmentToolStatus:
    err: str | None = None
    usable = False
    try:
        if try_build:
            build_segment_binary()
        usable = segment_binary_path().exists()
    except Exception as exc:  # pragma: no cover - diagnostic path
        err = repr(exc)
    return CppSegmentToolStatus(
        gpp=shutil.which("g++"),
        source_exists=segment_source_path().exists(),
        binary_exists=segment_binary_path().exists(),
        usable=usable,
        error=err,
    )


def cpp_segment_signatures(records: Sequence[PreparedSegmentRecord], *, force_build: bool = False) -> Dict[str, str]:
    exe = build_segment_binary(force=force_build)
    payload = "\n".join(r.to_tsv() for r in records) + ("\n" if records else "")
    proc = subprocess.run(
        [str(exe)],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        cwd=str(project_root()),
    )
    out: Dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line:
            continue
        sid, sig = line.split("\t", 1)
        out[sid] = sig
    return out


def _pending_kind(state) -> str:
    return "none" if state.pending_choice is None else str(state.pending_choice.kind)


def _score_for_player(result: MatchResult, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def _game_row(spec: CppNoChoiceSegmentSpec, state, result: MatchResult, segments: Sequence[CppNoChoiceSegmentRow], choice_frames: int) -> CppNoChoiceGameRow:
    p0_packet = reward_packet_from_state(state, 0)
    p1_packet = reward_packet_from_state(state, 1)
    return CppNoChoiceGameRow(
        simulator_revision=spec.simulator_revision,
        game_id=spec.game_id,
        strategy0=spec.strategy0,
        strategy1=spec.strategy1,
        deck0=spec.deck0_name,
        deck1=spec.deck1_name,
        agent0=spec.agent0,
        agent1=spec.agent1,
        mulligan0=spec.mulligan0,
        mulligan1=spec.mulligan1,
        starting_life=int(spec.starting_life),
        starting_player=int(spec.starting_player),
        seed=int(spec.seed),
        transition_seed=int(spec.seed),
        agent_seed=int(spec.seed) + 1000003,
        winner="None" if result.winner is None else str(result.winner),
        p0_score=_score_for_player(result, 0),
        p1_score=_score_for_player(result, 1),
        p0_terminal_win=1.0 if result.winner == 0 else 0.0,
        p1_terminal_win=1.0 if result.winner == 1 else 0.0,
        is_nonterminal_draw=result.winner is None,
        is_truncation=result.loss_reason == "max_decisions_reached",
        loss_reason=result.loss_reason,
        decisions=int(result.decisions),
        segments=len(segments),
        forced_actions=sum(s.length for s in segments),
        choice_frames=int(choice_frames),
        cpp_checked_segments=sum(1 for s in segments if s.cpp_match is not None),
        cpp_segment_mismatches=sum(1 for s in segments if s.cpp_match is False),
        log_events=int(result.log_events),
        turn_number=int(state.turn_number),
        reward_convention=REWARD_CONVENTION,
        interface=PUBLIC_INTERFACE,
        p0_terminal_only_score="None" if p0_packet.terminal_only_score is None else p0_packet.terminal_only_score,
        p1_terminal_only_score="None" if p1_packet.terminal_only_score is None else p1_packet.terminal_only_score,
    )


def finalize_segment_rows(
    rows: Sequence[CppNoChoiceSegmentRow],
    records: Sequence[PreparedSegmentRecord],
) -> Tuple[CppNoChoiceSegmentRow, ...]:
    if not rows:
        return tuple()
    cpp_sigs = cpp_segment_signatures(records) if records else {}
    out: list[CppNoChoiceSegmentRow] = []
    for row in rows:
        got = cpp_sigs.get(row.segment_id)
        if row.skipped_events > 0:
            match = None
        else:
            match = (got == row.expected_end_signature)
        out.append(
            replace(row, cpp_end_signature=got, cpp_match=match)
        )
    return tuple(out)


def play_public_game_collect_nochoice_segments(
    spec: CppNoChoiceSegmentSpec,
    *,
    agent_cache: Dict[str, object] | None = None,
    mulligan_cache: Dict[str, object] | None = None,
    finalize_cpp: bool = True,
) -> Tuple[CppNoChoiceGameRow, Tuple[CppNoChoiceSegmentRow, ...], Tuple[PreparedSegmentRecord, ...]]:
    """Run one Python-authoritative public game and collect forced-run C++ segment records."""

    agent_cache = {} if agent_cache is None else agent_cache
    mulligan_cache = {} if mulligan_cache is None else mulligan_cache

    def cached_agent(name: str):
        if name not in agent_cache:
            agent_cache[name] = make_public_agent(name)
        return agent_cache[name]

    def cached_mulligan(name: str):
        if name not in mulligan_cache:
            mulligan_cache[name] = make_mulligan_agent(name)
        return mulligan_cache[name]

    transition_rng = Random(int(spec.seed))
    agent_rng = Random(int(spec.seed) + 1000003)
    state = start_game(
        spec.deck0,
        spec.deck1,
        seed=int(spec.seed),
        starting_player=int(spec.starting_player),
        starting_life=int(spec.starting_life),
        mulligan_agents=(cached_mulligan(spec.mulligan0), cached_mulligan(spec.mulligan1)),
        record_log=False,
    )
    agents = [cached_agent(spec.agent0), cached_agent(spec.agent1)]

    pending_rows: list[CppNoChoiceSegmentRow] = []
    prepared: list[PreparedSegmentRecord] = []
    segment_rows: list[CppNoChoiceSegmentRow] = []
    active_records: list[PreparedSegmentRecord] = []
    active_actions: list[str] = []
    active_players: list[str] = []
    active_start_step: int | None = None
    active_start_signature = ""
    active_skipped = 0
    active_skipped_reasons: list[str] = []
    choice_frames = 0

    def finish_segment(end_step: int) -> None:
        nonlocal active_records, active_actions, active_players, active_start_step, active_start_signature, active_skipped, active_skipped_reasons
        if active_start_step is None:
            return
        segment_id = f"{spec.game_id}_seg{len(segment_rows):04d}"
        row = CppNoChoiceSegmentRow(
            game_id=spec.game_id,
            segment_id=segment_id,
            segment_index=len(segment_rows),
            start_step=int(active_start_step),
            end_step=int(end_step),
            length=len(active_actions),
            player_sequence="|".join(active_players),
            action_sequence=" || ".join(active_actions),
            all_pass=all(a == "PASS" for a in active_actions),
            start_signature=active_start_signature,
            expected_end_signature=state_signature(state),
            cpp_end_signature=None,
            cpp_match=None,
            supported_events=len(active_records),
            skipped_events=int(active_skipped),
            skipped_reason="; ".join(sorted(set(active_skipped_reasons))),
        )
        # Rewrite the temporary ids assigned before the real segment id existed.
        for rec in active_records:
            prepared.append(PreparedSegmentRecord(segment_id=segment_id, record=rec.record))
        segment_rows.append(row)
        active_records = []
        active_actions = []
        active_players = []
        active_start_step = None
        active_start_signature = ""
        active_skipped = 0
        active_skipped_reasons = []

    decisions = 0
    for decisions in range(1, int(spec.max_decisions) + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        if frame.action_count == 1:
            if active_start_step is None:
                active_start_step = decisions
                active_start_signature = state_signature(state)
            action_index = 0
            action = frame.legal_actions[0]
            action_compact = action.compact()
            pre_state = copy.deepcopy(state)
            apply_decision_index(state, frame, action_index, transition_rng)
            transported = with_jace_ultimate_shuffle_transport(pre_state, action, state)
            if is_supported_transition(pre_state, transported):
                # Temporary segment id, replaced when the segment finishes.
                rec = transition_record_from_state_action(pre_state, transported, f"{spec.game_id}_step{decisions}_{frame.player}_{action.kind}")
                active_records.append(PreparedSegmentRecord(segment_id="__pending__", record=rec))
            else:
                active_skipped += 1
                active_skipped_reasons.append(f"unsupported:{pre_state.frame}:{_pending_kind(pre_state)}:{action_compact}")
            active_actions.append(action_compact)
            active_players.append(str(frame.player))
        else:
            choice_frames += 1
            finish_segment(decisions - 1)
            action_index = agents[frame.player].choose_action_index(frame, agent_rng)  # type: ignore[attr-defined]
            if action_index < 0 or action_index >= frame.action_count:
                raise ValueError(f"{spec.game_id}: illegal public action index {action_index}/{frame.action_count}")
            apply_decision_index(state, frame, action_index, transition_rng)
    finish_segment(decisions)

    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    result = MatchResult(state.winner, state.loss_reason, int(decisions), len(state.log))
    final_rows = finalize_segment_rows(segment_rows, prepared) if finalize_cpp else tuple(segment_rows)
    return _game_row(spec, state, result, final_rows, choice_frames), final_rows, tuple(prepared)


def build_nochoice_segment_specs(
    strategies: Sequence[StrategyBundle],
    *,
    simulator_revision: str = "rev0031",
    life_totals: Sequence[int] = (20, 40),
    reps: int = 1,
    base_seed: int = 3100000,
    max_decisions: int = 620,
    limit_pairs: int | None = None,
) -> Tuple[CppNoChoiceSegmentSpec, ...]:
    specs: list[CppNoChoiceSegmentSpec] = []
    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                if limit_pairs is not None and len(specs) >= limit_pairs:
                    return tuple(specs)
                for starting_player in (0, 1):
                    for rep in range(reps):
                        specs.append(
                            CppNoChoiceSegmentSpec(
                                game_id=f"seg_g{k:05d}_life{life}_sp{starting_player}_{left.strategy_id}_vs_{right.strategy_id}_r{rep}",
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



def _refresh_game_row_cpp_counts(game_row: Dict[str, object], rows: Sequence[CppNoChoiceSegmentRow]) -> Dict[str, object]:
    out = dict(game_row)
    out["segments"] = int(len(rows))
    out["forced_actions"] = int(sum(r.length for r in rows))
    out["cpp_checked_segments"] = int(sum(1 for r in rows if r.cpp_match is not None))
    out["cpp_segment_mismatches"] = int(sum(1 for r in rows if r.cpp_match is False))
    return out


def _segment_summary_from_rows(
    game_rows: Sequence[Mapping[str, object]],
    segment_rows: Sequence[CppNoChoiceSegmentRow],
    *,
    revision: str,
) -> CppNoChoiceSegmentSummary:
    checked = [r for r in segment_rows if r.cpp_match is not None]
    mismatches = [r for r in segment_rows if r.cpp_match is False]
    skipped = [r for r in segment_rows if r.skipped_events > 0]
    decisions = sum(int(r["decisions"]) for r in game_rows)
    choice_frames = sum(int(r["choice_frames"]) for r in game_rows)
    forced_actions = sum(int(r.length) for r in segment_rows)
    estimated_steps = choice_frames + len(segment_rows)
    return CppNoChoiceSegmentSummary(
        revision=revision,
        games=len(game_rows),
        decisions=int(decisions),
        segments=len(segment_rows),
        checked_segments=len(checked),
        forced_actions=int(forced_actions),
        supported_events=sum(int(r.supported_events) for r in segment_rows),
        skipped_events=sum(int(r.skipped_events) for r in segment_rows),
        cpp_segment_mismatches=len(mismatches),
        cpp_match_rate_on_checked_segments=1.0 if not checked else (len(checked) - len(mismatches)) / len(checked),
        max_segment_length=max((r.length for r in segment_rows), default=0),
        mean_segment_length=float(forced_actions / max(1, len(segment_rows))),
        all_pass_segments=sum(1 for r in segment_rows if r.all_pass),
        all_pass_rate=sum(1 for r in segment_rows if r.all_pass) / max(1, len(segment_rows)),
        estimated_decision_compression_ratio=float(decisions / max(1, estimated_steps)),
        terminal_games=sum(1 for r in game_rows if not bool(r["is_truncation"])),
        truncations=sum(1 for r in game_rows if bool(r["is_truncation"])),
        tool_status=cpp_segment_tool_status().as_dict(),
        transition_tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(r.as_dict() for r in mismatches[:5]),
        skipped_examples=tuple(r.as_dict() for r in skipped[:5]),
    )


def run_nochoice_segment_cpp_panel_batched(
    specs: Sequence[CppNoChoiceSegmentSpec],
    *,
    revision: str = "rev0032",
) -> Tuple[Tuple[Dict[str, object], ...], Tuple[Dict[str, object], ...], CppNoChoiceSegmentSummary]:
    """Run public games and finalize all no-choice C++ segments in one batch.

    rev0031 proved no-choice segments could be checked in C++ but finalized the
    C++ signatures per game.  rev0032 makes the operational seam match the
    performance doctrine: Python remains semantic authority, but the C++ segment
    checker is fed all prepared segment records in one coarse batch.
    """

    raw_game_rows: list[Dict[str, object]] = []
    raw_segment_rows: list[CppNoChoiceSegmentRow] = []
    prepared: list[PreparedSegmentRecord] = []
    agent_cache: Dict[str, object] = {}
    mulligan_cache: Dict[str, object] = {}
    for spec in specs:
        game_row, rows, records = play_public_game_collect_nochoice_segments(
            spec,
            agent_cache=agent_cache,
            mulligan_cache=mulligan_cache,
            finalize_cpp=False,
        )
        raw_game_rows.append(game_row.as_dict())
        raw_segment_rows.extend(rows)
        prepared.extend(records)

    # One subprocess invocation for the whole panel.
    cpp_sigs = cpp_segment_signatures(prepared) if prepared else {}
    finalized_rows: list[CppNoChoiceSegmentRow] = []
    for row in raw_segment_rows:
        got = cpp_sigs.get(row.segment_id)
        if row.skipped_events > 0:
            match = None
        else:
            match = (got == row.expected_end_signature)
        finalized_rows.append(replace(row, cpp_end_signature=got, cpp_match=match))

    by_game: Dict[str, list[CppNoChoiceSegmentRow]] = {}
    for row in finalized_rows:
        by_game.setdefault(row.game_id, []).append(row)
    game_rows = tuple(_refresh_game_row_cpp_counts(row, by_game.get(str(row["game_id"]), [])) for row in raw_game_rows)
    summary = _segment_summary_from_rows(game_rows, finalized_rows, revision=revision)
    return game_rows, tuple(r.as_dict() for r in finalized_rows), summary

def run_nochoice_segment_cpp_panel(specs: Sequence[CppNoChoiceSegmentSpec], *, revision: str = "rev0031") -> Tuple[Tuple[Dict[str, object], ...], Tuple[Dict[str, object], ...], CppNoChoiceSegmentSummary]:
    game_rows: list[Dict[str, object]] = []
    segment_rows: list[CppNoChoiceSegmentRow] = []
    agent_cache: Dict[str, object] = {}
    mulligan_cache: Dict[str, object] = {}
    for spec in specs:
        game_row, rows, _records = play_public_game_collect_nochoice_segments(spec, agent_cache=agent_cache, mulligan_cache=mulligan_cache)
        game_rows.append(game_row.as_dict())
        segment_rows.extend(rows)

    checked = [r for r in segment_rows if r.cpp_match is not None]
    mismatches = [r for r in segment_rows if r.cpp_match is False]
    skipped = [r for r in segment_rows if r.skipped_events > 0]
    decisions = sum(int(r["decisions"]) for r in game_rows)
    choice_frames = sum(int(r["choice_frames"]) for r in game_rows)
    forced_actions = sum(int(r.length) for r in segment_rows)
    estimated_steps = choice_frames + len(segment_rows)
    summary = CppNoChoiceSegmentSummary(
        revision=revision,
        games=len(game_rows),
        decisions=int(decisions),
        segments=len(segment_rows),
        checked_segments=len(checked),
        forced_actions=int(forced_actions),
        supported_events=sum(int(r.supported_events) for r in segment_rows),
        skipped_events=sum(int(r.skipped_events) for r in segment_rows),
        cpp_segment_mismatches=len(mismatches),
        cpp_match_rate_on_checked_segments=1.0 if not checked else (len(checked) - len(mismatches)) / len(checked),
        max_segment_length=max((r.length for r in segment_rows), default=0),
        mean_segment_length=float(forced_actions / max(1, len(segment_rows))),
        all_pass_segments=sum(1 for r in segment_rows if r.all_pass),
        all_pass_rate=sum(1 for r in segment_rows if r.all_pass) / max(1, len(segment_rows)),
        estimated_decision_compression_ratio=float(decisions / max(1, estimated_steps)),
        terminal_games=sum(1 for r in game_rows if not bool(r["is_truncation"])),
        truncations=sum(1 for r in game_rows if bool(r["is_truncation"])),
        tool_status=cpp_segment_tool_status().as_dict(),
        transition_tool_status=cpp_transition_tool_status().as_dict(),
        mismatch_examples=tuple(r.as_dict() for r in mismatches[:5]),
        skipped_examples=tuple(r.as_dict() for r in skipped[:5]),
    )
    return tuple(game_rows), tuple(r.as_dict() for r in segment_rows), summary
