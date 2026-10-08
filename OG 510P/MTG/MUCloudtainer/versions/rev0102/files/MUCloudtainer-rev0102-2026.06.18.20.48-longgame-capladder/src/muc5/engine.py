from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from random import Random
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .action_schema import Action, PASS, PLAY_ISLAND, activate_jace, cast, choose
from .cards import (
    BLUE_NONLANDS,
    CARD_COUNTERSPELL,
    CARD_FORCE,
    CARD_ISLAND,
    CARD_JACE,
    CARD_OVERLORD,
    JACE_STARTING_LOYALTY,
    JACE_ULTIMATE_LOYALTY,
    MAX_HAND_SIZE,
    OPENING_HAND_SIZE,
    OVERLORD_FULL_COST,
    OVERLORD_IMPENDING_COST,
    OVERLORD_POWER,
    STARTING_LIFE,
    validate_starting_life,
)
from .deckspace import DeckVector
from .mulligan import MulliganAgent, MulliganPolicy, london_mulligan_opening_hand, london_mulligan_agent_opening_hand
from .tournament import TournamentConfig


@dataclass
class PlayerState:
    life: int = STARTING_LIFE
    mulligans_taken: int = 0
    library: List[str] = field(default_factory=list)  # top of library is list[-1]
    hand: Counter[str] = field(default_factory=Counter)
    graveyard: Counter[str] = field(default_factory=Counter)
    exile: Counter[str] = field(default_factory=Counter)
    islands_untapped: int = 0
    islands_tapped: int = 0
    jace_loyalty: Optional[int] = None
    jace_used_this_turn: bool = False
    overlord_ready: int = 0
    overlord_sick: int = 0
    overlord_tapped: int = 0
    impending_4: int = 0
    impending_3: int = 0
    impending_2: int = 0
    impending_1: int = 0

    def hand_count(self, card: str) -> int:
        return int(self.hand.get(card, 0))

    def total_hand(self) -> int:
        return sum(self.hand.values())

    def total_library(self) -> int:
        return len(self.library)

    def total_overlord_creatures(self) -> int:
        return self.overlord_ready + self.overlord_sick + self.overlord_tapped

    def public_dict(self) -> Dict[str, object]:
        return {
            "life": self.life,
            "mulligans_taken": self.mulligans_taken,
            "library_count": len(self.library),
            "hand_count": self.total_hand(),
            "graveyard": dict(self.graveyard),
            # Exile is a public zone in MUC-5.  Keep the legacy count for old
            # code, but expose identities so Force-of-Will pitch payments and
            # Jace ultimates are not hidden behind an aggregate.
            "exile": dict(self.exile),
            "exile_count": sum(self.exile.values()),
            "islands_untapped": self.islands_untapped,
            "islands_tapped": self.islands_tapped,
            "jace_loyalty": self.jace_loyalty,
            "jace_used_this_turn": self.jace_used_this_turn,
            "overlord_ready": self.overlord_ready,
            "overlord_sick": self.overlord_sick,
            "overlord_tapped": self.overlord_tapped,
            "impending_4": self.impending_4,
            "impending_3": self.impending_3,
            "impending_2": self.impending_2,
            "impending_1": self.impending_1,
        }


@dataclass
class StackSpell:
    spell_id: int
    controller: int
    card: str
    mode: str = "normal"
    params: Dict[str, object] = field(default_factory=dict)


@dataclass
class PendingChoice:
    player: int
    kind: str
    data: Dict[str, object] = field(default_factory=dict)


@dataclass
class PendingCombat:
    attacker: int
    defender: int
    to_player: int = 0
    to_jace: int = 0

    @property
    def total_attackers(self) -> int:
        return self.to_player + self.to_jace


