from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from random import Random
from typing import Counter as CounterType, Dict, List, Protocol, Sequence, Tuple, runtime_checkable

from .action_schema import Action
from .cards import (
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
    CARD_ORDER,
    OPENING_HAND_SIZE,
)

POLICY_KEEP_ALWAYS = "keep_always"
POLICY_LAND_BAND = "land_band"
POLICY_LAND_BAND_BUSINESS = "land_band_business"
MULLIGAN_POLICY_NAMES: Tuple[str, str, str] = (
    POLICY_KEEP_ALWAYS,
    POLICY_LAND_BAND,
    POLICY_LAND_BAND_BUSINESS,
)

MULLIGAN_KEEP = Action("MULLIGAN_KEEP")
MULLIGAN_TAKE = Action("MULLIGAN_TAKE")
MULLIGAN_BOTTOM_KIND = "MULLIGAN_BOTTOM"


def mulligan_bottom(card: str) -> Action:
    return Action(MULLIGAN_BOTTOM_KIND, {"card": card})


@dataclass(frozen=True)
class MulliganPolicy:
    """Deterministic London-mulligan baseline policy for MUC-5.

    The policy is intentionally simple and auditable. Rev0006 promotes mulligans
    to an agent-facing decision surface while preserving this class as a compact
    rule baseline and as a convenient constructor for scripted agents.
    """

    name: str = POLICY_KEEP_ALWAYS
    min_islands: int = 2
    max_islands: int = 5
    max_mulligans: int = 2
    require_business: bool = False

    def validate(self) -> "MulliganPolicy":
        if self.name not in MULLIGAN_POLICY_NAMES:
            raise ValueError(f"unknown mulligan policy {self.name!r}; expected one of {MULLIGAN_POLICY_NAMES}")
        if not 0 <= self.min_islands <= self.max_islands <= OPENING_HAND_SIZE:
            raise ValueError("expected 0 <= min_islands <= max_islands <= opening hand size")
        if self.max_mulligans < 0:
            raise ValueError("max_mulligans must be nonnegative")
        return self


@dataclass(frozen=True)
class MulliganResult:
    player: int
    policy_name: str
    mulligans_taken: int
    kept_hand_size: int
    opening_hand: Dict[str, int]
    bottomed: Dict[str, int]
    decision_count: int = 0

    def to_row(self) -> Dict[str, int | str]:
        row: Dict[str, int | str] = {
            "player": self.player,
            "policy_name": self.policy_name,
            "mulligans_taken": self.mulligans_taken,
            "kept_hand_size": self.kept_hand_size,
            "decision_count": self.decision_count,
        }
        for card in CARD_ORDER:
            row[f"opening_{card}"] = int(self.opening_hand.get(card, 0))
            row[f"bottomed_{card}"] = int(self.bottomed.get(card, 0))
        return row


@dataclass(frozen=True)
class MulliganObservation:
    """Pregame observation for a mulligan/bottoming agent.

    It deliberately contains only the player's own current hand plus public
    pregame metadata. The opponent's opening hand remains hidden. This lets a
    future learned constructor/pilot share the same action-mask pattern as the
    gameplay environment without forcing the main engine into a full pregame AEC
    implementation yet.
    """

    player: int
    stage: str  # keep_or_mulligan, bottom
    mulligans_taken: int
    hand: Dict[str, int]
    hand_size: int
    library_count: int
    bottom_remaining: int = 0
    starting_life: int = 20
    deck_counts: Dict[str, int] | None = None

    def to_row(self) -> Dict[str, int | str]:
        row: Dict[str, int | str] = {
            "player": self.player,
            "stage": self.stage,
            "mulligans_taken": self.mulligans_taken,
            "hand_size": self.hand_size,
            "library_count": self.library_count,
            "bottom_remaining": self.bottom_remaining,
            "starting_life": self.starting_life,
        }
        for card in CARD_ORDER:
            row[f"hand_{card}"] = int(self.hand.get(card, 0))
            if self.deck_counts is not None:
                row[f"deck_{card}"] = int(self.deck_counts.get(card, 0))
        return row


