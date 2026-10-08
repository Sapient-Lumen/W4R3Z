from __future__ import annotations

from dataclasses import dataclass
import hashlib
from random import Random
from typing import Dict, Iterable, List, Protocol, Tuple

from .action_schema import Action, PASS
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD, CARD_ORDER, OVERLORD_POWER, STARTING_LIFE
from .engine import GameState, apply_action, legal_actions, start_game
from .mulligan import MulliganAgent, MulliganPolicy
from .deckspace import DeckVector
from .decision import PublicDecisionAgent, build_decision_frame, apply_decision_index
from .agent_lifecycle import EpisodeContext, EpisodeResult, end_episode, require_distinct_seat_objects, reset_episode


class Agent(Protocol):
    name: str

    def choose_action(self, state: GameState, rng: Random) -> Action: ...


@dataclass
class RandomAgent:
    name: str = "random"

    def choose_action(self, state: GameState, rng: Random) -> Action:
        return rng.choice(legal_actions(state))


@dataclass
class HeuristicAgent:
    """A deliberately small public-info heuristic pilot.

    This is not meant to encode MUC theory. It exists so arenas produce less nonsense
    than RandomAgent and so future learned pilots have a named baseline to beat.
    """

    name: str = "heuristic_rev0004_lifeaware"

    def choose_action(self, state: GameState, rng: Random) -> Action:
        actions = legal_actions(state)
        if not actions:
            raise ValueError("no legal actions")
        pidx = state.current_player()
        obs = state.observation(pidx)
        scored = [(self.score_action(obs, action), rng.random(), action) for action in actions]
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]

    def score_action(self, obs: Dict[str, object], action: Action) -> float:
        kind = action.kind
        frame = str(obs.get("frame", "MAIN"))
        if kind == "PASS":
            if frame == "RESPONSE":
                return -1.0
            if frame == "BLOCK":
                return 0.0
            return 0.2
        if kind == "PLAY_ISLAND":
            return 9.0
        if kind == "CAST":
            card = str(action.params.get("card"))
            if frame == "RESPONSE":
                return self._score_counter_action(obs, action)
            if card == CARD_JACE:
                opp = obs.get("public_opponent", {}) or {}
                return 7.0 + 0.25 * float(opp.get("islands_tapped", 0) or 0)
            if card == CARD_OVERLORD:
                mode = str(action.params.get("mode", "full_cost"))
                opp = obs.get("public_opponent", {}) or {}
                base = 6.2 if mode == "impending" else 6.0
                if opp.get("jace_loyalty") is not None and mode == "full_cost":
                    base += 1.5
                return base
            return 0.0
        if kind == "ACTIVATE_JACE":
            return self._score_jace_action(obs, action)
        if kind == "ATTACK":
            to_player = int(action.params.get("to_player", 0))
            to_jace = int(action.params.get("to_jace", 0))
            opp_public = obs.get("public_opponent", {}) or {}
            starting_life = max(1.0, float(obs.get("starting_life", STARTING_LIFE) or STARTING_LIFE))
            opp_life = max(0.0, float(opp_public.get("life", starting_life) or starting_life))
            # Face damage is intrinsically more urgent in 20-life games and becomes
            # increasingly urgent as the opponent approaches zero. Jace damage keeps
            # a high fixed priority because Jace can dominate long games.
            face_pressure = 2.0 + (1.0 if starting_life <= 20 else 0.0) + 4.0 * max(0.0, 1.0 - opp_life / starting_life)
            return face_pressure * to_player + 5.5 * to_jace
        if kind == "BLOCK":
            self_public = obs.get("public_self", {}) or {}
            starting_life = max(1.0, float(obs.get("starting_life", STARTING_LIFE) or STARTING_LIFE))
            life = max(0.0, float(self_public.get("life", starting_life) or starting_life))
            life_danger = max(0.0, 1.0 - life / starting_life)
            return (4.0 + 4.0 * life_danger) * int(action.params.get("block_player_attackers", 0)) + 5.0 * int(action.params.get("block_jace_attackers", 0))
        if kind == "CHOOSE_FOR_EFFECT":
            return self._score_choice(obs, action)
        return 0.0

    def _score_counter_action(self, obs: Dict[str, object], action: Action) -> float:
        target_card = str(action.params.get("target_card", ""))
        card = str(action.params.get("card", ""))
        target_value = {
            CARD_JACE: 10.0,
            CARD_OVERLORD: 8.5,
            CARD_COUNTERSPELL: 6.5,
            CARD_FORCE: 6.5,
        }.get(target_card, 3.0)
        score = target_value
        if card == CARD_COUNTERSPELL:
            score += 0.8
        if card == CARD_FORCE:
            payment = action.params.get("payment")
            if payment == "mana":
                score -= 1.2
            else:
                pitch = str(action.params.get("pitch_card", ""))
                pitch_penalty = {
                    CARD_COUNTERSPELL: 2.0,
                    CARD_FORCE: 2.4,
                    CARD_JACE: 3.0,
                    CARD_OVERLORD: 2.7,
                }.get(pitch, 2.0)
                self_public = obs.get("public_self", {}) or {}
                life = float(self_public.get("life", STARTING_LIFE) or STARTING_LIFE)
                starting_life = float(obs.get("starting_life", STARTING_LIFE) or STARTING_LIFE)
                life_fraction = life / max(1.0, starting_life)
                # One Force life matters much less at 40 than 20, but paying down to 0 is still fatal.
                score -= pitch_penalty
                score -= 0.65 / max(0.05, life_fraction)
                if life <= 1:
                    score -= 100.0
                elif life <= OVERLORD_POWER:
                    score -= 2.0
        return score

    def _score_jace_action(self, obs: Dict[str, object], action: Action) -> float:
        mode = str(action.params.get("mode", ""))
        self_public = obs.get("public_self", {}) or {}
        opp_public = obs.get("public_opponent", {}) or {}
        if mode == "ultimate":
            return 100.0 if action.params.get("target_player") == "opponent" else -100.0
        if mode == "minus1":
            if action.params.get("target_player") == "opponent":
                return 8.0 + 2.0 * float(opp_public.get("overlord_ready", 0) or 0)
            return 0.5
        if mode == "zero":
            own_hand = sum((obs.get("own_hand", {}) or {}).values())
            return 5.0 if own_hand <= 6 else 2.0
        if mode == "plus2":
            return 4.5 if action.params.get("target_player") == "opponent" else 2.5
        return 0.0

    def _score_choice(self, obs: Dict[str, object], action: Action) -> float:
        effect = str(action.params.get("effect", ""))
        if effect in {"discard", "cleanup_discard"}:
            discard = str(action.params.get("discard", ""))
            # Prefer discarding redundant mana, then redundant expensive cards, then interaction last.
            return {
                CARD_ISLAND: 5.0,
                CARD_OVERLORD: 3.8,
                CARD_JACE: 3.0,
                CARD_FORCE: 2.0,
                CARD_COUNTERSPELL: 1.0,
            }.get(discard, 0.0)
        if effect == "jace_plus2":
            pending = obs.get("pending_choice_data", {}) or {}
            target = pending.get("target_player")
            player = obs.get("player")
            seen = str(pending.get("seen_top_card", ""))
            put = str(action.params.get("put", "leave"))
            good_for_target = seen in {CARD_JACE, CARD_OVERLORD, CARD_FORCE, CARD_COUNTERSPELL}
            target_self = int(target) == int(player) if target is not None and player is not None else False
            if target_self:
                return 4.0 if (put == "leave" and good_for_target) or (put == "bottom" and seen == CARD_ISLAND) else 1.0
            return 4.0 if (put == "bottom" and good_for_target) or (put == "leave" and seen == CARD_ISLAND) else 1.0
        if effect == "jace_brainstorm_putback":
            first = str(action.params.get("first_draw", ""))
            second = str(action.params.get("second_draw", ""))
            # Higher score means more willing to put these two back; Islands are usually safest to put back here.
            putback_value = {CARD_ISLAND: 4.0, CARD_OVERLORD: 2.5, CARD_JACE: 2.0, CARD_FORCE: 1.0, CARD_COUNTERSPELL: 0.5}
            return putback_value.get(first, 0.0) + putback_value.get(second, 0.0)
        if effect == "jace_legend":
            return 4.0 if action.params.get("keep") == "new" else 3.0
        return 0.0


