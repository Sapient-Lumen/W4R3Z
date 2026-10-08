from __future__ import annotations

from dataclasses import asdict, dataclass
from math import log2
from typing import Dict, Iterable, Mapping, Sequence


TOP_THREAT = "threat"
TOP_BLANK = "blank"
PITCH_NONE = "none"
PITCH_ISLAND = "Island"
PITCH_JACE = "Jace"

HOLD_COUNTER = "hold_counter"
JACE_PLUS2 = "jace_plus2"
LEAVE_TOP = "leave_top"
BOTTOM_TOP = "bottom_top"
CAST_THREAT = "cast_threat"
WAIT = "wait"
DECLINE = "decline"
COUNTERSPELL = "counterspell"
FORCE_OF_WILL = "force_of_will"
STOP = "stop"
PRESS_AGAIN = "press_again"


@dataclass(frozen=True)
class ReducedMUCState:
    """A tiny extensive-form state preserving the mechanisms CFR must respect.

    Player 0 is the control/Jace/Force player.  Player 1 is the pressure
    player.  ``top`` is player 1's hidden library top before any Jace action;
    ``force_pitch`` is player 0's private Force resource.  Histories are stored
    as semantic fields so public and private information can be projected
    without accidentally leaking hidden variables.
    """

    top: str
    force_pitch: str
    opening: str | None = None
    jace_order: str | None = None
    pressure_action: str | None = None
    control_response: str | None = None
    pressure_followup: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CFRMetrics:
    iteration: int
    average_value_p0: float
    best_response_value_p0: float
    best_response_value_p1: float
    nash_conv: float
    exploitability: float
    infosets: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class ReducedMUCCFRGame:
    """Reduced hidden-information closure game for tabular CFR calibration.

    The game is intentionally much smaller than MUC-5 but keeps the failure
    modes that made a direct return to learning risky:

    * player 0 can spend tempo on Jace +2 to learn player 1's hidden top card;
    * the leave/bottom choice is public but the card identity is private;
    * Force of Will's pitched card becomes public if Force is cast;
    * waiting can favor the controller through closure only when the top-card
      situation is safe.
    """

    top_probs: Mapping[str, float] = {TOP_THREAT: 0.55, TOP_BLANK: 0.45}
    pitch_probs: Mapping[str, float] = {PITCH_NONE: 0.45, PITCH_ISLAND: 0.35, PITCH_JACE: 0.20}

    def chance_deals(self) -> tuple[tuple[ReducedMUCState, float], ...]:
        deals: list[tuple[ReducedMUCState, float]] = []
        for top, top_prob in self.top_probs.items():
            for pitch, pitch_prob in self.pitch_probs.items():
                deals.append((ReducedMUCState(top=top, force_pitch=pitch), float(top_prob) * float(pitch_prob)))
        total = sum(prob for _, prob in deals)
        if abs(total - 1.0) > 1e-12:
            raise ValueError(f"chance probabilities must sum to 1, got {total}")
        return tuple(deals)

    def current_player(self, state: ReducedMUCState) -> int | None:
        if self.is_terminal(state):
            return None
        if state.opening is None:
            return 0
        if state.opening == JACE_PLUS2 and state.jace_order is None:
            return 0
        if state.pressure_action is None:
            return 1
        if state.pressure_action == WAIT:
            return None
        if state.control_response is None:
            return 0
        if state.control_response.startswith("force_pitch:") and state.pressure_followup is None:
            return 1
        return None

    def legal_actions(self, state: ReducedMUCState) -> tuple[str, ...]:
        player = self.current_player(state)
        if player is None:
            return ()
        if state.opening is None:
            return (HOLD_COUNTER, JACE_PLUS2)
        if state.opening == JACE_PLUS2 and state.jace_order is None:
            return (LEAVE_TOP, BOTTOM_TOP)
        if state.pressure_action is None:
            return (CAST_THREAT, WAIT)
        if state.pressure_action == CAST_THREAT and state.control_response is None:
            actions = [DECLINE]
            if state.opening == HOLD_COUNTER:
                actions.append(COUNTERSPELL)
            if state.force_pitch != PITCH_NONE:
                actions.append(FORCE_OF_WILL)
            return tuple(actions)
        if state.control_response and state.control_response.startswith("force_pitch:") and state.pressure_followup is None:
            return (STOP, PRESS_AGAIN)
        return ()

    def next_state(self, state: ReducedMUCState, action: str) -> ReducedMUCState:
        if action not in self.legal_actions(state):
            raise ValueError(f"illegal action {action!r} for {state}")
        if state.opening is None:
            return ReducedMUCState(top=state.top, force_pitch=state.force_pitch, opening=action)
        if state.opening == JACE_PLUS2 and state.jace_order is None:
            return ReducedMUCState(
                top=state.top,
                force_pitch=state.force_pitch,
                opening=state.opening,
                jace_order=action,
            )
        if state.pressure_action is None:
            return ReducedMUCState(
                top=state.top,
                force_pitch=state.force_pitch,
                opening=state.opening,
                jace_order=state.jace_order,
                pressure_action=action,
            )
        if state.pressure_action == CAST_THREAT and state.control_response is None:
            response = f"force_pitch:{state.force_pitch}" if action == FORCE_OF_WILL else action
            return ReducedMUCState(
                top=state.top,
                force_pitch=state.force_pitch,
                opening=state.opening,
                jace_order=state.jace_order,
                pressure_action=state.pressure_action,
                control_response=response,
            )
        if state.control_response and state.control_response.startswith("force_pitch:") and state.pressure_followup is None:
            return ReducedMUCState(
                top=state.top,
                force_pitch=state.force_pitch,
                opening=state.opening,
                jace_order=state.jace_order,
                pressure_action=state.pressure_action,
                control_response=state.control_response,
                pressure_followup=action,
            )
        raise ValueError(f"terminal state has no next state: {state}")

    def effective_top(self, state: ReducedMUCState) -> str:
        if state.opening == JACE_PLUS2 and state.jace_order == BOTTOM_TOP:
            return TOP_BLANK
        return state.top

    def is_terminal(self, state: ReducedMUCState) -> bool:
        if state.pressure_action == WAIT:
            return True
        if state.control_response in {DECLINE, COUNTERSPELL}:
            return True
        if state.control_response and state.control_response.startswith("force_pitch:"):
            return state.pressure_followup is not None
        return False

    def payoff_p0(self, state: ReducedMUCState) -> float:
        """Zero-sum payoff from player 0's perspective in [-1, 1]."""

        if not self.is_terminal(state):
            raise ValueError("payoff requested before terminal state")
        top = self.effective_top(state)
        if state.pressure_action == WAIT:
            if top == TOP_BLANK:
                return 0.55 if state.opening == JACE_PLUS2 else 0.35
            return -0.15 if state.opening == JACE_PLUS2 else -0.35
        if state.control_response == DECLINE:
            return -0.90 if top == TOP_THREAT else -0.55
        if state.control_response == COUNTERSPELL:
            return 0.45 if top == TOP_BLANK else 0.25
        if state.control_response and state.control_response.startswith("force_pitch:"):
            pitch = state.control_response.split(":", 1)[1]
            safe_top_bonus = 0.08 if top == TOP_BLANK else -0.08
            if state.pressure_followup == STOP:
                base = 0.30 if pitch == PITCH_ISLAND else 0.15
                return base + safe_top_bonus
            if state.pressure_followup == PRESS_AGAIN:
                base = 0.05 if pitch == PITCH_ISLAND else -0.35
                return base + safe_top_bonus
        raise ValueError(f"unrecognized terminal state: {state}")

    def public_events(self, state: ReducedMUCState) -> tuple[str, ...]:
        events: list[str] = []
        if state.opening == HOLD_COUNTER:
            events.append("control:hold_counter")
        elif state.opening == JACE_PLUS2:
            events.append("control:jace_plus2")
            if state.jace_order == LEAVE_TOP:
                events.append("jace:leave_top")
            elif state.jace_order == BOTTOM_TOP:
                events.append("jace:bottom_top")
        if state.pressure_action == CAST_THREAT:
            events.append("pressure:cast_threat")
        elif state.pressure_action == WAIT:
            events.append("pressure:wait")
        if state.control_response == DECLINE:
            events.append("control:decline")
        elif state.control_response == COUNTERSPELL:
            events.append("control:counterspell")
        elif state.control_response and state.control_response.startswith("force_pitch:"):
            events.append(f"control:force_pitch:{state.control_response.split(':', 1)[1]}")
        if state.pressure_followup:
            events.append(f"pressure:{state.pressure_followup}")
        return tuple(events)

    def information_state_key(self, state: ReducedMUCState, player: int) -> str:
        public = "/".join(self.public_events(state)) or "root"
        if player == 0:
            private = [f"force={state.force_pitch}"]
            if state.opening == JACE_PLUS2:
                private.append(f"known_top={state.top}")
                if state.jace_order == BOTTOM_TOP:
                    private.append("known_top_cleared_by_bottom")
                elif state.jace_order == LEAVE_TOP:
                    private.append(f"known_top_retained={state.top}")
            return f"P0|public={public}|private={'/'.join(private)}"
        if player == 1:
            # The pressure player sees the public order choice and any Force
            # pitch identity, but not the Jace-viewed card or player 0's hand.
            return f"P1|public={public}|private=pressure_hand_only"
        raise ValueError("player must be 0 or 1")

    def infoset_summary(self, key: str) -> dict[str, object]:
        player = 0 if key.startswith("P0|") else 1
        return {
            "player": player,
            "infoset": key,
            "reveals_jace_top_to_pressure": player == 1 and "known_top=" in key,
            "reveals_force_pitch_publicly": "force_pitch:" in key,
            "contains_jace_private_top": player == 0 and "known_top=" in key,
        }