@runtime_checkable
class MulliganAgent(Protocol):
    name: str

    def choose_mulligan_action(self, obs: MulliganObservation, legal: Sequence[Action], rng: Random) -> Action: ...


@dataclass(frozen=True)
class RuleMulliganAgent:
    """Adapter turning a MulliganPolicy into explicit pregame choices."""

    policy: MulliganPolicy | str | None = POLICY_KEEP_ALWAYS
    name: str | None = None

    def __post_init__(self) -> None:
        pol = policy_from_name(self.policy)
        object.__setattr__(self, "policy", pol)
        if self.name is None:
            object.__setattr__(self, "name", f"mulligan_rule_{pol.name}")

    def choose_mulligan_action(self, obs: MulliganObservation, legal: Sequence[Action], rng: Random) -> Action:
        pol = policy_from_name(self.policy)
        if obs.stage == "keep_or_mulligan":
            hand = Counter(obs.hand)
            if should_keep_hand(hand, obs.mulligans_taken, pol):
                return MULLIGAN_KEEP
            if MULLIGAN_TAKE in legal:
                return MULLIGAN_TAKE
            return MULLIGAN_KEEP
        if obs.stage == "bottom":
            hand = Counter(obs.hand)
            card = choose_next_bottom_card(hand, obs.bottom_remaining)
            action = mulligan_bottom(card)
            if action in legal:
                return action
            return legal[0]
        raise ValueError(f"unknown mulligan observation stage {obs.stage!r}")


@dataclass(frozen=True)
class MulliganDecisionEvent:
    player: int
    agent_name: str
    stage: str
    action: str
    mulligans_taken: int
    hand_size: int
    bottom_remaining: int
    hand: Dict[str, int]
    starting_life: int = 20
    deck_counts: Dict[str, int] | None = None

    def to_row(self) -> Dict[str, int | str]:
        row: Dict[str, int | str] = {
            "player": self.player,
            "agent_name": self.agent_name,
            "stage": self.stage,
            "action": self.action,
            "mulligans_taken": self.mulligans_taken,
            "hand_size": self.hand_size,
            "bottom_remaining": self.bottom_remaining,
            "starting_life": self.starting_life,
        }
        for card in CARD_ORDER:
            row[f"hand_{card}"] = int(self.hand.get(card, 0))
            if self.deck_counts is not None:
                row[f"deck_{card}"] = int(self.deck_counts.get(card, 0))
        return row


def policy_from_name(policy: str | MulliganPolicy | None) -> MulliganPolicy:
    if policy is None:
        return MulliganPolicy(POLICY_KEEP_ALWAYS)
    if isinstance(policy, MulliganPolicy):
        return policy.validate()
    if policy == POLICY_KEEP_ALWAYS:
        return MulliganPolicy(POLICY_KEEP_ALWAYS).validate()
    if policy == POLICY_LAND_BAND:
        return MulliganPolicy(POLICY_LAND_BAND, require_business=False).validate()
    if policy == POLICY_LAND_BAND_BUSINESS:
        return MulliganPolicy(POLICY_LAND_BAND_BUSINESS, require_business=True).validate()
    raise ValueError(f"unknown mulligan policy {policy!r}; expected one of {MULLIGAN_POLICY_NAMES}")


def mulligan_agent_from_policy(policy: str | MulliganPolicy | MulliganAgent | None) -> MulliganAgent:
    if hasattr(policy, "choose_mulligan_action"):
        return policy  # type: ignore[return-value]
    if policy is None or isinstance(policy, MulliganPolicy) or str(policy) in MULLIGAN_POLICY_NAMES:
        return RuleMulliganAgent(policy)
    # Learned/experimental mulligan agents live outside this rules module. Lazy
    # import keeps the base London-mulligan surface small and avoids a module
    # cycle during normal rule-policy use.
    from .mulligan_ranker import make_mulligan_agent

    return make_mulligan_agent(policy)