@dataclass
class MatchResult:
    winner: int | None
    loss_reason: str
    decisions: int
    log_events: int


def play_agent_game(
    deck0: DeckVector,
    deck1: DeckVector,
    agent0: Agent,
    agent1: Agent,
    seed: int = 1,
    starting_player: int = 0,
    max_decisions: int = 500,
    starting_life: int = STARTING_LIFE,
    mulligan_policy: str | MulliganPolicy | None = None,
    mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
    validate_actions: bool = False,
    record_log: bool = True,
) -> Tuple[GameState, MatchResult]:
    rng = Random(seed)
    state = start_game(deck0, deck1, seed=seed, starting_player=starting_player, starting_life=starting_life, mulligan_policy=mulligan_policy, mulligan_agents=mulligan_agents, record_log=record_log)
    agents = [agent0, agent1]
    decisions = 0
    for step in range(1, max_decisions + 1):
        if state.winner is not None:
            break
        actor = state.current_player()
        action = agents[actor].choose_action(state, rng)
        apply_action(state, action, rng, validate=validate_actions)
        decisions = int(step)
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    return state, MatchResult(state.winner, state.loss_reason, decisions, len(state.log))


def play_public_agent_game(
    deck0: DeckVector,
    deck1: DeckVector,
    agent0: PublicDecisionAgent,
    agent1: PublicDecisionAgent,
    seed: int = 1,
    starting_player: int = 0,
    max_decisions: int = 500,
    starting_life: int = STARTING_LIFE,
    mulligan_policy: str | MulliganPolicy | None = None,
    mulligan_policies: Tuple[str | MulliganPolicy | None, str | MulliganPolicy | None] | None = None,
    mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
    record_log: bool = True,
    transition_seed: int | None = None,
    agent_seed: int | None = None,
    episode_id: str | None = None,
) -> Tuple[GameState, MatchResult]:
    """Play a game through hidden-information-correct DecisionFrames.

    This is the preferred path for future learned/search/evolutionary policies.
    Agents receive observation + legal action list, not the omniscient GameState.
    The chosen action is applied with the fast no-recompute path guarded by the
    frame revision number.

    rev0026 splits policy tie-break randomness from state-transition randomness.
    This prevents an agent from accidentally affecting shuffle outcomes merely
    by consuming more random numbers while ranking legal actions.  The default
    seeds match the replay-trace convention: transition_seed=seed and
    agent_seed=seed+1000003.
    """

    require_distinct_seat_objects(agent0, agent1)
    transition_rng = Random(seed if transition_seed is None else int(transition_seed))
    agent_rng = Random(seed + 1000003 if agent_seed is None else int(agent_seed))
    opaque_id = episode_id or "muc5-" + hashlib.sha256(
        f"{seed}|{starting_player}|{starting_life}|{max_decisions}".encode("utf-8")
    ).hexdigest()[:20]
    contexts = (
        EpisodeContext(opaque_id, 0, int(starting_player), int(starting_life)),
        EpisodeContext(opaque_id, 1, int(starting_player), int(starting_life)),
    )
    reset_episode(agent0, contexts[0])
    reset_episode(agent1, contexts[1])
    if mulligan_agents is not None:
        m0, m1 = mulligan_agents
        if m0 is not None and m0 is m1 and not isinstance(m0, (str, MulliganPolicy)):
            raise ValueError(
                "mulligan agents must be distinct objects across seats; sharing one instance can merge private memories"
            )
        if m0 is not None and not isinstance(m0, (str, MulliganPolicy)):
            reset_episode(m0, contexts[0])
        if m1 is not None and not isinstance(m1, (str, MulliganPolicy)):
            reset_episode(m1, contexts[1])

    state = start_game(
        deck0,
        deck1,
        seed=seed,
        starting_player=starting_player,
        starting_life=starting_life,
        mulligan_policy=mulligan_policy,
        mulligan_policies=mulligan_policies,
        mulligan_agents=mulligan_agents,
        record_log=record_log,
    )
    agents = [agent0, agent1]
    decisions = 0
    for step in range(1, max_decisions + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        apply_decision_index(state, frame, action_index, transition_rng)
        decisions = int(step)
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    result = MatchResult(state.winner, state.loss_reason, decisions, len(state.log))
    for player, agent in enumerate(agents):
        score = 0.5 if result.winner is None else (1.0 if result.winner == player else 0.0)
        end_episode(
            agent,
            EpisodeResult(
                episode_id=opaque_id,
                player=player,
                score=score,
                winner=result.winner,
                loss_reason=result.loss_reason,
                decisions=result.decisions,
            ),
        )
    if mulligan_agents is not None:
        for player, mulligan_agent in enumerate(mulligan_agents):
            if mulligan_agent is not None and not isinstance(mulligan_agent, (str, MulliganPolicy)):
                score = 0.5 if result.winner is None else (1.0 if result.winner == player else 0.0)
                end_episode(
                    mulligan_agent,
                    EpisodeResult(
                        episode_id=opaque_id,
                        player=player,
                        score=score,
                        winner=result.winner,
                        loss_reason=result.loss_reason,
                        decisions=result.decisions,
                    ),
                )
    return state, result


class CounterHappyAgent:
    """Rev0007 style baseline: over-values fighting on the stack.

    This is intentionally not expert MUC play. It exists as a distinct sparring
    partner for the external gametable and later payoff-table diversity checks.
    """

    name = "counter_happy_rev0007"

    def __init__(self) -> None:
        self.base = HeuristicAgent()

    def choose_action(self, state: GameState, rng: Random) -> Action:
        actions = legal_actions(state)
        if not actions:
            raise ValueError("no legal actions")
        pidx = state.current_player()
        obs = state.observation(pidx)
        scored = [(self.score_action(obs, action), rng.random(), action) for action in actions]
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]

    def score_action(self, obs: Dict[str, object], action: Action) -> float:
        score = self.base.score_action(obs, action)
        if str(obs.get("frame")) == "RESPONSE":
            if action.kind == "CAST":
                target_card = str(action.params.get("target_card", ""))
                score += 5.0
                if target_card in {CARD_JACE, CARD_OVERLORD}:
                    score += 2.0
                if action.params.get("card") == CARD_COUNTERSPELL:
                    score += 1.0
            elif action.kind == "PASS":
                score -= 3.0
        return score


