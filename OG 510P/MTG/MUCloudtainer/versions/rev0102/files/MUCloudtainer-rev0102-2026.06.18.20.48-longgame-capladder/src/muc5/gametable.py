from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from random import Random
from typing import Dict, List, Optional, Sequence, Tuple
import pickle

from .action_schema import Action
from .agents import Agent, HeuristicAgent, RandomAgent, make_agent
from .cards import CARD_ORDER, CARD_SPECS, STARTING_LIFE, validate_starting_life
from .deckspace import DeckVector
from .engine import GameState, apply_action, legal_actions, start_game
from .mulligan import MulliganAgent, MulliganPolicy, RuleMulliganAgent


EXTERNAL_SEAT = "external"


@dataclass(frozen=True)
class SeatSpec:
    """A table seat: either an external chooser or a named in-process agent."""

    kind: str
    name: str
    agent: Optional[Agent] = None

    @classmethod
    def external(cls, name: str = "assistant_external") -> "SeatSpec":
        return cls(EXTERNAL_SEAT, name, None)

    @classmethod
    def from_agent_name(cls, name: str) -> "SeatSpec":
        return cls("agent", name, make_agent(name))

    @property
    def is_external(self) -> bool:
        return self.kind == EXTERNAL_SEAT


@dataclass
class TableSnapshot:
    """Compact machine-readable frame for an external seat.

    This is deliberately smaller than full GameState serialization. It is the object
    a future ChatGPT/LLM/remote controller should read before choosing an action slot.
    """

    terminal: bool
    external_to_act: bool
    current_player: int
    perspective_player: int
    frame: str
    main_phase: str
    turn_number: int
    starting_life: int
    winner: Optional[int]
    loss_reason: str
    legal_actions: List[str]
    public: Dict[str, object]
    own_hand: Dict[str, int]
    stack: List[Dict[str, object]]
    pending_choice_kind: Optional[str]
    transcript_tail: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "terminal": self.terminal,
            "external_to_act": self.external_to_act,
            "current_player": self.current_player,
            "perspective_player": self.perspective_player,
            "frame": self.frame,
            "main_phase": self.main_phase,
            "turn_number": self.turn_number,
            "starting_life": self.starting_life,
            "winner": self.winner,
            "loss_reason": self.loss_reason,
            "legal_actions": self.legal_actions,
            "public": self.public,
            "own_hand": self.own_hand,
            "stack": self.stack,
            "pending_choice_kind": self.pending_choice_kind,
            "transcript_tail": self.transcript_tail,
        }