@dataclass
class GameState:
    players: List[PlayerState]
    # Incremented after every applied macro-action. Decision-frame wrappers use
    # this as a cheap stale-frame guard so fast paths do not need to recompute
    # legal actions while still rejecting replayed/out-of-date choices.
    revision: int = 0
    starting_life: int = STARTING_LIFE
    active_player: int = 0
    priority_player: Optional[int] = None
    frame: str = "MAIN"  # MAIN, RESPONSE, ATTACK, BLOCK, GAME_OVER
    main_phase: str = "precombat"  # precombat or postcombat when frame == MAIN
    stack: List[StackSpell] = field(default_factory=list)
    pending_choice: Optional[PendingChoice] = None
    pending_combat: Optional[PendingCombat] = None
    land_played_this_turn: bool = False
    turn_number: int = 1
    first_turn_draw_skipped: bool = False
    consecutive_passes: int = 0
    next_spell_id: int = 1
    winner: Optional[int] = None
    loss_reason: str = ""
    log: List[str] = field(default_factory=list)
    record_log: bool = True
    pre_stack_frame: str = "MAIN"
    mulligan_log: List[Dict[str, object]] = field(default_factory=list)
    mulligan_decision_log: List[Dict[str, object]] = field(default_factory=list)
    starting_deck_counts: List[Dict[str, int]] = field(default_factory=list)
    # Machine-readable perfect-recall substrate.  ``observation`` remains the
    # compact snapshot used by legacy public agents; ``information_state`` adds
    # ordered public events plus private events known to the acting player.
    event_seq: int = 0
    public_events: List[Dict[str, object]] = field(default_factory=list)
    private_events: List[List[Dict[str, object]]] = field(default_factory=lambda: [[], []])
    known_top_cards: List[Dict[int, str]] = field(default_factory=lambda: [{}, {}])

    def opponent(self, player: int) -> int:
        return 1 - player

    def current_player(self) -> int:
        if self.pending_choice is not None:
            return self.pending_choice.player
        if self.frame == "RESPONSE" and self.priority_player is not None:
            return self.priority_player
        if self.frame in {"MAIN", "ATTACK"}:
            return self.active_player
        if self.frame == "BLOCK" and self.pending_combat is not None:
            return self.pending_combat.defender
        return self.active_player

    def observation(self, player: int) -> Dict[str, object]:
        """Hidden-information-correct observation for one player.

        The state object itself is omniscient, but this method is the boundary
        intended for learned agents and external controllers. In particular,
        pending choice payloads can contain private information: Jace +2 stores
        the seen top card here. Only the player currently making that choice may
        see the payload. Other observers get the public fact that a choice is
        pending, but not the private data.
        """
        pending_kind = None if self.pending_choice is None else self.pending_choice.kind
        if self.pending_choice is None:
            pending_data = None
        elif self.pending_choice.player == player:
            pending_data = dict(self.pending_choice.data)
        else:
            pending_data = {"redacted": True, "player": self.pending_choice.player, "kind": self.pending_choice.kind}
        return {
            "player": player,
            "active_player": self.active_player,
            "to_act": self.current_player(),
            "frame": self.frame,
            "main_phase": self.main_phase,
            "turn_number": self.turn_number,
            "starting_life": self.starting_life,
            "starting_life_total": self.starting_life,
            "own_hand": dict(self.players[player].hand),
            "own_library_count": len(self.players[player].library),
            "public_self": self.players[player].public_dict(),
            "public_opponent": self.players[self.opponent(player)].public_dict(),
            "stack": [s.__dict__.copy() for s in self.stack],
            "pending_choice_kind": pending_kind,
            "pending_choice_data": pending_data,
        }

    def information_state(self, player: int) -> Dict[str, object]:
        """Return the agent-facing perfect-recall information state.

        ``observation(player)`` is intentionally compact and snapshot-shaped.
        This method is the durable history boundary for imperfect-information
        agents: it contains the current observation, every public event emitted
        so far, and only the private events/knowledge available to ``player``.
        The referee may know more, but policies should not need omniscient
        ``GameState`` access to remember a Jace-seen top card or a public Force
        pitch card.
        """

        return {
            "schema": "muc5.information_state.v1",
            "player": int(player),
            "state_revision": int(self.revision),
            "event_seq": int(self.event_seq),
            "observation": self.observation(player),
            "public_events": [dict(event) for event in self.public_events],
            "private_events": [dict(event) for event in self.private_events[player]],
            "known_top_cards": {str(target): card for target, card in sorted(self.known_top_cards[player].items())},
        }


def deck_to_library(deck: DeckVector, rng: Random) -> List[str]:
    cards: List[str] = []
    for card, count in deck.counts().items():
        cards.extend([card] * count)
    rng.shuffle(cards)
    return cards


def start_game(
    deck0: DeckVector,
    deck1: DeckVector,
    seed: int = 1,
    starting_player: int = 0,
    starting_life: int | None = None,
    starting_life_total: int | None = None,
    match_config: TournamentConfig | None = None,
    mulligan_policy: str | MulliganPolicy | None = None,
    mulligan_policies: Tuple[str | MulliganPolicy | None, str | MulliganPolicy | None] | None = None,
    mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None,
    record_log: bool = True,
) -> GameState:
    """Create a new MUC-5 game.

    The life-total dial is public once the game begins. The uncertainty experiment
    belongs to deck construction: did the constructor know this value before
    registering its 40/60-card deck, or did it have to build for a mixed field?

    `starting_life` is kept as a short compatibility alias; new scripts should
    prefer `starting_life_total` or `match_config`.
    """
    if match_config is not None:
        chosen_life = match_config.starting_life
    elif starting_life_total is not None:
        chosen_life = starting_life_total
    elif starting_life is not None:
        chosen_life = starting_life
    else:
        chosen_life = STARTING_LIFE
    chosen_life = validate_starting_life(chosen_life)
    rng = Random(seed)
    state = GameState(
        players=[
            PlayerState(life=chosen_life, library=deck_to_library(deck0, rng)),
            PlayerState(life=chosen_life, library=deck_to_library(deck1, rng)),
        ],
        starting_life=chosen_life,
        record_log=record_log,
        starting_deck_counts=[deck0.counts(), deck1.counts()],
    )
    state.active_player = starting_player
    if mulligan_agents is not None and len(mulligan_agents) != 2:
        raise ValueError("mulligan_agents must contain exactly two agents/policies")
    if mulligan_policies is not None and len(mulligan_policies) != 2:
        raise ValueError("mulligan_policies must contain exactly two policies")
    if mulligan_agents is not None and (mulligan_policy is not None or mulligan_policies is not None):
        raise ValueError("pass either mulligan_agents or mulligan_policy/mulligan_policies, not both")
    if mulligan_policies is None and mulligan_policy is not None:
        mulligan_policies = (mulligan_policy, mulligan_policy)

    if mulligan_agents is not None:
        for p, agent in enumerate(mulligan_agents):
            hand, result, events = london_mulligan_agent_opening_hand(
                state.players[p].library,
                rng,
                agent,
                player=p,
                starting_life=chosen_life,
                deck_counts=state.starting_deck_counts[p],
            )
            state.players[p].hand = hand
            state.players[p].mulligans_taken = result.mulligans_taken
            state.mulligan_log.append(result.to_row())
            state.mulligan_decision_log.extend(event.to_row() for event in events)
            _log(state, 
                f"MULLIGAN_AGENCY player={p} agent={result.policy_name} mulligans={result.mulligans_taken} kept={result.kept_hand_size} decisions={result.decision_count}"
            )
    elif mulligan_policies is None:
        for p in range(2):
            _draw_cards(state, p, OPENING_HAND_SIZE)
    else:
        for p, policy in enumerate(mulligan_policies):
            hand, result, events = london_mulligan_agent_opening_hand(
                state.players[p].library,
                rng,
                policy,
                player=p,
                starting_life=chosen_life,
                deck_counts=state.starting_deck_counts[p],
            )
            state.players[p].hand = hand
            state.players[p].mulligans_taken = result.mulligans_taken
            state.mulligan_log.append(result.to_row())
            _log(state, 
                f"MULLIGAN player={p} policy={result.policy_name} mulligans={result.mulligans_taken} kept={result.kept_hand_size}"
            )
    # First player skips their first draw in two-player Magic.
    _start_turn(state, starting_player, skip_draw=True)
    _log(state, f"START_GAME starting_player={starting_player} seed={seed} starting_life={chosen_life}")
    return state


