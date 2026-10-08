from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence

from .agents import MatchResult, play_public_agent_game
from .cards import STARTING_LIFE_OPTIONS
from .payoff import StrategyBundle
from .decision import PublicDecisionAgent
from .public_agents import make_public_agent
from .mulligan_ranker import make_mulligan_agent
from .reward_guard import reward_packet_from_state

REWARD_CONVENTION = "draw_half_reporting_terminal_only_training"
PUBLIC_INTERFACE = "public_decision_frame"


def score_for_player(result: MatchResult, player: int) -> float:
    if result.winner is None:
        return 0.5
    return 1.0 if result.winner == player else 0.0


def play_public_strategy_pair_row(
    left: StrategyBundle,
    right: StrategyBundle,
    *,
    simulator_revision: str,
    seed: int,
    starting_player: int,
    starting_life: int,
    max_decisions: int = 500,
    agent0: PublicDecisionAgent | None = None,
    agent1: PublicDecisionAgent | None = None,
    mulligan_agent0: object | None = None,
    mulligan_agent1: object | None = None,
) -> Dict[str, object]:
    """Play one public DecisionFrame strategy-bundle game with full provenance.

    rev0022 lets callers pass prebuilt public agents. That matters because some
    policy objects load model weights from JSON; bulk payoff/race loops should
    not reload the same frozen model once per game.  Agents are still public-safe
    and receive only DecisionFrames during gameplay.
    """

    transition_seed = int(seed)
    agent_seed = int(seed) + 1000003
    state, result = play_public_agent_game(
        left.deck,
        right.deck,
        agent0 if agent0 is not None else make_public_agent(left.agent_name),
        agent1 if agent1 is not None else make_public_agent(right.agent_name),
        seed=seed,
        transition_seed=transition_seed,
        agent_seed=agent_seed,
        starting_player=starting_player,
        starting_life=starting_life,
        max_decisions=max_decisions,
        mulligan_agents=(
            mulligan_agent0 if mulligan_agent0 is not None else make_mulligan_agent(left.mulligan_policy),
            mulligan_agent1 if mulligan_agent1 is not None else make_mulligan_agent(right.mulligan_policy),
        ),
        record_log=False,
    )
    p0_packet = reward_packet_from_state(state, 0)
    p1_packet = reward_packet_from_state(state, 1)
    return {
        "simulator_revision": simulator_revision,
        "strategy0": left.strategy_id,
        "strategy1": right.strategy_id,
        "deck0": left.deck_name,
        "deck1": right.deck_name,
        "agent0": left.agent_name,
        "agent1": right.agent_name,
        "mulligan0": str(left.mulligan_policy),
        "mulligan1": str(right.mulligan_policy),
        "starting_life": int(starting_life),
        "starting_player": int(starting_player),
        "seed": int(seed),
        "transition_seed": int(transition_seed),
        "agent_seed": int(agent_seed),
        "winner": "None" if result.winner is None else str(result.winner),
        "p0_score": score_for_player(result, 0),
        "p1_score": score_for_player(result, 1),
        "p0_terminal_win": 1.0 if result.winner == 0 else 0.0,
        "p1_terminal_win": 1.0 if result.winner == 1 else 0.0,
        "is_nonterminal_draw": result.winner is None,
        "is_truncation": result.loss_reason == "max_decisions_reached",
        "loss_reason": result.loss_reason,
        "decisions": result.decisions,
        "log_events": result.log_events,
        "turn_number": state.turn_number,
        "reward_convention": REWARD_CONVENTION,
        "interface": PUBLIC_INTERFACE,
        "p0_terminal_only_score": "None" if p0_packet.terminal_only_score is None else p0_packet.terminal_only_score,
        "p1_terminal_only_score": "None" if p1_packet.terminal_only_score is None else p1_packet.terminal_only_score,
    }


def build_public_payoff_rows(
    strategies: Sequence[StrategyBundle],
    *,
    simulator_revision: str,
    life_totals: Sequence[int] = STARTING_LIFE_OPTIONS,
    reps: int = 1,
    base_seed: int = 13000,
    max_decisions: int = 500,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    # Cache expensive immutable model weights per seat, never one mutable policy
    # object across both players.  ``play_public_agent_game`` resets each wrapper
    # at episode start, so recurrent policies may be reused across games safely.
    agent_cache: Dict[tuple[str, int], PublicDecisionAgent] = {}
    mulligan_cache: Dict[tuple[str, int], object] = {}

    def cached_agent(name: str, seat: int) -> PublicDecisionAgent:
        key = (name, int(seat))
        if key not in agent_cache:
            agent_cache[key] = make_public_agent(name)
        return agent_cache[key]

    def cached_mulligan(policy: object, seat: int) -> object:
        key = (str(policy), int(seat))
        if key not in mulligan_cache:
            mulligan_cache[key] = make_mulligan_agent(policy)
        return mulligan_cache[key]

    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                for starting_player in (0, 1):
                    for rep in range(reps):
                        row = play_public_strategy_pair_row(
                            left,
                            right,
                            simulator_revision=simulator_revision,
                            seed=base_seed + k,
                            starting_player=starting_player,
                            starting_life=int(life),
                            max_decisions=max_decisions,
                            agent0=cached_agent(left.agent_name, 0),
                            agent1=cached_agent(right.agent_name, 1),
                            mulligan_agent0=cached_mulligan(left.mulligan_policy, 0),
                            mulligan_agent1=cached_mulligan(right.mulligan_policy, 1),
                        )
                        row["rep"] = rep
                        row["pair_index"] = f"{i}:{j}"
                        rows.append(row)
                        k += 1
    return rows
