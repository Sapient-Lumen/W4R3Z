from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from .action_schema import Action
from .cards import CARD_COUNTERSPELL, CARD_FORCE, CARD_ISLAND, CARD_JACE, CARD_OVERLORD
from .decision import DecisionFrame

CARD_FEATURE_ORDER = (CARD_ISLAND, CARD_COUNTERSPELL, CARD_FORCE, CARD_JACE, CARD_OVERLORD)
ACTION_FEATURE_NAMES: tuple[str, ...] = (
    # kind one-hots
    "kind_pass", "kind_play_island", "kind_cast", "kind_activate_jace", "kind_attack", "kind_block", "kind_choose_for_effect",
    # cast card one-hots
    "cast_counterspell", "cast_force", "cast_jace", "cast_overlord",
    # force/payment flags
    "payment_mana", "payment_pitch", "pitch_counterspell", "pitch_force", "pitch_jace", "pitch_overlord",
    # target-card flags
    "target_counterspell", "target_force", "target_jace", "target_overlord",
    # Jace modes
    "jace_plus2", "jace_zero", "jace_minus1", "jace_ultimate",
    # Overlord modes
    "overlord_full", "overlord_impending",
    # choice effects
    "choose_discard", "choose_force_pitch", "choose_jace_plus2", "choose_jace_brainstorm", "choose_jace_legend",
    # choice card one-hots
    "choice_island", "choice_counterspell", "choice_force", "choice_jace", "choice_overlord",
    # numeric slots, normalized/clipped by small constants
    "attack_to_player_norm", "attack_to_jace_norm", "block_player_norm", "block_jace_norm",
    "target_state_ready", "target_state_sick", "target_state_tapped",
    "is_pass_main", "is_pass_response",
)


def action_feature_names() -> tuple[str, ...]:
    return ACTION_FEATURE_NAMES


def _clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _card_flag(card: str, target: str) -> float:
    return 1.0 if card == target else 0.0