def start_game_from_pregame_state(
    deck0: DeckVector,
    deck1: DeckVector,
    *,
    library0: Iterable[str],
    hand0: Dict[str, int] | Counter[str],
    mulligans0: int = 0,
    library1: Iterable[str],
    hand1: Dict[str, int] | Counter[str],
    mulligans1: int = 0,
    starting_player: int = 0,
    starting_life: int | None = None,
    starting_life_total: int | None = None,
    record_log: bool = True,
    mulligan_log: List[Dict[str, object]] | None = None,
    mulligan_decision_log: List[Dict[str, object]] | None = None,
) -> GameState:
    """Create a game from explicit post-mulligan private states.

    This is a diagnostic/research helper, not the normal tournament constructor.
    It is used for counterfactual mulligan probes where the branch being tested
    must not perturb the opponent's opening hand or later transition RNG.  The
    caller supplies each player's remaining library, kept hand, and mulligan
    count after London-mulligan resolution.  The regular turn-start semantics
    then begin with the starting player's first draw skipped, matching
    ``start_game``.

    Inputs are copied so later simulation cannot mutate the caller's cached
    pregame branch data.
    """
    chosen_life = STARTING_LIFE if starting_life is None and starting_life_total is None else (starting_life_total if starting_life_total is not None else starting_life)
    chosen_life = validate_starting_life(int(chosen_life))
    h0 = Counter({card: int(count) for card, count in dict(hand0).items() if int(count) > 0})
    h1 = Counter({card: int(count) for card, count in dict(hand1).items() if int(count) > 0})
    state = GameState(
        players=[
            PlayerState(life=chosen_life, library=list(library0), hand=h0, mulligans_taken=int(mulligans0)),
            PlayerState(life=chosen_life, library=list(library1), hand=h1, mulligans_taken=int(mulligans1)),
        ],
        starting_life=chosen_life,
        record_log=record_log,
        starting_deck_counts=[deck0.counts(), deck1.counts()],
        mulligan_log=list(mulligan_log or []),
        mulligan_decision_log=list(mulligan_decision_log or []),
    )
    state.active_player = int(starting_player)
    _start_turn(state, int(starting_player), skip_draw=True)
    _log(state, f"START_GAME_FROM_PREGAME starting_player={starting_player} starting_life={chosen_life}")
    return state


def _other(player: int) -> int:
    return 1 - player


def _log(state: GameState, message: str) -> None:
    if state.record_log:
        state.log.append(message)


def _next_event_seq(state: GameState) -> int:
    state.event_seq += 1
    return state.event_seq


def _public_event(state: GameState, kind: str, **payload: object) -> None:
    event: Dict[str, object] = {"seq": _next_event_seq(state), "kind": kind}
    event.update(payload)
    state.public_events.append(event)


def _private_event(state: GameState, player_idx: int, kind: str, **payload: object) -> None:
    while len(state.private_events) <= player_idx:
        state.private_events.append([])
    event: Dict[str, object] = {"seq": _next_event_seq(state), "kind": kind}
    event.update(payload)
    state.private_events[player_idx].append(event)


def _clear_known_top(state: GameState, target_player: int) -> None:
    for knowledge in state.known_top_cards:
        knowledge.pop(int(target_player), None)


def _set_known_top(state: GameState, observer: int, target_player: int, card: str) -> None:
    while len(state.known_top_cards) <= observer:
        state.known_top_cards.append({})
    state.known_top_cards[int(observer)][int(target_player)] = str(card)


def _can_pay(player: PlayerState, generic: int, blue: int) -> bool:
    return player.islands_untapped >= generic + blue


def _tap_islands(player: PlayerState, total: int) -> None:
    if total < 0 or player.islands_untapped < total:
        raise ValueError("cannot tap requested Islands")
    player.islands_untapped -= total
    player.islands_tapped += total


def _remove_from_hand(player: PlayerState, card: str, count: int = 1) -> None:
    if player.hand[card] < count:
        raise ValueError(f"not enough {card} in hand")
    player.hand[card] -= count
    if player.hand[card] <= 0:
        del player.hand[card]


def _add_to_hand(player: PlayerState, card: str, count: int = 1) -> None:
    player.hand[card] += count