class TabularCFRSolver:
    """Deterministic vanilla CFR for the reduced MUC calibration game."""

    def __init__(self, game: ReducedMUCCFRGame | None = None) -> None:
        self.game = game or ReducedMUCCFRGame()
        self.regret_sums: Dict[str, Dict[str, float]] = {}
        self.strategy_sums: Dict[str, Dict[str, float]] = {}
        self.actions_by_infoset: Dict[str, tuple[str, ...]] = {}
        self.iterations = 0

    def _ensure_infoset(self, state: ReducedMUCState) -> tuple[str, int, tuple[str, ...]]:
        player = self.game.current_player(state)
        if player is None:
            raise ValueError("terminal state has no infoset")
        actions = self.game.legal_actions(state)
        key = self.game.information_state_key(state, player)
        if key in self.actions_by_infoset and self.actions_by_infoset[key] != actions:
            raise ValueError(
                f"imperfect-recall or leaking abstraction: infoset {key} saw actions "
                f"{self.actions_by_infoset[key]} and {actions}"
            )
        self.actions_by_infoset.setdefault(key, actions)
        self.regret_sums.setdefault(key, {action: 0.0 for action in actions})
        self.strategy_sums.setdefault(key, {action: 0.0 for action in actions})
        return key, player, actions

    def current_strategy(self, key: str, actions: Sequence[str] | None = None) -> dict[str, float]:
        if actions is None:
            actions = self.actions_by_infoset[key]
        regrets = self.regret_sums.setdefault(key, {action: 0.0 for action in actions})
        positive = {action: max(0.0, float(regrets.get(action, 0.0))) for action in actions}
        total = sum(positive.values())
        if total <= 0.0:
            return {action: 1.0 / len(actions) for action in actions}
        return {action: positive[action] / total for action in actions}

    def average_strategy(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        for key, actions in self.actions_by_infoset.items():
            sums = self.strategy_sums.get(key, {})
            total = sum(float(sums.get(action, 0.0)) for action in actions)
            if total <= 0.0:
                out[key] = self.current_strategy(key, actions)
            else:
                out[key] = {action: float(sums.get(action, 0.0)) / total for action in actions}
        return out

    def train(self, iterations: int, *, checkpoints: Iterable[int] = ()) -> list[CFRMetrics]:
        checkpoint_set = {int(value) for value in checkpoints}
        metrics: list[CFRMetrics] = []
        for _ in range(int(iterations)):
            for updating_player in (0, 1):
                for deal, chance_prob in self.game.chance_deals():
                    self._cfr(deal, updating_player, reach0=1.0, reach1=1.0, chance_reach=chance_prob)
            self.iterations += 1
            self._accumulate_average_strategy()
            if self.iterations in checkpoint_set:
                metrics.append(self.metrics(iteration=self.iterations))
        return metrics

    def _cfr(
        self,
        state: ReducedMUCState,
        updating_player: int,
        *,
        reach0: float,
        reach1: float,
        chance_reach: float,
    ) -> float:
        if self.game.is_terminal(state):
            return self.game.payoff_p0(state)
        key, player, actions = self._ensure_infoset(state)
        strategy = self.current_strategy(key, actions)
        action_values: dict[str, float] = {}
        node_value = 0.0
        for action in actions:
            prob = strategy[action]
            child = self.game.next_state(state, action)
            if player == 0:
                value = self._cfr(
                    child,
                    updating_player,
                    reach0=reach0 * prob,
                    reach1=reach1,
                    chance_reach=chance_reach,
                )
            else:
                value = self._cfr(
                    child,
                    updating_player,
                    reach0=reach0,
                    reach1=reach1 * prob,
                    chance_reach=chance_reach,
                )
            action_values[action] = value
            node_value += prob * value

        if player == updating_player:
            if player == 0:
                weight = reach1 * chance_reach
                for action in actions:
                    self.regret_sums[key][action] += weight * (action_values[action] - node_value)
            else:
                weight = reach0 * chance_reach
                node_value_p1 = -node_value
                for action in actions:
                    self.regret_sums[key][action] += weight * ((-action_values[action]) - node_value_p1)
        return node_value

    def _accumulate_average_strategy(self) -> None:
        visited: set[str] = set()
        for deal, _chance_prob in self.game.chance_deals():
            self._accumulate_from_state(deal, reach0=1.0, reach1=1.0, visited=visited)

    def _accumulate_from_state(self, state: ReducedMUCState, *, reach0: float, reach1: float, visited: set[str]) -> None:
        if self.game.is_terminal(state):
            return
        key, player, actions = self._ensure_infoset(state)
        strategy = self.current_strategy(key, actions)
        if key not in visited:
            visited.add(key)
            weight = reach0 if player == 0 else reach1
            for action in actions:
                self.strategy_sums[key][action] += weight * strategy[action]
        for action in actions:
            prob = strategy[action]
            child = self.game.next_state(state, action)
            if player == 0:
                self._accumulate_from_state(child, reach0=reach0 * prob, reach1=reach1, visited=visited)
            else:
                self._accumulate_from_state(child, reach0=reach0, reach1=reach1 * prob, visited=visited)

    def policy_value_p0(self, strategy_profile: Mapping[str, Mapping[str, float]] | None = None) -> float:
        profile = strategy_profile or self.average_strategy()
        return sum(
            chance_prob * self._policy_value_from_state(deal, profile)
            for deal, chance_prob in self.game.chance_deals()
        )

    def _policy_value_from_state(self, state: ReducedMUCState, profile: Mapping[str, Mapping[str, float]]) -> float:
        if self.game.is_terminal(state):
            return self.game.payoff_p0(state)
        key, _player, actions = self._ensure_infoset(state)
        strategy = _normalized_strategy(profile.get(key), actions)
        return sum(
            strategy[action] * self._policy_value_from_state(self.game.next_state(state, action), profile)
            for action in actions
        )

    def best_response_value(self, br_player: int, strategy_profile: Mapping[str, Mapping[str, float]] | None = None) -> float:
        """Return an imperfect-information best response value.

        A tempting shortcut is to maximize independently at every concrete
        state.  That leaks hidden cards inside an information set.  This method
        first collects all states in each responding-player information set
        with chance/opponent reach weights, then chooses one shared action per
        information set and evaluates the resulting policy.
        """

        profile = strategy_profile or self.average_strategy()
        states_by_infoset: dict[str, list[tuple[ReducedMUCState, float]]] = {}
        for deal, chance_prob in self.game.chance_deals():
            self._collect_br_infosets(deal, br_player, profile, chance_prob, states_by_infoset)

        chosen_actions: dict[str, str] = {}

        def state_value(state: ReducedMUCState) -> float:
            if self.game.is_terminal(state):
                payoff = self.game.payoff_p0(state)
                return payoff if br_player == 0 else -payoff
            key, player, actions = self._ensure_infoset(state)
            if player == br_player:
                if key not in chosen_actions:
                    action_values: dict[str, float] = {}
                    for action in actions:
                        total = 0.0
                        for hidden_state, weight in states_by_infoset[key]:
                            total += weight * state_value(self.game.next_state(hidden_state, action))
                        action_values[action] = total
                    chosen_actions[key] = max(actions, key=lambda action: action_values[action])
                return state_value(self.game.next_state(state, chosen_actions[key]))
            strategy = _normalized_strategy(profile.get(key), actions)
            return sum(strategy[action] * state_value(self.game.next_state(state, action)) for action in actions)

        return sum(chance_prob * state_value(deal) for deal, chance_prob in self.game.chance_deals())

    def _collect_br_infosets(
        self,
        state: ReducedMUCState,
        br_player: int,
        profile: Mapping[str, Mapping[str, float]],
        weight: float,
        out: dict[str, list[tuple[ReducedMUCState, float]]],
    ) -> None:
        if self.game.is_terminal(state):
            return
        key, player, actions = self._ensure_infoset(state)
        if player == br_player:
            out.setdefault(key, []).append((state, weight))
            for action in actions:
                self._collect_br_infosets(self.game.next_state(state, action), br_player, profile, weight, out)
        else:
            strategy = _normalized_strategy(profile.get(key), actions)
            for action in actions:
                self._collect_br_infosets(
                    self.game.next_state(state, action),
                    br_player,
                    profile,
                    weight * strategy[action],
                    out,
                )

    def metrics(self, *, iteration: int | None = None) -> CFRMetrics:
        profile = self.average_strategy()
        value_p0 = self.policy_value_p0(profile)
        br0 = self.best_response_value(0, profile)
        br1 = self.best_response_value(1, profile)
        nash_conv = (br0 - value_p0) + (br1 + value_p0)
        return CFRMetrics(
            iteration=self.iterations if iteration is None else int(iteration),
            average_value_p0=value_p0,
            best_response_value_p0=br0,
            best_response_value_p1=br1,
            nash_conv=nash_conv,
            exploitability=nash_conv / 2.0,
            infosets=len(self.actions_by_infoset),
        )

    def strategy_rows(self) -> list[dict[str, object]]:
        profile = self.average_strategy()
        rows: list[dict[str, object]] = []
        for key in sorted(profile):
            actions = self.actions_by_infoset[key]
            probs = profile[key]
            entropy = -sum(prob * log2(prob) for prob in probs.values() if prob > 0.0)
            best_action = max(actions, key=lambda action: probs.get(action, 0.0))
            summary = self.game.infoset_summary(key)
            for action in actions:
                rows.append(
                    {
                        **summary,
                        "action": action,
                        "probability": probs[action],
                        "best_action": best_action,
                        "action_count": len(actions),
                        "entropy_bits": entropy,
                    }
                )
        return rows


def _normalized_strategy(raw: Mapping[str, float] | None, actions: Sequence[str]) -> dict[str, float]:
    if raw is None:
        return {action: 1.0 / len(actions) for action in actions}
    clipped = {action: max(0.0, float(raw.get(action, 0.0))) for action in actions}
    total = sum(clipped.values())
    if total <= 0.0:
        return {action: 1.0 / len(actions) for action in actions}
    return {action: clipped[action] / total for action in actions}