def hand_total(hand: CounterType[str]) -> int:
    return int(sum(hand.values()))


def has_business(hand: CounterType[str]) -> bool:
    """Crude MUC-5 business test: any interaction or threat."""
    return any(hand.get(card, 0) > 0 for card in (CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD))


def should_keep_hand(hand: CounterType[str], mulligans_taken: int, policy: MulliganPolicy) -> bool:
    policy = policy.validate()
    if policy.name == POLICY_KEEP_ALWAYS:
        return True
    if mulligans_taken >= policy.max_mulligans:
        return True
    islands = int(hand.get(CARD_ISLAND, 0))
    if not (policy.min_islands <= islands <= policy.max_islands):
        return False
    if policy.require_business and not has_business(hand):
        return False
    return True


def _draw_from_library(library: List[str], n: int) -> Counter[str]:
    hand: Counter[str] = Counter()
    for _ in range(n):
        if not library:
            break
        hand[library.pop()] += 1
    return hand


def _return_hand_and_shuffle(library: List[str], hand: CounterType[str], rng: Random) -> None:
    for card, count in hand.items():
        library.extend([card] * count)
    rng.shuffle(library)


def legal_mulligan_actions(hand: CounterType[str], mulligans_taken: int, *, max_mulligans_allowed: int = OPENING_HAND_SIZE) -> List[Action]:
    """Legal keep/take-mulligan actions for a current seven-card look."""
    actions = [MULLIGAN_KEEP]
    if mulligans_taken < max_mulligans_allowed:
        actions.append(MULLIGAN_TAKE)
    return actions


def legal_bottom_actions(hand: CounterType[str]) -> List[Action]:
    return [mulligan_bottom(card) for card, n in sorted(hand.items()) if n > 0]


def choose_next_bottom_card(hand: CounterType[str], bottom_remaining: int) -> str:
    """Choose one bottom card using the rev0005 deterministic priority."""
    if bottom_remaining <= 0:
        raise ValueError("bottom_remaining must be positive")
    # Bottom excess Islands first, but keep at least two if possible.
    if hand.get(CARD_ISLAND, 0) > 2:
        return CARD_ISLAND
    for card in (CARD_OVERLORD, CARD_JACE, CARD_FORCE, CARD_COUNTERSPELL, CARD_ISLAND):
        if hand.get(card, 0) > 0:
            return card
    raise ValueError("cannot bottom from empty hand")


def choose_bottom_cards(hand: CounterType[str], bottom_count: int) -> Counter[str]:
    """Deterministically choose London-mulligan bottom cards.

    This mutates `hand`, preserving the rev0005 API. Rev0006 additionally exposes
    the same behavior one card at a time through `choose_next_bottom_card` and
    `legal_bottom_actions`, so learned mulligan agents can own the choice later.
    """
    bottomed: Counter[str] = Counter()
    while bottom_count > 0:
        card = choose_next_bottom_card(hand, bottom_count)
        hand[card] -= 1
        if hand[card] <= 0:
            del hand[card]
        bottomed[card] += 1
        bottom_count -= 1
    return bottomed


def london_mulligan_opening_hand(
    library: List[str],
    rng: Random,
    policy: str | MulliganPolicy | None = None,
    *,
    player: int = 0,
) -> Tuple[Counter[str], MulliganResult]:
    """Run a deterministic-policy London mulligan on an already shuffled library.

    `library` is mutated in place. Its top is list[-1], matching engine.py.
    """
    agent = RuleMulliganAgent(policy)
    hand, result, _events = london_mulligan_agent_opening_hand(library, rng, agent, player=player)
    return hand, result