def _draw_cards(state: GameState, player_idx: int, n: int) -> None:
    player = state.players[player_idx]
    drawn_count = 0
    for _ in range(n):
        if not player.library:
            state.winner = _other(player_idx)
            state.loss_reason = f"player_{player_idx}_attempted_to_draw_from_empty_library"
            state.frame = "GAME_OVER"
            _public_event(state, "LOSE_EMPTY_LIBRARY_DRAW", player=player_idx)
            _log(state, f"LOSE player={player_idx} reason=empty_library_draw")
            return
        known_before = [
            (observer, knowledge[int(player_idx)])
            for observer, knowledge in enumerate(state.known_top_cards)
            if int(player_idx) in knowledge
        ]
        card = player.library.pop()
        for observer, known_card in known_before:
            # If a player previously learned this top card, preserve the fact
            # that the known card moved into the drawing player's hidden hand.
            _private_event(
                state,
                observer,
                "KNOWN_TOP_CARD_DRAWN",
                drawing_player=player_idx,
                card=card,
                matched_prediction=bool(known_card == card),
            )
        _clear_known_top(state, player_idx)
        player.hand[card] += 1
        _private_event(state, player_idx, "DRAW_CARD", card=card)
        drawn_count += 1
    if drawn_count:
        _public_event(state, "DRAW_CARDS", player=player_idx, count=drawn_count)


def _start_turn(state: GameState, player_idx: int, skip_draw: bool = False) -> None:
    if state.winner is not None:
        return
    state.active_player = player_idx
    state.priority_player = None
    state.frame = "MAIN"
    state.main_phase = "precombat"
    state.land_played_this_turn = False
    state.consecutive_passes = 0
    p = state.players[player_idx]
    p.islands_untapped += p.islands_tapped
    p.islands_tapped = 0
    p.overlord_ready += p.overlord_sick + p.overlord_tapped
    p.overlord_sick = 0
    p.overlord_tapped = 0
    p.jace_used_this_turn = False
    if not skip_draw:
        _draw_cards(state, player_idx, 1)
    _log(state, f"TURN_START player={player_idx} turn={state.turn_number} skip_draw={skip_draw}")


def _advance_to_next_turn(state: GameState) -> None:
    nxt = _other(state.active_player)
    if nxt == 0:
        state.turn_number += 1
    _start_turn(state, nxt, skip_draw=False)


def _begin_postcombat_main(state: GameState) -> None:
    state.frame = "MAIN"
    state.main_phase = "postcombat"
    state.priority_player = None
    state.consecutive_passes = 0
    _log(state, f"POSTCOMBAT_MAIN player={state.active_player} turn={state.turn_number}")


def _end_turn(state: GameState) -> None:
    p = state.players[state.active_player]
    # Impending removes one counter at the beginning of that controller's end step.
    awakened = p.impending_1
    p.overlord_ready += awakened
    p.impending_1 = p.impending_2
    p.impending_2 = p.impending_3
    p.impending_3 = p.impending_4
    p.impending_4 = 0
    if awakened:
        _log(state, f"IMPENDING_AWAKENS player={state.active_player} count={awakened}")
    if p.total_hand() > MAX_HAND_SIZE:
        state.pending_choice = PendingChoice(state.active_player, "cleanup_discard", {"resume": "NEXT_TURN"})
        state.frame = "MAIN"
        return
    _advance_to_next_turn(state)


def _force_pitch_cards(hand: Counter[str]) -> List[str]:
    out: List[str] = []
    for card in BLUE_NONLANDS:
        available = hand.get(card, 0)
        if card == CARD_FORCE:
            available -= 1
        if available > 0:
            out.append(card)
    return out


def _overlord_creature_state_counts(player: PlayerState) -> Dict[str, int]:
    """Counts of actual Overlord creature objects by tactical state.

    Impending Overlords with time counters are deliberately absent: they are
    permanents, but not creatures, so Jace -1 cannot target them. Keeping the
    state in the legal action fixes an early aggregation shortcut where Jace
    always bounced a ready Overlord even when a sick/tapped one was the intended
    target.
    """

    return {
        "ready": int(player.overlord_ready),
        "sick": int(player.overlord_sick),
        "tapped": int(player.overlord_tapped),
    }


def _overlord_attr_for_state(creature_state: str) -> str:
    mapping = {
        "ready": "overlord_ready",
        "sick": "overlord_sick",
        "tapped": "overlord_tapped",
    }
    if creature_state not in mapping:
        raise ValueError(f"unknown Overlord creature_state={creature_state!r}")
    return mapping[creature_state]


def _begin_overlord_trigger_sequence(state: GameState, player_idx: int, *, trigger_count: int, resume: str) -> None:
    """Resolve Overlord draw/discard triggers one at a time.

    Earlier revisions aggregated N attack triggers as draw 2N, then discard N.
    That was too generous: with two attacking Overlords, Magic resolves the
    triggers separately, so the player must discard after the first draw-two
    before seeing the second draw-two. There are no MUC-5 responses to these
    abilities, so we can still auto-resolve each draw portion, but the discard
    choice remains sequential and agent-facing.
    """

    if trigger_count <= 0:
        state.frame = resume if resume != "BLOCK_OR_DAMAGE" else state.frame
        if resume == "BLOCK_OR_DAMAGE":
            _after_attack_triggers(state)
        return
    _draw_cards(state, player_idx, 2)
    if state.winner is not None:
        return
    state.pending_choice = PendingChoice(
        player_idx,
        "discard",
        {"remaining": 1, "resume": resume, "overlord_triggers_remaining": int(trigger_count) - 1},
    )


def legal_actions(state: GameState) -> List[Action]:
    if state.winner is not None or state.frame == "GAME_OVER":
        return []
    if state.pending_choice is not None:
        return _legal_choice_actions(state)
    if state.frame == "RESPONSE":
        return _legal_response_actions(state)
    if state.frame == "MAIN":
        return _legal_main_actions(state)
    if state.frame == "ATTACK":
        return _legal_attack_actions(state)
    if state.frame == "BLOCK":
        return _legal_block_actions(state)
    return [PASS]