def action_feature_dict(action: Action, observation: Dict[str, object] | None = None) -> Dict[str, float]:
    """Stable public action features for imitation/ranking/neural prototypes.

    These features are derived only from the legal action object and optional
    public observation metadata such as the current frame. They are not meant to
    replace the action itself; they give future sandpeople a small listwise
    encoder that does not require parsing action strings ad hoc.
    """

    obs = observation or {}
    frame = str(obs.get("frame", ""))
    p = action.params
    kind = action.kind
    card = str(p.get("card", ""))
    target_card = str(p.get("target_card", ""))
    pitch_card = str(p.get("pitch_card", p.get("pitch", "")))
    mode = str(p.get("mode", ""))
    effect = str(p.get("effect", ""))
    choice_card = str(p.get("discard", p.get("card", p.get("pitch_card", ""))))
    target_state = str(p.get("target_state", ""))

    out = {name: 0.0 for name in ACTION_FEATURE_NAMES}
    out["kind_pass"] = 1.0 if kind == "PASS" else 0.0
    out["kind_play_island"] = 1.0 if kind == "PLAY_ISLAND" else 0.0
    out["kind_cast"] = 1.0 if kind == "CAST" else 0.0
    out["kind_activate_jace"] = 1.0 if kind == "ACTIVATE_JACE" else 0.0
    out["kind_attack"] = 1.0 if kind == "ATTACK" else 0.0
    out["kind_block"] = 1.0 if kind == "BLOCK" else 0.0
    out["kind_choose_for_effect"] = 1.0 if kind == "CHOOSE_FOR_EFFECT" else 0.0

    out["cast_counterspell"] = 1.0 if kind == "CAST" and card == CARD_COUNTERSPELL else 0.0
    out["cast_force"] = 1.0 if kind == "CAST" and card == CARD_FORCE else 0.0
    out["cast_jace"] = 1.0 if kind == "CAST" and card == CARD_JACE else 0.0
    out["cast_overlord"] = 1.0 if kind == "CAST" and card == CARD_OVERLORD else 0.0

    payment = str(p.get("payment", ""))
    out["payment_mana"] = 1.0 if payment == "mana" else 0.0
    out["payment_pitch"] = 1.0 if payment == "pitch" else 0.0
    out["pitch_counterspell"] = _card_flag(pitch_card, CARD_COUNTERSPELL)
    out["pitch_force"] = _card_flag(pitch_card, CARD_FORCE)
    out["pitch_jace"] = _card_flag(pitch_card, CARD_JACE)
    out["pitch_overlord"] = _card_flag(pitch_card, CARD_OVERLORD)

    out["target_counterspell"] = _card_flag(target_card, CARD_COUNTERSPELL)
    out["target_force"] = _card_flag(target_card, CARD_FORCE)
    out["target_jace"] = _card_flag(target_card, CARD_JACE)
    out["target_overlord"] = _card_flag(target_card, CARD_OVERLORD)

    out["jace_plus2"] = 1.0 if mode == "plus2" else 0.0
    out["jace_zero"] = 1.0 if mode == "zero" else 0.0
    out["jace_minus1"] = 1.0 if mode == "minus1" else 0.0
    out["jace_ultimate"] = 1.0 if mode == "ultimate" else 0.0
    out["overlord_full"] = 1.0 if kind == "CAST" and card == CARD_OVERLORD and mode in {"normal", "full", ""} else 0.0
    out["overlord_impending"] = 1.0 if kind == "CAST" and card == CARD_OVERLORD and mode == "impending" else 0.0

    out["choose_discard"] = 1.0 if effect in {"discard", "overlord_discard", "cleanup_discard"} else 0.0
    out["choose_force_pitch"] = 1.0 if effect == "force_pitch" else 0.0
    out["choose_jace_plus2"] = 1.0 if effect == "jace_plus2" else 0.0
    out["choose_jace_brainstorm"] = 1.0 if effect == "jace_brainstorm_putback" else 0.0
    out["choose_jace_legend"] = 1.0 if effect == "jace_legend" else 0.0
    out["choice_island"] = _card_flag(choice_card, CARD_ISLAND)
    out["choice_counterspell"] = _card_flag(choice_card, CARD_COUNTERSPELL)
    out["choice_force"] = _card_flag(choice_card, CARD_FORCE)
    out["choice_jace"] = _card_flag(choice_card, CARD_JACE)
    out["choice_overlord"] = _card_flag(choice_card, CARD_OVERLORD)

    out["attack_to_player_norm"] = _clip01(float(p.get("to_player", 0) or 0) / 4.0)
    out["attack_to_jace_norm"] = _clip01(float(p.get("to_jace", 0) or 0) / 4.0)
    out["block_player_norm"] = _clip01(float(p.get("block_player_attackers", p.get("block_player", 0)) or 0) / 4.0)
    out["block_jace_norm"] = _clip01(float(p.get("block_jace_attackers", p.get("block_jace", 0)) or 0) / 4.0)
    out["target_state_ready"] = 1.0 if target_state == "ready" else 0.0
    out["target_state_sick"] = 1.0 if target_state == "sick" else 0.0
    out["target_state_tapped"] = 1.0 if target_state == "tapped" else 0.0
    out["is_pass_main"] = 1.0 if kind == "PASS" and frame == "MAIN" else 0.0
    out["is_pass_response"] = 1.0 if kind == "PASS" and frame == "RESPONSE" else 0.0
    return out


def action_feature_vector(action: Action, observation: Dict[str, object] | None = None) -> List[float]:
    d = action_feature_dict(action, observation)
    return [float(d[name]) for name in ACTION_FEATURE_NAMES]


def frame_action_feature_matrix(frame: DecisionFrame) -> List[List[float]]:
    return [action_feature_vector(action, frame.observation) for action in frame.legal_actions]