@dataclass
class MUC5GameTable:
    """Assistant-facing gametable around the MUC-5 referee.

    The table has two modes of control:
    - named agents act automatically;
    - an external seat stops at decision frames and exposes a numbered menu.

    This is not a polished human UI. It is a small protocol for letting an outside
    chooser, including this assistant in later turns, play legal MUC-5 actions.
    """

    deck0: DeckVector
    deck1: DeckVector
    seats: Tuple[SeatSpec, SeatSpec]
    seed: int = 1
    starting_player: int = 0
    starting_life: int = STARTING_LIFE
    mulligan_agents: Tuple[MulliganAgent | str | MulliganPolicy | None, MulliganAgent | str | MulliganPolicy | None] | None = None
    mulligan_policy: str | MulliganPolicy | None = None
    max_decisions: int = 500
    state: Optional[GameState] = None
    rng: Random = field(default_factory=lambda: Random(1))
    decisions: int = 0
    table_log: List[str] = field(default_factory=list)

    def start(self) -> "MUC5GameTable":
        self.starting_life = validate_starting_life(self.starting_life)
        self.rng = Random(self.seed)
        if self.mulligan_agents is not None:
            mg_agents = self.mulligan_agents
            mg_policy = None
        else:
            # External seats still get explicit, logged mulligan decisions through
            # simple rule agents for now; interactive external mulligan menus are a
            # later revision target.
            mg_agents = tuple(RuleMulliganAgent(self.mulligan_policy) for _ in range(2))  # type: ignore[assignment]
            mg_policy = None
        self.state = start_game(
            self.deck0,
            self.deck1,
            seed=self.seed,
            starting_player=self.starting_player,
            starting_life=self.starting_life,
            mulligan_agents=mg_agents,
            mulligan_policy=mg_policy,
        )
        self.decisions = 0
        start_event = f"TABLE_START seed={self.seed} starting_player={self.starting_player} starting_life={self.starting_life} seats={[s.name for s in self.seats]}"
        self.table_log.append(start_event)
        self.state.log.append(start_event)
        self.autoplay_until_external_or_terminal()
        return self

    def require_state(self) -> GameState:
        if self.state is None:
            raise RuntimeError("table has not been started")
        return self.state

    def current_seat(self) -> SeatSpec:
        state = self.require_state()
        return self.seats[state.current_player()]

    def is_terminal(self) -> bool:
        state = self.require_state()
        return state.winner is not None or state.frame == "GAME_OVER"

    def external_to_act(self) -> bool:
        if self.is_terminal():
            return False
        return self.current_seat().is_external

    def legal_menu(self) -> List[Action]:
        return legal_actions(self.require_state())

    def autoplay_until_external_or_terminal(self) -> None:
        state = self.require_state()
        while not self.is_terminal() and not self.current_seat().is_external:
            if self.decisions >= self.max_decisions:
                state.frame = "GAME_OVER"
                state.loss_reason = "max_decisions_reached"
                self.table_log.append("TABLE_STOP max_decisions_reached")
                state.log.append("TABLE_STOP max_decisions_reached")
                break
            actor = state.current_player()
            seat = self.seats[actor]
            assert seat.agent is not None
            action = seat.agent.choose_action(state, self.rng)
            event = f"AUTO player={actor} seat={seat.name} action={action.compact()}"
            self.table_log.append(event)
            state.log.append(event)
            apply_action(state, action, self.rng)
            self.decisions += 1

    def apply_external_action(self, action_index: int) -> TableSnapshot:
        state = self.require_state()
        if not self.external_to_act():
            raise RuntimeError("external seat is not currently to act")
        actions = legal_actions(state)
        if action_index < 0 or action_index >= len(actions):
            raise ValueError(f"action_index {action_index} outside legal range 0..{len(actions)-1}")
        actor = state.current_player()
        action = actions[action_index]
        event = f"EXTERNAL player={actor} seat={self.seats[actor].name} action={action.compact()}"
        self.table_log.append(event)
        state.log.append(event)
        apply_action(state, action, self.rng)
        self.decisions += 1
        self.autoplay_until_external_or_terminal()
        return self.snapshot()

    def snapshot(self, perspective_player: Optional[int] = None, *, transcript_tail: int = 8) -> TableSnapshot:
        state = self.require_state()
        if perspective_player is None:
            if self.external_to_act():
                perspective_player = state.current_player()
            else:
                # Terminal/non-external views default to player 0 for deterministic output.
                perspective_player = 0
        obs = state.observation(perspective_player)
        public = {
            "self": obs["public_self"],
            "opponent": obs["public_opponent"],
            "active_player": obs["active_player"],
            "to_act": obs["to_act"],
        }
        actions = [] if self.is_terminal() else [a.compact() for a in legal_actions(state)]
        return TableSnapshot(
            terminal=self.is_terminal(),
            external_to_act=self.external_to_act(),
            current_player=state.current_player(),
            perspective_player=perspective_player,
            frame=state.frame,
            main_phase=state.main_phase,
            turn_number=state.turn_number,
            starting_life=state.starting_life,
            winner=state.winner,
            loss_reason=state.loss_reason,
            legal_actions=actions,
            public=public,
            own_hand={card: int(obs["own_hand"].get(card, 0)) for card in CARD_ORDER if obs["own_hand"].get(card, 0)},
            stack=list(obs.get("stack", [])),
            pending_choice_kind=obs.get("pending_choice_kind"),
            transcript_tail=state.log[-transcript_tail:],
        )

    def render_markdown(self, perspective_player: Optional[int] = None, *, reveal_hidden: bool = False, transcript_tail: int = 8) -> str:
        state = self.require_state()
        snap = self.snapshot(perspective_player, transcript_tail=transcript_tail)
        p = snap.perspective_player
        opp = 1 - p
        lines: List[str] = []
        lines.append(f"# MUC-5 GameTable — turn {snap.turn_number}, frame {snap.frame}/{snap.main_phase}")
        lines.append("")
        lines.append(f"Perspective: player {p} ({self.seats[p].name}); opponent player {opp} ({self.seats[opp].name})")
        lines.append(f"Starting life: {snap.starting_life}; current actor: player {snap.current_player}; external_to_act: {snap.external_to_act}")
        if snap.terminal:
            lines.append(f"Terminal: winner={snap.winner}, reason={snap.loss_reason}")
        lines.append("")
        lines.append("## Public table")
        lines.append(_render_public_player("You", state.players[p]))
        lines.append(_render_public_player("Opponent", state.players[opp]))
        if reveal_hidden:
            lines.append("")
            lines.append("## Hidden debug reveal")
            lines.append(f"Opponent hand: {_format_counts(state.players[opp].hand)}")
            lines.append(f"Opponent top library sample: {list(reversed(state.players[opp].library[-5:]))}")
        lines.append("")
        lines.append("## Your hand")
        lines.append(_format_counts(state.players[p].hand) or "(empty)")
        if state.stack:
            lines.append("")
            lines.append("## Stack")
            for spell in reversed(state.stack):
                lines.append(f"- id={spell.spell_id} controller=P{spell.controller} card={spell.card} mode={spell.mode} params={spell.params}")
        if state.pending_choice is not None:
            lines.append("")
            if state.pending_choice.player == p or reveal_hidden:
                pending_data = state.pending_choice.data
            else:
                pending_data = {"redacted": True}
            lines.append(f"Pending choice: player={state.pending_choice.player} kind={state.pending_choice.kind} data={pending_data}")
        lines.append("")
        lines.append("## Legal actions")
        if snap.terminal:
            lines.append("(none; game is over)")
        else:
            for i, action in enumerate(legal_actions(state)):
                lines.append(f"{i}. `{action.compact()}`")
        lines.append("")
        lines.append("## Transcript tail")
        tail = state.log[-transcript_tail:]
        if not tail:
            lines.append("(no events yet)")
        else:
            for item in tail:
                lines.append(f"- {item}")
        return "\n".join(lines) + "\n"