def _legal_main_actions(state: GameState) -> List[Action]:
    player = state.players[state.active_player]
    opp = state.players[_other(state.active_player)]
    actions = [PASS]
    if not state.land_played_this_turn and player.hand_count(CARD_ISLAND) > 0:
        actions.append(PLAY_ISLAND)
    if player.hand_count(CARD_JACE) > 0 and _can_pay(player, 2, 2):
        actions.append(cast(CARD_JACE))
    if player.hand_count(CARD_OVERLORD) > 0 and _can_pay(player, OVERLORD_IMPENDING_COST.generic, OVERLORD_IMPENDING_COST.blue):
        actions.append(cast(CARD_OVERLORD, mode="impending"))
    if player.hand_count(CARD_OVERLORD) > 0 and _can_pay(player, OVERLORD_FULL_COST.generic, OVERLORD_FULL_COST.blue):
        actions.append(cast(CARD_OVERLORD, mode="full_cost"))
    if player.jace_loyalty is not None and not player.jace_used_this_turn:
        actions.append(activate_jace("plus2", target_player="self"))
        actions.append(activate_jace("plus2", target_player="opponent"))
        actions.append(activate_jace("zero"))
        if player.jace_loyalty >= 1:
            for creature_state, count in _overlord_creature_state_counts(opp).items():
                if count > 0:
                    actions.append(activate_jace("minus1", target_player="opponent", target_state=creature_state))
            for creature_state, count in _overlord_creature_state_counts(player).items():
                if count > 0:
                    actions.append(activate_jace("minus1", target_player="self", target_state=creature_state))
        if player.jace_loyalty >= JACE_ULTIMATE_LOYALTY:
            actions.append(activate_jace("ultimate", target_player="opponent"))
            actions.append(activate_jace("ultimate", target_player="self"))
    return actions


def _legal_response_actions(state: GameState) -> List[Action]:
    player_idx = state.priority_player
    if player_idx is None:
        return [PASS]
    player = state.players[player_idx]
    actions = [PASS]
    # Counterspell/Force can target any spell on the stack, except a spell cannot target itself.
    for target in state.stack:
        if player.hand_count(CARD_COUNTERSPELL) > 0 and _can_pay(player, 0, 2):
            actions.append(cast(CARD_COUNTERSPELL, target_id=target.spell_id, target_card=target.card))
        if player.hand_count(CARD_FORCE) > 0 and _can_pay(player, 3, 2):
            actions.append(cast(CARD_FORCE, payment="mana", target_id=target.spell_id, target_card=target.card))
        if player.hand_count(CARD_FORCE) > 0 and player.life >= 1:
            for pitch_card in _force_pitch_cards(player.hand):
                actions.append(cast(CARD_FORCE, payment="pitch", pitch_card=pitch_card, target_id=target.spell_id, target_card=target.card))
    return actions


def _legal_attack_actions(state: GameState) -> List[Action]:
    player = state.players[state.active_player]
    opp = state.players[_other(state.active_player)]
    n = player.overlord_ready
    actions = [PASS]
    if n <= 0:
        return actions
    for to_player in range(0, n + 1):
        max_to_jace = n - to_player if opp.jace_loyalty is not None else 0
        for to_jace in range(0, max_to_jace + 1):
            if to_player + to_jace > 0:
                actions.append(Action("ATTACK", {"to_player": to_player, "to_jace": to_jace}))
    return actions


def _legal_block_actions(state: GameState) -> List[Action]:
    combat = state.pending_combat
    if combat is None:
        return [PASS]
    defender = state.players[combat.defender]
    ready = defender.overlord_ready
    actions = [PASS]
    for bp in range(0, min(combat.to_player, ready) + 1):
        remain = ready - bp
        for bj in range(0, min(combat.to_jace, remain) + 1):
            if bp + bj > 0:
                actions.append(Action("BLOCK", {"block_player_attackers": bp, "block_jace_attackers": bj}))
    return actions


def _legal_choice_actions(state: GameState) -> List[Action]:
    pc = state.pending_choice
    assert pc is not None
    player = state.players[pc.player]
    if pc.kind == "discard" or pc.kind == "cleanup_discard":
        return [choose(pc.kind, discard=card) for card, n in sorted(player.hand.items()) if n > 0]
    if pc.kind == "jace_plus2":
        return [choose("jace_plus2", put="leave"), choose("jace_plus2", put="bottom")]
    if pc.kind == "jace_brainstorm_putback":
        cards = sorted([c for c, n in player.hand.items() if n > 0])
        actions: List[Action] = []
        for first in cards:
            for second in cards:
                if first == second and player.hand[first] < 2:
                    continue
                actions.append(choose("jace_brainstorm_putback", first_draw=first, second_draw=second))
        return actions
    if pc.kind == "jace_legend":
        return [choose("jace_legend", keep="old"), choose("jace_legend", keep="new")]
    return [PASS]


