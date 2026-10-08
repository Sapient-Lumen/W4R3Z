from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .action_schema import Action
from .agent_lifecycle import EpisodeContext, EpisodeResult, end_episode, require_distinct_seat_objects, reset_episode
from .decision import PublicDecisionAgent, build_decision_frame, apply_decision_index
from .deckspace import DeckVector
from .engine import GameState, start_game
from .mulligan import MulliganAgent, MulliganPolicy
from .mulligan_ranker import make_mulligan_agent


def _counter_dict(counter: Counter[str] | Mapping[str, int]) -> Dict[str, int]:
    return {str(k): int(v) for k, v in sorted(counter.items()) if int(v) != 0}


def deck_to_json(deck: DeckVector) -> Dict[str, int]:
    return {
        "size": int(deck.size),
        "Island": int(deck.island),
        "Counterspell": int(deck.counterspell),
        "ForceOfWill": int(deck.force),
        "JaceTheMindSculptor": int(deck.jace),
        "OverlordOfTheFloodpits": int(deck.overlord),
    }


def deck_from_json(payload: Mapping[str, Any]) -> DeckVector:
    deck = DeckVector(
        int(payload["size"]),
        int(payload.get("Island", 0)),
        int(payload.get("Counterspell", 0)),
        int(payload.get("ForceOfWill", 0)),
        int(payload.get("JaceTheMindSculptor", 0)),
        int(payload.get("OverlordOfTheFloodpits", 0)),
    )
    deck.validate()
    return deck


def action_to_json(action: Action) -> Dict[str, Any]:
    return {"kind": action.kind, "params": dict(action.params), "compact": action.compact()}


def canonical_state_snapshot(state: GameState, *, include_private: bool = True) -> Dict[str, Any]:
    """Canonical, JSON-serializable snapshot for deterministic replay hashing.

    This is intentionally not an agent observation. It is an omniscient referee
    checksum used by audits, traces, and reproducibility tests. The snapshot is
    stable across equivalent Counter insertion orders but preserves library and
    stack order where order matters.
    """

    def player_snapshot(p) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "life": int(p.life),
            "mulligans_taken": int(p.mulligans_taken),
            "library_count": len(p.library),
            "hand": _counter_dict(p.hand),
            "graveyard": _counter_dict(p.graveyard),
            "exile": _counter_dict(p.exile),
            "islands_untapped": int(p.islands_untapped),
            "islands_tapped": int(p.islands_tapped),
            "jace_loyalty": None if p.jace_loyalty is None else int(p.jace_loyalty),
            "jace_used_this_turn": bool(p.jace_used_this_turn),
            "overlord_ready": int(p.overlord_ready),
            "overlord_sick": int(p.overlord_sick),
            "overlord_tapped": int(p.overlord_tapped),
            "impending_4": int(p.impending_4),
            "impending_3": int(p.impending_3),
            "impending_2": int(p.impending_2),
            "impending_1": int(p.impending_1),
        }
        if include_private:
            payload["library"] = list(p.library)
        return payload

    pending_choice = None
    if state.pending_choice is not None:
        pending_choice = {
            "player": int(state.pending_choice.player),
            "kind": str(state.pending_choice.kind),
            "data": _canonical_jsonable(state.pending_choice.data),
        }
    pending_combat = None
    if state.pending_combat is not None:
        pending_combat = {
            "attacker": int(state.pending_combat.attacker),
            "defender": int(state.pending_combat.defender),
            "to_player": int(state.pending_combat.to_player),
            "to_jace": int(state.pending_combat.to_jace),
        }

    return {
        "players": [player_snapshot(p) for p in state.players],
        "revision": int(state.revision),
        "starting_life": int(state.starting_life),
        "active_player": int(state.active_player),
        "priority_player": state.priority_player,
        "frame": state.frame,
        "main_phase": state.main_phase,
        "stack": [
            {
                "spell_id": int(s.spell_id),
                "controller": int(s.controller),
                "card": s.card,
                "mode": s.mode,
                "params": _canonical_jsonable(s.params),
            }
            for s in state.stack
        ],
        "pending_choice": pending_choice,
        "pending_combat": pending_combat,
        "land_played_this_turn": bool(state.land_played_this_turn),
        "turn_number": int(state.turn_number),
        "consecutive_passes": int(state.consecutive_passes),
        "next_spell_id": int(state.next_spell_id),
        "winner": state.winner,
        "loss_reason": state.loss_reason,
        "pre_stack_frame": state.pre_stack_frame,
        "starting_deck_counts": _canonical_jsonable(state.starting_deck_counts),
    }