def _format_counts(counts: Dict[str, int]) -> str:
    parts: List[str] = []
    for card in CARD_ORDER:
        n = int(counts.get(card, 0))
        if n:
            display = CARD_SPECS[card].display_name
            parts.append(f"{display}×{n}")
    return ", ".join(parts)



def _render_public_player(label: str, player) -> str:  # PlayerState, kept unannotated to avoid import cycle noise in docs.
    pieces = [
        f"life={player.life}",
        f"hand={player.total_hand()}",
        f"library={len(player.library)}",
        f"mulligans={player.mulligans_taken}",
        f"islands={player.islands_untapped} untapped/{player.islands_tapped} tapped",
        f"jace={player.jace_loyalty if player.jace_loyalty is not None else '-'}",
        f"overlords=ready {player.overlord_ready}, sick {player.overlord_sick}, tapped {player.overlord_tapped}",
        f"impending=4:{player.impending_4} 3:{player.impending_3} 2:{player.impending_2} 1:{player.impending_1}",
        f"graveyard={_format_counts(player.graveyard) or '-'}",
        f"exile_count={sum(player.exile.values())}",
    ]
    return f"- **{label}:** " + "; ".join(pieces)



def save_table(table: MUC5GameTable, path: str | Path) -> None:
    with Path(path).open("wb") as f:
        pickle.dump(table, f)



def load_table(path: str | Path) -> MUC5GameTable:
    with Path(path).open("rb") as f:
        obj = pickle.load(f)
    if not isinstance(obj, MUC5GameTable):
        raise TypeError(f"pickle did not contain MUC5GameTable: {type(obj)!r}")
    return obj