def apply_action(state: GameState, action: Action, rng: Optional[Random] = None, *, validate: bool = True) -> None:
    """Apply a macro-action.

    By default this validates against the current legal-action list. Hot arena
    loops may pass ``validate=False`` only when the action came directly from
    ``legal_actions(state)`` for this exact state. This avoids enumerating legal
    actions twice per decision while keeping the safer default for tests, CLI,
    and external callers.
    """
    rng = rng or Random(0)
    if state.winner is not None:
        return
    if validate:
        legal = legal_actions(state)
        if action not in legal:
            raise ValueError(f"illegal action {action.compact()} in frame={state.frame}; legal={[a.compact() for a in legal]}")
    if state.record_log:
        state.log.append(f"ACTION player={state.current_player()} {action.compact()}")
    if state.pending_choice is not None:
        _apply_choice_action(state, action, rng)
    elif state.frame == "MAIN":
        _apply_main_action(state, action, rng)
    elif state.frame == "RESPONSE":
        _apply_response_action(state, action, rng)
    elif state.frame == "ATTACK":
        _apply_attack_action(state, action, rng)
    elif state.frame == "BLOCK":
        _apply_block_action(state, action, rng)
    _check_state_based(state)
    state.revision += 1


def _apply_main_action(state: GameState, action: Action, rng: Random) -> None:
    pidx = state.active_player
    player = state.players[pidx]
    if action.kind == "PASS":
        if state.main_phase == "precombat":
            state.frame = "ATTACK"
        else:
            _end_turn(state)
        return
    if action.kind == "PLAY_ISLAND":
        _remove_from_hand(player, CARD_ISLAND)
        player.islands_untapped += 1
        state.land_played_this_turn = True
        return
    if action.kind == "CAST":
        card = action.params["card"]
        if card == CARD_JACE:
            _cast_spell(state, pidx, CARD_JACE, mode="normal", params={}, generic=2, blue=2)
        elif card == CARD_OVERLORD:
            mode = str(action.params.get("mode", "full_cost"))
            if mode == "impending":
                _cast_spell(state, pidx, CARD_OVERLORD, mode="impending", params={}, generic=1, blue=2)
            else:
                _cast_spell(state, pidx, CARD_OVERLORD, mode="full_cost", params={}, generic=3, blue=2)
        return
    if action.kind == "ACTIVATE_JACE":
        _activate_jace(state, pidx, action, rng)
        return


def _cast_spell(state: GameState, player_idx: int, card: str, mode: str, params: Dict[str, object], generic: int, blue: int) -> None:
    player = state.players[player_idx]
    _remove_from_hand(player, card)
    _tap_islands(player, generic + blue)
    spell = StackSpell(state.next_spell_id, player_idx, card, mode, params)
    state.next_spell_id += 1
    state.stack.append(spell)
    state.pre_stack_frame = state.frame
    state.frame = "RESPONSE"
    state.priority_player = player_idx  # exact-ish: controller receives priority after casting.
    state.consecutive_passes = 0


def _apply_response_action(state: GameState, action: Action, rng: Random) -> None:
    player_idx = state.priority_player
    assert player_idx is not None
    player = state.players[player_idx]
    if action.kind == "PASS":
        state.consecutive_passes += 1
        if state.consecutive_passes >= 2:
            _resolve_top_of_stack(state, rng)
        else:
            state.priority_player = _other(player_idx)
        return
    if action.kind == "CAST":
        card = action.params["card"]
        target_id = int(action.params["target_id"])
        if card == CARD_COUNTERSPELL:
            _remove_from_hand(player, CARD_COUNTERSPELL)
            _tap_islands(player, 2)
            spell = StackSpell(state.next_spell_id, player_idx, CARD_COUNTERSPELL, "normal", {"target_id": target_id})
        elif card == CARD_FORCE:
            payment = action.params.get("payment")
            _remove_from_hand(player, CARD_FORCE)
            if payment == "mana":
                _tap_islands(player, 5)
            else:
                pitch_card = str(action.params["pitch_card"])
                _remove_from_hand(player, pitch_card)
                player.exile[pitch_card] += 1
                player.life -= 1
                _public_event(
                    state,
                    "FORCE_PITCH_PAYMENT",
                    player=player_idx,
                    pitch_card=pitch_card,
                    life_paid=1,
                    target_id=target_id,
                )
            spell = StackSpell(state.next_spell_id, player_idx, CARD_FORCE, str(payment), {"target_id": target_id})
        else:
            raise ValueError(f"unexpected response spell: {card}")
        state.next_spell_id += 1
        state.stack.append(spell)
        state.priority_player = player_idx
        state.consecutive_passes = 0


def _resolve_top_of_stack(state: GameState, rng: Random) -> None:
    if not state.stack:
        state.frame = state.pre_stack_frame
        state.priority_player = None
        state.consecutive_passes = 0
        return
    spell = state.stack.pop()
    _log(state, f"RESOLVE spell_id={spell.spell_id} card={spell.card} controller={spell.controller} mode={spell.mode}")
    controller = state.players[spell.controller]
    if spell.card in {CARD_COUNTERSPELL, CARD_FORCE}:
        target_id = int(spell.params.get("target_id", -1))
        target_i = next((i for i, s in enumerate(state.stack) if s.spell_id == target_id), None)
        if target_i is not None:
            target = state.stack.pop(target_i)
            state.players[target.controller].graveyard[target.card] += 1
            _log(state, f"COUNTERED target_id={target.spell_id} card={target.card}")
        controller.graveyard[spell.card] += 1
    elif spell.card == CARD_JACE:
        if controller.jace_loyalty is None:
            controller.jace_loyalty = JACE_STARTING_LOYALTY
        else:
            # Choice is exposed because high-loyalty old Jace can matter.
            state.pending_choice = PendingChoice(
                spell.controller,
                "jace_legend",
                {"old_loyalty": controller.jace_loyalty, "old_used": controller.jace_used_this_turn, "new_loyalty": JACE_STARTING_LOYALTY},
            )
            controller.jace_loyalty = JACE_STARTING_LOYALTY
            controller.jace_used_this_turn = False
        # Planeswalker spells do not go to graveyard when they resolve.
    elif spell.card == CARD_OVERLORD:
        if spell.mode == "impending":
            controller.impending_4 += 1
        else:
            controller.overlord_sick += 1
        _begin_overlord_trigger_sequence(state, spell.controller, trigger_count=1, resume=state.pre_stack_frame)
    if state.pending_choice is None and state.winner is None:
        if state.stack:
            state.frame = "RESPONSE"
            state.priority_player = state.active_player
            state.consecutive_passes = 0
        else:
            state.frame = state.pre_stack_frame
            state.priority_player = None
            state.consecutive_passes = 0