class ThreatRushAgent:
    """Rev0007 style baseline: pushes Jace/Overlord deployment and attacks.

    It still uses the balanced heuristic for choices and emergency countering, but
    its main-phase bias is closer to a tap-out pressure pilot.
    """

    name = "threat_rush_rev0007"

    def __init__(self) -> None:
        self.base = HeuristicAgent()

    def choose_action(self, state: GameState, rng: Random) -> Action:
        actions = legal_actions(state)
        if not actions:
            raise ValueError("no legal actions")
        pidx = state.current_player()
        obs = state.observation(pidx)
        scored = [(self.score_action(obs, action), rng.random(), action) for action in actions]
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]

    def score_action(self, obs: Dict[str, object], action: Action) -> float:
        score = self.base.score_action(obs, action)
        frame = str(obs.get("frame", "MAIN"))
        if frame == "MAIN" and action.kind == "CAST":
            card = str(action.params.get("card", ""))
            if card == CARD_OVERLORD:
                score += 4.0
            elif card == CARD_JACE:
                score += 2.5
        if action.kind == "ATTACK":
            score += 3.0
        if frame == "RESPONSE" and action.kind == "CAST":
            target_card = str(action.params.get("target_card", ""))
            if target_card not in {CARD_JACE, CARD_OVERLORD}:
                score -= 4.0
        if frame == "MAIN" and action.kind == "PASS":
            score -= 1.5
        return score


def make_agent(name: str) -> Agent:
    """Factory for named rev0007 sparring agents."""
    normalized = name.strip().lower().replace("-", "_")
    if normalized in {"random", "random_rev0003"}:
        return RandomAgent()
    if normalized in {"heuristic", "balanced", "heuristic_rev0004_lifeaware", "heuristic_rev0007"}:
        return HeuristicAgent()
    if normalized in {"counter_happy", "counterhappy", "counter_happy_rev0007"}:
        return CounterHappyAgent()
    if normalized in {"threat_rush", "threatrush", "threat_rush_rev0007"}:
        return ThreatRushAgent()
    raise ValueError("unknown agent name {!r}; expected random, heuristic, counter_happy, or threat_rush".format(name))
