from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_ORDER, CARD_OVERLORD

PENDING_KIND_ORDER = [
    "none",
    "discard",
    "cleanup_discard",
    "jace_plus2",
    "jace_brainstorm_putback",
    "jace_legend",
]
FRAME_ORDER = ["MAIN", "RESPONSE", "ATTACK", "BLOCK", "GAME_OVER"]
MAIN_PHASE_ORDER = ["precombat", "postcombat"]


def _one_hot(value: str, choices: Iterable[str]) -> Dict[str, float]:
    return {f"{value_name}_{choice}": 1.0 if value == choice else 0.0 for value_name, choice in [("is", c) for c in choices]}


def public_player_features(prefix: str, public: Dict[str, object]) -> Dict[str, float]:
    graveyard = public.get("graveyard", {}) or {}
    out: Dict[str, float] = {
        f"{prefix}_life": float(public.get("life", 0) or 0),
        f"{prefix}_library_count": float(public.get("library_count", 0) or 0),
        f"{prefix}_hand_count": float(public.get("hand_count", 0) or 0),
        f"{prefix}_mulligans_taken": float(public.get("mulligans_taken", 0) or 0),
        f"{prefix}_islands_untapped": float(public.get("islands_untapped", 0) or 0),
        f"{prefix}_islands_tapped": float(public.get("islands_tapped", 0) or 0),
        f"{prefix}_jace_loyalty": float(public.get("jace_loyalty") or 0),
        f"{prefix}_jace_present": 1.0 if public.get("jace_loyalty") is not None else 0.0,
        f"{prefix}_jace_used": 1.0 if public.get("jace_used_this_turn") else 0.0,
        f"{prefix}_overlord_ready": float(public.get("overlord_ready", 0) or 0),
        f"{prefix}_overlord_sick": float(public.get("overlord_sick", 0) or 0),
        f"{prefix}_overlord_tapped": float(public.get("overlord_tapped", 0) or 0),
        f"{prefix}_impending_4": float(public.get("impending_4", 0) or 0),
        f"{prefix}_impending_3": float(public.get("impending_3", 0) or 0),
        f"{prefix}_impending_2": float(public.get("impending_2", 0) or 0),
        f"{prefix}_impending_1": float(public.get("impending_1", 0) or 0),
        f"{prefix}_exile_count": float(public.get("exile_count", 0) or 0),
    }
    for card in CARD_ORDER:
        out[f"{prefix}_graveyard_{card}"] = float(graveyard.get(card, 0))
    return out


def observation_feature_dict(obs: Dict[str, object]) -> Dict[str, float]:
    """Encode a hidden-information observation as a stable numeric feature dictionary.

    This is deliberately simple. It is not meant to be the final neural representation;
    it is a stable baseline for heuristic agents, tabular audits, and tiny MLP pilots.
    """
    out: Dict[str, float] = {
        "player": float(obs.get("player", 0) or 0),
        "active_player": float(obs.get("active_player", 0) or 0),
        "to_act": float(obs.get("to_act", 0) or 0),
        "turn_number": float(obs.get("turn_number", 0) or 0),
        "starting_life": float(obs.get("starting_life", 20) or 20),
        "own_library_count": float(obs.get("own_library_count", 0) or 0),
    }
    frame = str(obs.get("frame", "MAIN"))
    main_phase = str(obs.get("main_phase", "precombat"))
    for choice in FRAME_ORDER:
        out[f"frame_{choice}"] = 1.0 if frame == choice else 0.0
    for choice in MAIN_PHASE_ORDER:
        out[f"main_phase_{choice}"] = 1.0 if main_phase == choice else 0.0

    hand = obs.get("own_hand", {}) or {}
    for card in CARD_ORDER:
        out[f"own_hand_{card}"] = float(hand.get(card, 0))

    self_public = obs.get("public_self", {}) or {}
    opp_public = obs.get("public_opponent", {}) or {}
    out.update(public_player_features("self", self_public))
    out.update(public_player_features("opp", opp_public))
    starting_life = float(obs.get("starting_life", 20) or 20)
    out["self_life_fraction"] = float(self_public.get("life", 0) or 0) / max(1.0, starting_life)
    out["opp_life_fraction"] = float(opp_public.get("life", 0) or 0) / max(1.0, starting_life)

    stack = obs.get("stack", []) or []
    out["stack_len"] = float(len(stack))
    for card in CARD_ORDER:
        out[f"stack_{card}"] = float(sum(1 for s in stack if s.get("card") == card))

    kind = str(obs.get("pending_choice_kind") or "none")
    for choice in PENDING_KIND_ORDER:
        out[f"pending_{choice}"] = 1.0 if kind == choice else 0.0
    return out


def feature_names() -> List[str]:
    # Build from a small canonical blank observation so downstream code has stable columns.
    blank_public = {
        "life": 20,
        "library_count": 0,
        "hand_count": 0,
        "mulligans_taken": 0,
        "graveyard": {},
        "exile_count": 0,
        "islands_untapped": 0,
        "islands_tapped": 0,
        "jace_loyalty": None,
        "jace_used_this_turn": False,
        "overlord_ready": 0,
        "overlord_sick": 0,
        "overlord_tapped": 0,
        "impending_4": 0,
        "impending_3": 0,
        "impending_2": 0,
        "impending_1": 0,
    }
    blank_obs = {
        "player": 0,
        "active_player": 0,
        "to_act": 0,
        "frame": "MAIN",
        "main_phase": "precombat",
        "turn_number": 1,
        "starting_life": 20,
        "own_hand": {},
        "own_library_count": 0,
        "public_self": blank_public,
        "public_opponent": blank_public,
        "stack": [],
        "pending_choice_kind": None,
    }
    return sorted(observation_feature_dict(blank_obs).keys())


def observation_vector(obs: Dict[str, object]) -> Tuple[List[float], List[str]]:
    fd = observation_feature_dict(obs)
    names = feature_names()
    return [float(fd.get(name, 0.0)) for name in names], names