def _canonical_jsonable(value: Any) -> Any:
    if isinstance(value, Counter):
        return _counter_dict(value)
    if isinstance(value, Mapping):
        return {str(k): _canonical_jsonable(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical_jsonable(v) for v in value]
    return value


def state_fingerprint(state: GameState, *, include_private: bool = True) -> str:
    payload = canonical_state_snapshot(state, include_private=include_private)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def observation_fingerprint(observation: Mapping[str, Any]) -> str:
    encoded = json.dumps(_canonical_jsonable(observation), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def information_state_fingerprint(information_state: Mapping[str, Any]) -> str:
    encoded = json.dumps(_canonical_jsonable(information_state), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReplayResult:
    passed: bool
    checked_steps: int
    final_fingerprint: str
    final_winner: int | None
    final_loss_reason: str
    errors: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "checked_steps": self.checked_steps,
            "final_fingerprint": self.final_fingerprint,
            "final_winner": self.final_winner,
            "final_loss_reason": self.final_loss_reason,
            "errors": list(self.errors),
        }


def record_public_decision_trace(
    deck0: DeckVector,
    deck1: DeckVector,
    agent0: PublicDecisionAgent,
    agent1: PublicDecisionAgent,
    *,
    seed: int = 1,
    transition_seed: int | None = None,
    agent_seed: int | None = None,
    starting_player: int = 0,
    starting_life: int = 20,
    max_decisions: int = 500,
    mulligan_policy: str | MulliganPolicy | None = None,
    mulligan_policies: Tuple[str | MulliganPolicy | None, str | MulliganPolicy | None] | None = None,
    mulligan_agents: Tuple[object | str | MulliganPolicy | None, object | str | MulliganPolicy | None] | None = None,
) -> Dict[str, Any]:
    """Record a replayable public-DecisionFrame game trace.

    The trace path deliberately separates agent tie-break randomness from state
    transition randomness. That prevents a replay from depending on how many
    random numbers an agent consumed while ranking legal actions.
    """

    require_distinct_seat_objects(agent0, agent1)
    transition_seed = seed if transition_seed is None else int(transition_seed)
    agent_seed = seed + 1000003 if agent_seed is None else int(agent_seed)
    state_rng = Random(transition_seed)
    agent_rng = Random(agent_seed)
    episode_id = "trace-" + hashlib.sha256(
        f"{seed}|{transition_seed}|{agent_seed}|{starting_player}|{starting_life}|{max_decisions}".encode("utf-8")
    ).hexdigest()[:20]
    contexts = (
        EpisodeContext(episode_id, 0, int(starting_player), int(starting_life)),
        EpisodeContext(episode_id, 1, int(starting_player), int(starting_life)),
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
        record_log=False,
    )
    agents = [agent0, agent1]
    events: List[Dict[str, Any]] = []
    for step in range(1, max_decisions + 1):
        if state.winner is not None:
            break
        frame = build_decision_frame(state)
        if frame.action_count <= 0:
            break
        pre_hash = state_fingerprint(state)
        obs_hash = observation_fingerprint(frame.observation)
        info_hash = information_state_fingerprint(frame.information_state)
        action_index = agents[frame.player].choose_action_index(frame, agent_rng)
        if action_index < 0 or action_index >= frame.action_count:
            raise ValueError(f"agent chose illegal index {action_index} for {frame.action_count} actions")
        chosen = frame.legal_actions[action_index]
        apply_decision_index(state, frame, action_index, state_rng)
        post_hash = state_fingerprint(state)
        events.append(
            {
                "step": step,
                "player": int(frame.player),
                "state_revision": int(frame.state_revision),
                "pre_fingerprint": pre_hash,
                "observation_fingerprint": obs_hash,
                "information_state_fingerprint": info_hash,
                "information_state_schema": str(frame.information_state.get("schema", "")),
                "public_event_seq": int(frame.information_state.get("event_seq", 0)),
                "legal_action_count": int(frame.action_count),
                "legal_actions": list(frame.legal_action_strings),
                "action_index": int(action_index),
                "action": action_to_json(chosen),
                "post_fingerprint": post_hash,
                "post_revision": int(state.revision),
            }
        )
    truncated = state.winner is None and len(events) >= max_decisions
    if truncated:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    decisions = int(len(events))
    for player, agent in enumerate((agent0, agent1)):
        score = 0.5 if state.winner is None else (1.0 if state.winner == player else 0.0)
        end_episode(
            agent,
            EpisodeResult(episode_id, player, score, state.winner, state.loss_reason, decisions),
        )
    if mulligan_agents is not None:
        for player, mulligan_agent in enumerate(mulligan_agents):
            if mulligan_agent is not None and not isinstance(mulligan_agent, (str, MulliganPolicy)):
                score = 0.5 if state.winner is None else (1.0 if state.winner == player else 0.0)
                end_episode(
                    mulligan_agent,
                    EpisodeResult(episode_id, player, score, state.winner, state.loss_reason, decisions),
                )
    return {
        "schema": "muc5.public_decision_trace.v1",
        "simulator_revision_min": "rev0011",
        "config": {
            "deck0": deck_to_json(deck0),
            "deck1": deck_to_json(deck1),
            "seed": int(seed),
            "transition_seed": int(transition_seed),
            "agent_seed": int(agent_seed),
            "starting_player": int(starting_player),
            "starting_life": int(starting_life),
            "max_decisions": int(max_decisions),
            "mulligan_policy": None if mulligan_policy is None else str(mulligan_policy),
            "mulligan_policies": None if mulligan_policies is None else [None if p is None else str(p) for p in mulligan_policies],
            "mulligan_agents": None if mulligan_agents is None else [None if a is None else getattr(a, "name", str(a)) for a in mulligan_agents],
            "agent0": getattr(agent0, "name", type(agent0).__name__),
            "agent1": getattr(agent1, "name", type(agent1).__name__),
        },
        "initial_fingerprint": events[0]["pre_fingerprint"] if events else state_fingerprint(state),
        "events": events,
        "final": {
            "fingerprint": state_fingerprint(state),
            "winner": state.winner,
            "loss_reason": state.loss_reason,
            "truncated": bool(truncated),
            "decisions": int(len(events)),
            "turn_number": int(state.turn_number),
        },
    }


def replay_public_decision_trace(trace: Mapping[str, Any]) -> ReplayResult:
    cfg = trace["config"]
    deck0 = deck_from_json(cfg["deck0"])
    deck1 = deck_from_json(cfg["deck1"])
    state_rng = Random(int(cfg.get("transition_seed", cfg["seed"])))
    mulligan_policies_payload = cfg.get("mulligan_policies")
    mulligan_policies = None
    if mulligan_policies_payload is not None:
        mulligan_policies = tuple(mulligan_policies_payload)  # type: ignore[assignment]
    mulligan_agents_payload = cfg.get("mulligan_agents")
    mulligan_agents = None
    if mulligan_agents_payload is not None:
        mulligan_agents = tuple(make_mulligan_agent(a) for a in mulligan_agents_payload)  # type: ignore[assignment]
    state = start_game(
        deck0,
        deck1,
        seed=int(cfg["seed"]),
        starting_player=int(cfg["starting_player"]),
        starting_life=int(cfg["starting_life"]),
        mulligan_policy=cfg.get("mulligan_policy"),
        mulligan_policies=mulligan_policies,  # type: ignore[arg-type]
        mulligan_agents=mulligan_agents,  # type: ignore[arg-type]
        record_log=False,
    )
    errors: List[str] = []
    events = list(trace.get("events", []))
    for i, event in enumerate(events):
        frame = build_decision_frame(state)
        pre_hash = state_fingerprint(state)
        if pre_hash != event.get("pre_fingerprint"):
            errors.append(f"step {i+1}: pre_fingerprint mismatch got={pre_hash} expected={event.get('pre_fingerprint')}")
            break
        if "information_state_fingerprint" in event:
            info_hash = information_state_fingerprint(frame.information_state)
            if info_hash != event.get("information_state_fingerprint"):
                errors.append(f"step {i+1}: information_state_fingerprint mismatch got={info_hash} expected={event.get('information_state_fingerprint')}")
                break
        legal_strings = list(frame.legal_action_strings)
        if legal_strings != list(event.get("legal_actions", [])):
            errors.append(f"step {i+1}: legal action list mismatch")
            break
        action_index = int(event["action_index"])
        if action_index < 0 or action_index >= frame.action_count:
            errors.append(f"step {i+1}: action_index outside legal range")
            break
        if frame.legal_action_strings[action_index] != event.get("action", {}).get("compact"):
            errors.append(f"step {i+1}: chosen action compact mismatch")
            break
        apply_decision_index(state, frame, action_index, state_rng)
        post_hash = state_fingerprint(state)
        if post_hash != event.get("post_fingerprint"):
            errors.append(f"step {i+1}: post_fingerprint mismatch got={post_hash} expected={event.get('post_fingerprint')}")
            break
    final_payload = trace.get("final", {})
    if final_payload.get("truncated") and state.winner is None:
        state.frame = "GAME_OVER"
        state.loss_reason = "max_decisions_reached"
    expected_final = final_payload.get("fingerprint")
    final_hash = state_fingerprint(state)
    if not errors and expected_final and final_hash != expected_final:
        errors.append(f"final fingerprint mismatch got={final_hash} expected={expected_final}")
    return ReplayResult(
        passed=not errors,
        checked_steps=(len(events) if not errors else max(0, i)),
        final_fingerprint=final_hash,
        final_winner=state.winner,
        final_loss_reason=state.loss_reason,
        errors=tuple(errors),
    )


def write_trace_jsonl(traces: Iterable[Mapping[str, Any]], path: str | Path) -> None:
    p = Path(path)
    with p.open("w") as f:
        for trace in traces:
            f.write(json.dumps(trace, sort_keys=True) + "\n")


def read_trace_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    with p.open() as f:
        return [json.loads(line) for line in f if line.strip()]
