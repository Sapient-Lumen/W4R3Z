from __future__ import annotations

import cProfile
import io
import pstats
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from .agents import HeuristicAgent, play_agent_game, play_public_agent_game
from .decision import PublicHeuristicAgent
from .deckspace import DeckVector
from .mulligan import POLICY_LAND_BAND


@dataclass(frozen=True)
class ThroughputResult:
    games: int
    decisions: int
    seconds: float
    games_per_second: float
    decisions_per_second: float
    validate_actions: bool
    record_log: bool
    max_decisions: int

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def benchmark_agent_games(
    deck0: DeckVector,
    deck1: DeckVector,
    *,
    games: int = 100,
    max_decisions: int = 500,
    starting_life: int = 20,
    validate_actions: bool = False,
    seed_base: int = 9000,
    record_log: bool = False,
) -> ThroughputResult:
    agent0 = HeuristicAgent()
    agent1 = HeuristicAgent()
    t0 = time.perf_counter()
    decisions = 0
    for i in range(games):
        _, result = play_agent_game(
            deck0,
            deck1,
            agent0,
            agent1,
            seed=seed_base + i,
            starting_player=i % 2,
            max_decisions=max_decisions,
            starting_life=starting_life,
            mulligan_policy=POLICY_LAND_BAND,
            validate_actions=validate_actions,
            record_log=record_log,
        )
        decisions += int(result.decisions)
    seconds = max(1e-12, time.perf_counter() - t0)
    return ThroughputResult(
        games=games,
        decisions=decisions,
        seconds=seconds,
        games_per_second=games / seconds,
        decisions_per_second=decisions / seconds,
        validate_actions=validate_actions,
        record_log=record_log,
        max_decisions=max_decisions,
    )


def profile_agent_games(
    deck0: DeckVector,
    deck1: DeckVector,
    *,
    games: int = 40,
    max_decisions: int = 500,
    starting_life: int = 20,
    validate_actions: bool = False,
    limit: int = 30,
) -> str:
    profiler = cProfile.Profile()

    def run() -> None:
        benchmark_agent_games(
            deck0,
            deck1,
            games=games,
            max_decisions=max_decisions,
            starting_life=starting_life,
            validate_actions=validate_actions,
            record_log=False,
        )

    profiler.enable()
    run()
    profiler.disable()
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s).strip_dirs().sort_stats("cumulative")
    stats.print_stats(limit)
    return s.getvalue()


def benchmark_public_decision_games(
    deck0: DeckVector,
    deck1: DeckVector,
    *,
    games: int = 100,
    max_decisions: int = 500,
    starting_life: int = 20,
    seed_base: int = 9100,
    record_log: bool = False,
) -> ThroughputResult:
    """Benchmark the safe DecisionFrame agent path.

    This path gives agents only observation+legal-actions, then applies the chosen
    action with revision-guarded validate=False. It is the default target for
    future learned methods even if old trusted baselines still use GameState.
    """

    agent0 = PublicHeuristicAgent()
    agent1 = PublicHeuristicAgent()
    t0 = time.perf_counter()
    decisions = 0
    for i in range(games):
        _, result = play_public_agent_game(
            deck0,
            deck1,
            agent0,
            agent1,
            seed=seed_base + i,
            starting_player=i % 2,
            max_decisions=max_decisions,
            starting_life=starting_life,
            mulligan_policy=POLICY_LAND_BAND,
            record_log=record_log,
        )
        decisions += int(result.decisions)
    seconds = max(1e-12, time.perf_counter() - t0)
    return ThroughputResult(
        games=games,
        decisions=decisions,
        seconds=seconds,
        games_per_second=games / seconds,
        decisions_per_second=decisions / seconds,
        validate_actions=False,
        record_log=record_log,
        max_decisions=max_decisions,
    )