def _activate_jace(state: GameState, player_idx: int, action: Action, rng: Random) -> None:
    player = state.players[player_idx]
    assert player.jace_loyalty is not None
    mode = str(action.params["mode"])
    player.jace_used_this_turn = True
    if mode == "plus2":
        player.jace_loyalty += 2
        target = player_idx if action.params.get("target_player") == "self" else _other(player_idx)
        top_card = state.players[target].library[-1] if state.players[target].library else None
        if top_card is None:
            _public_event(state, "JACE_PLUS2_EMPTY_LIBRARY", player=player_idx, target_player=target)
            return
        _set_known_top(state, observer=player_idx, target_player=target, card=top_card)
        _public_event(state, "JACE_PLUS2_LOOK", player=player_idx, target_player=target)
        _private_event(state, player_idx, "SAW_TOP_CARD", source="jace_plus2", target_player=target, card=top_card)
        state.pending_choice = PendingChoice(player_idx, "jace_plus2", {"target_player": target, "seen_top_card": top_card, "resume": "MAIN"})
    elif mode == "zero":
        _draw_cards(state, player_idx, 3)
        if state.winner is None:
            state.pending_choice = PendingChoice(player_idx, "jace_brainstorm_putback", {"resume": "MAIN"})
    elif mode == "minus1":
        player.jace_loyalty -= 1
        target = player_idx if action.params.get("target_player") == "self" else _other(player_idx)
        target_state = str(action.params.get("target_state", ""))
        _bounce_one_overlord(state.players[target], target_state=target_state)
    elif mode == "ultimate":
        player.jace_loyalty -= 12
        target = player_idx if action.params.get("target_player") == "self" else _other(player_idx)
        target_player = state.players[target]
        exiled_count = len(target_player.library)
        for exiled_card in target_player.library:
            target_player.exile[exiled_card] += 1
        target_player.library.clear()
        _clear_known_top(state, target)
        new_lib: List[str] = []
        for card, count in list(target_player.hand.items()):
            new_lib.extend([card] * count)
        target_player.hand.clear()
        rng.shuffle(new_lib)
        target_player.library = new_lib
        _clear_known_top(state, target)
        _public_event(state, "JACE_ULTIMATE", player=player_idx, target_player=target, exiled_library_count=exiled_count, new_library_count=len(new_lib))


def _bounce_one_overlord(player: PlayerState, *, target_state: str = "") -> None:
    attrs: Tuple[str, ...]
    if target_state:
        attrs = (_overlord_attr_for_state(target_state),)
    else:
        # Backward-compatible fallback for older saved/debug actions. Legal
        # actions generated in rev0010 and later always include target_state.
        attrs = ("overlord_ready", "overlord_sick", "overlord_tapped")
    for attr in attrs:
        n = getattr(player, attr)
        if n > 0:
            setattr(player, attr, n - 1)
            player.hand[CARD_OVERLORD] += 1
            return
    raise ValueError(f"no Overlord creature available to bounce in target_state={target_state!r}")


def _apply_attack_action(state: GameState, action: Action, rng: Random) -> None:
    if action.kind == "PASS":
        _begin_postcombat_main(state)
        return
    attacker = state.active_player
    defender = _other(attacker)
    to_player = int(action.params.get("to_player", 0))
    to_jace = int(action.params.get("to_jace", 0))
    total = to_player + to_jace
    p = state.players[attacker]
    p.overlord_ready -= total
    state.pending_combat = PendingCombat(attacker=attacker, defender=defender, to_player=to_player, to_jace=to_jace)
    # Attack triggers resolve sequentially: draw two, discard one, then the
    # next trigger. This avoids leaking future trigger draws into an earlier
    # discard decision.
    if total > 0:
        _begin_overlord_trigger_sequence(state, attacker, trigger_count=total, resume="BLOCK_OR_DAMAGE")
    else:
        _after_attack_triggers(state)


def _after_attack_triggers(state: GameState) -> None:
    combat = state.pending_combat
    if combat is None:
        state.frame = "ATTACK"
        return
    defender = state.players[combat.defender]
    if defender.overlord_ready > 0 and combat.total_attackers > 0:
        state.frame = "BLOCK"
    else:
        _resolve_combat(state, 0, 0)


def _apply_block_action(state: GameState, action: Action, rng: Random) -> None:
    if action.kind == "PASS":
        _resolve_combat(state, 0, 0)
    else:
        _resolve_combat(state, int(action.params.get("block_player_attackers", 0)), int(action.params.get("block_jace_attackers", 0)))


