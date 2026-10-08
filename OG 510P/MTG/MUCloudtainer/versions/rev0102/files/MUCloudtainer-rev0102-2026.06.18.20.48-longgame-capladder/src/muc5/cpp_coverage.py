from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from random import Random
from typing import Iterable

from .cpp_transition import is_supported_transition
from .decision import apply_decision_index, build_decision_frame
from .deckspace import DeckVector
from .engine import legal_actions, start_game
from .public_agents import make_public_agent


@dataclass(frozen=True)
class CppTransitionCoverageRow:
    frame: str
    pending_choice_kind: str
    action_kind: str
    supported: bool
    count: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CppTransitionCoverageSummary:
    games: int
    decisions: int
    chosen_supported: int
    chosen_unsupported: int
    chosen_support_rate: float
    legal_actions_seen: int
    legal_actions_supported: int
    legal_action_support_rate: float
    unsupported_chosen_examples: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def collect_transition_coverage(
    decks: Iterable[DeckVector],
    *,
    games: int = 32,
    max_decisions: int = 400,
    seed: int = 18018,
) -> tuple[CppTransitionCoverageSummary, list[CppTransitionCoverageRow]]:
    """Measure how much of live public-agent play the C++ transition bridge covers.

    This is intentionally descriptive. Python remains authoritative, and C++
    coverage is allowed to be partial. The purpose is to keep porting priorities
    grounded in actual decision-frame traffic rather than gut feel.
    """

    deck_list = list(decks)
    if not deck_list:
        raise ValueError("at least one deck is required")
    agents = [make_public_agent("heuristic"), make_public_agent("counter_happy"), make_public_agent("threat_rush"), make_public_agent("patient")]
    rng = Random(seed)
    chosen_counter: Counter[tuple[str, str, str, bool]] = Counter()
    all_legal_counter: Counter[tuple[str, str, str, bool]] = Counter()
    unsupported_examples: list[str] = []
    decisions = 0
    chosen_supported = 0
    chosen_unsupported = 0
    legal_seen = 0
    legal_supported = 0

    for game_index in range(games):
        d0 = deck_list[game_index % len(deck_list)]
        d1 = deck_list[(game_index * 3 + 1) % len(deck_list)]
        state = start_game(
            d0,
            d1,
            seed=seed + game_index,
            starting_player=game_index % 2,
            starting_life=20 if game_index % 2 == 0 else 40,
            mulligan_policies=("land_band", "land_band_business"),
            record_log=False,
        )
        a0 = agents[game_index % len(agents)]
        a1 = agents[(game_index + 1) % len(agents)]
        for _ in range(max_decisions):
            if state.winner is not None:
                break
            frame = build_decision_frame(state)
            if frame.action_count <= 0:
                break
            pending_kind = state.pending_choice.kind if state.pending_choice is not None else "none"
            for action in legal_actions(state):
                supp = is_supported_transition(state, action)
                all_legal_counter[(state.frame, pending_kind, action.kind, supp)] += 1
                legal_seen += 1
                legal_supported += int(supp)
            agent = [a0, a1][frame.player]
            idx = agent.choose_action_index(frame, rng)
            action = frame.legal_actions[idx]
            supp = is_supported_transition(state, action)
            chosen_counter[(state.frame, pending_kind, action.kind, supp)] += 1
            decisions += 1
            chosen_supported += int(supp)
            chosen_unsupported += int(not supp)
            if not supp and len(unsupported_examples) < 20:
                unsupported_examples.append(f"frame={state.frame} pending={pending_kind} action={action.compact()}")
            apply_decision_index(state, frame, idx, rng)

    row_counter: Counter[tuple[str, str, str, bool]] = Counter()
    row_counter.update(chosen_counter)
    rows = [
        CppTransitionCoverageRow(frame=k[0], pending_choice_kind=k[1], action_kind=k[2], supported=k[3], count=v)
        for k, v in sorted(row_counter.items())
    ]
    summary = CppTransitionCoverageSummary(
        games=games,
        decisions=decisions,
        chosen_supported=chosen_supported,
        chosen_unsupported=chosen_unsupported,
        chosen_support_rate=chosen_supported / decisions if decisions else 0.0,
        legal_actions_seen=legal_seen,
        legal_actions_supported=legal_supported,
        legal_action_support_rate=legal_supported / legal_seen if legal_seen else 0.0,
        unsupported_chosen_examples=tuple(unsupported_examples),
    )
    return summary, rows