def london_mulligan_agent_opening_hand(
    library: List[str],
    rng: Random,
    agent: MulliganAgent | str | MulliganPolicy | None = None,
    *,
    player: int = 0,
    max_mulligans_allowed: int = OPENING_HAND_SIZE,
    starting_life: int = 20,
    deck_counts: Dict[str, int] | None = None,
) -> Tuple[Counter[str], MulliganResult, List[MulliganDecisionEvent]]:
    """Run the London mulligan through explicit agent choices.

    The agent first chooses KEEP or MULLIGAN for each seven-card look. After it
    keeps, it chooses `mulligans_taken` individual bottom-card actions. This is
    the pregame analogue of the main legal-action mask: the referee lists legal
    actions, the agent ranks/chooses, and the engine applies the choice.
    """
    ag = mulligan_agent_from_policy(agent)
    if deck_counts is None:
        deck_counts = {card: int(library.count(card)) for card in CARD_ORDER}
    else:
        deck_counts = {card: int(deck_counts.get(card, 0)) for card in CARD_ORDER}
    mulligans = 0
    events: List[MulliganDecisionEvent] = []
    while True:
        hand = _draw_from_library(library, OPENING_HAND_SIZE)
        obs = MulliganObservation(
            player=player,
            stage="keep_or_mulligan",
            mulligans_taken=mulligans,
            hand={card: int(hand.get(card, 0)) for card in CARD_ORDER if hand.get(card, 0) > 0},
            hand_size=hand_total(hand),
            library_count=len(library),
            starting_life=int(starting_life),
            deck_counts=dict(deck_counts),
        )
        legal = legal_mulligan_actions(hand, mulligans, max_mulligans_allowed=max_mulligans_allowed)
        action = ag.choose_mulligan_action(obs, legal, rng)
        if action not in legal:
            raise ValueError(f"mulligan agent {ag.name!r} chose illegal action {action.compact()}; legal={[a.compact() for a in legal]}")
        events.append(
            MulliganDecisionEvent(
                player=player,
                agent_name=ag.name,
                stage=obs.stage,
                action=action.compact(),
                mulligans_taken=mulligans,
                hand_size=hand_total(hand),
                bottom_remaining=0,
                hand={card: int(hand.get(card, 0)) for card in CARD_ORDER if hand.get(card, 0) > 0},
                starting_life=int(starting_life),
                deck_counts=dict(deck_counts),
            )
        )
        if action == MULLIGAN_KEEP:
            break
        _return_hand_and_shuffle(library, hand, rng)
        mulligans += 1

    bottomed: Counter[str] = Counter()
    bottom_remaining = mulligans
    while bottom_remaining > 0:
        obs = MulliganObservation(
            player=player,
            stage="bottom",
            mulligans_taken=mulligans,
            hand={card: int(hand.get(card, 0)) for card in CARD_ORDER if hand.get(card, 0) > 0},
            hand_size=hand_total(hand),
            library_count=len(library),
            bottom_remaining=bottom_remaining,
            starting_life=int(starting_life),
            deck_counts=dict(deck_counts),
        )
        legal = legal_bottom_actions(hand)
        action = ag.choose_mulligan_action(obs, legal, rng)
        if action not in legal:
            raise ValueError(f"mulligan agent {ag.name!r} chose illegal bottom action {action.compact()}; legal={[a.compact() for a in legal]}")
        card = str(action.params["card"])
        hand[card] -= 1
        if hand[card] <= 0:
            del hand[card]
        bottomed[card] += 1
        library.insert(0, card)
        events.append(
            MulliganDecisionEvent(
                player=player,
                agent_name=ag.name,
                stage=obs.stage,
                action=action.compact(),
                mulligans_taken=mulligans,
                hand_size=hand_total(hand) + 1,
                bottom_remaining=bottom_remaining,
                hand=obs.hand,
                starting_life=int(starting_life),
                deck_counts=dict(deck_counts),
            )
        )
        bottom_remaining -= 1

    result = MulliganResult(
        player=player,
        policy_name=ag.name,
        mulligans_taken=mulligans,
        kept_hand_size=hand_total(hand),
        opening_hand={card: int(hand.get(card, 0)) for card in CARD_ORDER if hand.get(card, 0) > 0},
        bottomed={card: int(bottomed.get(card, 0)) for card in CARD_ORDER if bottomed.get(card, 0) > 0},
        decision_count=len(events),
    )
    return hand, result, events