def _resolve_combat(state: GameState, block_player_attackers: int, block_jace_attackers: int) -> None:
    combat = state.pending_combat
    assert combat is not None
    attacker = state.players[combat.attacker]
    defender = state.players[combat.defender]
    bp = min(block_player_attackers, combat.to_player, defender.overlord_ready)
    bj = min(block_jace_attackers, combat.to_jace, defender.overlord_ready - bp)
    blocked = bp + bj
    unblocked_player = combat.to_player - bp
    unblocked_jace = combat.to_jace - bj
    if blocked:
        attacker.graveyard[CARD_OVERLORD] += blocked
        defender.graveyard[CARD_OVERLORD] += blocked
        defender.overlord_ready -= blocked
    survivors = unblocked_player + unblocked_jace
    attacker.overlord_tapped += survivors
    if unblocked_player:
        defender.life -= OVERLORD_POWER * unblocked_player
    if unblocked_jace and defender.jace_loyalty is not None:
        defender.jace_loyalty -= OVERLORD_POWER * unblocked_jace
    state.pending_combat = None
    _check_state_based(state)
    if state.winner is None:
        _begin_postcombat_main(state)


def _apply_choice_action(state: GameState, action: Action, rng: Random) -> None:
    pc = state.pending_choice
    assert pc is not None
    player = state.players[pc.player]
    if pc.kind in {"discard", "cleanup_discard"}:
        discard = str(action.params["discard"])
        _remove_from_hand(player, discard)
        player.graveyard[discard] += 1
        if pc.kind == "cleanup_discard":
            if player.total_hand() > MAX_HAND_SIZE:
                state.pending_choice = PendingChoice(pc.player, "cleanup_discard", pc.data)
            else:
                state.pending_choice = None
                _advance_to_next_turn(state)
            return
        remaining = int(pc.data.get("remaining", 1)) - 1
        resume = str(pc.data.get("resume", "MAIN"))
        triggers_remaining = int(pc.data.get("overlord_triggers_remaining", 0))
        if remaining > 0:
            next_data = {"remaining": remaining, "resume": resume}
            if triggers_remaining:
                next_data["overlord_triggers_remaining"] = triggers_remaining
            state.pending_choice = PendingChoice(pc.player, "discard", next_data)
            return
        state.pending_choice = None
        if triggers_remaining > 0:
            _begin_overlord_trigger_sequence(state, pc.player, trigger_count=triggers_remaining, resume=resume)
            return
        if resume == "BLOCK_OR_DAMAGE":
            _after_attack_triggers(state)
        else:
            state.frame = resume
        return
    if pc.kind == "jace_plus2":
        target_idx = int(pc.data["target_player"])
        put = str(action.params.get("put"))
        if put == "bottom" and state.players[target_idx].library:
            card = state.players[target_idx].library.pop()
            state.players[target_idx].library.insert(0, card)
            _clear_known_top(state, target_idx)
        elif put == "leave" and state.players[target_idx].library:
            seen = pc.data.get("seen_top_card")
            if isinstance(seen, str):
                _set_known_top(state, observer=pc.player, target_player=target_idx, card=seen)
        _public_event(state, "JACE_PLUS2_ORDER", player=pc.player, target_player=target_idx, put=put)
        state.pending_choice = None
        state.frame = str(pc.data.get("resume", "MAIN"))
        return
    if pc.kind == "jace_brainstorm_putback":
        first = str(action.params["first_draw"])
        second = str(action.params["second_draw"])
        _remove_from_hand(player, first)
        _remove_from_hand(player, second)
        # top is list[-1], so append second first and first last.
        player.library.append(second)
        player.library.append(first)
        _clear_known_top(state, pc.player)
        _set_known_top(state, observer=pc.player, target_player=pc.player, card=first)
        _private_event(state, pc.player, "JACE_BRAINSTORM_PUTBACK", top_card=first, second_card=second)
        _public_event(state, "JACE_ZERO_PUTBACK", player=pc.player, count=2)
        state.pending_choice = None
        state.frame = str(pc.data.get("resume", "MAIN"))
        return
    if pc.kind == "jace_legend":
        # The new Jace was temporarily installed when the spell resolved. Keeping old restores old loyalty.
        if action.params.get("keep") == "old":
            player.jace_loyalty = int(pc.data["old_loyalty"])
            player.jace_used_this_turn = bool(pc.data.get("old_used", False))
        else:
            player.jace_loyalty = int(pc.data["new_loyalty"])
            player.jace_used_this_turn = False
        player.graveyard[CARD_JACE] += 1
        state.pending_choice = None
        if state.stack:
            state.frame = "RESPONSE"
            state.priority_player = state.active_player
            state.consecutive_passes = 0
        else:
            state.frame = state.pre_stack_frame
            state.priority_player = None
            state.consecutive_passes = 0
        return


def _check_state_based(state: GameState) -> None:
    for idx, p in enumerate(state.players):
        if p.life <= 0 and state.winner is None:
            state.winner = _other(idx)
            state.loss_reason = f"player_{idx}_life_total_zero_or_less"
            state.frame = "GAME_OVER"
        if p.jace_loyalty is not None and p.jace_loyalty <= 0:
            p.graveyard[CARD_JACE] += 1
            p.jace_loyalty = None
            p.jace_used_this_turn = False


def choose_random_action(state: GameState, rng: Random) -> Action:
    actions = legal_actions(state)
    if not actions:
        raise ValueError("no legal actions")
    return rng.choice(actions)


def play_random_game(
    deck0: DeckVector,
    deck1: DeckVector,
    seed: int = 1,
    max_decisions: int = 500,
    starting_life: int = STARTING_LIFE,
    mulligan_policy: str | MulliganPolicy | None = None,
) -> GameState:
    rng = Random(seed)
    state = start_game(deck0, deck1, seed=seed, starting_player=0, starting_life=starting_life, mulligan_policy=mulligan_policy)
    for _ in range(max_decisions):
        if state.winner is not None:
            break
        action = choose_random_action(state, rng)
        apply_action(state, action, rng, validate=False)
    if state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    return state
